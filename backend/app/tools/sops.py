"""SOP indexing and retrieval — vector (embeddings) + keyword fallback."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import SopChunk
from app.services.embeddings import cosine_similarity, embed_texts_sync

SOPS_DIR = Path(__file__).resolve().parents[1] / "knowledge" / "sops"

CATEGORY_FROM_FILE = {
    "food.md": "Food",
    "medical.md": "Medical",
    "shelter.md": "Shelter",
    "blood.md": "Blood",
    "education.md": "Education",
    "integrity_hitl.md": "Other",
    "urdu_faq.md": "Other",
}


def _parse_front_meta(text_body: str) -> tuple[str, str, str]:
    title = "SOP"
    category = "Other"
    keywords = ""
    for line in text_body.splitlines()[:12]:
        if line.startswith("# "):
            title = line[2:].strip()
        if "**Category:**" in line:
            category = line.split("**Category:**", 1)[1].strip()
        if "**Keywords:**" in line:
            keywords = line.split("**Keywords:**", 1)[1].strip()
    return title, category, keywords


def _strip_markdown_inline(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return text.strip()


def _build_excerpt(body: str) -> str:
    """Plain-text excerpt: skip title/meta lines and markdown formatting."""
    parts: list[str] = []
    for line in body.replace("\r\n", "\n").split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith("# "):
            continue
        if "**Category:**" in s or "**Keywords:**" in s:
            continue
        if s.startswith("## "):
            continue
        parts.append(_strip_markdown_inline(s))
    text = re.sub(r"\s+", " ", " ".join(parts)).strip()
    return text[:280]


def _chunk_to_hit(chunk: SopChunk, score: float, mode: str) -> dict[str, Any]:
    excerpt_text = _build_excerpt(chunk.body)
    return {
        "id": chunk.id,
        "title": chunk.title,
        "category": chunk.category,
        "excerpt": excerpt_text,
        "score": round(float(score), 4),
        "source_file": chunk.source_file,
        "retrieval_mode": mode,
    }


def _sync_pgvector(db: Session, chunk_id: str, embedding: list[float]) -> None:
    if not settings.is_postgres or not embedding:
        return
    if len(embedding) != settings.embedding_dim:
        return
    vec_literal = "[" + ",".join(str(float(x)) for x in embedding) + "]"
    try:
        db.execute(
            text(
                "UPDATE sop_chunks SET embedding_vec = CAST(:v AS vector) WHERE id = :id"
            ),
            {"v": vec_literal, "id": chunk_id},
        )
    except Exception:
        # Column may be missing on some hosts
        pass


def index_sops_from_files(db: Session, *, force: bool = False, embed: bool = True) -> int:
    """Load SOP markdown into sop_chunks. Optionally embed with DashScope."""
    if not force and db.query(SopChunk).count() > 0:
        # Backfill embeddings if missing and key present
        if embed and settings.dashscope_api_key:
            _embed_missing(db)
        return db.query(SopChunk).count()

    if force:
        db.query(SopChunk).delete()
        db.commit()

    if not SOPS_DIR.exists():
        return 0

    chunks: list[SopChunk] = []
    for path in sorted(SOPS_DIR.glob("*.md")):
        body = path.read_text(encoding="utf-8")
        title, category, keywords = _parse_front_meta(body)
        category = CATEGORY_FROM_FILE.get(path.name, category)
        chunk = SopChunk(
            id=str(uuid.uuid4()),
            category=category,
            title=title,
            body=body,
            keywords=keywords,
            source_file=path.name,
            embedding=None,
        )
        db.add(chunk)
        chunks.append(chunk)
    db.commit()

    if embed and settings.dashscope_api_key and chunks:
        _embed_chunks(db, chunks)
    return len(chunks)


def _embed_chunks(db: Session, chunks: list[SopChunk]) -> None:
    texts = [f"{c.title}\n{c.keywords or ''}\n{c.body[:2000]}" for c in chunks]
    try:
        vectors = embed_texts_sync(texts)
    except Exception as exc:  # noqa: BLE001
        print(f"[sops] embed failed: {exc}")
        return
    for chunk, vec in zip(chunks, vectors):
        if vec:
            chunk.embedding = vec
            _sync_pgvector(db, chunk.id, vec)
    db.commit()


def _embed_missing(db: Session) -> None:
    missing = db.query(SopChunk).filter(SopChunk.embedding.is_(None)).all()
    if missing:
        _embed_chunks(db, missing)
    # JSON embeddings may exist before pgvector column was added
    sync_embedding_vec_from_json(db)


def sync_embedding_vec_from_json(db: Session) -> int:
    """Copy JSON embeddings into embedding_vec when the pgvector column is empty."""
    if not settings.is_postgres:
        return 0
    rows = db.query(SopChunk).filter(SopChunk.embedding.isnot(None)).all()
    synced = 0
    for chunk in rows:
        emb = chunk.embedding or []
        if not emb or len(emb) != settings.embedding_dim:
            continue
        try:
            exists = db.execute(
                text(
                    "SELECT embedding_vec IS NOT NULL FROM sop_chunks WHERE id = :id"
                ),
                {"id": chunk.id},
            ).scalar()
        except Exception:
            return synced
        if exists:
            continue
        _sync_pgvector(db, chunk.id, emb)
        synced += 1
    if synced:
        db.commit()
    return synced


def _search_keyword(
    db: Session,
    *,
    category: Optional[str],
    query: str,
    limit: int,
) -> list[dict[str, Any]]:
    rows = db.query(SopChunk).all()
    if not rows:
        index_sops_from_files(db, embed=False)
        rows = db.query(SopChunk).all()

    tokens = {t.lower() for t in re.findall(r"[a-zA-Z0-9\u0600-\u06FF]+", query) if len(t) > 2}
    scored: list[tuple[float, SopChunk]] = []
    for chunk in rows:
        score = 0.0
        if category and chunk.category.lower() == category.lower():
            score += 3.0
        elif category and chunk.category == "Other":
            score += 0.5
        hay = f"{chunk.title} {chunk.keywords or ''} {chunk.body}".lower()
        for token in tokens:
            if token in hay:
                score += 1.0
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda item: -item[0])
    if not scored and category:
        scored = [(1.0, c) for c in rows if c.category.lower() == category.lower()]
    if not scored:
        scored = [(0.5, c) for c in rows[:limit]]

    return [_chunk_to_hit(c, s, "keyword") for s, c in scored[:limit]]


def _search_vector_python(
    db: Session,
    *,
    category: Optional[str],
    query: str,
    limit: int,
) -> list[dict[str, Any]] | None:
    rows = db.query(SopChunk).filter(SopChunk.embedding.isnot(None)).all()
    if not rows:
        return None
    try:
        q_vecs = embed_texts_sync([query])
    except Exception:
        return None
    if not q_vecs or not q_vecs[0]:
        return None
    q = q_vecs[0]
    scored: list[tuple[float, SopChunk]] = []
    for chunk in rows:
        emb = chunk.embedding or []
        sim = cosine_similarity(q, emb)
        if category and chunk.category.lower() == category.lower():
            sim += 0.05
        scored.append((sim, chunk))
    scored.sort(key=lambda item: -item[0])
    return [_chunk_to_hit(c, s, "vector") for s, c in scored[:limit]]


def _search_vector_pg(
    db: Session,
    *,
    category: Optional[str],
    query: str,
    limit: int,
) -> list[dict[str, Any]] | None:
    if not settings.is_postgres:
        return None
    try:
        q_vecs = embed_texts_sync([query])
    except Exception:
        return None
    if not q_vecs or not q_vecs[0]:
        return None
    vec_literal = "[" + ",".join(str(float(x)) for x in q_vecs[0]) + "]"
    sql = """
        SELECT id, 1 - (embedding_vec <=> CAST(:v AS vector)) AS score
        FROM sop_chunks
        WHERE embedding_vec IS NOT NULL
    """
    params: dict[str, Any] = {"v": vec_literal, "lim": limit}
    if category:
        sql += " AND (category = :cat OR category = 'Other')"
        params["cat"] = category
    sql += " ORDER BY embedding_vec <=> CAST(:v AS vector) LIMIT :lim"
    try:
        rows = db.execute(text(sql), params).fetchall()
    except Exception:
        return None
    if not rows:
        return None
    results: list[dict[str, Any]] = []
    for row in rows:
        chunk = db.query(SopChunk).filter(SopChunk.id == row[0]).first()
        if chunk:
            results.append(_chunk_to_hit(chunk, float(row[1] or 0), "vector"))
    return results or None


def search_sops(
    db: Session,
    *,
    category: Optional[str] = None,
    query: str = "",
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Vector retrieval when embeddings exist; keyword fallback otherwise."""
    if not db.query(SopChunk).count():
        index_sops_from_files(db)

    if settings.dashscope_api_key:
        hits = _search_vector_pg(db, category=category, query=query, limit=limit)
        if hits:
            return hits
        hits = _search_vector_python(db, category=category, query=query, limit=limit)
        if hits:
            return hits

    return _search_keyword(db, category=category, query=query, limit=limit)

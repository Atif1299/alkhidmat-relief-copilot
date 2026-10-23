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

# Cross-cutting SOPs are never returned by category search; they are attached
# explicitly (Language for Urdu requests, Integrity when the gate flags a case).
LANGUAGE_CATEGORY = "Language"
INTEGRITY_CATEGORY = "Integrity"
CROSS_CUTTING = {LANGUAGE_CATEGORY, INTEGRITY_CATEGORY}

INTEGRITY_DUPLICATE_SOP = "integrity_duplicates.md"
INTEGRITY_ESCALATION_SOP = "integrity_escalation.md"

DEFAULT_MARKER = "**Default:** yes"

# A second SOP is shown only when it scores at least this share of the best one.
KEYWORD_KEEP_RATIO = 0.5
# Vector hits within this cosine distance of the best hit are kept.
VECTOR_KEEP_MARGIN = 0.05

_STOPWORDS = {
    "the", "and", "for", "with", "need", "needs", "help", "please", "phone", "lahore",
    "family", "our", "are", "has", "have", "from", "this", "that", "hai", "hain", "aur",
    "mein", "kay", "ke", "ki", "ko", "bhi",
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
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text.strip()


def _is_table_sep(line: str) -> bool:
    s = line.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")
    return line.startswith("|") and not s


def _parse_table_row(line: str) -> list[str]:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return [_strip_markdown_inline(c) for c in cells if c]


def _citation_from_body(body: str) -> tuple[str, list[str]]:
    """Readable SOP card: purpose sentence + complete rules/phrases (no raw markdown)."""
    purpose = ""
    points: list[str] = []
    section = ""
    table_header: list[str] = []
    for raw in body.replace("\r\n", "\n").split("\n"):
        line = raw.strip()
        if not line or line.startswith("# "):
            continue
        if "**Category:**" in line or "**Keywords:**" in line or "**Default:**" in line:
            continue
        if line.startswith("## "):
            section = line[3:].strip().lower()
            table_header = []
            continue
        if line.startswith("|"):
            if _is_table_sep(line):
                continue
            cells = _parse_table_row(line)
            if not cells:
                continue
            if not table_header:
                table_header = [c.lower() for c in cells]
                continue
            phrase = cells[0]
            meaning = cells[1] if len(cells) > 1 else ""
            category = cells[2] if len(cells) > 2 else ""
            if meaning and category:
                points.append(f"{phrase} — {meaning} ({category})")
            elif meaning:
                points.append(f"{phrase} — {meaning}")
            else:
                points.append(phrase)
            continue
        numbered = re.match(r"^(\d+)\.\s+(.*)$", line)
        if numbered:
            points.append(_strip_markdown_inline(numbered.group(2)))
            continue
        text = _strip_markdown_inline(line)
        if not text:
            continue
        if section == "purpose" and not purpose:
            purpose = text
        elif not purpose and section in ("", "purpose"):
            purpose = text
    points = [p for p in points if p][:6]
    if not purpose and points:
        purpose = points[0]
        points = points[1:]
    return purpose, points


def _chunk_to_hit(chunk: SopChunk, score: float, mode: str) -> dict[str, Any]:
    purpose, points = _citation_from_body(chunk.body)
    return {
        "id": chunk.id,
        "title": chunk.title,
        "category": chunk.category,
        "excerpt": purpose,
        "points": points,
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


def _read_sop_files() -> dict[str, str]:
    if not SOPS_DIR.exists():
        return {}
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(SOPS_DIR.glob("*.md"))}


def index_sops_from_files(db: Session, *, force: bool = False, embed: bool = True) -> int:
    """Load SOP markdown into sop_chunks. Optionally embed with DashScope.

    Rebuilds whenever the files on disk differ from the indexed copy, so a
    deploy with new or edited SOPs reindexes on startup without a manual step.
    """
    files = _read_sop_files()
    rows = db.query(SopChunk).all()
    in_sync = bool(rows) and {r.source_file: r.body for r in rows} == files
    if not force and in_sync:
        # Backfill embeddings if missing and key present
        if embed and settings.dashscope_api_key:
            _embed_missing(db)
        return len(rows)

    if rows:
        db.query(SopChunk).delete()
        db.commit()

    chunks: list[SopChunk] = []
    for name, body in files.items():
        title, category, keywords = _parse_front_meta(body)
        chunk = SopChunk(
            id=str(uuid.uuid4()),
            category=category,
            title=title,
            body=body,
            keywords=keywords,
            source_file=name,
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


def _tokens(value: str) -> set[str]:
    return {
        t
        for t in re.findall(r"[a-z0-9؀-ۿ]+", value.lower())
        if len(t) > 2 and t not in _STOPWORDS
    }


def _is_default(chunk: SopChunk) -> bool:
    return DEFAULT_MARKER in (chunk.body or "")


def _category_chunks(db: Session, category: str) -> list[SopChunk]:
    rows = db.query(SopChunk).filter(SopChunk.category == category).all()
    # Default SOP first, then by file name, so ties are stable.
    return sorted(rows, key=lambda c: (not _is_default(c), c.source_file))


def _search_keyword(
    db: Session,
    *,
    category: str,
    query: str,
    limit: int,
) -> list[dict[str, Any]]:
    rows = _category_chunks(db, category)
    if not rows:
        return []

    q = _tokens(query)
    scored: list[tuple[float, SopChunk]] = []
    for chunk in rows:
        keywords = _tokens(chunk.keywords or "")
        title = _tokens(chunk.title)
        body = _tokens(chunk.body) - keywords - title
        score = 2.0 * len(q & keywords) + 1.0 * len(q & title) + 0.5 * len(q & body)
        scored.append((score, chunk))
    # Stable sort keeps the default SOP ahead on ties.
    scored.sort(key=lambda item: -item[0])

    top = scored[0][0]
    if top <= 0:
        return [_chunk_to_hit(scored[0][1], 0.0, "keyword")]
    floor = max(1.0, top * KEYWORD_KEEP_RATIO)
    kept = [(s, c) for s, c in scored if s >= floor][:limit]
    return [_chunk_to_hit(c, s, "keyword") for s, c in kept]


def _keep_vector(scored: list[tuple[float, SopChunk]], limit: int) -> list[dict[str, Any]]:
    scored.sort(key=lambda item: -item[0])
    top = scored[0][0]
    kept = [(s, c) for s, c in scored if s >= top - VECTOR_KEEP_MARGIN][:limit]
    return [_chunk_to_hit(c, s, "vector") for s, c in kept]


def _search_vector_python(
    db: Session,
    *,
    category: str,
    query: str,
    limit: int,
) -> list[dict[str, Any]] | None:
    rows = [c for c in _category_chunks(db, category) if c.embedding]
    if not rows:
        return None
    try:
        q_vecs = embed_texts_sync([query])
    except Exception:
        return None
    if not q_vecs or not q_vecs[0]:
        return None
    q = q_vecs[0]
    scored = [(cosine_similarity(q, chunk.embedding or []), chunk) for chunk in rows]
    return _keep_vector(scored, limit)


def _search_vector_pg(
    db: Session,
    *,
    category: str,
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
        WHERE embedding_vec IS NOT NULL AND category = :cat
        ORDER BY embedding_vec <=> CAST(:v AS vector)
    """
    try:
        rows = db.execute(text(sql), {"v": vec_literal, "cat": category}).fetchall()
    except Exception:
        return None
    if not rows:
        return None
    by_id = {c.id: c for c in _category_chunks(db, category)}
    scored = [(float(row[1] or 0), by_id[row[0]]) for row in rows if row[0] in by_id]
    return _keep_vector(scored, limit) if scored else None


def sop_hits_for_files(db: Session, source_files: list[str], mode: str) -> list[dict[str, Any]]:
    """Attach specific SOPs by file name (cross-cutting guidance)."""
    if not source_files:
        return []
    rows = db.query(SopChunk).filter(SopChunk.source_file.in_(source_files)).all()
    order = {name: i for i, name in enumerate(source_files)}
    rows.sort(key=lambda c: order.get(c.source_file, 99))
    return [_chunk_to_hit(c, 1.0, mode) for c in rows]


def merge_sop_hits(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    for group in groups:
        for hit in group or []:
            key = hit.get("source_file") or hit.get("title") or ""
            if key in seen:
                continue
            seen.add(key)
            merged.append(hit)
    return merged


def search_sops(
    db: Session,
    *,
    category: Optional[str] = None,
    query: str = "",
    limit: int = 2,
    language: Optional[str] = None,
) -> list[dict[str, Any]]:
    """SOPs for the case's own category only, best first, weak matches dropped.

    Vector retrieval when embeddings exist; keyword fallback otherwise. Urdu
    requests also get the Urdu phrase guide.
    """
    if not db.query(SopChunk).count():
        index_sops_from_files(db)

    hits: list[dict[str, Any]] = []
    if category and category not in CROSS_CUTTING:
        if settings.dashscope_api_key:
            hits = _search_vector_pg(db, category=category, query=query, limit=limit) or []
            if not hits:
                hits = _search_vector_python(db, category=category, query=query, limit=limit) or []
        if not hits:
            hits = _search_keyword(db, category=category, query=query, limit=limit)

    if language == "ur":
        language_files = [c.source_file for c in _category_chunks(db, LANGUAGE_CATEGORY)]
        hits = merge_sop_hits(hits, sop_hits_for_files(db, language_files[:1], "language"))
    return hits

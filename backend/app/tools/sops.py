"""SOP indexing and keyword retrieval for Knowledge agent."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.db.models import SopChunk

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


def _parse_front_meta(text: str) -> tuple[str, str, str]:
    """Extract title, category line, keywords from markdown."""
    title = "SOP"
    category = "Other"
    keywords = ""
    for line in text.splitlines()[:12]:
        if line.startswith("# "):
            title = line[2:].strip()
        if "**Category:**" in line:
            category = line.split("**Category:**", 1)[1].strip()
        if "**Keywords:**" in line:
            keywords = line.split("**Keywords:**", 1)[1].strip()
    return title, category, keywords


def index_sops_from_files(db: Session, *, force: bool = False) -> int:
    """Load SOP markdown into sop_chunks. Rebuild if empty or force=True."""
    if not force and db.query(SopChunk).count() > 0:
        return db.query(SopChunk).count()

    if force:
        db.query(SopChunk).delete()
        db.commit()

    if not SOPS_DIR.exists():
        return 0

    count = 0
    for path in sorted(SOPS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title, category, keywords = _parse_front_meta(text)
        category = CATEGORY_FROM_FILE.get(path.name, category)
        db.add(
            SopChunk(
                id=str(uuid.uuid4()),
                category=category,
                title=title,
                body=text,
                keywords=keywords,
                source_file=path.name,
            )
        )
        count += 1
    db.commit()
    return count


def search_sops(
    db: Session,
    *,
    category: Optional[str] = None,
    query: str = "",
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Keyword + category filter over sop_chunks."""
    rows = db.query(SopChunk).all()
    if not rows:
        index_sops_from_files(db)
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
        # Fallback: top category SOPs
        scored = [(1.0, c) for c in rows if c.category.lower() == category.lower()]
    if not scored:
        scored = [(0.5, c) for c in rows[:limit]]

    results: list[dict[str, Any]] = []
    for score, chunk in scored[:limit]:
        excerpt = chunk.body.strip().replace("\r\n", "\n")
        # Prefer first rules bullet block
        lines = [ln.strip() for ln in excerpt.split("\n") if ln.strip()]
        excerpt_text = " ".join(lines[1:6])[:280]
        results.append(
            {
                "id": chunk.id,
                "title": chunk.title,
                "category": chunk.category,
                "excerpt": excerpt_text,
                "score": round(score, 2),
                "source_file": chunk.source_file,
            }
        )
    return results

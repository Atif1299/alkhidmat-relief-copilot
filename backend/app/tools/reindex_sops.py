"""CLI: reindex SOP corpus and (re)embed for Knowledge RAG.

Usage (from backend/):
  python -m app.tools.reindex_sops
  python -m app.tools.reindex_sops --force
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reindex SOP chunks + embeddings")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing sop_chunks and rebuild from markdown files",
    )
    parser.add_argument(
        "--no-embed",
        action="store_true",
        help="Index text only (skip DashScope embeddings)",
    )
    args = parser.parse_args(argv)

    from app.db.session import SessionLocal, init_db
    from app.tools.sops import index_sops_from_files, sync_embedding_vec_from_json

    init_db()
    db = SessionLocal()
    try:
        n = index_sops_from_files(db, force=args.force, embed=not args.no_embed)
        synced = sync_embedding_vec_from_json(db)
        print(f"Indexed {n} SOP chunk(s); synced {synced} embedding_vec row(s).")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

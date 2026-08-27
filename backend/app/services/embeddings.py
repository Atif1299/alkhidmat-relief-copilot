"""DashScope embeddings + cosine helpers for Knowledge RAG."""

from __future__ import annotations

import math
from typing import Any

import httpx

from app.config import settings


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed via DashScope OpenAI-compatible embeddings API. Empty if no key."""
    if not texts:
        return []
    if not settings.dashscope_api_key:
        return [[] for _ in texts]

    url = settings.dashscope_base_url.rstrip("/") + "/embeddings"
    headers = {
        "Authorization": f"Bearer {settings.dashscope_api_key}",
        "Content-Type": "application/json",
    }
    # Batch in chunks of 8 to stay under provider limits
    out: list[list[float]] = [[] for _ in texts]
    batch_size = 8
    async with httpx.AsyncClient(timeout=60.0) as client:
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            payload: dict[str, Any] = {
                "model": settings.dashscope_embedding_model,
                "input": batch if len(batch) > 1 else batch[0],
            }
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("data") or []
            # OpenAI-style: data[].embedding with index
            for item in items:
                idx = item.get("index", 0)
                emb = item.get("embedding") or []
                out[start + idx] = emb
            # Some providers return parallel order without index
            if items and all(i.get("index") is None for i in items):
                for offset, item in enumerate(items):
                    out[start + offset] = item.get("embedding") or []
    return out


def embed_texts_sync(texts: list[str]) -> list[list[float]]:
    """Sync wrapper for seed/index paths."""
    if not texts:
        return []
    if not settings.dashscope_api_key:
        return [[] for _ in texts]

    url = settings.dashscope_base_url.rstrip("/") + "/embeddings"
    headers = {
        "Authorization": f"Bearer {settings.dashscope_api_key}",
        "Content-Type": "application/json",
    }
    out: list[list[float]] = [[] for _ in texts]
    batch_size = 8
    with httpx.Client(timeout=60.0) as client:
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            payload: dict[str, Any] = {
                "model": settings.dashscope_embedding_model,
                "input": batch if len(batch) > 1 else batch[0],
            }
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("data") or []
            for item in items:
                idx = item.get("index")
                emb = item.get("embedding") or []
                if idx is not None:
                    out[start + idx] = emb
            if items and all(i.get("index") is None for i in items):
                for offset, item in enumerate(items):
                    out[start + offset] = item.get("embedding") or []
    return out

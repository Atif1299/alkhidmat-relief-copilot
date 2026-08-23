"""Pydantic request schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    case_id: Optional[str] = None


class DecideRequest(BaseModel):
    decision: str = Field(pattern="^(approve|reject)$")
    note: Optional[str] = None

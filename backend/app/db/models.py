"""SQLAlchemy models for the Aid Desk."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticket_id: Mapped[Optional[str]] = mapped_column(String(32), unique=True, nullable=True)
    raw_message: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(8), default="en")
    category: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="processing")
    # pending_hitl | open | dispatched | rejected | closed | flagged_duplicate

    requester_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    requester_phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    need_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    duplicate_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_hitl: Mapped[bool] = mapped_column(Boolean, default=False)
    hitl_decision: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    hitl_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    matched_resource_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("resources.id"), nullable=True
    )
    volunteer_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("volunteers.id"), nullable=True
    )

    agent_trace: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    time_to_ticket_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    matched_resource = relationship("Resource", foreign_keys=[matched_resource_id])
    volunteer = relationship("Volunteer", foreign_keys=[volunteer_id])
    events = relationship("CaseEvent", back_populates="case", cascade="all, delete-orphan")


class CaseEvent(Base):
    __tablename__ = "case_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    actor: Mapped[str] = mapped_column(String(64))
    event_type: Mapped[str] = mapped_column(String(64))
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="events")


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    category: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(256))
    city: Mapped[str] = mapped_column(String(64), default="Lahore")
    area: Mapped[str] = mapped_column(String(128))
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    contact: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Volunteer(Base):
    __tablename__ = "volunteers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    phone: Mapped[str] = mapped_column(String(32))
    skills: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    area: Mapped[str] = mapped_column(String(128))
    available: Mapped[bool] = mapped_column(Boolean, default=True)

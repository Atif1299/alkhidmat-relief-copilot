"""Lahore seed data for demo scenarios."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.db.models import Case, Resource, Volunteer
from app.db.session import SessionLocal, init_db

# Demo duplicate phone (Tier A acceptance)
DUPLICATE_DEMO_PHONE = "03001234567"

RESOURCES = [
    {"category": "Food", "name": "Alkhidmat Lahore Kitchen", "area": "Township", "stock": 120, "capacity": 200, "contact": "042-111-300-800"},
    {"category": "Food", "name": "Food Pack Depot Johar Town", "area": "Johar Town", "stock": 80, "capacity": 100, "contact": "0300-1112233"},
    {"category": "Food", "name": "Community Kitchen Model Town", "area": "Model Town", "stock": 45, "capacity": 60, "contact": "0300-4455667"},
    {"category": "Medical", "name": "Alkhidmat Mobile Clinic", "area": "Johar Town", "stock": 10, "capacity": 15, "contact": "042-35789012"},
    {"category": "Medical", "name": "Emergency First Aid Unit", "area": "Gulberg", "stock": 8, "capacity": 12, "contact": "0301-9988776"},
    {"category": "Shelter", "name": "Temporary Camp Johar Town", "area": "Johar Town", "stock": 40, "capacity": 40, "contact": "0302-5566778"},
    {"category": "Shelter", "name": "Relief Shelter Raiwind Road", "area": "Raiwind", "stock": 25, "capacity": 50, "contact": "0303-1122334"},
    {"category": "Blood", "name": "Sundas Foundation Blood Bank", "area": "Jail Road", "stock": 30, "capacity": 50, "contact": "042-111-178-632"},
    {"category": "Blood", "name": "Alkhidmat Blood Centre", "area": "Garden Town", "stock": 18, "capacity": 40, "contact": "0304-6677889"},
    {"category": "Education", "name": "School Kit Distribution Hub", "area": "Allama Iqbal Town", "stock": 200, "capacity": 300, "contact": "0305-2233445"},
    {"category": "Other", "name": "General Relief Warehouse", "area": "Thokar Niaz Baig", "stock": 60, "capacity": 100, "contact": "0306-3344556"},
]

VOLUNTEERS = [
    {"name": "Ahmed Khan", "phone": "03011110001", "skills": ["Food", "Logistics"], "area": "Township"},
    {"name": "Fatima Ali", "phone": "03011110002", "skills": ["Medical", "FirstAid"], "area": "Johar Town"},
    {"name": "Bilal Hassan", "phone": "03011110003", "skills": ["Shelter", "Transport"], "area": "Model Town"},
    {"name": "Ayesha Raza", "phone": "03011110004", "skills": ["Blood", "Coordination"], "area": "Gulberg"},
    {"name": "Usman Malik", "phone": "03011110005", "skills": ["Food", "Volunteer"], "area": "Johar Town"},
    {"name": "Sara Iqbal", "phone": "03011110006", "skills": ["Education", "Outreach"], "area": "Allama Iqbal Town"},
    {"name": "Hamza Siddiqui", "phone": "03011110007", "skills": ["Medical", "Ambulance"], "area": "Gulberg"},
    {"name": "Zainab Noor", "phone": "03011110008", "skills": ["Shelter", "Food"], "area": "Raiwind"},
    {"name": "Omar Farooq", "phone": "03011110009", "skills": ["Logistics", "Other"], "area": "Thokar Niaz Baig"},
    {"name": "Maryam Shah", "phone": "03011110010", "skills": ["Blood", "Medical"], "area": "Garden Town"},
]


def _uid() -> str:
    return str(uuid.uuid4())


def seed_if_empty(db: Session) -> dict:
    """Seed Lahore demo data if tables are empty."""
    if db.query(Resource).count() == 0:
        for r in RESOURCES:
            db.add(
                Resource(
                    id=_uid(),
                    category=r["category"],
                    name=r["name"],
                    city="Lahore",
                    area=r["area"],
                    stock=r["stock"],
                    capacity=r["capacity"],
                    contact=r["contact"],
                    active=True,
                )
            )

    if db.query(Volunteer).count() == 0:
        for v in VOLUNTEERS:
            db.add(
                Volunteer(
                    id=_uid(),
                    name=v["name"],
                    phone=v["phone"],
                    skills=v["skills"],
                    area=v["area"],
                    available=True,
                )
            )

    if db.query(Case).count() == 0:
        db.add(
            Case(
                id=_uid(),
                ticket_id="AKD-SEED-001",
                raw_message="Need food packs for family after rain, Township Lahore",
                language="en",
                category="Food",
                priority="medium",
                status="dispatched",
                requester_name="Seed Requester",
                requester_phone=DUPLICATE_DEMO_PHONE,
                location="Township Lahore",
                need_summary="Food packs for family",
                risk_score=0.1,
                duplicate_flag=False,
                requires_hitl=False,
                agent_trace=[{"agent": "seed", "action": "preloaded_case"}],
            )
        )

    db.commit()
    return {
        "resources": db.query(Resource).count(),
        "volunteers": db.query(Volunteer).count(),
        "cases": db.query(Case).count(),
        "duplicate_demo_phone": DUPLICATE_DEMO_PHONE,
    }


def run_seed() -> dict:
    init_db()
    db = SessionLocal()
    try:
        return seed_if_empty(db)
    finally:
        db.close()


if __name__ == "__main__":
    print(run_seed())

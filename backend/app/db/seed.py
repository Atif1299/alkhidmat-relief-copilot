"""Lahore seed data for demo scenarios (Tier B expanded)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import Case, CaseEvent, Resource, User, Volunteer
from app.db.session import SessionLocal, init_db
from app.services.security import hash_password
from app.tools.sops import index_sops_from_files

# Demo duplicate phone (Tier A acceptance)
DUPLICATE_DEMO_PHONE = "03001234567"
HITL_STATUS_DEMO_TICKET = "AKD-SEED-006"
HITL_STATUS_DEMO_PHONE = "03019991111"

# Tier 3 seeded users (demo password for all)
DEMO_PASSWORD = "AidDesk!2026"
SEED_USERS = [
    {"email": "citizen@aiddesk.example", "role": "requester"},
    {"email": "desk@aiddesk.example", "role": "desk"},
    {"email": "supervisor@aiddesk.example", "role": "supervisor"},
]

RESOURCES = [
    # Food
    {"category": "Food", "name": "Alkhidmat Lahore Kitchen", "area": "Township", "stock": 120, "capacity": 200, "contact": "042-111-300-800"},
    {"category": "Food", "name": "Food Pack Depot Johar Town", "area": "Johar Town", "stock": 80, "capacity": 100, "contact": "0300-1112233"},
    {"category": "Food", "name": "Community Kitchen Model Town", "area": "Model Town", "stock": 45, "capacity": 60, "contact": "0300-4455667"},
    {"category": "Food", "name": "Ration Point Gulberg", "area": "Gulberg", "stock": 55, "capacity": 80, "contact": "0300-5566771"},
    {"category": "Food", "name": "Kitchen Allama Iqbal Town", "area": "Allama Iqbal Town", "stock": 70, "capacity": 90, "contact": "0300-6677882"},
    {"category": "Food", "name": "Thokar Relief Kitchen", "area": "Thokar Niaz Baig", "stock": 40, "capacity": 70, "contact": "0300-7788993"},
    # Medical
    {"category": "Medical", "name": "Alkhidmat Mobile Clinic", "area": "Johar Town", "stock": 10, "capacity": 15, "contact": "042-35789012"},
    {"category": "Medical", "name": "Emergency First Aid Unit", "area": "Gulberg", "stock": 8, "capacity": 12, "contact": "0301-9988776"},
    {"category": "Medical", "name": "Township Field Clinic", "area": "Township", "stock": 12, "capacity": 20, "contact": "0301-1122334"},
    {"category": "Medical", "name": "Model Town Health Desk", "area": "Model Town", "stock": 6, "capacity": 10, "contact": "0301-2233445"},
    {"category": "Medical", "name": "Raiwind Ambulance Post", "area": "Raiwind", "stock": 2, "capacity": 4, "contact": "0301-3344556"},
    # Shelter
    {"category": "Shelter", "name": "Temporary Camp Johar Town", "area": "Johar Town", "stock": 40, "capacity": 40, "contact": "0302-5566778"},
    {"category": "Shelter", "name": "Relief Shelter Raiwind Road", "area": "Raiwind", "stock": 25, "capacity": 50, "contact": "0303-1122334"},
    {"category": "Shelter", "name": "Township Night Shelter", "area": "Township", "stock": 18, "capacity": 30, "contact": "0302-6677889"},
    {"category": "Shelter", "name": "Thokar Family Camp", "area": "Thokar Niaz Baig", "stock": 22, "capacity": 35, "contact": "0302-7788990"},
    {"category": "Shelter", "name": "Gulberg Transit Shelter", "area": "Gulberg", "stock": 10, "capacity": 20, "contact": "0302-8899001"},
    # Blood
    {"category": "Blood", "name": "Sundas Foundation Blood Bank", "area": "Jail Road", "stock": 30, "capacity": 50, "contact": "042-111-178-632"},
    {"category": "Blood", "name": "Alkhidmat Blood Centre", "area": "Garden Town", "stock": 18, "capacity": 40, "contact": "0304-6677889"},
    {"category": "Blood", "name": "Johar Town Blood Desk", "area": "Johar Town", "stock": 12, "capacity": 25, "contact": "0304-7788991"},
    {"category": "Blood", "name": "Model Town Donor Camp", "area": "Model Town", "stock": 9, "capacity": 20, "contact": "0304-8899002"},
    # Education
    {"category": "Education", "name": "School Kit Distribution Hub", "area": "Allama Iqbal Town", "stock": 200, "capacity": 300, "contact": "0305-2233445"},
    {"category": "Education", "name": "Township Learning Support", "area": "Township", "stock": 90, "capacity": 120, "contact": "0305-3344556"},
    {"category": "Education", "name": "Gulberg Education Desk", "area": "Gulberg", "stock": 60, "capacity": 80, "contact": "0305-4455667"},
    {"category": "Education", "name": "Johar Town School Kits", "area": "Johar Town", "stock": 75, "capacity": 100, "contact": "0305-5566778"},
    # Other
    {"category": "Other", "name": "General Relief Warehouse", "area": "Thokar Niaz Baig", "stock": 60, "capacity": 100, "contact": "0306-3344556"},
    {"category": "Other", "name": "Logistics Hub Raiwind", "area": "Raiwind", "stock": 40, "capacity": 80, "contact": "0306-4455667"},
    {"category": "Other", "name": "Volunteer Coordination Desk", "area": "Jail Road", "stock": 25, "capacity": 50, "contact": "0306-5566778"},
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
    {"name": "Imran Qureshi", "phone": "03011110011", "skills": ["Food", "Shelter"], "area": "Township"},
    {"name": "Nadia Butt", "phone": "03011110012", "skills": ["Education", "Food"], "area": "Model Town"},
    {"name": "Kashif Mehmood", "phone": "03011110013", "skills": ["Blood", "Logistics"], "area": "Jail Road"},
    {"name": "Hina Tariq", "phone": "03011110014", "skills": ["Medical", "Shelter"], "area": "Raiwind"},
    {"name": "Saad Anwar", "phone": "03011110015", "skills": ["Other", "Coordination"], "area": "Gulberg"},
]


def _uid() -> str:
    return str(uuid.uuid4())


def _seed_historical_cases(db: Session) -> None:
    """Preload cases + events for duplicate demo and timeline polish."""
    db.flush()
    now = datetime.utcnow()
    food_case_id = _uid()
    medical_case_id = _uid()
    shelter_case_id = _uid()
    blood_case_id = _uid()
    edu_case_id = _uid()
    hitl_case_id = _uid()
    kitchen = db.query(Resource).filter(Resource.name == "Alkhidmat Lahore Kitchen").first()
    volunteer = db.query(Volunteer).filter(Volunteer.name == "Ahmed Khan").first()

    cases = [
        Case(
            id=food_case_id,
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
            matched_resource_id=kitchen.id if kitchen else None,
            volunteer_id=volunteer.id if volunteer else None,
            agent_trace=[
                {"agent": "Intake", "action": "extracted"},
                {"agent": "Triage", "action": "classified", "detail": "Food"},
                {"agent": "Knowledge", "action": "sop_retrieved", "detail": "Food Relief SOP"},
                {"agent": "Integrity", "action": "cleared"},
                {"agent": "Matcher", "action": "matched"},
                {"agent": "Dispatch", "action": "ticket_created"},
            ],
            created_at=now - timedelta(hours=6),
            time_to_ticket_ms=42000,
        ),
        Case(
            id=medical_case_id,
            ticket_id="AKD-SEED-002",
            raw_message="Fever and medicine needed, Gulberg Lahore",
            language="en",
            category="Medical",
            priority="medium",
            status="dispatched",
            requester_name="Ali Raza",
            requester_phone="03009876543",
            location="Gulberg Lahore",
            need_summary="Medicine and clinic referral",
            risk_score=0.2,
            duplicate_flag=False,
            requires_hitl=False,
            agent_trace=[{"agent": "seed", "action": "preloaded_medical"}],
            created_at=now - timedelta(days=1),
            time_to_ticket_ms=51000,
        ),
        Case(
            id=shelter_case_id,
            ticket_id="AKD-SEED-003",
            raw_message="Family of 4 needs overnight shelter after flood, Johar Town",
            language="en",
            category="Shelter",
            priority="high",
            status="dispatched",
            requester_name="Nida Khan",
            requester_phone="03005551234",
            location="Johar Town Lahore",
            need_summary="Overnight shelter for 4",
            risk_score=0.25,
            duplicate_flag=False,
            requires_hitl=False,
            agent_trace=[{"agent": "seed", "action": "preloaded_shelter"}],
            created_at=now - timedelta(days=2),
            time_to_ticket_ms=63000,
        ),
        Case(
            id=blood_case_id,
            ticket_id="AKD-SEED-004",
            raw_message="Need O+ blood for surgery tomorrow, Jail Road",
            language="en",
            category="Blood",
            priority="high",
            status="closed",
            requester_name="Hassan Ali",
            requester_phone="03004443322",
            location="Jail Road Lahore",
            need_summary="O+ blood units",
            risk_score=0.3,
            duplicate_flag=False,
            requires_hitl=False,
            agent_trace=[{"agent": "seed", "action": "preloaded_blood"}],
            created_at=now - timedelta(days=3),
            resolved_at=now - timedelta(days=2),
            time_to_ticket_ms=48000,
        ),
        Case(
            id=edu_case_id,
            ticket_id="AKD-SEED-005",
            raw_message="School kits for 3 children, Allama Iqbal Town",
            language="en",
            category="Education",
            priority="low",
            status="dispatched",
            requester_name="Sana Malik",
            requester_phone="03003332211",
            location="Allama Iqbal Town Lahore",
            need_summary="School kits x3",
            risk_score=0.05,
            duplicate_flag=False,
            requires_hitl=False,
            agent_trace=[{"agent": "seed", "action": "preloaded_education"}],
            created_at=now - timedelta(days=4),
            time_to_ticket_ms=35000,
        ),
        Case(
            id=hitl_case_id,
            ticket_id=HITL_STATUS_DEMO_TICKET,
            raw_message="Chest pain, need ambulance, Johar Town. Phone 03019991111",
            language="en",
            category="Medical",
            priority="critical",
            status="pending_hitl",
            requester_name="HITL Demo",
            requester_phone=HITL_STATUS_DEMO_PHONE,
            location="Johar Town Lahore",
            need_summary="Ambulance for chest pain",
            risk_score=0.9,
            duplicate_flag=False,
            requires_hitl=True,
            agent_trace=[
                {"agent": "Intake", "action": "extracted"},
                {"agent": "Triage", "action": "classified", "detail": "Medical critical"},
                {"agent": "Knowledge", "action": "sop_retrieved", "detail": "Medical Emergency SOP"},
                {"agent": "Integrity", "action": "escalated", "detail": "Critical priority"},
                {"agent": "Supervisor", "action": "awaiting", "detail": "Paused for human approval"},
            ],
            created_at=now - timedelta(minutes=25),
        ),
    ]
    db.add_all(cases)

    events = [
        (food_case_id, "system", "requested", "Case received"),
        (food_case_id, "Triage", "triaged", "Category Food"),
        (food_case_id, "Knowledge", "sop_retrieved", "Food Relief SOP"),
        (food_case_id, "Integrity", "integrity_checked", "Risk cleared"),
        (food_case_id, "Matcher", "matched", "Alkhidmat Lahore Kitchen"),
        (food_case_id, "Dispatch", "dispatched", "Ticket AKD-SEED-001"),
        (medical_case_id, "system", "requested", "Case received"),
        (medical_case_id, "Triage", "triaged", "Category Medical"),
        (medical_case_id, "Dispatch", "dispatched", "Ticket AKD-SEED-002"),
        (shelter_case_id, "system", "requested", "Case received"),
        (shelter_case_id, "Triage", "triaged", "Category Shelter"),
        (shelter_case_id, "Dispatch", "dispatched", "Ticket AKD-SEED-003"),
        (blood_case_id, "system", "requested", "Case received"),
        (blood_case_id, "Dispatch", "dispatched", "Ticket AKD-SEED-004"),
        (blood_case_id, "system", "closed", "Fulfilled"),
        (edu_case_id, "system", "requested", "Case received"),
        (edu_case_id, "Dispatch", "dispatched", "Ticket AKD-SEED-005"),
        (hitl_case_id, "system", "requested", "Case received"),
        (hitl_case_id, "Triage", "triaged", "Category Medical"),
        (hitl_case_id, "Knowledge", "sop_retrieved", "Medical Emergency SOP"),
        (hitl_case_id, "Integrity", "escalated", "Critical priority"),
    ]
    for case_id, actor, event_type, detail in events:
        db.add(
            CaseEvent(
                case_id=case_id,
                actor=actor,
                event_type=event_type,
                detail=detail,
            )
        )


def _seed_hitl_status_demo(db: Session) -> None:
    """Top-up a waiting HITL ticket for the public status demo."""
    hitl_case_id = _uid()
    now = datetime.utcnow()
    db.add(
        Case(
            id=hitl_case_id,
            ticket_id=HITL_STATUS_DEMO_TICKET,
            raw_message="Chest pain, need ambulance, Johar Town. Phone 03019991111",
            language="en",
            category="Medical",
            priority="critical",
            status="pending_hitl",
            requester_name="HITL Demo",
            requester_phone=HITL_STATUS_DEMO_PHONE,
            location="Johar Town Lahore",
            need_summary="Ambulance for chest pain",
            risk_score=0.9,
            duplicate_flag=False,
            requires_hitl=True,
            agent_trace=[
                {"agent": "Intake", "action": "extracted"},
                {"agent": "Triage", "action": "classified", "detail": "Medical critical"},
                {"agent": "Knowledge", "action": "sop_retrieved", "detail": "Medical Emergency SOP"},
                {"agent": "Integrity", "action": "escalated", "detail": "Critical priority"},
                {"agent": "Supervisor", "action": "awaiting", "detail": "Paused for human approval"},
            ],
            created_at=now - timedelta(minutes=25),
        )
    )
    db.add(
        CaseEvent(
            case_id=hitl_case_id,
            actor="system",
            event_type="requested",
            detail="Case received",
        )
    )
    db.add(
        CaseEvent(
            case_id=hitl_case_id,
            actor="Integrity",
            event_type="escalated",
            detail="Critical priority",
        )
    )


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
    else:
        # Top-up missing Tier B resources without wiping live data
        existing = {r.name for r in db.query(Resource).all()}
        for r in RESOURCES:
            if r["name"] not in existing:
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
    else:
        existing_v = {v.phone for v in db.query(Volunteer).all()}
        for v in VOLUNTEERS:
            if v["phone"] not in existing_v:
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
        _seed_historical_cases(db)
    else:
        # Keep duplicate-demo case fresh so Integrity 48h window still hits
        demo = (
            db.query(Case)
            .filter(Case.requester_phone == DUPLICATE_DEMO_PHONE)
            .order_by(Case.created_at.desc())
            .first()
        )
        if demo:
            demo.created_at = datetime.utcnow()
            demo.status = "dispatched"
        if not db.query(Case).filter(Case.ticket_id == HITL_STATUS_DEMO_TICKET).first():
            _seed_hitl_status_demo(db)

    sop_count = index_sops_from_files(db)

    # Tier 3 auth users
    existing_emails = {u.email for u in db.query(User).all()}
    for u in SEED_USERS:
        email = u["email"].lower()
        if email not in existing_emails:
            db.add(
                User(
                    id=_uid(),
                    email=email,
                    password_hash=hash_password(DEMO_PASSWORD),
                    role=u["role"],
                    active=True,
                )
            )

    db.commit()
    return {
        "resources": db.query(Resource).count(),
        "volunteers": db.query(Volunteer).count(),
        "cases": db.query(Case).count(),
        "sop_chunks": sop_count,
        "users": db.query(User).count(),
        "duplicate_demo_phone": DUPLICATE_DEMO_PHONE,
        "demo_password": DEMO_PASSWORD,
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

"""Guest status lookup — ticket + phone, no JWT."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import StatusRequest
from app.services.public_status import NOT_FOUND, lookup_public_status

router = APIRouter(prefix="/api/v1/public", tags=["public"])


@router.post("/status")
def public_status(body: StatusRequest, db: Session = Depends(get_db)):
    payload = lookup_public_status(db, ticket_id=body.ticket_id, phone=body.phone)
    if payload is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return payload

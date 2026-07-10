from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.crud import crud
from app.schemas.schemas import RecipientCreate, RecipientOut
from app.models.models import User
from typing import List

router = APIRouter(prefix="/recipients", tags=["Recipients"])

@router.get("", response_model=List[RecipientOut])
def list_recipients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_recipients(db, user_id=current_user.id)

@router.post("", response_model=RecipientOut)
def create_recipient(
    recipient: RecipientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_recipient(db, user_id=current_user.id, recipient=recipient)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, SecurityLog
from app.schemas.schemas import UserOut, SecurityLogOut, UpdateLimitRequest, ChangePasswordRequest
from app.core.security import verify_password, get_password_hash
from typing import List
import json

router = APIRouter(prefix="/security", tags=["Security Operations"])


@router.post("/freeze", response_model=UserOut)
def freeze_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Freeze own account instantly to block all outgoing transactions."""
    current_user.is_frozen = True
    db.add(current_user)
    
    sec_log = SecurityLog(
        user_id=current_user.id,
        event_type="ACCOUNT_FROZEN",
        details=json.dumps({"action": "SELF_FREEZE"})
    )
    db.add(sec_log)
    db.commit()
    db.refresh(current_user)
    return current_user


class UnfreezeRequest(BaseModel := None):
    # We can use a simple inline schema or verify mpin
    pass

from pydantic import BaseModel
class VerifyMpinRequest(BaseModel):
    mpin: str


@router.post("/unfreeze", response_model=UserOut)
def unfreeze_account(
    req: VerifyMpinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unfreeze account. Requires correct MPIN confirmation."""
    if current_user.mpin != req.mpin:
        raise HTTPException(status_code=400, detail="Invalid Security MPIN")
    
    current_user.is_frozen = False
    db.add(current_user)

    sec_log = SecurityLog(
        user_id=current_user.id,
        event_type="ACCOUNT_UNFROZEN",
        details=json.dumps({"action": "SELF_UNFREEZE"})
    )
    db.add(sec_log)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/activity-log", response_model=List[SecurityLogOut])
def get_security_activity_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return security log entries for the active user."""
    return db.query(SecurityLog).filter(
        SecurityLog.user_id == current_user.id
    ).order_by(SecurityLog.timestamp.desc()).limit(50).all()


@router.put("/update-limit", response_model=UserOut)
def update_daily_limit(
    req: UpdateLimitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update daily transfer limit. Requires MPIN verification."""
    if current_user.mpin != req.mpin:
        raise HTTPException(status_code=400, detail="Invalid Security MPIN")
    
    old_limit = current_user.daily_transfer_limit
    current_user.daily_transfer_limit = req.limit
    db.add(current_user)

    sec_log = SecurityLog(
        user_id=current_user.id,
        event_type="LIMIT_CHANGED",
        details=json.dumps({"old_limit": old_limit, "new_limit": req.limit})
    )
    db.add(sec_log)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/change-password")
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change current password. Validates existing password first."""
    if not verify_password(req.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    import re
    # Validate new password strength
    v = req.new_password
    if len(v) < 8:
        raise HTTPException(status_code=400, detail='Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', v):
        raise HTTPException(status_code=400, detail='Password must contain at least one uppercase letter')
    if not re.search(r'[0-9]', v):
        raise HTTPException(status_code=400, detail='Password must contain at least one digit')
    if not re.search(r'[^a-zA-Z0-9]', v):
        raise HTTPException(status_code=400, detail='Password must contain at least one special character')

    current_user.hashed_password = get_password_hash(req.new_password)
    db.add(current_user)

    sec_log = SecurityLog(
        user_id=current_user.id,
        event_type="PASSWORD_CHANGED"
    )
    db.add(sec_log)
    db.commit()
    return {"status": "success", "message": "Password updated successfully."}

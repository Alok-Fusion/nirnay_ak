from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.crud.crud import get_user_by_username, get_user_by_email, create_user, update_user_profile
from app.schemas.schemas import UserCreate, UserLogin, UserOut, Token, UserProfileUpdate
from app.api.deps import get_current_user
from app.models.models import User, SecurityLog
from datetime import datetime, timezone, timedelta
import json

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    user_by_username = get_user_by_username(db, username=user_in.username)
    if user_by_username:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists in the system."
        )
    user_by_email = get_user_by_email(db, email=user_in.email)
    if user_by_email:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists in the system."
        )
    
    user = create_user(db, user_in)
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_json(user_in: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username=user_in.username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    # Check lockout
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if user.locked_until and user.locked_until > now_utc:
        diff_mins = int((user.locked_until - now_utc).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=403,
            detail=f"Account locked due to multiple failed login attempts. Try again in {diff_mins} minute(s)."
        )

    if not verify_password(user_in.password, user.hashed_password):
        user.failed_login_attempts += 1
        details = {"failed_attempts": user.failed_login_attempts}
        if user.failed_login_attempts >= 5:
            user.locked_until = now_utc + timedelta(minutes=15)
            details["action"] = "ACCOUNT_LOCKED"
        
        db.add(user)
        sec_log = SecurityLog(
            user_id=user.id,
            event_type="LOGIN_FAILED",
            details=json.dumps(details)
        )
        db.add(sec_log)
        db.commit()

        if user.failed_login_attempts >= 5:
            raise HTTPException(
                status_code=403,
                detail="Account locked due to 5 consecutive failed login attempts. Locked for 15 minutes."
            )
        raise HTTPException(
            status_code=401,
            detail=f"Incorrect username or password. Attempts remaining: {5 - user.failed_login_attempts}."
        )

    # Success
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now_utc
    db.add(user)

    sec_log = SecurityLog(
        user_id=user.id,
        event_type="LOGIN_SUCCESS"
    )
    db.add(sec_log)
    db.commit()

    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-jwt", response_model=Token)
def login_oauth2(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username=form_data.username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    # Check lockout
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if user.locked_until and user.locked_until > now_utc:
        diff_mins = int((user.locked_until - now_utc).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=403,
            detail=f"Account locked. Try again in {diff_mins} minute(s)."
        )

    if not verify_password(form_data.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = now_utc + timedelta(minutes=15)
        db.add(user)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now_utc
    db.add(user)
    db.commit()

    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserOut)
def update_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = update_user_profile(
        db=db,
        user_id=current_user.id,
        phone=profile_data.phone,
        address=profile_data.address,
        email=profile_data.email
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.post("/tour-complete")
def complete_tour(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.is_tour_completed = True
    db.add(current_user)
    db.commit()
    return {"status": "success", "message": "Onboarding tour marked as completed."}

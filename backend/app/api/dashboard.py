from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, DigitalTwin, Transaction
from app.schemas.schemas import DashboardSummary, DigitalTwinOut, TransactionOut
from typing import List
import json

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch recent transactions
    recent_txs = db.query(Transaction).filter(
        Transaction.sender_id == current_user.id
    ).order_by(Transaction.timestamp.desc()).limit(5).all()

    # Get Digital Twin to find trust level and count
    twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == current_user.id).first()
    
    trust_level = "NEW"
    tx_count = 0
    if twin:
        trust_level = twin.trust_level
        tx_count = twin.transaction_count

    return {
        "balance": current_user.balance,
        "security_score": current_user.security_score,
        "trust_level": trust_level,
        "transaction_count": tx_count,
        "recent_transactions": recent_txs
    }

@router.get("/digital-twin")
def get_digital_twin_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == current_user.id).first()
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin profile not found")

    try:
        devices = json.loads(twin.known_devices or "[]")
    except Exception:
        devices = []

    try:
        locations = json.loads(twin.known_locations or "[]")
    except Exception:
        locations = []

    return {
        "trust_level": twin.trust_level,
        "transaction_count": twin.transaction_count,
        "avg_transaction_amount": twin.avg_transaction_amount,
        "total_spend": twin.total_spend,
        "known_devices": devices,
        "known_locations": locations,
        "trusted_recipients_count": twin.trusted_recipients_count
    }

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

@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.models import Recipient, AuditLog
    
    all_txs = db.query(Transaction).filter(
        Transaction.sender_id == current_user.id
    ).order_by(Transaction.timestamp.asc()).all()

    total_count = len(all_txs)
    if total_count == 0:
        return {
            "total_transactions": 0,
            "total_volume": 0,
            "approved_count": 0,
            "challenged_count": 0,
            "blocked_count": 0,
            "avg_risk_score": 0,
            "max_risk_score": 0,
            "category_breakdown": [],
            "risk_timeline": [],
            "status_distribution": {"APPROVED": 0, "CHALLENGED": 0, "BLOCKED": 0},
        }

    total_volume = sum(tx.amount for tx in all_txs)
    approved = [tx for tx in all_txs if tx.status == "APPROVED"]
    challenged = [tx for tx in all_txs if tx.status in ("CHALLENGED", "AWAITING_CLARIFICATION")]
    blocked = [tx for tx in all_txs if tx.status == "BLOCKED"]
    
    risk_scores = [tx.risk_score for tx in all_txs if tx.risk_score is not None]
    avg_risk = round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else 0
    max_risk = round(max(risk_scores), 1) if risk_scores else 0

    # Category breakdown: group by recipient
    category_map = {}
    for tx in all_txs:
        recip = db.query(Recipient).filter(Recipient.id == tx.recipient_id).first()
        name = recip.name if recip else f"Recipient #{tx.recipient_id}"
        if name not in category_map:
            category_map[name] = 0.0
        category_map[name] += tx.amount
    
    categories = []
    for name, amount in sorted(category_map.items(), key=lambda x: -x[1]):
        pct = round((amount / total_volume) * 100, 1) if total_volume > 0 else 0
        categories.append({"name": name, "amount": amount, "percentage": pct})

    # Risk timeline: each transaction as a data point
    risk_timeline = []
    for tx in all_txs:
        risk_timeline.append({
            "date": tx.timestamp.isoformat() if tx.timestamp else "",
            "risk_score": tx.risk_score or 0,
            "amount": tx.amount,
            "status": tx.status
        })

    return {
        "total_transactions": total_count,
        "total_volume": round(total_volume, 2),
        "approved_count": len(approved),
        "challenged_count": len(challenged),
        "blocked_count": len(blocked),
        "avg_risk_score": avg_risk,
        "max_risk_score": max_risk,
        "category_breakdown": categories,
        "risk_timeline": risk_timeline,
        "status_distribution": {
            "APPROVED": len(approved),
            "CHALLENGED": len(challenged),
            "BLOCKED": len(blocked)
        },
    }

@router.get("/heatmap")
def get_transaction_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return a 7x24 heatmap grid of transaction activity (day-of-week × hour-of-day).
    Each cell contains: count of transactions, average risk score, and total volume.
    """
    all_txs = db.query(Transaction).filter(
        Transaction.sender_id == current_user.id
    ).all()

    # Initialize 7 days × 24 hours grid
    # Day 0 = Monday, Day 6 = Sunday
    grid = {}
    for day in range(7):
        for hour in range(24):
            key = f"{day}_{hour}"
            grid[key] = {"count": 0, "total_risk": 0.0, "total_volume": 0.0}

    for tx in all_txs:
        if tx.timestamp:
            day = tx.timestamp.weekday()  # 0=Mon, 6=Sun
            hour = tx.timestamp.hour
            key = f"{day}_{hour}"
            grid[key]["count"] += 1
            grid[key]["total_risk"] += (tx.risk_score or 0)
            grid[key]["total_volume"] += tx.amount

    # Build response
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    heatmap = []
    for day in range(7):
        row = []
        for hour in range(24):
            key = f"{day}_{hour}"
            cell = grid[key]
            avg_risk = round(cell["total_risk"] / cell["count"], 1) if cell["count"] > 0 else 0
            row.append({
                "day": day_names[day],
                "hour": hour,
                "count": cell["count"],
                "avg_risk": avg_risk,
                "volume": round(cell["total_volume"], 2)
            })
        heatmap.append(row)

    return {"heatmap": heatmap, "days": day_names}


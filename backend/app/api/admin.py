from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Transaction, AuditLog
from app.schemas.schemas import AdminOverrideRequest
from app.services.digital_twin import DigitalTwinService
from app.crud import crud
from typing import List
import json

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.get("/escalations")
def get_admin_escalations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Retrieve escalated transactions across the platform
    # For a real multi-user app we might check if user is_admin, but for our prototype we allow review
    escalations = db.query(Transaction).filter(
        Transaction.status.in_(["ESCALATED", "CHALLENGED"])
    ).order_by(Transaction.timestamp.desc()).all()
    
    results = []
    for tx in escalations:
        audit = db.query(AuditLog).filter(AuditLog.transaction_id == tx.id).first()
        agent_logs = []
        if audit and audit.agent_logs:
            try:
                agent_logs = json.loads(audit.agent_logs)
            except Exception:
                pass
                
        results.append({
            "id": tx.id,
            "sender_username": tx.sender.username if tx.sender else "Unknown",
            "recipient_name": tx.recipient.name if tx.recipient else "Unknown",
            "amount": tx.amount,
            "device": tx.device,
            "location": tx.location,
            "timestamp": tx.timestamp,
            "status": tx.status,
            "risk_score": tx.risk_score,
            "agent_logs": agent_logs
        })
    return results

@router.post("/override")
def admin_override(
    req: AdminOverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(Transaction.id == req.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    sender = db.query(User).filter(User.id == tx.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender user not found")

    audit = db.query(AuditLog).filter(AuditLog.transaction_id == tx.id).first()
    logs = []
    if audit and audit.agent_logs:
        try:
            logs = json.loads(audit.agent_logs)
        except Exception:
            pass

    if req.action == "FORCE_APPROVE":
        if tx.status == "APPROVED":
            raise HTTPException(status_code=400, detail="Transaction is already approved")
            
        if sender.balance < tx.amount:
            raise HTTPException(status_code=400, detail="Sender has insufficient balance to complete transfer")

        # Deduct balance & approve
        sender.balance -= tx.amount
        tx.status = "APPROVED"
        
        db.add(sender)
        db.add(tx)
        db.commit()

        # Update Digital Twin
        DigitalTwinService.update_profile(
            db=db,
            sender_id=sender.id,
            transaction_amount=tx.amount,
            device=tx.device,
            location=tx.location
        )

        logs.append({
            "agent": "Admin Override",
            "action": "Override Approve",
            "message": f"Administrator '{current_user.username}' executed FORCE_APPROVE override."
        })
        if audit:
            audit.agent_logs = json.dumps(logs)
            audit.decision = "APPROVED"
            db.add(audit)
            db.commit()

        return {"message": "Transaction force-approved successfully", "status": "APPROVED"}

    elif req.action == "FORCE_BLOCK":
        if tx.status == "BLOCKED":
            raise HTTPException(status_code=400, detail="Transaction is already blocked")

        tx.status = "BLOCKED"
        db.add(tx)
        db.commit()

        logs.append({
            "agent": "Admin Override",
            "action": "Override Block",
            "message": f"Administrator '{current_user.username}' executed FORCE_BLOCK override."
        })
        if audit:
            audit.agent_logs = json.dumps(logs)
            audit.decision = "BLOCKED"
            db.add(audit)
            db.commit()

        return {"message": "Transaction force-blocked successfully", "status": "BLOCKED"}

    else:
        raise HTTPException(status_code=400, detail="Invalid admin override action. Use FORCE_APPROVE or FORCE_BLOCK.")

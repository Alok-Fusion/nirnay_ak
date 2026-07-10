from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Transaction, AuditLog
from app.schemas.schemas import TransactionInitiate, TransactionOut, TransactionAuthChallenge, TransactionClarification
from app.services.orchestrator import TransactionOrchestrator
from app.services.digital_twin import DigitalTwinService
from app.core.security import verify_password
from typing import List
import json

router = APIRouter(prefix="/transactions", tags=["Transactions"])
orchestrator = TransactionOrchestrator()

@router.get("", response_model=List[TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch user transactions, eager loading the recipients
    return db.query(Transaction).filter(
        Transaction.sender_id == current_user.id
    ).order_by(Transaction.timestamp.desc()).all()

@router.post("/initiate")
def initiate_transaction(
    tx_in: TransactionInitiate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = orchestrator.process_transaction(
        db=db,
        sender_id=current_user.id,
        recipient_id=tx_in.recipient_id,
        amount=tx_in.amount,
        device=tx_in.device,
        location=tx_in.location
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@router.post("/authenticate")
def authenticate_challenge(
    challenge: TransactionAuthChallenge,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(
        Transaction.id == challenge.transaction_id,
        Transaction.sender_id == current_user.id
    ).first()
    
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    if tx.status not in ["CHALLENGED", "PENDING"]:
        raise HTTPException(status_code=400, detail=f"Transaction cannot be verified, current status is {tx.status}")

    required_steps = tx.auth_steps_required.split(",")
    completed_steps = tx.auth_steps_completed.split(",")

    # 1. Verify Password if required
    if "PASSWORD" in required_steps and "PASSWORD" not in completed_steps:
        if not challenge.password:
            raise HTTPException(status_code=400, detail="Password is required to proceed")
        if not verify_password(challenge.password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect account password")
        completed_steps.append("PASSWORD")

    # 2. Verify MPIN if required
    if "MPIN" in required_steps and "MPIN" not in completed_steps:
        if not challenge.mpin:
            raise HTTPException(status_code=400, detail="MPIN is required to proceed")
        if challenge.mpin != current_user.mpin:
            raise HTTPException(status_code=400, detail="Incorrect security MPIN")
        completed_steps.append("MPIN")

    # 3. Verify OTP if required (Simulate check: expect '123456' as seeded OTP for simplicity)
    if "OTP" in required_steps and "OTP" not in completed_steps:
        if not challenge.otp:
            raise HTTPException(status_code=400, detail="One-Time Password (OTP) is required")
        if challenge.otp != "123456":
            raise HTTPException(status_code=400, detail="Invalid OTP code. For testing, please enter '123456'")
        completed_steps.append("OTP")

    # Update completed steps list
    tx.auth_steps_completed = ",".join(completed_steps)
    db.add(tx)
    db.commit()

    # Check if we have completed all required verification steps
    all_completed = all(step in completed_steps for step in required_steps)
    
    # Check if audit log shows conversation agent requires interaction and if they answered
    audit_log = db.query(AuditLog).filter(AuditLog.transaction_id == tx.id).first()
    requires_clarify = False
    if audit_log and audit_log.agent_logs:
        logs = json.loads(audit_log.agent_logs)
        for log in logs:
            if log.get("agent") == "Conversation Agent" and log.get("requires_interaction") is True:
                requires_clarify = True

    # Check if they have already submitted a clarification comment
    # For simulation, if clarification was required, we check if they also submitted a clarification text or wait
    is_clarified = True
    if requires_clarify and not tx.explanation.startswith("[CLARIFIED]"):
        is_clarified = False

    if all_completed:
        if not is_clarified:
            tx.status = "CHALLENGED" # Still waiting for user clarification input
            db.add(tx)
            db.commit()
            return {
                "message": "Authentication factors verified successfully. Transaction requires natural language explanation to execute.",
                "status": "AWAITING_CLARIFICATION",
                "completed_steps": completed_steps
            }
        else:
            # Everything verified and clarified -> EXECUTE!
            if current_user.balance < tx.amount:
                raise HTTPException(status_code=400, detail="Insufficient account balance to complete transfer")
            
            # Deduct balance
            current_user.balance -= tx.amount
            tx.status = "APPROVED"
            db.add(current_user)
            db.add(tx)
            db.commit()

            # Update Digital Twin
            DigitalTwinService.update_profile(
                db=db,
                sender_id=current_user.id,
                transaction_amount=tx.amount,
                device=tx.device,
                location=tx.location
            )
            
            # Append success to agent logs in Audit
            if audit_log:
                logs = json.loads(audit_log.agent_logs or "[]")
                logs.append({"agent": "Memory Agent", "action": "Commit transaction", "message": "Transaction cleared authentication challenges and executed successfully."})
                audit_log.agent_logs = json.dumps(logs)
                audit_log.decision = "APPROVED"
                db.add(audit_log)
                db.commit()

            return {
                "message": "Authentication completed. Transaction executed successfully.",
                "status": "APPROVED",
                "completed_steps": completed_steps
            }
            
    return {
        "message": "Authentication factor verified.",
        "status": "CHALLENGED",
        "completed_steps": completed_steps
    }

@router.post("/clarify")
def submit_clarification(
    clarification: TransactionClarification,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(
        Transaction.id == clarification.transaction_id,
        Transaction.sender_id == current_user.id
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Mark explanation as clarified with their response
    tx.explanation = f"[CLARIFIED] User Response: '{clarification.response_text}'"
    db.add(tx)
    db.commit()

    # Append response details to agent logs
    audit_log = db.query(AuditLog).filter(AuditLog.transaction_id == tx.id).first()
    if audit_log:
        logs = json.loads(audit_log.agent_logs or "[]")
        logs.append({
            "agent": "Conversation Agent",
            "action": "Clarification Received",
            "message": f"User confirmed transaction intent: '{clarification.response_text}'"
        })
        audit_log.agent_logs = json.dumps(logs)
        db.add(audit_log)
        db.commit()

    # Check if they have also completed authentication factors
    required_steps = tx.auth_steps_required.split(",")
    completed_steps = tx.auth_steps_completed.split(",")
    all_auth_completed = all(step in completed_steps for step in required_steps)

    if all_auth_completed:
        # Check balance
        if current_user.balance < tx.amount:
            raise HTTPException(status_code=400, detail="Insufficient account balance to complete transfer")
            
        current_user.balance -= tx.amount
        tx.status = "APPROVED"
        db.add(current_user)
        db.add(tx)
        db.commit()

        # Update Digital Twin
        DigitalTwinService.update_profile(
            db=db,
            sender_id=current_user.id,
            transaction_amount=tx.amount,
            device=tx.device,
            location=tx.location
        )
        
        if audit_log:
            logs = json.loads(audit_log.agent_logs or "[]")
            logs.append({"agent": "Memory Agent", "action": "Commit transaction", "message": "Transaction cleared all intent challenges and executed successfully."})
            audit_log.agent_logs = json.dumps(logs)
            audit_log.decision = "APPROVED"
            db.add(audit_log)
            db.commit()

        return {"message": "Clarification recorded. Transaction executed successfully.", "status": "APPROVED"}

    return {"message": "Clarification recorded. Awaiting authentication factors.", "status": "CHALLENGED"}

@router.get("/{transaction_id}/audit")
def get_transaction_audit(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.sender_id == current_user.id
    ).first()

    if not tx:
         raise HTTPException(status_code=404, detail="Transaction not found")

    audit = db.query(AuditLog).filter(AuditLog.transaction_id == tx.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit log not found")

    # Load and parse logs
    try:
        agent_logs = json.loads(audit.agent_logs or "[]")
    except Exception:
        agent_logs = []
        
    try:
        rule_triggers = json.loads(audit.rule_triggers or "[]")
    except Exception:
        rule_triggers = []

    try:
        ml_features = json.loads(audit.ml_features or "{}")
    except Exception:
        ml_features = {}

    # Get ML result to include SHAP values dynamically
    ml_risk_res = MLEngine.evaluate_risk(
        db=db,
        sender_id=tx.sender_id,
        recipient_id=tx.recipient_id,
        amount=tx.amount,
        device=tx.device,
        location=tx.location
    )

    return {
        "transaction_id": tx.id,
        "amount": tx.amount,
        "timestamp": tx.timestamp,
        "status": tx.status,
        "risk_score": tx.risk_score,
        "rule_triggers": rule_triggers,
        "agent_logs": agent_logs,
        "ml_features": ml_features,
        "shap_values": ml_risk_res.get("shap_values", {}),
        "reason_codes": ml_risk_res.get("reason_codes", []),
        "execution_time_ms": audit.execution_time_ms
    }

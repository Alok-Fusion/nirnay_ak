from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, LedgerEntry, Recipient, Transaction
from app.schemas.schemas import DepositRequest, P2PTransferRequest, LedgerEntryOut
from app.crud.crud import record_approved_transaction_ledger
from app.services.orchestrator import TransactionOrchestrator
from typing import List, Dict, Any
from datetime import datetime, timezone
import json

router = APIRouter(prefix="/banking", tags=["Banking Operations"])
orchestrator = TransactionOrchestrator()


@router.post("/deposit")
def deposit_funds(
    req: DepositRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deposit money to user account (credits balance and adds credit ledger entry)."""
    current_user.balance += req.amount
    db.add(current_user)
    db.commit()

    # Create credit LedgerEntry
    ledger = LedgerEntry(
        user_id=current_user.id,
        type="CREDIT",
        category=req.category,
        amount=req.amount,
        balance_after=current_user.balance,
        description=f"Received via {req.category.replace('_', ' ')}",
        counterparty="External Source"
    )
    db.add(ledger)
    db.commit()

    return {
        "status": "success",
        "message": f"Successfully credited ${req.amount:,.2f} to your account.",
        "new_balance": current_user.balance
    }


@router.get("/passbook", response_model=List[LedgerEntryOut])
def get_passbook(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full passbook statement ledger for the current user."""
    return db.query(LedgerEntry).filter(
        LedgerEntry.user_id == current_user.id
    ).order_by(LedgerEntry.timestamp.desc()).limit(100).all()


@router.get("/balance")
def get_balance_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve available balance and aggregate credit/debit metrics."""
    credits_sum = db.query(LedgerEntry).filter(
        LedgerEntry.user_id == current_user.id,
        LedgerEntry.type == "CREDIT"
    ).all()
    debits_sum = db.query(LedgerEntry).filter(
        LedgerEntry.user_id == current_user.id,
        LedgerEntry.type == "DEBIT"
    ).all()

    total_credits = sum(item.amount for item in credits_sum)
    total_debits = sum(item.amount for item in debits_sum)

    return {
        "balance": current_user.balance,
        "account_number": current_user.account_number,
        "ifsc_code": current_user.ifsc_code,
        "total_credits": round(total_credits, 2),
        "total_debits": round(total_debits, 2)
    }


@router.get("/lookup")
def lookup_recipient(
    account_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Look up system user by account number for P2P transaction verification."""
    target_user = db.query(User).filter(User.account_number == account_number).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Account number not found")
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot transfer to yourself")
    return {
        "full_name": target_user.full_name or target_user.username,
        "username": target_user.username
    }


@router.post("/p2p-transfer")
def initiate_p2p_transfer(
    req: P2PTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a peer-to-peer (P2P) transfer protected by standard AI policies."""
    # 1. Lookup recipient user
    recip_user = db.query(User).filter(User.account_number == req.recipient_account_number).first()
    if not recip_user:
        raise HTTPException(status_code=404, detail="Recipient account number not found.")
    
    if recip_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot transfer funds to yourself.")

    # 2. Check or create Recipient link for sender
    recip = db.query(Recipient).filter(
        Recipient.user_id == current_user.id,
        Recipient.account_number == req.recipient_account_number
    ).first()
    
    if not recip:
        recip = Recipient(
            user_id=current_user.id,
            name=recip_user.full_name or recip_user.username,
            account_number=req.recipient_account_number,
            bank_name="NIRNAY Digital Bank",
            trust_score=80.0
        )
        db.add(recip)
        db.commit()
        db.refresh(recip)

    # 3. Call core transaction pipeline
    res = orchestrator.process_transaction(
        db=db,
        sender_id=current_user.id,
        recipient_id=recip.id,
        amount=req.amount,
        device=req.device,
        location=req.location
    )

    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    # 4. If immediately APPROVED, trigger P2P ledger credit/debit mappings
    if res.get("status") == "APPROVED":
        record_approved_transaction_ledger(db, res["transaction_id"])

    return res

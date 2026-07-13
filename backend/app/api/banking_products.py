from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, VirtualCard, FixedDeposit, LedgerEntry, SecurityLog
from app.schemas.schemas import (
    VirtualCardCreate, VirtualCardOut, CardLimitUpdate,
    FixedDepositCreate, FixedDepositOut, OfferOut
)
from datetime import datetime, timezone, timedelta
import random
import json
from typing import List

router = APIRouter(prefix="/banking-products", tags=["Banking Products"])


# --- VIRTUAL CARDS ---

@router.post("/cards", response_model=VirtualCardOut)
def create_virtual_card(
    req: VirtualCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a new secure virtual credit/debit card."""
    # Limit to 3 virtual cards per customer to simulate real bank policies
    existing_cards = db.query(VirtualCard).filter(
        VirtualCard.user_id == current_user.id,
        VirtualCard.status == "ACTIVE"
    ).count()
    if existing_cards >= 3:
        raise HTTPException(status_code=400, detail="Maximum limit of 3 active virtual cards exceeded.")

    # Generate random 16-digit card number (starting with 4 for Visa or 5 for Mastercard)
    prefix = "4532" if req.card_type == "VISA_DEBIT" else "5422"
    card_number = prefix + "".join([str(random.randint(0, 9)) for _ in range(12)])
    
    # Expiry 5 years from now
    now = datetime.now(timezone.utc)
    expiry_date = f"{now.month:02d}/{(now.year + 5) % 100:02d}"
    
    cvv = "".join([str(random.randint(0, 9)) for _ in range(3)])

    db_card = VirtualCard(
        user_id=current_user.id,
        card_number=card_number,
        expiry_date=expiry_date,
        cvv=cvv,
        card_holder=current_user.full_name or current_user.username,
        status="ACTIVE",
        card_type=req.card_type,
        spend_limit=req.spend_limit,
        total_spent=0.0
    )
    db.add(db_card)

    # Log Security Action
    sec_log = SecurityLog(
        user_id=current_user.id,
        event_type="CARD_CREATED",
        details=json.dumps({"card_type": req.card_type, "last4": card_number[-4:]})
    )
    db.add(sec_log)
    db.commit()
    db.refresh(db_card)
    return db_card


@router.get("/cards", response_model=List[VirtualCardOut])
def list_virtual_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all virtual cards registered for the customer."""
    return db.query(VirtualCard).filter(VirtualCard.user_id == current_user.id).all()


@router.post("/cards/{card_id}/toggle-status", response_model=VirtualCardOut)
def toggle_card_status(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Freeze or unfreeze a virtual card instantly."""
    card = db.query(VirtualCard).filter(
        VirtualCard.id == card_id,
        VirtualCard.user_id == current_user.id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="Virtual card not found")

    card.status = "FROZEN" if card.status == "ACTIVE" else "ACTIVE"
    db.add(card)

    sec_log = SecurityLog(
        user_id=current_user.id,
        event_type="CARD_STATUS_TOGGLED",
        details=json.dumps({"card_id": card.id, "new_status": card.status})
    )
    db.add(sec_log)
    db.commit()
    db.refresh(card)
    return card


@router.put("/cards/{card_id}/limit", response_model=VirtualCardOut)
def update_card_limit(
    card_id: int,
    req: CardLimitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update spending limits on a virtual card."""
    card = db.query(VirtualCard).filter(
        VirtualCard.id == card_id,
        VirtualCard.user_id == current_user.id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="Virtual card not found")

    old_limit = card.spend_limit
    card.spend_limit = req.spend_limit
    db.add(card)

    sec_log = SecurityLog(
        user_id=current_user.id,
        event_type="CARD_LIMIT_UPDATED",
        details=json.dumps({"card_id": card.id, "old_limit": old_limit, "new_limit": req.spend_limit})
    )
    db.add(sec_log)
    db.commit()
    db.refresh(card)
    return card


# --- FIXED DEPOSITS (FD) ---

@router.post("/fd", response_model=FixedDepositOut)
def create_fixed_deposit(
    req: FixedDepositCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Open a new Fixed Deposit (FD) using available account balance."""
    if current_user.balance < req.principal_amount:
        raise HTTPException(status_code=400, detail="Insufficient account balance to open Fixed Deposit.")

    # Determine Interest Rate
    if req.duration_months < 12:
        interest_rate = 5.5
    elif req.duration_months < 24:
        interest_rate = 7.0
    elif req.duration_months < 36:
        interest_rate = 7.5
    else:
        interest_rate = 8.0

    # Calculate maturity amount
    duration_years = req.duration_months / 12.0
    maturity_amount = req.principal_amount * (1 + (interest_rate / 100.0) * duration_years)

    # Date limits
    created_at = datetime.now(timezone.utc).replace(tzinfo=None)
    matures_at = created_at + timedelta(days=30 * req.duration_months)

    # Deduct principal
    current_user.balance -= req.principal_amount
    db.add(current_user)
    db.commit() # commit user balance change to get correct snapshot after

    # Create FD record
    db_fd = FixedDeposit(
        user_id=current_user.id,
        principal_amount=req.principal_amount,
        interest_rate=interest_rate,
        duration_months=req.duration_months,
        maturity_amount=round(maturity_amount, 2),
        status="ACTIVE",
        created_at=created_at,
        matures_at=matures_at
    )
    db.add(db_fd)
    db.commit()
    db.refresh(db_fd)

    # Create debit LedgerEntry
    ledger = LedgerEntry(
        user_id=current_user.id,
        type="DEBIT",
        category="FD_CREATE",
        amount=req.principal_amount,
        balance_after=current_user.balance,
        description=f"Opened FD #{db_fd.id} for {req.duration_months} months @ {interest_rate}%",
        reference_id=str(db_fd.id),
        counterparty="NIRNAY Term Deposit"
    )
    db.add(ledger)
    db.commit()

    return db_fd


@router.get("/fd", response_model=List[FixedDepositOut])
def list_fixed_deposits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all fixed deposits registered for the customer."""
    # Check if any ACTIVE FD has reached its maturity date. If so, mature it!
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    active_fds = db.query(FixedDeposit).filter(
        FixedDeposit.user_id == current_user.id,
        FixedDeposit.status == "ACTIVE"
    ).all()

    for fd in active_fds:
        if fd.matures_at <= now_naive:
            # Mature the FD! Credit user balance with maturity amount
            fd.status = "MATURED"
            current_user.balance += fd.maturity_amount
            db.add(fd)
            db.add(current_user)
            db.commit()

            # Record Ledger Entry
            ledger = LedgerEntry(
                user_id=current_user.id,
                type="CREDIT",
                category="FD_LIQUIDATE",
                amount=fd.maturity_amount,
                balance_after=current_user.balance,
                description=f"Maturity payout of FD #{fd.id}",
                reference_id=str(fd.id),
                counterparty="NIRNAY Term Deposit"
            )
            db.add(ledger)
            db.commit()

    return db.query(FixedDeposit).filter(FixedDeposit.user_id == current_user.id).all()


@router.post("/fd/{fd_id}/liquidate", response_model=FixedDepositOut)
def liquidate_fixed_deposit(
    fd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Prematurely liquidate an active Fixed Deposit. Applies a 1% penalty deduction."""
    fd = db.query(FixedDeposit).filter(
        FixedDeposit.id == fd_id,
        FixedDeposit.user_id == current_user.id,
        FixedDeposit.status == "ACTIVE"
    ).first()
    if not fd:
        raise HTTPException(status_code=404, detail="Active fixed deposit not found.")

    # Calculate premature payout: Principal + reduced interest (applying a 1% penalty fee)
    payout_rate = max(0.5, fd.interest_rate - 1.0)
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    days_elapsed = (now_naive - fd.created_at).days
    years_elapsed = max(0.01, days_elapsed / 365.0)

    payout_amount = fd.principal_amount * (1 + (payout_rate / 100.0) * years_elapsed)
    payout_amount = round(payout_amount, 2)

    fd.status = "LIQUIDATED"
    current_user.balance += payout_amount
    db.add(fd)
    db.add(current_user)
    db.commit() # commit balance change to get correct snapshot after

    # Create credit LedgerEntry
    ledger = LedgerEntry(
        user_id=current_user.id,
        type="CREDIT",
        category="FD_LIQUIDATE",
        amount=payout_amount,
        balance_after=current_user.balance,
        description=f"Premature liquidation of FD #{fd.id} (Penalty rate: {payout_rate}%)",
        reference_id=str(fd.id),
        counterparty="NIRNAY Term Deposit"
    )
    db.add(ledger)
    db.commit()

    return fd


# --- OFFERS & DISCOUNTS ---

@router.get("/offers", response_model=List[OfferOut])
def get_curated_offers(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve personalized discount/cashback offers.
    Curated dynamically based on user's security integrity score!
    """
    sec_score = current_user.security_score
    
    all_offers = [
        {
            "id": "OFFER_01",
            "title": "Vanguard Fraud-Shield Cashback",
            "description": "Unlock 5% cashback on all online transaction insurance purchases.",
            "reward_rate": "5% Cashback",
            "category": "INSURANCE",
            "unlock_score": 0.0
        },
        {
            "id": "OFFER_02",
            "title": "Amazon Prime Safety Discount Voucher",
            "description": "Get a $15 discount voucher on annual Amazon Prime subscriptions.",
            "reward_rate": "$15 Off Voucher",
            "category": "SHOPPING",
            "unlock_score": 75.0
        },
        {
            "id": "OFFER_03",
            "title": "NordVPN Cybersecurity Protection Deal",
            "description": "Unlock a premium 3-month free trial subscription code for NordVPN threat protection.",
            "reward_rate": "3 Months Free Premium",
            "category": "CYBERSECURITY",
            "unlock_score": 85.0
        },
        {
            "id": "OFFER_04",
            "title": "Elite Integrity Cashback Bonus Card",
            "description": "Exclusive reward: Get an additional 2.5% cashback on P2P inter-user transfers.",
            "reward_rate": "2.5% Cashback Booster",
            "category": "P2P_BONUS",
            "unlock_score": 90.0
        }
    ]

    response = []
    for offer in all_offers:
        unlocked = sec_score >= offer["unlock_score"]
        response.append(OfferOut(
            id=offer["id"],
            title=offer["title"],
            description=offer["description"],
            reward_rate=offer["reward_rate"],
            category=offer["category"],
            unlocked=unlocked,
            unlock_score=offer["unlock_score"]
        ))
    
    return response

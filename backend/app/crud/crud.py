from sqlalchemy.orm import Session
from app.models.models import User, DigitalTwin, Recipient, Transaction, AuditLog
from app.schemas.schemas import UserCreate, RecipientCreate
from app.core.security import get_password_hash
from datetime import datetime, timedelta, timezone
import json

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    import random
    from app.models.models import LedgerEntry, SecurityLog

    # Generate a unique 12-digit account number
    account_number = "".join([str(random.randint(0, 9)) for _ in range(12)])
    while db.query(User).filter(User.account_number == account_number).first() is not None:
        account_number = "".join([str(random.randint(0, 9)) for _ in range(12)])

    hashed_pwd = get_password_hash(user.password)
    initial_balance = 25000.0
    
    # Check if is_demo
    is_demo = user.username.lower().startswith("demo") or user.username in ["robert_miller", "alok_kumar", "alex_jones"]
    if is_demo:
        initial_balance = 150000.0

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd,
        mpin=user.mpin,
        balance=initial_balance,
        security_score=85.0,
        full_name=user.full_name,
        phone=user.phone,
        address=user.address,
        aadhaar_last4=user.aadhaar_number[-4:],
        pan_number=user.pan_number,
        driving_license=user.driving_license,
        account_number=account_number,
        ifsc_code="NIRN0000001",
        is_tour_completed=False,
        is_frozen=False,
        daily_transfer_limit=200000.0,
        failed_login_attempts=0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Initialize Digital Twin
    db_twin = DigitalTwin(
        user_id=db_user.id,
        trust_level="NEW",
        transaction_count=0,
        avg_transaction_amount=0.0,
        total_spend=0.0,
        known_devices=json.dumps(["Windows-Chrome"]),
        known_locations=json.dumps(["Mumbai"]),
        trusted_recipients_count=0
    )
    db.add(db_twin)
    db.commit()

    # Create initial LedgerEntry recording the initial account balance
    initial_ledger = LedgerEntry(
        user_id=db_user.id,
        type="CREDIT",
        category="BANK_TRANSFER",
        amount=initial_balance,
        balance_after=initial_balance,
        description="Account opened & Initial balance seeded",
        counterparty="NIRNAY Reserve"
    )
    db.add(initial_ledger)
    db.commit()

    # Create initial SecurityLog
    sec_log = SecurityLog(
        user_id=db_user.id,
        event_type="ACCOUNT_CREATED",
        device="Windows-Chrome",
        details=json.dumps({"username": db_user.username, "account_number": db_user.account_number})
    )
    db.add(sec_log)
    db.commit()
    
    if is_demo:
        seed_mock_history(db, db_user.id)
    
    return db_user

def update_user_profile(db: Session, user_id: int, phone: str, address: str, email: str) -> User:
    from app.models.models import SecurityLog
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    old_details = {
        "phone": db_user.phone,
        "address": db_user.address,
        "email": db_user.email
    }
    
    db_user.phone = phone
    db_user.address = address
    db_user.email = email
    
    db.add(db_user)
    
    sec_log = SecurityLog(
        user_id=user_id,
        event_type="PROFILE_UPDATED",
        details=json.dumps({"old": old_details, "new": {"phone": phone, "address": address, "email": email}})
    )
    db.add(sec_log)
    db.commit()
    db.refresh(db_user)
    return db_user


def seed_mock_history(db: Session, user_id: int):
    # 1. Create a few recipients
    r1 = Recipient(user_id=user_id, name="Aarav Sharma (Brother)", account_number="9128374652", bank_name="State Bank of India", trust_score=98.0, is_blacklisted=False)
    r2 = Recipient(user_id=user_id, name="Priya Patel (Landlord)", account_number="8837461524", bank_name="HDFC Bank", trust_score=92.0, is_blacklisted=False)
    r3 = Recipient(user_id=user_id, name="QuickBuy Crypto OTC", account_number="5546372819", bank_name="Global Trade Bank", trust_score=35.0, is_blacklisted=False)
    r4 = Recipient(user_id=user_id, name="Suspect Escrow Services", account_number="1029384756", bank_name="Shadow Finance Corp", trust_score=12.0, is_blacklisted=True)
    
    db.add_all([r1, r2, r3, r4])
    db.commit()
    db.refresh(r1)
    db.refresh(r2)
    db.refresh(r3)
    db.refresh(r4)

    # 2. Add some transactions over the last 15 days
    now = datetime.now(timezone.utc)
    t1 = Transaction(
        sender_id=user_id, recipient_id=r1.id, amount=12000.0,
        device="Windows-Chrome", location="Mumbai", timestamp=now - timedelta(days=12),
        status="APPROVED", risk_score=8.5, explanation="Regular transfer to family. Matching device and location.",
        auth_steps_required="PASSWORD", auth_steps_completed="PASSWORD"
    )
    t2 = Transaction(
        sender_id=user_id, recipient_id=r2.id, amount=45000.0,
        device="Windows-Chrome", location="Mumbai", timestamp=now - timedelta(days=8),
        status="APPROVED", risk_score=12.0, explanation="Monthly rent payment. Matches typical billing amount.",
        auth_steps_required="PASSWORD", auth_steps_completed="PASSWORD"
    )
    t3 = Transaction(
        sender_id=user_id, recipient_id=r1.id, amount=8500.0,
        device="Windows-Chrome", location="Mumbai", timestamp=now - timedelta(days=4),
        status="APPROVED", risk_score=7.0, explanation="Small sibling transfer.",
        auth_steps_required="PASSWORD", auth_steps_completed="PASSWORD"
    )
    t4 = Transaction(
        sender_id=user_id, recipient_id=r3.id, amount=95000.0,
        device="Windows-Chrome", location="Mumbai", timestamp=now - timedelta(days=1),
        status="APPROVED", risk_score=48.0, explanation="Crypto exchange buy. Triggered multi-step verification. Challenged and approved with MPIN and OTP.",
        auth_steps_required="PASSWORD,MPIN,OTP", auth_steps_completed="PASSWORD,MPIN,OTP"
    )

    db.add_all([t1, t2, t3, t4])
    db.commit()
    db.refresh(t1)
    db.refresh(t2)
    db.refresh(t3)
    db.refresh(t4)

    # 3. Add corresponding Audit Logs
    a1 = AuditLog(
        transaction_id=t1.id, user_id=user_id, timestamp=t1.timestamp,
        ml_features=json.dumps({"amount": 12000, "dev_ratio": 0.8, "location_match": 1, "device_match": 1}),
        rule_triggers=json.dumps([]),
        agent_logs=json.dumps([
            {"agent": "Context", "action": "Fetched customer digital twin profile. Verified Aarav Sharma has a high trust score of 98.0."},
            {"agent": "Policy", "action": "Deterministic check: Under daily limit. No warning indicators."},
            {"agent": "Decision", "action": "Transaction approved immediately without extra authentication."}
        ]),
        decision="APPROVE", execution_time_ms=120
    )
    
    a2 = AuditLog(
        transaction_id=t2.id, user_id=user_id, timestamp=t2.timestamp,
        ml_features=json.dumps({"amount": 45000, "dev_ratio": 1.2, "location_match": 1, "device_match": 1}),
        rule_triggers=json.dumps(["large_amount_threshold"]),
        agent_logs=json.dumps([
            {"agent": "Context", "action": "Fetched user profile. Recipient Priya Patel trust score: 92.0."},
            {"agent": "Policy", "action": "Rule 'large_amount_threshold' fired (amount > 25,000). Challenged with MPIN check."},
            {"agent": "Decision", "action": "Challenged sender with MPIN. Authentication successful."}
        ]),
        decision="CHALLENGE", execution_time_ms=210
    )
    
    a3 = AuditLog(
        transaction_id=t3.id, user_id=user_id, timestamp=t3.timestamp,
        ml_features=json.dumps({"amount": 8500, "dev_ratio": 0.5, "location_match": 1, "device_match": 1}),
        rule_triggers=json.dumps([]),
        agent_logs=json.dumps([
            {"agent": "Context", "action": "Fetched user profile. Recipient Aarav Sharma trust score: 98.0."},
            {"agent": "Policy", "action": "Deterministic check: Small transaction, trusted family recipient. Bypassed extra checks."},
            {"agent": "Decision", "action": "Transaction fast-tracked and approved immediately."}
        ]),
        decision="APPROVED", execution_time_ms=90
    )
    
    a4 = AuditLog(
        transaction_id=t4.id, user_id=user_id, timestamp=t4.timestamp,
        ml_features=json.dumps({"amount": 95000, "dev_ratio": 2.5, "location_match": 1, "device_match": 1}),
        rule_triggers=json.dumps(["large_amount_threshold", "crypto_recipient"]),
        agent_logs=json.dumps([
            {"agent": "Context", "action": "Detected transaction to crypto entity QuickBuy Crypto OTC."},
            {"agent": "Interpretation", "action": "ML flag raised due to amount (95k) being 2.5x the average transaction size."},
            {"agent": "Policy", "action": "Crypto compliance rule triggered. Elevated transaction security level to high risk."},
            {"agent": "Decision", "action": "Challenged sender with MPIN & OTP verification. Completed."}
        ]),
        decision="CHALLENGE", execution_time_ms=450
    )
    db.add_all([a1, a2, a3, a4])
    db.commit()

    # 4. Update the Digital Twin with historical averages
    twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == user_id).first()
    if twin:
        twin.trust_level = "STABLE"
        twin.transaction_count = 4
        twin.total_spend = 12000.0 + 45000.0 + 8500.0 + 95000.0
        twin.avg_transaction_amount = twin.total_spend / 4
        twin.known_devices = json.dumps(["Windows-Chrome"])
        twin.known_locations = json.dumps(["Mumbai"])
        twin.trusted_recipients_count = 2
        db.add(twin)
        db.commit()

def get_recipients(db: Session, user_id: int):
    return db.query(Recipient).filter(Recipient.user_id == user_id).all()

def get_recipient_by_id(db: Session, recipient_id: int, user_id: int):
    return db.query(Recipient).filter(Recipient.id == recipient_id, Recipient.user_id == user_id).first()

def create_recipient(db: Session, user_id: int, recipient: RecipientCreate):
    db_recipient = Recipient(
        user_id=user_id,
        name=recipient.name,
        account_number=recipient.account_number,
        bank_name=recipient.bank_name,
        trust_score=80.0  # Initial default trust score
    )
    db.add(db_recipient)
    db.commit()
    db.refresh(db_recipient)
    return db_recipient

def get_transactions(db: Session, user_id: int):
    return db.query(Transaction).filter(Transaction.sender_id == user_id).order_by(Transaction.timestamp.desc()).all()

def get_transaction_by_id(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def get_audit_log_by_transaction_id(db: Session, transaction_id: int):
    return db.query(AuditLog).filter(AuditLog.transaction_id == transaction_id).first()

def get_escalated_transactions(db: Session):
    return db.query(Transaction).filter(Transaction.status == "ESCALATED").order_by(Transaction.timestamp.desc()).all()

def record_approved_transaction_ledger(db: Session, tx_id: int):
    from app.models.models import Transaction, User, LedgerEntry
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx or tx.status != "APPROVED":
        return
    
    sender = db.query(User).filter(User.id == tx.sender_id).first()
    # Check if we already recorded a ledger entry for this transaction to avoid duplicates
    existing_debit = db.query(LedgerEntry).filter(
        LedgerEntry.user_id == tx.sender_id,
        LedgerEntry.reference_id == str(tx.id),
        LedgerEntry.type == "DEBIT"
    ).first()
    if existing_debit:
        return
    
    recipient = tx.recipient
    # Check if recipient is a registered local user by looking up their account number
    recip_user = db.query(User).filter(User.account_number == recipient.account_number).first()
    
    if recip_user:
        # Credit recipient balance
        recip_user.balance += tx.amount
        db.add(recip_user)
        db.commit() # commit immediately to get correct snapshot balance_after
        
        # Create credit ledger entry for recipient
        recip_ledger = LedgerEntry(
            user_id=recip_user.id,
            type="CREDIT",
            category="P2P_RECEIVE",
            amount=tx.amount,
            balance_after=recip_user.balance,
            description=f"Received funds from {sender.full_name or sender.username}",
            reference_id=str(tx.id),
            counterparty=sender.full_name or sender.username
        )
        db.add(recip_ledger)
        
        # Create debit ledger entry for sender
        sender_ledger = LedgerEntry(
            user_id=sender.id,
            type="DEBIT",
            category="P2P_SENT",
            amount=tx.amount,
            balance_after=sender.balance,
            description=f"Transferred funds to {recip_user.full_name or recip_user.username}",
            reference_id=str(tx.id),
            counterparty=recip_user.full_name or recip_user.username
        )
        db.add(sender_ledger)
    else:
        # Standard external recipient debit ledger entry
        sender_ledger = LedgerEntry(
            user_id=sender.id,
            type="DEBIT",
            category="TRANSFER_OUT",
            amount=tx.amount,
            balance_after=sender.balance,
            description=f"Transferred funds to {recipient.name} ({recipient.bank_name})",
            reference_id=str(tx.id),
            counterparty=recipient.name
        )
        db.add(sender_ledger)
    
    db.commit()


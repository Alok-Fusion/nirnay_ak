from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance = Column(Float, default=10000.0)
    security_score = Column(Float, default=85.0)
    mpin = Column(String, nullable=True) # Plain text MPIN for simplified demo validation or hashed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # KYC & Neo-Banking fields
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    aadhaar_last4 = Column(String(4), nullable=True)
    pan_number = Column(String(10), nullable=True)
    driving_license = Column(String, nullable=True)
    account_number = Column(String(12), unique=True, index=True, nullable=True)
    ifsc_code = Column(String, default="NIRN0000001")
    is_tour_completed = Column(Boolean, default=False)
    is_frozen = Column(Boolean, default=False)
    daily_transfer_limit = Column(Float, default=200000.0)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    last_login_device = Column(String, nullable=True)

    # Relationships
    digital_twin = relationship("DigitalTwin", back_populates="user", uselist=False)
    recipients = relationship("Recipient", back_populates="user")
    transactions = relationship("Transaction", back_populates="sender", foreign_keys="[Transaction.sender_id]")
    audit_logs = relationship("AuditLog", back_populates="user")
    ledger_entries = relationship("LedgerEntry", back_populates="user")
    security_logs = relationship("SecurityLog", back_populates="user")
    virtual_cards = relationship("VirtualCard", back_populates="user")
    fixed_deposits = relationship("FixedDeposit", back_populates="user")

class DigitalTwin(Base):
    __tablename__ = "digital_twins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    trust_level = Column(String, default="NEW") # NEW, STABLE, HIGHLY_TRUSTED
    transaction_count = Column(Integer, default=0)
    avg_transaction_amount = Column(Float, default=0.0)
    total_spend = Column(Float, default=0.0)
    known_devices = Column(Text, default="[]") # JSON list of devices
    known_locations = Column(Text, default="[]") # JSON list of locations
    trusted_recipients_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="digital_twin")

class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    trust_score = Column(Float, default=80.0) # 0 to 100
    is_blacklisted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="recipients")
    transactions = relationship("Transaction", back_populates="recipient", foreign_keys="[Transaction.recipient_id]")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("recipients.id"), nullable=False)
    amount = Column(Float, nullable=False)
    device = Column(String, nullable=False)
    location = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="PENDING") # PENDING, APPROVED, BLOCKED, ESCALATED, CHALLENGED
    risk_score = Column(Float, default=0.0)
    explanation = Column(Text, nullable=True) # SHAP reasons or descriptions
    auth_steps_required = Column(String, default="PASSWORD") # Comma-separated: PASSWORD, MPIN, OTP
    auth_steps_completed = Column(String, default="PASSWORD") # Comma-separated
    
    # Relationships
    sender = relationship("User", back_populates="transactions", foreign_keys=[sender_id])
    recipient = relationship("Recipient", back_populates="transactions", foreign_keys=[recipient_id])
    audit_log = relationship("AuditLog", back_populates="transaction", uselist=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ml_features = Column(Text, nullable=True) # JSON features
    rule_triggers = Column(Text, nullable=True) # JSON rules triggered
    agent_logs = Column(Text, nullable=True) # JSON list of agent thoughts/logs
    decision = Column(String, nullable=False) # e.g. APPROVE, BLOCK, ESCALATE, CHALLENGE
    execution_time_ms = Column(Integer, default=0)

    # Relationships
    transaction = relationship("Transaction", back_populates="audit_log")
    user = relationship("User", back_populates="audit_logs")

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False) # CREDIT or DEBIT
    category = Column(String, nullable=False) # SALARY, UPI_RECEIVE, BANK_TRANSFER, REFUND, P2P_RECEIVE, TRANSFER_OUT, P2P_SENT, FD_CREATE, FD_LIQUIDATE
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    reference_id = Column(String, nullable=True)
    counterparty = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="ledger_entries")

class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False) # LOGIN_SUCCESS, LOGIN_FAILED, ACCOUNT_FROZEN, etc.
    ip_address = Column(String, nullable=True)
    device = Column(String, nullable=True)
    details = Column(Text, nullable=True) # JSON details
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="security_logs")

class VirtualCard(Base):
    __tablename__ = "virtual_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_number = Column(String(16), unique=True, index=True, nullable=False)
    expiry_date = Column(String(5), nullable=False) # MM/YY
    cvv = Column(String(3), nullable=False)
    card_holder = Column(String, nullable=False)
    status = Column(String, default="ACTIVE") # ACTIVE, FROZEN
    card_type = Column(String, default="VISA_DEBIT") # VISA_DEBIT, MASTERCARD_PREMIUM
    spend_limit = Column(Float, default=50000.0)
    total_spent = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="virtual_cards")

class FixedDeposit(Base):
    __tablename__ = "fixed_deposits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    principal_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False) # % per annum
    duration_months = Column(Integer, nullable=False)
    maturity_amount = Column(Float, nullable=False)
    status = Column(String, default="ACTIVE") # ACTIVE, MATURED, LIQUIDATED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    matures_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="fixed_deposits")

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# Authentication Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    mpin: str = Field(..., min_length=4, max_length=6, description="MPIN must be 4 to 6 digits")

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    balance: float
    security_score: float
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Recipient Schemas
class RecipientCreate(BaseModel):
    name: str
    account_number: str
    bank_name: str

class RecipientOut(BaseModel):
    id: int
    user_id: int
    name: str
    account_number: str
    bank_name: str
    trust_score: float
    is_blacklisted: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionInitiate(BaseModel):
    recipient_id: int
    amount: float = Field(..., gt=0)
    device: str
    location: str

class TransactionOut(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    amount: float
    device: str
    location: str
    timestamp: datetime
    status: str
    risk_score: float
    explanation: Optional[str] = None
    auth_steps_required: str
    auth_steps_completed: str
    recipient: Optional[RecipientOut] = None

    class Config:
        from_attributes = True

class TransactionAuthChallenge(BaseModel):
    transaction_id: int
    password: Optional[str] = None
    mpin: Optional[str] = None
    otp: Optional[str] = None

class TransactionClarification(BaseModel):
    transaction_id: int
    response_text: str

# Dashboard / Security Center
class DigitalTwinOut(BaseModel):
    trust_level: str
    transaction_count: int
    avg_transaction_amount: float
    total_spend: float
    known_devices: List[str]
    known_locations: List[str]
    trusted_recipients_count: int

class DashboardSummary(BaseModel):
    balance: float
    security_score: float
    trust_level: str
    transaction_count: int
    recent_transactions: List[TransactionOut]

# Admin
class AdminOverrideRequest(BaseModel):
    transaction_id: int
    action: str # FORCE_APPROVE or FORCE_BLOCK

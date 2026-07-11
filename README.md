# NIRNAY: AI-Protected Neo-Banking & Autonomous Decision Intelligence Platform

> **Tagline:** Moving Beyond Passive Fraud Detection. Entering the Era of Autonomous Decision Protection.

---

## 📌 Table of Contents
1. [Executive Summary & Problem Statement](#-executive-summary--problem-statement)
2. [Platform Architecture & Core Flow](#-platform-architecture--core-flow)
3. [Deep-Dive Feature Catalog](#-deep-dive-feature-catalog)
   - [AI & Social Engineering Protection Core](#ai--social-engineering-protection-core)
   - [Neo-Banking Operations & Ledger System](#neo-banking-operations--ledger-system)
   - [Enterprise Security Controls](#enterprise-security-controls)
   - [Unique Strategic Capabilities](#unique-strategic-capabilities)
4. [API Endpoints Reference](#-api-endpoints-reference)
5. [Database Models & Schemas](#-database-models--schemas)
6. [Detailed Installation & Setup Guide](#-detailed-installation--setup-guide)
7. [Verification & Testing Suite](#-verification--testing-suite)

---

## 🎯 Executive Summary & Problem Statement

Modern digital banking systems suffer from a critical flaw: **traditional fraud detection is reactive, binary, and easily bypassed by social engineering.** When a victim is coached by a scammer over a call, they complete standard multi-factor authentication (OTP, MPIN) themselves. To the bank, the transaction appears completely legitimate.

**NIRNAY** solves this by establishing a **hybrid decision intelligence platform** that operates inside a full neo-banking container. NIRNAY evaluates transactions not as isolated events, but as actions within a behavioral context:
1. **Behavioral Digital Twin**: Analyzes deviation from the user's spending habits (amount, location, device, frequency).
2. **Rule Engine & ML**: Runs deterministic policy rules alongside SHAP feature models.
3. **Multi-Agent Collaborative AI Core**: Invokes 5 specialized LLM agents (Context, Policy, Interpretation, Memory, Conversation) to evaluate intent, scan natural language justifications for scam patterns, and decide the final status (`APPROVED`, `CHALLENGED`, or `BLOCKED`).

---

## 🏗️ Platform Architecture & Core Flow

NIRNAY is split into a robust FastAPI backend and a responsive, high-fidelity React + TypeScript frontend.

```
   User Initiation (P2P or standard transfer)
                 │
                 ▼
     ┌───────────────────────┐
     │  Account Lock Checks  │ ➔ If user.is_frozen ➔ Reject Transfer
     └───────────┬───────────┘
                 ▼
     ┌───────────────────────┐
     │  Daily limit checks   │ ➔ If rolling 24h limit exceeded ➔ Reject
     └───────────┬───────────┘
                 ▼
     ┌───────────────────────┐
     │ Beneficiary Cooling?  │ ➔ If recipient created < 24h & transfer > $10,000
     └───────────┬───────────┘    ➔ Flag with rule trigger + force OTP
                 ▼
     ┌───────────────────────┐
     │ Hybrid Risk Evaluator │
     │  - Rule Engine        │ ➔ 8 compliance rules checked
     │  - ML Risk Model      │ ➔ Calculate SHAP feature weightings
     └───────────┬───────────┘
                 ▼
   ┌──────────────────────────┐
   │ Multi-Agent AI Core      │ ➔ Evaluates context, scans intent justifications
   │ (LangGraph Collaborative)│   using Groq API or local heuristics
   └─────────────┬────────────┘
                 ▼
    Are challenge inputs required?
         ├─── YES ➔ Challenge Screen (MPIN, OTP, Intent Clarification)
         │           ├── Verification passes ➔ APPROVED ➔ Deduct balance & seed Ledger
         │           └── Scam intent detected ➔ BLOCKED ➔ Record audit trail
         │
         └─── NO ➔ APPROVED ➔ Deduct balance, update twin profiles, write Ledger Entry
```

---

## 🧠 Deep-Dive Feature Catalog

### AI & Social Engineering Protection Core
*   **LangGraph Collaborative Agents**:
    *   *Context Agent*: Gathers and structure transaction history metadata.
    *   *Interpretation Agent*: Resolves anomalies between ML outputs and rule triggers.
    *   *Policy Agent*: Reviews compliance parameters.
    *   *Conversation Agent*: Prompts the user with natural language questions if intent is ambiguous.
    *   *Memory Agent*: Stores historical transaction logs for future context.
*   **Explainable ML Risk & SHAP values**: Computes risk probability based on features like location match, device integrity, spending velocity, and recipient reputation. Renders interactive horizontal SHAP chart bars to explain decision parameters.
*   **Fallback Heuristics**: If the primary Groq LLM API quota is exhausted or times out, the backend automatically fails-safe to robust local keyword policy scanners (checking 30+ scam terms) to protect users.

### Neo-Banking Operations & Ledger System
*   **Passbook Ledger**: All cash movements are logged inside a database Ledger containing credit/debit types, amount, snapshot balances, and description.
*   **Direct P2P Routing**: Send funds instantly to other accounts via a 12-digit account number. Fetches and verifies beneficiary legal name in real-time.
*   **Demo Balance Deposits**: Add mock funds instantly using UPI, Wire Transfer, Salary Credits, or Refund categories.
*   **Statement Exports**: Export full ledger statements in `.csv` format for accounting or reporting.

### Enterprise Security Controls
*   **Brute Force Lockout**: 5 failed login credentials entries locks the account for 15 minutes. Logs events to the security activity audit trail.
*   **Emergency Account Freeze**: User-initiated freeze instantly disables all outgoing transfers. Unfreezable only by inputting the correct 4-6 digit MPIN.
*   **Daily Spending Limits**: Custom daily spending limits validated and confirmed via security MPIN.
*   **Inactivity Session Timeout**: Standard 10-minute inactivity monitor. Prompts a warning alert at the 9-minute mark and auto-logouts the user to prevent screen-takeover threats.

### Unique Strategic Capabilities
*   **Scam Drill Simulator**: 8 interactive gamified training exercises based on real-world Indian scam scripts (phishing emails, KYC updates, police arrest threats, OLX UPI refund requests).
*   **AI Explainability Report**: Downloads a fully structured markdown audit report (`.md`) containing ML models parameters, SHAP variables, triggered policy rules, and multi-agent reasoning timelines for regulatory compliance.
*   **Velocity Heatmap**: Grid maps the frequency and risk of transactions over 7 days and 24 hours.

---

## 🔌 API Endpoints Reference

### Authentication Operations
*   `POST /api/v1/auth/register`: Create a new user with full KYC details (Aadhaar, PAN, DL, phone, address).
*   `POST /api/v1/auth/login`: Authenticate credentials, logs login events, increments brute lockout counters.
*   `GET /api/v1/auth/me`: Fetch authenticated user profile data.
*   `PUT /api/v1/auth/profile`: Update contact details (phone, email, address).
*   `POST /api/v1/auth/tour-complete`: Set onboarding tour state to completed.

### Banking Operations
*   `POST /api/v1/banking/deposit`: Add money to account balance.
*   `GET /api/v1/banking/passbook`: Fetch all credit/debit ledger events.
*   `GET /api/v1/banking/balance`: Fetch balance details, account number, IFSC, and credits/debits totals.
*   `GET /api/v1/banking/lookup`: Lookup local user's legal name by account number.
*   `POST /api/v1/banking/p2p-transfer`: Initiate P2P transfer route.

### Security Operations
*   `POST /api/v1/security/freeze`: Freeze account outgoing transfers.
*   `POST /api/v1/security/unfreeze`: Unfreeze account via MPIN.
*   `GET /api/v1/security/activity-log`: Fetch audit trails of security logs.
*   `PUT /api/v1/security/update-limit`: Modify rolling daily transfer limits.
*   `PUT /api/v1/security/change-password`: Update password (checks current password and validates password strength).

### Interactive Core APIs
*   `POST /api/v1/transactions/initiate`: Evaluate standard transaction requests.
*   `POST /api/v1/transactions/authenticate`: Submit MPIN/OTP challenges.
*   `POST /api/v1/transactions/clarify`: Submit natural language justification text.
*   `GET /api/v1/transactions/{transaction_id}/audit`: Fetch decision consensus trace logs.
*   `GET /api/v1/transactions/{transaction_id}/report`: Fetch full compliance download report data.
*   `GET /api/v1/drills/scenario`: Fetch a random scam simulator training task.
*   `POST /api/v1/drills/answer`: Verify scam simulator answers.

---

## 🗄️ Database Models & Schemas

### User Database Model (`models.py`)
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance = Column(Float, default=10000.0)
    security_score = Column(Float, default=85.0)
    mpin = Column(String, nullable=True)
    
    # KYC
    full_name = Column(String)
    phone = Column(String)
    address = Column(Text)
    aadhaar_last4 = Column(String(4))
    pan_number = Column(String(10))
    driving_license = Column(String, nullable=True)
    account_number = Column(String(12), unique=True)
    
    # Safety Locks
    is_frozen = Column(Boolean, default=False)
    daily_transfer_limit = Column(Float, default=200000.0)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
```

---

## ⚙️ Detailed Installation & Setup Guide

### System Prerequisites
- Python 3.9 or higher
- Node.js v16 or higher

### 1. Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run server
python run.py
```
FastAPI server starts on `http://localhost:8000`. Database file `nirnay.db` will be created automatically.

### 2. Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install packages
npm install

# Start Vite dev server
npm run dev
```
Open your browser and navigate to `http://localhost:5173`.

---

## 🧪 Verification & Testing Suite

NIRNAY is built with test-driven integrity. You can verify the behavior of all ML predictions, multi-agent decisions, and core endpoints using the python test suites.

### Run ML Models & Digital Twin Tests
```bash
cd backend
.\venv\Scripts\python test_ml_twin.py
```
*Verifies: ML risk score weighting calculations, SHAP contributions mapping, and Digital Twin parameter updates.*

### Run API Route Integration Tests
```bash
cd backend
.\venv\Scripts\python test_integration.py
```
*Verifies: Account creation KYC parameters parsing, login lockout timers, deposits execution, and P2P payments security evaluation.*

### Run TypeScript Compilation Check
```bash
cd frontend
npx tsc --noEmit
```
*Verifies: Full frontend TypeScript compilation compiles clean.*

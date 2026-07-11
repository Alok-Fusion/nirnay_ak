# NIRNAY: AI-Protected Neo-Banking & Decision Intelligence Platform

> **Tagline:** Beyond Fraud Detection. Towards Autonomous Neo-Banking Security.

NIRNAY is a premium, AI-powered Neo-Banking and Decision Intelligence Platform that redefines how digital transactions are protected, processed, and audited. 

Unlike traditional banking software or binary fraud systems that approve or block actions based on simple static indicators, NIRNAY evaluates customer behavioral profiles, recipient risk ratings, and compliance rules in real-time. It routes transaction evaluation through a collaborative Multi-Agent AI core, executes adaptive verification challenges, and logs every money movement inside an immutable passbook ledger.

---

## 🏗️ Technical Architecture & Money Flow

```
   KYC Sign-Up (Aadhaar, PAN) ➔ Onboarding Tour ➔ Available Balance Dashboard
                                                        │
 ┌──────────────────────────────────────────────────────┴──────────────────────────────────────────────────────┐
 ▼                                                                                                             ▼
Add Money / Deposit (UPI, Wire)                                                                 P2P / Standard Transfer (Protected)
 │                                                                                                             │
 ▼                                                                                                             ▼
CREDIT Ledger Entry                                                                              TransactionOrchestrator Checks:
                                                                                                 1. Freeze Lock Verification
                                                                                                 2. Daily limit evaluation
                                                                                                 3. Beneficiary cooling check
                                                                                                               │
                                                                                                               ▼
                                                                                                 Hybrid Decision Pipeline:
                                                                                                 - Rule Engine (8 compliance rules)
                                                                                                 - ML Risk Evaluator + SHAP Values
                                                                                                               │
                                                                                                               ▼
                                                                                                 Multi-Agent AI reasoning core:
                                                                                                 - Context, Policy, and Memory
                                                                                                               │
                                                                                                               ▼
                                                                                                 Adaptive Authentication Verification:
                                                                                                 - Password ➔ MPIN ➔ OTP intent prompt
                                                                                                               │
                                                                                                               ▼
                                                                                                      APPROVED / BLOCKED
                                                                                                               │
                                ┌──────────────────────────────────────────────────────────────────────────────┴──────────────────────────────┐
                                ▼                                                                                                             ▼
                         DEBIT Ledger Entry (Sender)                                                                                   CREDIT Ledger (Recipient)
```

---

## 🌟 Core Neo-Banking & Security Features

### 🏢 Banking Primitives
- **Immutable Passbook Ledger**: Tracks all cash flow movements (credits and debits) with running balance snapshots. Includes CSV statement download capability.
- **Auto-Generated Accounts**: Auto-generates unique 12-digit account numbers and IFSC code `NIRN0000001` on registration.
- **P2P Wire Transfers**: Instant transfers directly to other system users using their account numbers with name verification checkups.
- **Flexible Deposits**: "Add Money" feature supporting UPI, Bank Wire Transfers, Salary, and Refunds.
- **Guided Onboarding Tour**: Highlights dashboard metrics, transfer forms, and security insights step-by-step for fresh users.

### 🛡️ Enterprise Security Operations (Real-Bank Equivalents)
- **3-Step KYC Sign-up**: Gathers full name, email, phone, masked Aadhaar (only last 4 stored), PAN card formatting checks, and optional DL.
- **Failed Login Lockout**: 5 failed credentials attempts locks login for 15 minutes to defeat brute force.
- **Configurable Daily limits**: Users can customize their spending limits inside settings confirmed via security MPIN.
- **Instant Account Freeze**: Self-service emergency switch that locks all outgoing transfers. Unfreezable only with MPIN.
- **Activity Log Audit Trails**: Audit trails for logins, locks, freezes, and profile updates.
- **Session timeout Warning**: Auto-invalidates inactive sessions after 10 minutes with popup extend warnings at the 9-minute mark.
- **Beneficiary Cooling Period**: Transfers to recipients created <24h ago exceeding $10,000 auto-trigger high-risk OTP challenge paths.
- **Password Strength Rules**: Validates passwords for length (8+ chars), mixed casing, numerals, and special characters.

### 🧠 Unique AI Decisions Layer
- **Scam Drill Simulator**: Gamified social engineering exercises featuring 8 realistic India-specific scenarios (Tech Support, Phishing, KYC links, UPI OLX requests, romance/job scams) to train customer awareness.
- **AI Explainability Report**: Downloadable compliance audit report displaying SHAP factors, rule evaluations, decision steps, and agent logs.
- **Risk Velocity Heatmap**: 7x24 grid color-coding spending patterns to identify anomalous transaction periods.

---

## 📂 Project Structure

- `backend/`: FastAPI implementation, SQLite db, SQLAlchemy models, Pydantic schemas, and Multi-Agent Orchestrator.
- `frontend/`: React + Vite + TS client interface, dashboard, analytics charts, settings screens, passbook, and guided tours.

---

## ⚙️ Setup & Running Instructions

### Backend
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the development server:
   ```bash
   python run.py
   ```
   The backend API will run on `http://localhost:8000`.

### Frontend
1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite dev server:
   ```bash
   npm run dev
   ```
   The UI will be accessible at `http://localhost:5173`.

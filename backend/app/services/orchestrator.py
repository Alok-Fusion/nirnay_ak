from sqlalchemy.orm import Session
from app.models.models import User, DigitalTwin, Recipient, Transaction, AuditLog
from app.services.ml_engine import MLEngine
from app.services.rule_engine import RuleEngine
from app.services.agents import MultiAgentOrchestrator
from app.services.digital_twin import DigitalTwinService
from datetime import datetime, timezone
import json
import time

class TransactionOrchestrator:
    def __init__(self):
        self.agent_orchestrator = MultiAgentOrchestrator()

    def process_transaction(
        self,
        db: Session,
        sender_id: int,
        recipient_id: int,
        amount: float,
        device: str,
        location: str
    ) -> dict:
        start_time = time.time()
        
        # 1. Basic validation
        user = db.query(User).filter(User.id == sender_id).first()
        recipient = db.query(Recipient).filter(Recipient.id == recipient_id).first()
        twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == sender_id).first()

        if not user:
            return {"error": "Sender not found"}
        if not recipient:
            return {"error": "Recipient not found"}
        if not twin:
            return {"error": "Sender digital twin not initialized"}

        # 2. Check balance
        if user.balance < amount:
            return {"error": "Insufficient account balance"}

        # 3. Execute Deterministic Rule Engine
        rule_result = RuleEngine.evaluate_rules(
            db=db,
            sender_id=sender_id,
            recipient_id=recipient_id,
            amount=amount,
            device=device,
            location=location
        )
        rule_decision = rule_result["decision"]
        triggered_rules = rule_result["triggered_rules"]

        # 4. Execute ML Risk Engine
        ml_result = MLEngine.evaluate_risk(
            db=db,
            sender_id=sender_id,
            recipient_id=recipient_id,
            amount=amount,
            device=device,
            location=location
        )
        risk_score = ml_result["risk_score"]

        # 5. Hybrid Intelligence Decision Pipeline
        # Decide if AI Multi-Agent reasoning is needed
        agent_logs = []
        requires_clarification = False
        clarification_prompt = ""
        decision_status = "PENDING"
        
        # If rules or ML indicate any elevated risk, invoke AI agents
        if rule_decision != "SAFE" or risk_score >= 20.0:
            agent_result = self.agent_orchestrator.run_agents(
                db=db,
                sender_id=sender_id,
                recipient_id=recipient_id,
                amount=amount,
                device=device,
                location=location,
                ml_risk_data=ml_result,
                rule_data=rule_result
            )
            agent_logs = agent_result["agent_logs"]
            requires_clarification = agent_result["requires_clarification"]
            clarification_prompt = agent_result["clarification_prompt"]
        else:
            # Safe bypass logs
            agent_logs = [
                {"agent": "Context Agent", "action": "Scanned risk", "message": "Transaction parameters within green boundaries. Multi-agent bypass enabled."},
                {"agent": "Decision Engine", "action": "Fast-path approval", "message": "Low risk profile. Standard authentication required."}
            ]

        # 6. Determine Adaptive Authentication Challenge
        # Safe: PASSWORD (already authenticated via session login)
        # Suspicious: PASSWORD,MPIN
        # High Risk: PASSWORD,MPIN,OTP
        # Blacklisted / Emergency: BLOCK immediately
        
        auth_steps_required = "PASSWORD"
        if rule_decision == "HIGH_RISK" or risk_score >= 65.0:
            auth_steps_required = "PASSWORD,MPIN,OTP"
            decision_status = "CHALLENGED"
            if recipient.is_blacklisted:
                decision_status = "BLOCKED" # Hard block for blacklist
        elif rule_decision == "SUSPICIOUS" or risk_score >= 20.0:
            auth_steps_required = "PASSWORD,MPIN"
            decision_status = "CHALLENGED"
        else:
            decision_status = "APPROVED" # Safe transaction approved immediately!
            
        # If conversation agent demands clarification, make sure we challenge the user
        if requires_clarification and decision_status == "CHALLENGED":
            # Append OTP to force deep validation
            if "OTP" not in auth_steps_required:
                auth_steps_required += ",OTP"

        # 7. Create transaction record
        tx = Transaction(
            sender_id=sender_id,
            recipient_id=recipient_id,
            amount=amount,
            device=device,
            location=location,
            status=decision_status,
            risk_score=risk_score,
            explanation=json.dumps(ml_result.get("reason_codes", [])),
            auth_steps_required=auth_steps_required,
            auth_steps_completed="PASSWORD" # Session login is Step 1
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)

        # 8. Record Audit Log
        end_time = time.time()
        execution_time_ms = int((end_time - start_time) * 1000)
        
        audit = AuditLog(
            transaction_id=tx.id,
            user_id=sender_id,
            ml_features=json.dumps({
                "amount": amount,
                "risk_score": risk_score,
                "device": device,
                "location": location,
                "avg_amount": twin.avg_transaction_amount
            }),
            rule_triggers=json.dumps(triggered_rules),
            agent_logs=json.dumps(agent_logs),
            decision=decision_status,
            execution_time_ms=execution_time_ms
        )
        db.add(audit)
        db.commit()

        # 9. If transaction was fast-tracked and APPROVED, deduct balance & update Digital Twin
        if decision_status == "APPROVED":
            user.balance -= amount
            db.add(user)
            db.commit()
            
            # Update Digital Twin
            DigitalTwinService.update_profile(
                db=db,
                sender_id=sender_id,
                transaction_amount=amount,
                device=device,
                location=location
            )

        return {
            "transaction_id": tx.id,
            "status": decision_status,
            "risk_score": risk_score,
            "triggered_rules": triggered_rules,
            "auth_steps_required": auth_steps_required,
            "requires_clarification": requires_clarification,
            "clarification_prompt": clarification_prompt,
            "agent_logs": agent_logs,
            "shap_values": ml_result.get("shap_values", {}),
            "reason_codes": ml_result.get("reason_codes", []),
            "execution_time_ms": execution_time_ms
        }

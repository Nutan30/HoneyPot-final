from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from .connection import SessionLocal, init_db
from .models import SessionModel, MessageModel, ExtractedIOCModel

# Ensure tables exist on import
init_db()


class SessionRepository:
    """
    Central repository for persisting and querying Honeypot sessions,
    messages, and extracted IOCs using SQLite/SQLAlchemy.
    """

    @staticmethod
    def get_session(session_id: str) -> Optional[SessionModel]:
        with SessionLocal() as db:
            return db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

    @staticmethod
    def get_session_dict(session_id: str) -> Optional[Dict[str, Any]]:
        with SessionLocal() as db:
            session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            return session.to_dict() if session else None

    @staticmethod
    def get_or_create(session_id: str) -> SessionModel:
        with SessionLocal() as db:
            session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if not session:
                session = SessionModel(
                    session_id=session_id,
                    scam_detected=False,
                    confidence=0.0,
                    agent_active=False,
                    callback_sent=False,
                    total_messages=0,
                    turns=0,
                    fear_level=0.3,
                    persona={
                        "language": "English",
                        "tone": "middle-class cautious",
                        "tech_skill": "low",
                        "fear_level": 0.3,
                        "phase": "CONFUSED"
                    },
                    extracted_intelligence={
                        "bankAccounts": [],
                        "upiIds": [],
                        "phishingLinks": [],
                        "phoneNumbers": [],
                        "suspiciousKeywords": []
                    },
                    agent_notes="",
                    scam_classification="UNKNOWN"
                )
                db.add(session)
                db.commit()
                db.refresh(session)
            return session

    @staticmethod
    def get_or_create_dict(session_id: str) -> Dict[str, Any]:
        with SessionLocal() as db:
            session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if not session:
                session = SessionModel(
                    session_id=session_id,
                    scam_detected=False,
                    confidence=0.0,
                    agent_active=False,
                    callback_sent=False,
                    total_messages=0,
                    turns=0,
                    fear_level=0.3,
                    persona={
                        "language": "English",
                        "tone": "middle-class cautious",
                        "tech_skill": "low",
                        "fear_level": 0.3,
                        "phase": "CONFUSED"
                    },
                    extracted_intelligence={
                        "bankAccounts": [],
                        "upiIds": [],
                        "phishingLinks": [],
                        "phoneNumbers": [],
                        "suspiciousKeywords": []
                    },
                    agent_notes="",
                    scam_classification="UNKNOWN"
                )
                db.add(session)
                db.commit()
                db.refresh(session)
            return session.to_dict()

    @staticmethod
    def add_message(session_id: str, sender: str, text: str, detected_intent: Optional[str] = None) -> MessageModel:
        with SessionLocal() as db:
            session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if not session:
                session = SessionRepository.get_or_create(session_id)
                session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

            msg = MessageModel(
                session_id=session_id,
                sender=sender,
                text=text,
                detected_intent=detected_intent
            )
            db.add(msg)
            session.total_messages = (session.total_messages or 0) + 1
            db.commit()
            db.refresh(msg)
            return msg

    @staticmethod
    def update_detection(session_id: str, scam_detected: bool, confidence: float, agent_active: bool) -> None:
        with SessionLocal() as db:
            session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if session:
                if scam_detected:
                    session.scam_detected = True
                if agent_active:
                    session.agent_active = True
                session.confidence = max(session.confidence or 0.0, float(confidence or 0.0))
                db.commit()

    @staticmethod
    def update_agent_state(
        session_id: str,
        scenario: Optional[str] = None,
        phase: Optional[str] = None,
        turns: Optional[int] = None,
        fear_level: Optional[float] = None,
        persona: Optional[Dict[str, Any]] = None
    ) -> None:
        with SessionLocal() as db:
            session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if session:
                if scenario is not None:
                    session.scenario = scenario
                if phase is not None:
                    session.phase = phase
                if turns is not None:
                    session.turns = turns
                if fear_level is not None:
                    session.fear_level = float(fear_level)
                if persona is not None:
                    session.persona = persona
                db.commit()

    @staticmethod
    def update_intelligence(
        session_id: str,
        extracted_intelligence: Dict[str, Any],
        agent_notes: Optional[str] = None,
        scam_classification: Optional[str] = None,
        scam_detected: Optional[bool] = None
    ) -> None:
        with SessionLocal() as db:
            session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if session:
                # Merge existing intelligence with new fields
                current = session.extracted_intelligence or {}
                if isinstance(extracted_intelligence, dict):
                    for k, v in extracted_intelligence.items():
                        if isinstance(v, list):
                            current_list = current.get(k, [])
                            combined = list(dict.fromkeys(current_list + v))
                            current[k] = combined
                        elif v is not None:
                            current[k] = v

                session.extracted_intelligence = current

                if agent_notes is not None:
                    session.agent_notes = agent_notes
                if scam_classification is not None:
                    session.scam_classification = scam_classification
                if scam_detected is not None and scam_detected:
                    session.scam_detected = True

                # Save individual IOC rows for fast dashboard searching
                SessionRepository._sync_ioc_records(db, session_id, current)
                db.commit()

    @staticmethod
    def _sync_ioc_records(db: Session, session_id: str, intel: Dict[str, Any]) -> None:
        """Internal helper to insert unique IOC records into the extracted_iocs table."""
        ioc_mappings = {
            "upiIds": "upi",
            "phoneNumbers": "phone",
            "phishingLinks": "link",
            "bankAccounts": "bank_account",
            "suspiciousKeywords": "keyword"
        }

        existing_values = {
            (ioc.ioc_type, ioc.value)
            for ioc in db.query(ExtractedIOCModel).filter(ExtractedIOCModel.session_id == session_id).all()
        }

        for intel_key, ioc_type in ioc_mappings.items():
            items = intel.get(intel_key, [])
            if isinstance(items, list):
                for item in items:
                    val = str(item).strip()
                    if val and (ioc_type, val) not in existing_values:
                        db.add(ExtractedIOCModel(
                            session_id=session_id,
                            ioc_type=ioc_type,
                            value=val
                        ))
                        existing_values.add((ioc_type, val))

    @staticmethod
    def set_callback_sent(session_id: str, status: bool = True) -> None:
        with SessionLocal() as db:
            session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if session:
                session.callback_sent = status
                db.commit()

    @staticmethod
    def list_sessions(limit: int = 50, offset: int = 0, scam_only: bool = False) -> List[Dict[str, Any]]:
        with SessionLocal() as db:
            query = db.query(SessionModel)
            if scam_only:
                query = query.filter(SessionModel.scam_detected == True)
            sessions = query.order_by(SessionModel.updated_at.desc()).offset(offset).limit(limit).all()
            return [s.to_dict() for s in sessions]

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Aggregate stats for honeypot dashboard."""
        with SessionLocal() as db:
            total_sessions = db.query(SessionModel).count()
            scams_detected = db.query(SessionModel).filter(SessionModel.scam_detected == True).count()
            total_messages = db.query(MessageModel).count()
            total_iocs = db.query(ExtractedIOCModel).count()
            unique_upis = db.query(ExtractedIOCModel).filter(ExtractedIOCModel.ioc_type == "upi").distinct().count()
            unique_links = db.query(ExtractedIOCModel).filter(ExtractedIOCModel.ioc_type == "link").distinct().count()
            unique_phones = db.query(ExtractedIOCModel).filter(ExtractedIOCModel.ioc_type == "phone").distinct().count()

            return {
                "totalSessions": total_sessions,
                "scamsDetected": scams_detected,
                "totalMessages": total_messages,
                "totalIOCs": total_iocs,
                "uniqueUPIs": unique_upis,
                "uniquePhishingLinks": unique_links,
                "uniquePhoneNumbers": unique_phones
            }

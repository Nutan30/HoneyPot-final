from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Float,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    func
)
from sqlalchemy.orm import relationship
from .connection import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    scam_detected = Column(Boolean, default=False, index=True)
    confidence = Column(Float, default=0.0)
    agent_active = Column(Boolean, default=False)
    callback_sent = Column(Boolean, default=False)
    scenario = Column(String(128), nullable=True)
    phase = Column(String(64), nullable=True)
    total_messages = Column(Integer, default=0)
    turns = Column(Integer, default=0)
    fear_level = Column(Float, default=0.3)
    persona = Column(JSON, nullable=True)
    extracted_intelligence = Column(JSON, nullable=True)
    agent_notes = Column(Text, nullable=True)
    scam_classification = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.id", lazy="joined")
    iocs = relationship("ExtractedIOCModel", back_populates="session", cascade="all, delete-orphan", lazy="selectin")

    def to_dict(self):
        """Converts model to dictionary matching legacy session schema for backwards compatibility."""
        return {
            "sessionId": self.session_id,
            "scamDetected": bool(self.scam_detected),
            "confidence": float(self.confidence or 0.0),
            "agentActive": bool(self.agent_active),
            "callbackSent": bool(self.callback_sent),
            "scenario": self.scenario,
            "phase": self.phase,
            "totalMessages": self.total_messages or 0,
            "turns": self.turns or 0,
            "fearLevel": float(self.fear_level or 0.3),
            "persona": self.persona or {},
            "extractedIntelligence": self.extracted_intelligence or {},
            "agentNotes": self.agent_notes or "",
            "scamClassification": self.scam_classification or "UNKNOWN",
            "messages": [m.to_dict() for m in self.messages],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id", ondelete="CASCADE"), index=True, nullable=False)
    sender = Column(String(32), nullable=False, index=True)  # "scammer", "agent", "user"
    text = Column(Text, nullable=False)
    detected_intent = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=func.now())

    session = relationship("SessionModel", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "text": self.text,
            "detectedIntent": self.detected_intent,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class ExtractedIOCModel(Base):
    __tablename__ = "extracted_iocs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id", ondelete="CASCADE"), index=True, nullable=False)
    ioc_type = Column(String(32), nullable=False, index=True)  # "upi", "phone", "link", "bank_account", "keyword"
    value = Column(String(512), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    session = relationship("SessionModel", back_populates="iocs")

    def to_dict(self):
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "iocType": self.ioc_type,
            "value": self.value,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class CanaryTokenModel(Base):
    __tablename__ = "canary_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(String(64), unique=True, index=True, nullable=False)
    session_id = Column(String(64), nullable=True, index=True)
    token_type = Column(String(32), nullable=False, index=True)  # "card", "upi", "url"
    decoy_value = Column(String(256), nullable=False)
    tripped = Column(Boolean, default=False, index=True)
    tripped_at = Column(DateTime, nullable=True)
    client_ip = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "tokenId": self.token_id,
            "sessionId": self.session_id,
            "tokenType": self.token_type,
            "decoyValue": self.decoy_value,
            "tripped": bool(self.tripped),
            "trippedAt": self.tripped_at.isoformat() if self.tripped_at else None,
            "clientIp": self.client_ip,
            "userAgent": self.user_agent,
            "extraData": self.extra_data or {},
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

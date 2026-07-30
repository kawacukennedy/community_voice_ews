import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ReportType(str, enum.Enum):
    flood = "flood"
    drought = "drought"
    pest = "pest"
    disease = "disease"
    fire = "fire"
    conflict = "conflict"
    health = "health"
    other = "other"


class Severity(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class ReportStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    dismissed = "dismissed"


class AlertStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class Community(Base):
    __tablename__ = "communities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=False, unique=True)
    language = Column(String(10), default="en")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    region = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    reports = relationship("Report", back_populates="community")
    alerts = relationship("Alert", back_populates="community")


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id = Column(UUID(as_uuid=True), ForeignKey("communities.id"), nullable=True)
    message = Column(Text, nullable=False)
    source = Column(String(50), default="sms")
    report_type = Column(SAEnum(ReportType), default=ReportType.other)
    severity = Column(SAEnum(Severity), default=Severity.moderate)
    status = Column(SAEnum(ReportStatus), default=ReportStatus.pending)
    confidence = Column(Float, default=0.0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    media_url = Column(String(500), nullable=True)
    nlp_raw = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    community = relationship("Community", back_populates="reports")
    alerts = relationship("Alert", back_populates="report")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True)
    community_id = Column(UUID(as_uuid=True), ForeignKey("communities.id"), nullable=True)
    alert_type = Column(SAEnum(ReportType), default=ReportType.other)
    severity = Column(SAEnum(Severity), default=Severity.moderate)
    status = Column(SAEnum(AlertStatus), default=AlertStatus.active)
    region = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source = Column(String(100), default="system")
    sent_via_sms = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    report = relationship("Report", back_populates="alerts")
    community = relationship("Community", back_populates="alerts")

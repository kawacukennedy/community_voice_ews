import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Community(Base):
    __tablename__ = "communities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=False, unique=True)
    language = Column(String(10), default="en")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    region = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    reports = relationship("Report", back_populates="community")
    alerts = relationship("Alert", back_populates="community")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    community_id = Column(String(36), ForeignKey("communities.id"), nullable=True)
    message = Column(Text, nullable=False)
    source = Column(String(50), default="sms")
    report_type = Column(String(50), default="other")
    severity = Column(String(50), default="moderate")
    status = Column(String(50), default="pending")
    confidence = Column(Float, default=0.0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    media_url = Column(String(500), nullable=True)
    nlp_raw = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    community = relationship("Community", back_populates="reports")
    alerts = relationship("Alert", back_populates="report")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=True)
    community_id = Column(String(36), ForeignKey("communities.id"), nullable=True)
    alert_type = Column(String(50), default="other")
    severity = Column(String(50), default="moderate")
    status = Column(String(50), default="active")
    region = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source = Column(String(100), default="system")
    sent_via_sms = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    report = relationship("Report", back_populates="alerts")
    community = relationship("Community", back_populates="alerts")

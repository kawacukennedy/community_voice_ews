from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    contact_name: Optional[str] = None
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{6,14}$")
    language: str = "en"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None
    country: Optional[str] = None

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lng(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v


class CommunityResponse(BaseModel):
    id: UUID
    name: str
    contact_name: Optional[str]
    phone: str
    language: str
    latitude: Optional[float]
    longitude: Optional[float]
    region: Optional[str]
    country: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=1600)
    community_id: Optional[UUID] = None
    phone_number: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    source: str = "web"
    media_url: Optional[str] = None

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lng(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v


class ReportResponse(BaseModel):
    id: UUID
    community_id: Optional[UUID]
    message: str
    source: str
    report_type: str
    severity: str
    status: str
    confidence: float
    latitude: Optional[float]
    longitude: Optional[float]
    location_name: Optional[str]
    phone_number: Optional[str]
    submitted_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=1600)
    report_id: Optional[UUID] = None
    community_id: Optional[UUID] = None
    alert_type: str = "other"
    severity: str = "moderate"
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: str = "system"
    expires_at: Optional[datetime] = None

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lng(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v


class AlertResponse(BaseModel):
    id: UUID
    title: str
    message: str
    report_id: Optional[UUID]
    community_id: Optional[UUID]
    alert_type: str
    severity: str
    status: str
    region: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    source: str
    sent_via_sms: bool
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SMSWebhookPayload(BaseModel):
    from_number: str = Field(..., alias="from")
    text: str = Field(..., alias="text", min_length=1)
    date: Optional[str] = None
    id: Optional[str] = None
    linkId: Optional[str] = None

    class Config:
        populate_by_name = True


class SMSWebhookResponse(BaseModel):
    status: str
    message: str
    report_id: Optional[UUID] = None


class StatsResponse(BaseModel):
    total_reports: int
    total_alerts: int
    total_communities: int
    reports_by_type: dict
    reports_by_severity: dict
    active_alerts: int
    recent_reports: List[ReportResponse]


class ClassificationResult(BaseModel):
    report_type: str
    severity: str
    confidence: float
    keywords_found: List[str]


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

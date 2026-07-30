import uuid
import logging
import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.models import Base, Community, Report, Alert
from app.schemas import (
    CommunityCreate, CommunityResponse,
    ReportCreate, ReportResponse,
    AlertCreate, AlertResponse,
    SMSWebhookPayload, SMSWebhookResponse,
    StatsResponse, ClassificationResult,
)
from app.services.nlp import classify_message
from app.services.sms import send_sms, broadcast_alert
from app.services.icpac import get_icpac_alerts
from app.utils.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

engine = None
SessionLocal = None

if settings.database_url and settings.database_url.startswith("sqlite"):
    try:
        init_engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(init_engine)
        init_engine.dispose()
        logger.info("Database tables created at %s", settings.database_url)
    except Exception as e:
        logger.warning("Could not initialize database at startup: %s", e)


def get_db_engine():
    global engine
    if engine is None and settings.database_url:
        connect_args = {}
        if settings.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
    return engine


def get_session():
    global SessionLocal
    if SessionLocal is None:
        db_url = settings.database_url
        if db_url:
            SessionLocal = sessionmaker(bind=get_db_engine())
        else:
            return None
    try:
        session = SessionLocal()
        return session
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        return None


def get_db():
    session = get_session()
    if session is None:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Community Voice EWS API v%s", settings.app_version)
    if settings.database_url:
        try:
            engine = get_db_engine()
            if engine:
                Base.metadata.create_all(engine)
                logger.info("Database tables created/verified at %s", settings.database_url)
        except Exception as e:
            logger.warning("Could not initialize database: %s", e)
    else:
        logger.warning("No DATABASE_URL configured - running with in-memory storage")
    yield
    logger.info("Shutting down Community Voice EWS API")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InMemoryDB:
    def __init__(self):
        self.communities: dict = {}
        self.reports: dict = {}
        self.alerts: dict = {}

    def add_community(self, data: dict) -> dict:
        cid = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        record = {"id": cid, **data, "is_active": True, "created_at": now, "updated_at": now}
        self.communities[cid] = record
        return record

    def add_report(self, data: dict) -> dict:
        rid = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        record = {"id": rid, **data, "created_at": now, "submitted_at": now}
        self.reports[rid] = record
        return record

    def add_alert(self, data: dict) -> dict:
        aid = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        record = {"id": aid, **data, "created_at": now}
        self.alerts[aid] = record
        return record


memory_db = InMemoryDB()


def _to_dict(obj):
    if obj is None:
        return None
    d = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        d[col.name] = val
    return d


@app.get("/api/health")
async def health_check():
    db_status = "connected" if settings.database_url else "not_configured"
    return {
        "status": "ok",
        "version": settings.app_version,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(payload: ReportCreate, db: Session = Depends(get_db)):
    try:
        classification = classify_message(payload.message)

        report_data = {
            "message": payload.message,
            "source": payload.source,
            "phone_number": payload.phone_number,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "location_name": payload.location_name,
            "media_url": payload.media_url,
            "report_type": classification["report_type"],
            "severity": classification["severity"],
            "confidence": classification["confidence"],
            "status": "pending",
            "nlp_raw": str(classification),
        }

        community = None
        if db:
            if payload.community_id:
                community = db.query(Community).filter(Community.id == str(payload.community_id)).first()
            elif payload.phone_number:
                community = db.query(Community).filter(Community.phone == payload.phone_number).first()

            report = Report(
                community_id=str(community.id) if community else None,
                **report_data,
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            result = _to_dict(report)
        else:
            report_data["community_id"] = str(payload.community_id) if payload.community_id else None
            result = memory_db.add_report(report_data)

        logger.info("Report created: %s type=%s severity=%s confidence=%.2f",
                     result.get("id"), classification["report_type"], classification["severity"], classification["confidence"])

        if classification["severity"] in ("high", "critical"):
            try:
                alert_data = {
                    "title": f"{classification['report_type'].title()} Alert",
                    "message": f"Automated alert: {classification['report_type']} reported - {payload.message[:200]}",
                    "report_id": result.get("id"),
                    "alert_type": classification["report_type"],
                    "severity": classification["severity"],
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                    "source": "auto_nlp",
                    "status": "active",
                    "sent_via_sms": False,
                }
                if db:
                    alert = Alert(**alert_data)
                    db.add(alert)
                    db.commit()
                else:
                    memory_db.add_alert(alert_data)
                logger.info("Auto-alert created for high-severity report %s", result.get("id"))
            except Exception as e:
                logger.error("Failed to create auto-alert: %s", e)

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating report: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create report")


@app.get("/api/reports", response_model=list[ReportResponse])
async def get_reports(
    report_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        if db:
            query = db.query(Report)
            if report_type:
                query = query.filter(Report.report_type == report_type)
            if severity:
                query = query.filter(Report.severity == severity)
            if status:
                query = query.filter(Report.status == status)
            if region:
                query = query.filter(Report.location_name.ilike(f"%{region}%"))
            query = query.order_by(Report.submitted_at.desc()).offset(offset).limit(limit)
            return [_to_dict(r) for r in query.all()]
        else:
            results = list(memory_db.reports.values())
            if report_type:
                results = [r for r in results if r["report_type"] == report_type]
            if severity:
                results = [r for r in results if r["severity"] == severity]
            if status:
                results = [r for r in results if r["status"] == status]
            if region and results:
                results = [r for r in results if r.get("location_name") and region.lower() in r["location_name"].lower()]
            results.sort(key=lambda r: r["submitted_at"], reverse=True)
            return results[offset:offset + limit]
    except Exception as e:
        logger.error("Error fetching reports: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch reports")


@app.get("/api/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, db: Session = Depends(get_db)):
    try:
        if db:
            report = db.query(Report).filter(Report.id == report_id).first()
        else:
            report = memory_db.reports.get(report_id)

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return _to_dict(report) if db else report
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching report %s: %s", report_id, e)
        raise HTTPException(status_code=500, detail="Failed to fetch report")


@app.get("/api/alerts", response_model=list[AlertResponse])
async def get_alerts(
    alert_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: str = Query("active"),
    db: Session = Depends(get_db),
):
    try:
        if db:
            query = db.query(Alert)
            if alert_type:
                query = query.filter(Alert.alert_type == alert_type)
            if severity:
                query = query.filter(Alert.severity == severity)
            query = query.filter(Alert.status == status)
            query = query.order_by(Alert.created_at.desc()).limit(100)
            return [_to_dict(a) for a in query.all()]
        else:
            results = list(memory_db.alerts.values())
            if alert_type:
                results = [a for a in results if a["alert_type"] == alert_type]
            if severity:
                results = [a for a in results if a["severity"] == severity]
            results = [a for a in results if a.get("status") == status]
            results.sort(key=lambda a: a["created_at"], reverse=True)
            return results[:100]
    except Exception as e:
        logger.error("Error fetching alerts: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


@app.post("/api/alerts", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    try:
        alert_data = payload.model_dump()

        if db:
            alert = Alert(**alert_data, status="active", sent_via_sms=False)
            db.add(alert)
            db.commit()
            db.refresh(alert)
            result = _to_dict(alert)
        else:
            alert_data["status"] = "active"
            alert_data["sent_via_sms"] = False
            result = memory_db.add_alert(alert_data)

        communities = []
        if db:
            query = db.query(Community).filter(Community.is_active == True)
            if payload.region:
                query = query.filter(Community.region.ilike(f"%{payload.region}%"))
            communities = query.all()
        else:
            communities = list(memory_db.communities.values())
            if payload.region:
                communities = [c for c in communities if c.get("region") and payload.region.lower() in c["region"].lower()]

        if communities:
            phone_numbers = []
            if db:
                phone_numbers = [c.phone for c in communities if c.phone]
            else:
                phone_numbers = [c["phone"] for c in communities if c.get("phone")]
            broadcast_alert(phone_numbers, payload.title, payload.message, payload.severity)

            if db:
                alert.sent_via_sms = True
                alert.sent_at = datetime.now(timezone.utc)
                db.commit()

        logger.info("Alert created: %s sent to %d communities", result.get("id"), len(communities))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating alert: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create alert")


@app.post("/api/webhooks/sms", response_model=SMSWebhookResponse)
async def sms_webhook(payload: SMSWebhookPayload, request: Request):
    try:
        raw_body = await request.body()
        logger.info("SMS webhook received from %s: %s", payload.from_number, payload.text[:100])

        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type:
            form_data = await request.form()
            from_form = form_data.get("from") or form_data.get("From")
            text_form = form_data.get("text") or form_data.get("Body") or form_data.get("message")
            if from_form and text_form:
                payload.from_number = from_form
                payload.text = text_form

        classification = classify_message(payload.text)

        report_data = {
            "message": payload.text,
            "source": "sms",
            "phone_number": payload.from_number,
            "report_type": classification["report_type"],
            "severity": classification["severity"],
            "confidence": classification["confidence"],
            "status": "pending",
            "nlp_raw": str(classification),
        }

        db = get_session()
        report_id = None
        if db:
            community = db.query(Community).filter(Community.phone == payload.from_number).first()
            report = Report(community_id=str(community.id) if community else None, **report_data)
            db.add(report)
            db.commit()
            db.refresh(report)
            report_id = report.id
            db.close()
        else:
            result = memory_db.add_report(report_data)
            report_id = result["id"]

        confirmation = f"Received! Your report classified as {classification['report_type']} ({classification['severity']}). Thank you for keeping your community safe."
        send_sms(payload.from_number, confirmation)

        logger.info("SMS processed: report=%s type=%s severity=%s", report_id, classification["report_type"], classification["severity"])

        return SMSWebhookResponse(
            status="success",
            message="Report processed successfully",
            report_id=report_id,
        )
    except Exception as e:
        logger.error("Error processing SMS webhook: %s", e, exc_info=True)
        return SMSWebhookResponse(
            status="error",
            message="Failed to process SMS",
        )


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    try:
        if db:
            from sqlalchemy import func

            total_reports = db.query(Report).count()
            total_alerts = db.query(Alert).count()
            total_communities = db.query(Community).count()
            active_alerts = db.query(Alert).filter(Alert.status == "active").count()

            reports_by_type_rows = db.query(Report.report_type, func.count(Report.id)).group_by(Report.report_type).all()
            reports_by_severity_rows = db.query(Report.severity, func.count(Report.id)).group_by(Report.severity).all()

            recent = db.query(Report).order_by(Report.submitted_at.desc()).limit(5).all()
        else:
            total_reports = len(memory_db.reports)
            total_alerts = len(memory_db.alerts)
            total_communities = len(memory_db.communities)
            active_alerts = len([a for a in memory_db.alerts.values() if a.get("status") == "active"])

            from collections import Counter
            type_counter = Counter(r["report_type"] for r in memory_db.reports.values())
            severity_counter = Counter(r["severity"] for r in memory_db.reports.values())
            reports_by_type_rows = [(k, v) for k, v in type_counter.items()]
            reports_by_severity_rows = [(k, v) for k, v in severity_counter.items()]

            recent = sorted(memory_db.reports.values(), key=lambda r: r["submitted_at"], reverse=True)[:5]

        reports_by_type = {row[0]: row[1] for row in reports_by_type_rows}
        reports_by_severity = {row[0]: row[1] for row in reports_by_severity_rows}

        return StatsResponse(
            total_reports=total_reports,
            total_alerts=total_alerts,
            total_communities=total_communities,
            reports_by_type=reports_by_type,
            reports_by_severity=reports_by_severity,
            active_alerts=active_alerts,
            recent_reports=[_to_dict(r) if db else r for r in recent],
        )
    except Exception as e:
        logger.error("Error fetching stats: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch stats")


@app.get("/api/communities", response_model=list[CommunityResponse])
async def get_communities(db: Session = Depends(get_db)):
    try:
        if db:
            communities = db.query(Community).order_by(Community.created_at.desc()).limit(200).all()
            return [_to_dict(c) for c in communities]
        else:
            results = list(memory_db.communities.values())
            results.sort(key=lambda c: c["created_at"], reverse=True)
            return results[:200]
    except Exception as e:
        logger.error("Error fetching communities: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch communities")


@app.post("/api/communities", response_model=CommunityResponse, status_code=status.HTTP_201_CREATED)
async def create_community(payload: CommunityCreate, db: Session = Depends(get_db)):
    try:
        if db:
            existing = db.query(Community).filter(Community.phone == payload.phone).first()
            if existing:
                raise HTTPException(status_code=409, detail="Community with this phone already exists")
            community = Community(**payload.model_dump())
            db.add(community)
            db.commit()
            db.refresh(community)
            result = _to_dict(community)
        else:
            if any(c["phone"] == payload.phone for c in memory_db.communities.values()):
                raise HTTPException(status_code=409, detail="Community with this phone already exists")
            result = memory_db.add_community(payload.model_dump())

        logger.info("Community created: %s (%s)", result.get("name"), result.get("phone"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating community: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create community")


@app.post("/api/classify", response_model=ClassificationResult)
async def classify_message_endpoint(text: str = Query(..., min_length=1, max_length=1600)):
    try:
        result = classify_message(text)
        return ClassificationResult(**result)
    except Exception as e:
        logger.error("Error classifying message: %s", e)
        raise HTTPException(status_code=500, detail="Classification failed")


@app.post("/api/icpac/sync")
async def sync_icpac(db: Session = Depends(get_db)):
    try:
        alerts_data = await get_icpac_alerts()
        created = 0
        for item in alerts_data:
            if db:
                existing = db.query(Alert).filter(
                    Alert.title == item["title"],
                    Alert.region == item["region"],
                    Alert.status == "active",
                ).first()
                if existing:
                    continue
                alert = Alert(
                    title=item["title"],
                    message=item["description"][:1500],
                    alert_type=item["alert_type"],
                    severity=item["severity"],
                    region=item["region"],
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    source=item["source"],
                    status="active",
                )
                db.add(alert)
            else:
                memory_db.add_alert(item)
            created += 1

        if db:
            db.commit()

        return {"status": "success", "alerts_created": created, "source": "icpac"}
    except Exception as e:
        logger.error("Error syncing ICPAC: %s", e)
        raise HTTPException(status_code=500, detail="Failed to sync ICPAC data")


FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists():
    @app.get("/")
    async def serve_frontend():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/{full_path:path}")
    async def serve_frontend_spa(full_path: str):
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
            raise HTTPException(status_code=404, detail="Not found")
        fp = FRONTEND_DIR / full_path
        if fp.exists() and fp.is_file():
            return FileResponse(str(fp))
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    logger.info("Serving frontend from %s", FRONTEND_DIR)
else:
    logger.warning("Frontend not found at %s", FRONTEND_DIR)

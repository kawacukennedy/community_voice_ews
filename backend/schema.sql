-- Community Voice EWS - SQLite Schema
-- SQLAlchemy will auto-create tables via Base.metadata.create_all()
-- This schema is provided for reference and manual setup

CREATE TABLE IF NOT EXISTS communities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    contact_name TEXT,
    phone TEXT NOT NULL UNIQUE,
    language TEXT DEFAULT 'en',
    latitude REAL,
    longitude REAL,
    region TEXT,
    country TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    community_id TEXT REFERENCES communities(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    source TEXT DEFAULT 'sms',
    report_type TEXT DEFAULT 'other',
    severity TEXT DEFAULT 'moderate',
    status TEXT DEFAULT 'pending',
    confidence REAL DEFAULT 0.0,
    latitude REAL,
    longitude REAL,
    location_name TEXT,
    phone_number TEXT,
    media_url TEXT,
    nlp_raw TEXT,
    submitted_at TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    report_id TEXT REFERENCES reports(id) ON DELETE SET NULL,
    community_id TEXT REFERENCES communities(id) ON DELETE SET NULL,
    alert_type TEXT DEFAULT 'other',
    severity TEXT DEFAULT 'moderate',
    status TEXT DEFAULT 'active',
    region TEXT,
    latitude REAL,
    longitude REAL,
    source TEXT DEFAULT 'system',
    sent_via_sms INTEGER DEFAULT 0,
    sent_at TEXT,
    expires_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_severity ON reports(severity);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_submitted ON reports(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_communities_phone ON communities(phone);

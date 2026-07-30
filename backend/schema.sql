-- Community Voice EWS - Database Schema for Supabase (PostgreSQL)
-- Run this in the Supabase SQL Editor after creating a new project

-- Enable PostGIS for geospatial queries
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS communities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    phone VARCHAR(50) NOT NULL UNIQUE,
    language VARCHAR(10) DEFAULT 'en',
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    region VARCHAR(255),
    country VARCHAR(100),
    location GEOGRAPHY(Point, 4326),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    community_id UUID REFERENCES communities(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    source VARCHAR(50) DEFAULT 'sms',
    report_type VARCHAR(50) DEFAULT 'other',
    severity VARCHAR(50) DEFAULT 'moderate',
    status VARCHAR(50) DEFAULT 'pending',
    confidence DOUBLE PRECISION DEFAULT 0.0,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location GEOGRAPHY(Point, 4326),
    location_name VARCHAR(255),
    phone_number VARCHAR(50),
    media_url VARCHAR(500),
    nlp_raw TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    report_id UUID REFERENCES reports(id) ON DELETE SET NULL,
    community_id UUID REFERENCES communities(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) DEFAULT 'other',
    severity VARCHAR(50) DEFAULT 'moderate',
    status VARCHAR(50) DEFAULT 'active',
    region VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location GEOGRAPHY(Point, 4326),
    source VARCHAR(100) DEFAULT 'system',
    sent_via_sms BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_severity ON reports(severity);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_submitted ON reports(submitted_at DESC);
CREATE INDEX idx_reports_location ON reports USING GIST(location);

CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);

CREATE INDEX idx_communities_phone ON communities(phone);
CREATE INDEX idx_communities_region ON communities(region);
CREATE INDEX idx_communities_location ON communities USING GIST(location);

-- ============================================================
-- TRIGGER: auto-update updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_communities_updated_at ON communities;
CREATE TRIGGER trg_communities_updated_at
    BEFORE UPDATE ON communities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- TRIGGER: auto-set location from lat/lng
-- ============================================================

CREATE OR REPLACE FUNCTION set_location()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_reports_location ON reports;
CREATE TRIGGER trg_reports_location
    BEFORE INSERT OR UPDATE OF latitude, longitude ON reports
    FOR EACH ROW
    EXECUTE FUNCTION set_location();

DROP TRIGGER IF EXISTS trg_communities_location ON communities;
CREATE TRIGGER trg_communities_location
    BEFORE INSERT OR UPDATE OF latitude, longitude ON communities
    FOR EACH ROW
    EXECUTE FUNCTION set_location();

DROP TRIGGER IF EXISTS trg_alerts_location ON alerts;
CREATE TRIGGER trg_alerts_location
    BEFORE INSERT OR UPDATE OF latitude, longitude ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION set_location();

-- ============================================================
-- AUTO-CREATE ALERT FOR HIGH-SEVERITY REPORTS
-- ============================================================

CREATE OR REPLACE FUNCTION auto_create_alert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.severity IN ('high', 'critical') THEN
        INSERT INTO alerts (
            title, message, report_id, alert_type, severity,
            latitude, longitude, location, source, status
        ) VALUES (
            INITCAP(NEW.report_type) || ' Alert',
            'Automated alert: ' || NEW.report_type || ' reported - ' || LEFT(NEW.message, 200),
            NEW.id, NEW.report_type, NEW.severity,
            NEW.latitude, NEW.longitude, NEW.location, 'auto_nlp', 'active'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_reports_auto_alert ON reports;
CREATE TRIGGER trg_reports_auto_alert
    AFTER INSERT ON reports
    FOR EACH ROW
    EXECUTE FUNCTION auto_create_alert();

-- ============================================================
-- VIEWS
-- ============================================================

CREATE OR REPLACE VIEW v_active_alerts AS
SELECT
    a.id,
    a.title,
    a.message,
    a.alert_type,
    a.severity,
    a.region,
    a.latitude,
    a.longitude,
    a.source,
    a.created_at,
    COUNT(r.id) AS related_reports
FROM alerts a
LEFT JOIN reports r ON r.report_type = a.alert_type
    AND r.created_at >= NOW() - INTERVAL '7 days'
WHERE a.status = 'active'
GROUP BY a.id, a.title, a.message, a.alert_type, a.severity,
         a.region, a.latitude, a.longitude, a.source, a.created_at
ORDER BY a.severity DESC, a.created_at DESC;

CREATE OR REPLACE VIEW v_community_stats AS
SELECT
    c.id,
    c.name,
    c.region,
    c.country,
    c.latitude,
    c.longitude,
    COUNT(DISTINCT r.id) AS total_reports,
    COUNT(DISTINCT a.id) AS total_alerts,
    MAX(r.submitted_at) AS last_report_at
FROM communities c
LEFT JOIN reports r ON r.community_id = c.id
LEFT JOIN alerts a ON a.community_id = c.id
GROUP BY c.id, c.name, c.region, c.country, c.latitude, c.longitude;

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

ALTER TABLE communities ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Public read access for the dashboard
CREATE POLICY "Public read communities"
    ON communities FOR SELECT
    USING (TRUE);

CREATE POLICY "Public read reports"
    ON reports FOR SELECT
    USING (TRUE);

CREATE POLICY "Public read alerts"
    ON alerts FOR SELECT
    USING (TRUE);

-- Authenticated users can insert
CREATE POLICY "Authenticated insert communities"
    ON communities FOR INSERT
    WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'anon');

CREATE POLICY "Authenticated insert reports"
    ON reports FOR INSERT
    WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'anon');

-- Admin-only for updates/deletes
CREATE POLICY "Admin update communities"
    ON communities FOR UPDATE
    USING (auth.role() = 'authenticated');

CREATE POLICY "Admin update reports"
    ON reports FOR UPDATE
    USING (auth.role() = 'authenticated');

-- ============================================================
-- FUNCTIONS
-- ============================================================

CREATE OR REPLACE FUNCTION find_nearby_reports(
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    radius_km DOUBLE PRECISION DEFAULT 10.0,
    max_results INT DEFAULT 50
)
RETURNS TABLE(
    id UUID,
    message TEXT,
    report_type VARCHAR,
    severity VARCHAR,
    distance_m DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    submitted_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.message,
        r.report_type,
        r.severity,
        ST_Distance(
            r.location,
            ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography
        ) AS distance_m,
        r.latitude,
        r.longitude,
        r.submitted_at
    FROM reports r
    WHERE r.location IS NOT NULL
        AND ST_DWithin(
            r.location,
            ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography,
            radius_km * 1000
        )
    ORDER BY distance_m
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql STABLE;

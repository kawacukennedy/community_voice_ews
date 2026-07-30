import httpx
import logging
from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta
from app.utils.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

ICPAC_ENDPOINTS = {
    "flood_forecast": "https://maps.icpac.net/geoserver/icpac/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=icpac:flood_hazard&outputFormat=application/json",
    "drought_forecast": "https://maps.icpac.net/geoserver/icpac/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=icpac:drought_hazard&outputFormat=application/json",
    "rainfall": "https://maps.icpac.net/geoserver/icpac/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=icpac:rainfall_anomaly&outputFormat=application/json",
    "hazards": "https://maps.icpac.net/geoserver/icpac/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=icpac:multi_hazard&outputFormat=application/json",
}


async def fetch_icpac_data(data_type: str = "all") -> List[Dict]:
    results = []

    if data_type == "all":
        endpoints = ICPAC_ENDPOINTS
    elif data_type in ICPAC_ENDPOINTS:
        endpoints = {data_type: ICPAC_ENDPOINTS[data_type]}
    else:
        logger.warning("Unknown ICPAC data type: %s", data_type)
        return []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for name, url in endpoints.items():
            try:
                resp = await client.get(url, headers={"Accept": "application/json"})
                if resp.status_code == 200:
                    data = resp.json()
                    features = data.get("features", [])
                    parsed = [_parse_icpac_feature(f, name) for f in features[:50]]
                    results.extend(parsed)
                    logger.info("Fetched %d features from ICPAC %s", len(parsed), name)
                else:
                    logger.warning("ICPAC %s returned status %d", name, resp.status_code)
            except httpx.TimeoutException:
                logger.warning("Timeout fetching ICPAC %s", name)
            except Exception as e:
                logger.error("Error fetching ICPAC %s: %s", name, str(e))

    return results


def _parse_icpac_feature(feature: Dict, source: str) -> Dict:
    props = feature.get("properties", {})
    geom = feature.get("geometry", {})

    center = None
    if geom.get("type") == "Point":
        coords = geom.get("coordinates", [0, 0])
        center = {"longitude": coords[0], "latitude": coords[1]}
    elif geom.get("type") in ("Polygon", "MultiPolygon"):
        try:
            coords = geom.get("coordinates", [[[0, 0]]])
            if geom["type"] == "Polygon":
                ring = coords[0]
            else:
                ring = coords[0][0]
            lats = [c[1] for c in ring]
            lngs = [c[0] for c in ring]
            center = {"latitude": sum(lats) / len(lats), "longitude": sum(lngs) / len(lngs)}
        except (IndexError, TypeError, ZeroDivisionError):
            center = {"latitude": 0, "longitude": 0}

    hazard_type = source.split("_")[0] if "_" in source else "general"
    severity_raw = (props.get("hazard_class") or props.get("severity") or props.get("risk_level") or "moderate").lower()
    severity_map = {"1": "low", "2": "moderate", "3": "high", "4": "critical", "very low": "low", "low": "low", "moderate": "moderate", "high": "high", "very high": "critical", "extreme": "critical"}
    severity = severity_map.get(severity_raw, "moderate")

    return {
        "source": f"icpac_{source}",
        "alert_type": hazard_type,
        "severity": severity,
        "title": props.get("name") or props.get("title") or f"{hazard_type.capitalize()} Warning",
        "description": props.get("description") or props.get("abstract") or f"{hazard_type.capitalize()} hazard detected in the region",
        "region": props.get("admin_name") or props.get("region") or props.get("country") or "Unknown",
        "latitude": center["latitude"] if center else None,
        "longitude": center["longitude"] if center else None,
        "issued_at": props.get("date") or props.get("issued") or datetime.now(timezone.utc).isoformat(),
        "raw_data": dict(list(props.items())[:10])
    }


async def get_icpac_alerts() -> List[Dict]:
    data = await fetch_icpac_data("all")
    alerts = []
    for item in data:
        if item["severity"] in ("high", "critical"):
            alerts.append(item)
    return alerts

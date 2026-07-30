import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import Report, Alert, Community
from app.services.nlp import classify_message

logger = logging.getLogger(__name__)

SAMPLE_DATA = {
    "communities": [
        {"name": "Kibera Community Watch", "phone": "+254700100001", "region": "Nairobi",
         "country": "Kenya", "latitude": -1.3150, "longitude": 36.7850, "language": "sw"},
        {"name": "Garissa Flood Network", "phone": "+254700100002", "region": "Garissa",
         "country": "Kenya", "latitude": -0.4569, "longitude": 39.6583, "language": "sw"},
        {"name": "Bududa Landslide Monitors", "phone": "+256700200001", "region": "Bududa",
         "country": "Uganda", "latitude": 1.0175, "longitude": 34.3333, "language": "en"},
        {"name": "Kampala Urban Alert", "phone": "+256700200002", "region": "Kampala",
         "country": "Uganda", "latitude": 0.3136, "longitude": 32.5811, "language": "en"},
        {"name": "Adama Drought Watch", "phone": "+251700300001", "region": "Oromia",
         "country": "Ethiopia", "latitude": 8.5400, "longitude": 39.2700, "language": "en"},
        {"name": "Mogadishu Coastal Alert", "phone": "+252700400001", "region": "Benadir",
         "country": "Somalia", "latitude": 2.0469, "longitude": 45.3182, "language": "so"},
        {"name": "Juba River Monitors", "phone": "+211700500001", "region": "Central Equatoria",
         "country": "South Sudan", "latitude": 4.8594, "longitude": 31.5828, "language": "en"},
        {"name": "Kisumu Lake Basin", "phone": "+254700100003", "region": "Kisumu",
         "country": "Kenya", "latitude": -0.1022, "longitude": 34.7617, "language": "sw"},
        {"name": "Arusha Meru Watch", "phone": "+255700600001", "region": "Arusha",
         "country": "Tanzania", "latitude": -3.3869, "longitude": 36.6830, "language": "sw"},
        {"name": "Hargeisa Drought Network", "phone": "+252700400002", "region": "Maroodi Jeex",
         "country": "Somalia", "latitude": 9.5600, "longitude": 44.0650, "language": "so"},
    ],
    "reports": [
        {"message": "Maji yamefurika barabara ya Mombasa, maji yameingia nyumbani.",
         "latitude": -4.0435, "longitude": 39.6682, "location_name": "Mombasa"},
        {"message": "Heavy rains have caused the Tana River to burst its banks. "
         "Several villages are flooded near Garissa.",
         "latitude": -0.4569, "longitude": 39.6583, "location_name": "Garissa"},
        {"message": "Njaa kali inatuangamiza. Mazao yamekauka kabisa, hakuna mvua kwa miezi mitatu.",
         "latitude": -1.2921, "longitude": 36.8219, "location_name": "Nairobi"},
        {"message": "Crops are wilting in the field. The maize is completely dry. We need food aid urgently.",
         "latitude": 8.5400, "longitude": 39.2700, "location_name": "Oromia"},
        {"message": "Desert locusts have invaded our farm. They are eating everything - "
         "maize, beans, cassava. In less than 2 hours the field was gone.",
         "latitude": 3.1198, "longitude": 35.5964, "location_name": "Turkana"},
        {"message": "Ndege wadudu wamekula mazao yetu yote. Tuna njaa. Msaada!",
         "latitude": 0.5143, "longitude": 34.5913, "location_name": "Busia"},
        {"message": "Fire is spreading through the forest near Mount Kenya. "
         "The wind is strong and it's heading toward the village.",
         "latitude": -0.1552, "longitude": 37.3144, "location_name": "Mount Kenya"},
        {"message": "We have several cases of cholera in the village. "
         "Five people are sick with severe diarrhea after the floods.",
         "latitude": 4.8594, "longitude": 31.5828, "location_name": "Juba"},
        {"message": "Malaria cases are rising fast. The clinic has treated 40 people this week alone. "
         "We need medicine and mosquito nets.",
         "latitude": 0.3136, "longitude": 32.5811, "location_name": "Kampala"},
        {"message": "The river is rising fast. Water level is already 2 meters above normal. "
         "We are evacuating low-lying areas.",
         "latitude": -0.1022, "longitude": 34.7617, "location_name": "Kisumu"},
        {"message": "Heavy hailstorm destroyed 20 homes in the village last night. "
         "Families are sleeping outside in the cold.",
         "latitude": -3.3869, "longitude": 36.6830, "location_name": "Arusha"},
        {"message": "Mvua ya mawe imeharibu nyumba nyingi hapa Arusha. Tunaomba msaada wa haraka.",
         "latitude": -3.3800, "longitude": 36.6900, "location_name": "Arusha"},
        {"message": "Drought has killed 30 cattle this month. Water wells are completely dry. "
         "We walk 10km for water now.",
         "latitude": 9.5600, "longitude": 44.0650, "location_name": "Hargeisa"},
        {"message": "A landslide buried three houses at the foot of Mount Elgon. "
         "Heavy rain triggered it. People are digging through mud.",
         "latitude": 1.0175, "longitude": 34.3333, "location_name": "Bududa"},
        {"message": "Conflict over water resources has broken out between two communities. "
         "5 people injured. We need peacekeepers.",
         "latitude": 3.1200, "longitude": 35.6000, "location_name": "Turkana"},
        {"message": "Mafuriko yameleta nyoka na wanyama hatari katika nyumba zetu. "
         "Watoto watano wameumwa na nyoka.",
         "latitude": -0.4569, "longitude": 39.6583, "location_name": "Garissa"},
        {"message": "Flash floods swept through the market this morning. "
         "15 people missing. The bridge to the main road is destroyed.",
         "latitude": -1.3150, "longitude": 36.7850, "location_name": "Kibera"},
        {"message": "Water sources contaminated after flooding. "
         "Many people drinking dirty water. Risk of disease outbreak is high.",
         "latitude": 4.8600, "longitude": 31.5800, "location_name": "Juba"},
        {"message": "Locust swarm estimated at 5km-wide approaching farming region. "
         "Praying for wind to change direction.",
         "latitude": 8.5400, "longitude": 39.2700, "location_name": "Oromia"},
        {"message": "Joto kali sana. Watu wazee wawili wamekufa kwa joto kupita kiasi. Hatuwezi kupumua.",
         "latitude": -1.2921, "longitude": 36.8219, "location_name": "Nairobi"},
    ],
}


def seed_db(db: Session):
    existing = db.query(Report).count()
    if existing > 0:
        logger.info("DB already has %d reports — skipping seed", existing)
        return

    logger.info("Seeding sample data...")

    for c in SAMPLE_DATA["communities"]:
        exists = db.query(Community).filter(Community.phone == c["phone"]).first()
        if not exists:
            db.add(Community(**c))
    db.commit()

    for r in SAMPLE_DATA["reports"]:
        classification = classify_message(r["message"])
        report = Report(
            message=r["message"],
            source="sms",
            latitude=r["latitude"],
            longitude=r["longitude"],
            location_name=r["location_name"],
            report_type=classification["report_type"],
            severity=classification["severity"],
            confidence=classification["confidence"],
            status="pending",
            submitted_at=datetime.now(timezone.utc),
        )
        db.add(report)
        db.flush()

        if classification["severity"] in ("high", "critical"):
            alert = Alert(
                title=f"{classification['report_type'].title()} Alert",
                message=f"Automated alert: {classification['report_type']} reported - {r['message'][:200]}",
                report_id=report.id,
                alert_type=classification["report_type"],
                severity=classification["severity"],
                latitude=r["latitude"],
                longitude=r["longitude"],
                source="auto_nlp",
                status="active",
                sent_via_sms=False,
            )
            db.add(alert)

    db.commit()

    count = db.query(Report).count()
    alerts = db.query(Alert).count()
    communities = db.query(Community).count()
    logger.info("Seed complete: %d reports, %d alerts, %d communities", count, alerts, communities)

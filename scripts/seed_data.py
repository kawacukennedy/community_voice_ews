import httpx
import time
import sys
import os

BASE = os.environ.get("SEED_BASE", sys.argv[1] if len(sys.argv) > 1 else "https://community-voice-ews.onrender.com")

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
        {"message": "Maji yamefurika barabara ya Mombasa, maji yameingia nyumbani. Tafadhali msaada!", "latitude": -4.0435, "longitude": 39.6682, "location_name": "Mombasa", "source": "sms"},
        {"message": "Heavy rains have caused the Tana River to burst its banks. Several villages are flooded near Garissa.", "latitude": -0.4569, "longitude": 39.6583, "location_name": "Garissa", "source": "sms"},
        {"message": "Njaa kali inatuangamiza. Mazao yamekauka kabisa, hakuna mvua kwa miezi mitatu.", "latitude": -1.2921, "longitude": 36.8219, "location_name": "Nairobi", "source": "sms"},
        {"message": "Crops are wilting in the field. The maize is completely dry. We need food aid urgently.", "latitude": 8.5400, "longitude": 39.2700, "location_name": "Oromia", "source": "sms"},
        {"message": "Desert locusts have invaded our farm. They are eating everything - maize, beans, cassava. In less than 2 hours the field was gone.", "latitude": 3.1198, "longitude": 35.5964, "location_name": "Turkana", "source": "sms"},
        {"message": "Ndege wadudu wamekula mazao yetu yote. Tuna njaa. Msaada!", "latitude": 0.5143, "longitude": 34.5913, "location_name": "Busia", "source": "sms"},
        {"message": "Fire is spreading through the forest near Mount Kenya. The wind is strong and it's heading toward the village.", "latitude": -0.1552, "longitude": 37.3144, "location_name": "Mount Kenya", "source": "sms"},
        {"message": "We have several cases of cholera in the village. Five people are sick with severe diarrhea after the floods.", "latitude": 4.8594, "longitude": 31.5828, "location_name": "Juba", "source": "sms"},
        {"message": "Malaria cases are rising fast. The clinic has treated 40 people this week alone. We need medicine and mosquito nets.", "latitude": 0.3136, "longitude": 32.5811, "location_name": "Kampala", "source": "sms"},
        {"message": "The river is rising fast. Water level is already 2 meters above normal. We are evacuating low-lying areas.", "latitude": -0.1022, "longitude": 34.7617, "location_name": "Kisumu", "source": "sms"},
        {"message": "Heavy hailstorm destroyed 20 homes in the village last night. Families are sleeping outside in the cold.", "latitude": -3.3869, "longitude": 36.6830, "location_name": "Arusha", "source": "sms"},
        {"message": "Mvua ya mawe imeharibu nyumba nyingi hapa Arusha. Tunaomba msaada wa haraka.", "latitude": -3.3800, "longitude": 36.6900, "location_name": "Arusha", "source": "sms"},
        {"message": "Drought has killed 30 cattle this month. Water wells are completely dry. We walk 10km for water now.", "latitude": 9.5600, "longitude": 44.0650, "location_name": "Hargeisa", "source": "sms"},
        {"message": "A landslide buried three houses at the foot of Mount Elgon. Heavy rain triggered it. People are digging through mud.", "latitude": 1.0175, "longitude": 34.3333, "location_name": "Bududa", "source": "sms"},
        {"message": "Conflict over water resources has broken out between two communities. 5 people injured. We need peacekeepers.", "latitude": 3.1200, "longitude": 35.6000, "location_name": "Turkana", "source": "sms"},
        {"message": "Mafuriko yameleta nyoka na wanyama hatari katika nyumba zetu. Watoto watano wameumwa na nyoka.", "latitude": -0.4569, "longitude": 39.6583, "location_name": "Garissa", "source": "sms"},
        {"message": "Flash floods swept through the market this morning. 15 people missing. The bridge to the main road is destroyed.", "latitude": -1.3150, "longitude": 36.7850, "location_name": "Kibera", "source": "sms"},
        {"message": "Water sources contaminated after flooding. Many people drinking dirty water. Risk of disease outbreak is high.", "latitude": 4.8600, "longitude": 31.5800, "location_name": "Juba", "source": "sms"},
        {"message": "Locust swarm estimated at 5km-wide approaching farming region. Praying for wind to change direction.", "latitude": 8.5400, "longitude": 39.2700, "location_name": "Oromia", "source": "sms"},
        {"message": "Joto kali sana. Watu wazee wawili wamekufa kwa joto kupita kiasi. Hatuwezi kupumua.", "latitude": -1.2921, "longitude": 36.8219, "location_name": "Nairobi", "source": "sms"},
    ],
}


def seed_communities():
    print("\n--- Seeding Communities ---")
    created = 0
    for c in SAMPLE_DATA["communities"]:
        try:
            r = httpx.post(f"{BASE}/api/communities", json=c, timeout=10)
            if r.status_code == 201:
                print(f"  + {c['name']} ({c['region']})")
                created += 1
            elif r.status_code == 409:
                print(f"  = {c['name']} (already exists)")
            else:
                print(f"  ? {c['name']}: {r.status_code} {r.text[:100]}")
        except Exception as e:
            print(f"  ! {c['name']}: {e}")
    print(f"  Created: {created}")
    return created


def seed_reports():
    print("\n--- Seeding Reports ---")
    created = 0
    for r in SAMPLE_DATA["reports"]:
        try:
            resp = httpx.post(f"{BASE}/api/reports", json=r, timeout=10)
            if resp.status_code == 201:
                data = resp.json()
                print(f"  + {data['report_type']:8s} ({data['severity']:8s}) {r['location_name']:15s} | {r['message'][:50]}")
                created += 1
            else:
                print(f"  ? {resp.status_code} {r['message'][:50]}: {resp.text[:100]}")
        except Exception as e:
            print(f"  ! {r['message'][:30]}: {e}")
        time.sleep(0.2)
    print(f"  Created: {created}")
    return created


def verify():
    print("\n--- Verifying ---")
    r = httpx.get(f"{BASE}/api/stats", timeout=10)
    stats = r.json()
    print(f"  Reports:     {stats['total_reports']}")
    print(f"  Alerts:      {stats['total_alerts']}")
    print(f"  Communities: {stats['total_communities']}")
    print(f"  Active Alerts: {stats['active_alerts']}")
    print(f"  By Type:     {stats['reports_by_type']}")
    print(f"  By Severity: {stats['reports_by_severity']}")


if __name__ == "__main__":
    print(f"Seeding data to {BASE}")
    seed_communities()
    seed_reports()
    verify()
    print("\nDone!")

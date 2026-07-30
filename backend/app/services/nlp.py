import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

CLASSIFICATION_KEYWORDS: Dict[str, List[Dict[str, object]]] = {
    "flood": [
        {"en": ["flood", "flooding", "water", "rain", "heavy rain", "river", "overflow", "submerged", "drowning", "swamped", "inundated", "torrential"], "sw": ["mafuriko", "maji", "mvua", "mvua kubwa", "ziwa", "kufurika", "kuzama", "gharika"], "severity_hint": {"critical": ["drowning", "evacuat", "emergency", "kuzama", "dharura"], "high": ["waist", "chest", "house", "nyumba", "majengo"], "moderate": ["road", "garden", "shamba", "barabara"]}},
        {"weight": 3, "severity_boost": 2}
    ],
    "drought": [
        {"en": ["drought", "dry", "no rain", "famine", "crop failure", "water shortage", "thirst", "arid", "barren", "dust", "cracked earth", "livestock dying"], "sw": ["ukame", "kavu", "hakuna mvua", "njaa", "mazao kukauka", "ukosefu wa maji", "mifugo kufa", "mboga kukauka"], "severity_hint": {"critical": ["starvation", "death", "dead", "kufa", "njaa kali"], "high": ["livestock", "mifugo", "crop", "mazao"], "moderate": ["dry", "kavu"]}},
        {"weight": 3, "severity_boost": 2}
    ],
    "pest": [
        {"en": ["pest", "locust", "armyworm", "caterpillar", "bugs", "infestation", "insects", "grasshopper", "aphid", "weevil", "borer", "invasion"], "sw": ["wadudu", "nzige", "vijasumu", "viwavi", "mbung'o", "kushambuliwa", "nyuki", "sisimizi"], "severity_hint": {"critical": ["swarm", "kundi", "swarming"], "high": ["infestation", "kushambulia", "spread"], "moderate": ["seen", "found", "some", "baadhi"]}},
        {"weight": 3, "severity_boost": 1}
    ],
    "disease": [
        {"en": ["disease", "outbreak", "sick", "illness", "cholera", "malaria", "typhoid", "fever", "diarrhea", "vomiting", "symptoms", "infection", "epidemic"], "sw": ["ugonjwa", "mlipuko", "mgonjwa", "maradhi", "kipindupindu", "malaria", "homa", "kuhara", "kutapika", "maambukizi"], "severity_hint": {"critical": ["deaths", "dying", "kufa", "epidemic", "janga"], "high": ["hospital", "hospitali", "many", "wengi"], "moderate": ["few", "wachache", "some"]}},
        {"weight": 3, "severity_boost": 2}
    ],
    "fire": [
        {"en": ["fire", "burning", "wildfire", "forest fire", "bush fire", "smoke", "flames", "blaze", "scorched", "charred", "arson"], "sw": ["moto", "kuungua", "mwako", "moshi", "waliowaka"], "severity_hint": {"critical": ["spread", "enaa", "uncontrollable", "homes", "nyumba"], "high": ["forest", "msitu", "bush", "vichaka"], "moderate": ["small", "ndogo"]}},
        {"weight": 2}
    ],
    "conflict": [
        {"en": ["conflict", "violence", "attack", "raid", "clash", "fighting", "war", "displaced", "refugee", "protest", "riot", "security"], "sw": ["vita", "mapigano", "shambulio", "uvunjifu", "watu wakimbia"], "severity_hint": {"critical": ["weapon", "silaha", "death", "kufa", "shooting", "risasi"], "high": ["injured", "kujeruhiwa", "attack", "shambulio"], "moderate": ["protest", "maandamano", "dispute", "mabishano"]}},
        {"weight": 2}
    ],
    "health": [
        {"en": ["health", "clinic", "hospital", "medical", "vaccination", "medicine", "treatment", "nutrition", "pregnant", "childbirth", "sanitation"], "sw": ["afya", "kliniki", "hospitali", "dawa", "chanjo", "matibabu", "lishe", "mimba", "usafi"], "severity_hint": {"critical": ["emergency", "dharura", "immediate", "mara moja"], "high": ["severe", "kali", "serious", "mbaya"], "moderate": ["need", "hitaji", "require"]}},
        {"weight": 1}
    ]
}

SEVERITY_ORDER = {"low": 0, "moderate": 1, "high": 2, "critical": 3}


def classify_message(text: str) -> dict:
    if not text or not text.strip():
        return {"report_type": "other", "severity": "low", "confidence": 0.0, "keywords_found": []}

    text_lower = text.lower().strip()
    scores: Dict[str, float] = {}
    severity_scores: Dict[str, int] = {}
    keywords_found: Dict[str, List[str]] = {}

    for category, config in CLASSIFICATION_KEYWORDS.items():
        category_score = 0.0
        category_severity = 0
        category_keywords = []
        weight = 1
        severity_boost = 1

        for entry in config:
            if isinstance(entry, dict) and "weight" in entry:
                weight = entry.get("weight", 1)
                severity_boost = entry.get("severity_boost", 1)
                continue

            keywords_en = entry.get("en", [])
            keywords_sw = entry.get("sw", [])
            severity_hints = entry.get("severity_hint", {})

            found = [kw for kw in keywords_en + keywords_sw if kw in text_lower]
            if found:
                match_count = len(found)
                category_score += match_count * weight
                category_keywords.extend(found)

                for sev_level, sev_kws in severity_hints.items():
                    if any(skw in text_lower for skw in sev_kws):
                        sev_idx = SEVERITY_ORDER.get(sev_level, 0)
                        category_severity = max(category_severity, sev_idx + severity_boost)

        if category_score > 0:
            scores[category] = category_score
            severity_scores[category] = min(category_severity, 3)
            keywords_found[category] = list(set(category_keywords))

    if not scores:
        return {"report_type": "other", "severity": "low", "confidence": 0.0, "keywords_found": []}

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    total_score = sum(scores.values())
    confidence = min(best_score / max(total_score, 1) * 0.95, 0.95)

    severity_idx = severity_scores.get(best_category, 0)
    severity_map = {0: "low", 1: "moderate", 2: "high", 3: "critical"}
    severity = severity_map.get(severity_idx, "moderate")

    logger.info(
        "Classified message as %s (severity=%s, confidence=%.2f) keywords=%s",
        best_category, severity, confidence, keywords_found.get(best_category, [])
    )

    return {
        "report_type": best_category,
        "severity": severity,
        "confidence": round(confidence, 4),
        "keywords_found": keywords_found.get(best_category, [])
    }

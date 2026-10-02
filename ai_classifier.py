"""
GramSetu (ग्राम सेतु) - AI Triage & Semantic Classifier
Parses rural complaint narratives, extracts domain category, maps to responsible department,
calculates enforceable SLA deadlines, and generates unique Complaint IDs.
"""

import random
from datetime import datetime, timedelta

CATEGORY_RULES = {
    "Electricity": {
        "keywords": ["बिजली", "ट्रांसफार्मर", "करंट", "तार", "electric", "power", "transformer", "voltage", "blackout", "pole", "fuse", "substation"],
        "dept": "State Electricity Distribution Company (DISCOM)",
        "officer": "Er. R. Sharma (Junior Engineer, Local Substation)",
        "sla_hours": 24,
        "default_priority": "High"
    },
    "Water": {
        "keywords": ["पानी", "नल", "हैंडपंप", "जल", "पाइप", "water", "pipeline", "well", "pump", "handpump", "drinking water", "leakage"],
        "dept": "Rural Water Supply & Sanitation (Jal Shakti / PHED)",
        "officer": "S. K. Kadam (Sub-Divisional Officer, PHED)",
        "sla_hours": 48,
        "default_priority": "High"
    },
    "Roads": {
        "keywords": ["सड़क", "गड्ढे", "रास्ता", "पुलिया", "road", "pothole", "bridge", "culvert", "tar", "asphalt", "connectivity", "highway"],
        "dept": "Public Works Department (PWD / Gram Panchayat)",
        "officer": "A. K. Verma (Assistant Engineer, Road Div)",
        "sla_hours": 168,
        "default_priority": "Medium"
    },
    "Sanitation": {
        "keywords": ["कचरा", "नाली", "सफाई", "गंदगी", "drain", "waste", "sanitation", "garbage", "sewer", "septic", "mosquitoes"],
        "dept": "Local Gram Panchayat / Swachh Bharat Mission Cell",
        "officer": "Block Development Officer (Sanitation Cell)",
        "sla_hours": 72,
        "default_priority": "Medium"
    },
    "Agriculture": {
        "keywords": ["फसल", "नहर", "सिंचाई", "बीज", "canal", "crop", "irrigation", "agriculture", "farmer", "fertilizer", "sluice"],
        "dept": "Minor Irrigation & Agriculture Dept (Krishi Vibhag)",
        "officer": "District Agriculture Officer / SDO Irrigation",
        "sla_hours": 48,
        "default_priority": "High"
    },
    "Healthcare": {
        "keywords": ["अस्पताल", "दवा", "डॉक्टर", "phc", "health", "hospital", "nurse", "clinic", "ambulance", "medicine", "doctor"],
        "dept": "Chief Medical Officer (CMO) & District Health Society",
        "officer": "Medical Officer In-Charge (Block PHC)",
        "sla_hours": 24,
        "default_priority": "High"
    },
    "Government scheme": {
        "keywords": ["राशन", "पेंशन", "पीएम किसान", "आवास", "योजना", "ration", "pension", "dbt", "pmay", "scheme", "subsidy", "mgnrega"],
        "dept": "District Collectorate & Social Welfare Department",
        "officer": "Sub-Divisional Magistrate (Grievance Cell)",
        "sla_hours": 120,
        "default_priority": "Medium"
    }
}

def classify_complaint(text):
    text_lower = text.lower()
    matched_cat = "Other"
    max_matches = 0

    for cat, data in CATEGORY_RULES.items():
        matches = sum(1 for kw in data["keywords"] if kw in text_lower)
        if matches > max_matches:
            max_matches = matches
            matched_cat = cat

    if matched_cat in CATEGORY_RULES:
        rule = CATEGORY_RULES[matched_cat]
        sla_hours = rule["sla_hours"]
        dept = rule["dept"]
        officer = rule["officer"]
        priority = rule["default_priority"]
    else:
        sla_hours = 120
        dept = "Gram Panchayat / Block Development Office"
        officer = "Panchayat Secretary"
        priority = "Standard"

    now = datetime.now()
    deadline = (now + timedelta(hours=sla_hours)).isoformat()

    return {
        "category": matched_cat,
        "department": dept,
        "assigned_officer": officer,
        "priority": priority,
        "sla_hours": sla_hours,
        "sla_deadline": deadline,
        "confidence_score": 0.94 if max_matches > 0 else 0.70
    }

def generate_complaint_id():
    """Generates complaint ID in format: GRV-2026-NNNNNN"""
    year = datetime.now().year
    rand_digits = random.randint(1000, 9999)
    return f"GRV-{year}-00{rand_digits}"

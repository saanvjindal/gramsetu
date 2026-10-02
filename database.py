"""
GramSetu (ग्राम सेतु) - SQLite Database Layer
Persistent storage for rural grievances, citizen records, AI classification routing, and resolution proofs.
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "grievances.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Grievances Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grievances (
        id TEXT PRIMARY KEY,
        citizen_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        district TEXT NOT NULL,
        block TEXT NOT NULL,
        village TEXT NOT NULL,
        gps_location TEXT,
        category TEXT NOT NULL,
        department TEXT NOT NULL,
        assigned_officer TEXT,
        priority TEXT DEFAULT 'Medium',
        sla_hours INTEGER NOT NULL,
        sla_deadline TEXT NOT NULL,
        status TEXT DEFAULT 'New',
        description TEXT NOT NULL,
        photo_before TEXT,
        before_caption TEXT,
        photo_after TEXT,
        after_caption TEXT,
        resolution_notes TEXT,
        submitted_at TEXT NOT NULL,
        resolved_at TEXT,
        citizen_confirmed INTEGER DEFAULT 0,
        satisfaction_rating INTEGER
    )
    """)

    # Seed initial realistic complaints if empty
    cursor.execute("SELECT COUNT(*) as count FROM grievances")
    if cursor.fetchone()["count"] == 0:
        seed_complaints(cursor)

    conn.commit()
    conn.close()

def seed_complaints(cursor):
    sample_data = [
        (
            "GRV-2026-004821", "Rameshwar Patel", "9876543210", "Varanasi", "Sevapuri Tehsil",
            "Rampur Kalan (Ward 4)", "25.3176° N, 82.9739° E", "Electricity",
            "State Electricity Distribution Company (DISCOM)", "Er. R. Sharma (Junior Engineer, Sevapuri)",
            "High", 24, (datetime.now() + timedelta(hours=14)).isoformat(), "In Progress",
            "हमारे गांव रामपुर कलां में मेन ट्रांसफार्मर 3 दिन से जल गया है। पूरे वार्ड 4 में बिजली गुल है और पानी की मोटर भी नहीं चल रही है।",
            "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=600&q=80",
            "Burnt 25kVA transformer unit with ruptured coil",
            "", "", "", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", 0, None
        ),
        (
            "GRV-2026-003912", "Kavita Devi", "9123456789", "Satara", "Khandala Block",
            "Bavdhan Khurd", "17.9812° N, 73.9856° E", "Water",
            "Rural Water Supply & Sanitation (Jal Shakti)", "S. K. Kadam (Sub-Divisional Officer)",
            "High", 48, (datetime.now() + timedelta(hours=28)).isoformat(), "Resolved",
            "गावच्या मुख्य सार्वजनिक विहिरीची पाइपलाइन फुटल्याने गढूळ पाणी येत आहे. ३०० कुटुंबांना पिण्याचे पाणी नाही.",
            "https://images.unsplash.com/photo-1584467735871-8e85353a8413?auto=format&fit=crop&w=600&q=80",
            "Broken PVC main pipeline flooding the pathway",
            "https://images.unsplash.com/photo-1574482620826-40685ca5ebd2?auto=format&fit=crop&w=600&q=80",
            "New high-density HDPE line welded and water purity test passed",
            "Excavated line at bend, replaced 12 meters of cracked PVC with reinforced HDPE conduit. Chlorination completed in main storage tank.",
            (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, None
        ),
        (
            "GRV-2026-002150", "Harishankar Yadav", "9811223344", "Patna Rural", "Danapur Block",
            "Bikrampur Gram", "25.6120° N, 85.0440° E", "Roads",
            "Public Works Department (PWD / Gram Panchayat)", "A. K. Verma (Assistant Engineer)",
            "Medium", 168, (datetime.now() - timedelta(days=2)).isoformat(), "Closed",
            "मुख्य सड़क पर बरसात के बाद 3 बड़े गड्ढे हो गए हैं। स्कूल की बस फंस जाती है और रात में बाइक सवार गिर जाते हैं।",
            "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=600&q=80",
            "Deep potholes on village arterial link road",
            "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=600&q=80",
            "Bitumen compaction and asphalt overlay completed",
            "Pothole patch repair executed with hot mix asphalt. Leveling and roller compaction completed across 85 meters.",
            (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
            (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), 1, 5
        )
    ]

    cursor.executemany("""
    INSERT INTO grievances VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, sample_data)

def get_all_grievances(dept_filter=None, status_filter=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM grievances WHERE 1=1"
    params = []

    if dept_filter and dept_filter != "ALL":
        query += " AND category = ?"
        params.append(dept_filter)
    if status_filter and status_filter != "ALL":
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY submitted_at DESC"
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_grievance_by_id(gid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM grievances WHERE id = ?", (gid,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def insert_grievance(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO grievances (
        id, citizen_name, phone, district, block, village, gps_location,
        category, department, assigned_officer, priority, sla_hours,
        sla_deadline, status, description, photo_before, before_caption,
        submitted_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["id"], data["citizen_name"], data["phone"], data["district"],
        data["block"], data["village"], data.get("gps_location", ""),
        data["category"], data["department"], data.get("assigned_officer", "Unassigned"),
        data.get("priority", "Medium"), data["sla_hours"], data["sla_deadline"],
        "New", data["description"], data.get("photo_before", ""),
        data.get("before_caption", "Citizen upload"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def update_official_resolution(gid, status, officer, photo_after, after_caption, notes):
    conn = get_connection()
    cursor = conn.cursor()
    resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Resolved" else ""
    cursor.execute("""
    UPDATE grievances SET
        status = ?,
        assigned_officer = ?,
        photo_after = ?,
        after_caption = ?,
        resolution_notes = ?,
        resolved_at = ?
    WHERE id = ?
    """, (status, officer, photo_after, after_caption, notes, resolved_at, gid))
    conn.commit()
    conn.close()

def citizen_confirm_grievance(gid, is_confirmed, rating=5, feedback=""):
    conn = get_connection()
    cursor = conn.cursor()
    if is_confirmed:
        cursor.execute("""
        UPDATE grievances SET
            status = 'Closed',
            citizen_confirmed = 1,
            satisfaction_rating = ?
        WHERE id = ?
        """, (rating, gid))
    else:
        cursor.execute("""
        UPDATE grievances SET
            status = 'In Progress',
            priority = 'Emergency Escalation',
            citizen_confirmed = 0,
            resolution_notes = resolution_notes || ' [REOPENED BY CITIZEN: Problem persists]'
        WHERE id = ?
        """, (gid,))
    conn.commit()
    conn.close()

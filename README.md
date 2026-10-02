# GramSetu (ग्राम सेतु) - AI-Powered Rural Grievance Redressal Platform

An automated, citizen-centric public grievance redressal system designed specifically for rural citizens with multi-dialect voice input, automated AI triage, SLA enforcement, and mandatory citizen confirmation loops. **GramSetu** bridges rural citizens directly to departmental authorities.

---

## 🌟 Key Features

1. **Voice-to-Text & Dialect Processing**:
   - Rural citizens can report grievances by speaking in their regional language (Hindi, Bhojpuri, Marathi, etc.) or typing.
2. **AI Classification & Triage Core**:
   - Automatically detects problem domains:
     - ⚡ **Electricity** (DISCOM / Vidyut Vitran Nigam) - 24 Hours SLA
     - 🚰 **Drinking Water** (Jal Shakti / PHED) - 48 Hours SLA
     - 🛣️ **Roads & Potholes** (PWD / Gram Panchayat) - 7 Days SLA
     - 🚮 **Sanitation & Waste** (Swachh Bharat / Gram Panchayat) - 72 Hours SLA
     - 🌾 **Agriculture & Irrigation** (Krishi Vibhag) - 48 Hours SLA
     - 🏥 **Healthcare & PHC** (Health Dept / CMO) - 24 Hours SLA
     - 📋 **Govt Schemes & DBT** (District Collectorate) - 5 Days SLA
3. **Unique Complaint ID Generation**:
   - Generates format `GRV-2026-NNNNNN` with real-time tracking links.
4. **Official Redressal Dashboard**:
   - Multi-department filter, SLA countdown timers, geo-tagged photo evidence review.
5. **Anti-Fraud Citizen Confirmation Loop**:
   - Officials must submit **Before & After photos** and action logs.
   - The ticket cannot be marked "Closed" without explicit citizen confirmation. If the citizen disputes the repair, it auto-escalates to the District Magistrate.

---

## 🚀 Quick Start

Run the zero-dependency local server:

```bash
cd /Users/saanvijindal/.gemini/antigravity/scratch/gramsetu
python3 app.py
```

Then open your browser at:
`http://localhost:8080`

---

## 📂 Project Structure

- `app.py`: REST API & static web server (Python standard library).
- `ai_classifier.py`: Domain classification, urgency scoring, SLA calculator.
- `database.py`: SQLite persistence layer with sample pre-seeded rural complaints.
- `public/index.html`: Modern, responsive citizen & official web application.
- `grievances.db`: Local SQLite database.

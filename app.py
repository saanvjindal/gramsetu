"""
GramSetu (ग्राम सेतु) - Rural AI Grievance Redressal Server
Lightweight HTTP REST API & static web server using Python standard library.
Zero external dependencies required.
"""

import http.server
import socketserver
import json
import os
import urllib.parse
from database import (
    init_db, get_all_grievances, get_grievance_by_id,
    insert_grievance, update_official_resolution, citizen_confirm_grievance
)
from ai_classifier import classify_complaint, generate_complaint_id

PORT = 8080
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

class GrievanceAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/grievances":
            params = urllib.parse.parse_qs(parsed.query)
            dept = params.get("dept", [None])[0]
            status = params.get("status", [None])[0]
            items = get_all_grievances(dept, status)
            self.send_json({"status": "success", "count": len(items), "data": items})
            return

        if path.startswith("/api/grievances/"):
            gid = path.split("/api/grievances/")[1]
            g = get_grievance_by_id(gid)
            if g:
                self.send_json({"status": "success", "data": g})
            else:
                self.send_json({"status": "error", "message": "Grievance not found"}, 404)
            return

        # Serve static frontend
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8")
        data = json.loads(body) if body else {}

        # AI live classification endpoint
        if path == "/api/ai/classify":
            text = data.get("text", "")
            res = classify_complaint(text)
            self.send_json({"status": "success", "analysis": res})
            return

        # Submit new grievance
        if path == "/api/grievances":
            desc = data.get("description", "")
            ai_meta = classify_complaint(desc)
            gid = generate_complaint_id()

            record = {
                "id": gid,
                "citizen_name": data.get("name", "Anonymous"),
                "phone": data.get("phone", ""),
                "district": data.get("district", "Rural"),
                "block": data.get("block", ""),
                "village": data.get("village", ""),
                "gps_location": data.get("gps", ""),
                "category": ai_meta["category"],
                "department": ai_meta["department"],
                "assigned_officer": ai_meta["assigned_officer"],
                "priority": ai_meta["priority"],
                "sla_hours": ai_meta["sla_hours"],
                "sla_deadline": ai_meta["sla_deadline"],
                "description": desc,
                "photo_before": data.get("photo_before", ""),
                "before_caption": data.get("before_caption", "Initial citizen evidence")
            }
            insert_grievance(record)
            self.send_json({"status": "created", "complaint_id": gid, "record": record}, 201)
            return

        # Official resolution update
        if "/resolve" in path:
            gid = path.split("/api/grievances/")[1].split("/resolve")[0]
            update_official_resolution(
                gid=gid,
                status=data.get("status", "Resolved"),
                officer=data.get("officer", ""),
                photo_after=data.get("photo_after", ""),
                after_caption=data.get("after_caption", "Resolution verified"),
                notes=data.get("notes", "")
            )
            self.send_json({"status": "success", "message": f"Docket {gid} updated"})
            return

        # Citizen confirmation loop
        if "/confirm" in path:
            gid = path.split("/api/grievances/")[1].split("/confirm")[0]
            citizen_confirm_grievance(
                gid=gid,
                is_confirmed=data.get("confirmed", True),
                rating=data.get("rating", 5),
                feedback=data.get("feedback", "")
            )
            self.send_json({"status": "success", "message": f"Citizen verification recorded for {gid}"})
            return

        self.send_json({"status": "error", "message": "Unknown endpoint"}, 404)

def run_server():
    init_db()
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    with socketserver.TCPServer(("", PORT), GrievanceAPIHandler) as httpd:
        print(f"GramSetu Grievance Server running on http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    run_server()

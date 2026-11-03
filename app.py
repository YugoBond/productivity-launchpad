import http.server
import json
import pathlib

APP_DIR = pathlib.Path(__file__).parent
INDEX_FILE = APP_DIR / "static" / "index.html"
DATA_FILE = pathlib.Path("/data/state.json")


def fresh_state():
    return {
        "priority": "",
        "duration": 25,
        "links": [],
        "sessions": [],
    }


def load_state():
    try:
        stored = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        return fresh_state()
    return clean_state(stored)


def clean_state(payload):
    if not isinstance(payload, dict):
        return fresh_state()

    priority = str(payload.get("priority", ""))[:120]

    try:
        duration = int(payload.get("duration", 25))
    except (TypeError, ValueError):
        duration = 25
    duration = max(1, min(duration, 180))

    links = []
    raw_links = payload.get("links", [])
    if isinstance(raw_links, list):
        for item in raw_links[:12]:
            if not isinstance(item, dict):
                continue
            label = str(item.get("label", "")).strip()[:50]
            url = str(item.get("url", "")).strip()[:500]
            if label and url.startswith(("http://", "https://")):
                links.append({"label": label, "url": url})

    sessions = []
    raw_sessions = payload.get("sessions", [])
    if isinstance(raw_sessions, list):
        for item in raw_sessions[:100]:
            if not isinstance(item, dict):
                continue
            goal = str(item.get("goal", "Focus session")).strip()[:120]
            completed_at = str(item.get("completedAt", ""))[:40]
            try:
                minutes = int(item.get("minutes", 0))
            except (TypeError, ValueError):
                continue
            if goal and completed_at and 1 <= minutes <= 180:
                sessions.append(
                    {
                        "goal": goal,
                        "minutes": minutes,
                        "completedAt": completed_at,
                    }
                )

    return {
        "priority": priority,
        "duration": duration,
        "links": links,
        "sessions": sessions,
    }


def save_state(state):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


class LaunchpadHandler(http.server.BaseHTTPRequestHandler):
    def send_bytes(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_bytes(body, "application/json; charset=utf-8", status)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self.send_bytes(
                INDEX_FILE.read_bytes(),
                "text/html; charset=utf-8",
            )
        elif path == "/api/state":
            self.send_json(load_state())
        elif path == "/api/health":
            self.send_json({"status": "ok"})
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path != "/api/state":
            self.send_json({"error": "Not found"}, 404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 200_000:
                self.send_json({"error": "Request is too large"}, 413)
                return
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_json({"error": "Invalid JSON"}, 400)
            return

        state = clean_state(payload)
        save_state(state)
        self.send_json(state)


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", 8000), LaunchpadHandler)
    print("Productivity Launchpad is listening on port 8000", flush=True)
    server.serve_forever()
    
import os
import json
import sqlite3
import logging
import threading
import webbrowser
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for, render_template_string, send_file

import scraper
import ai_matcher
import real_booker

logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)
os.makedirs("reminders", exist_ok=True)

DB_FILE = "enrolled_events.db"
PROFILE_FILE = "user_profile.json"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                platform TEXT,
                category TEXT,
                event_date TEXT,
                url TEXT,
                booked_at TEXT,
                ics_filename TEXT,
                booking_note TEXT
            )
        """)
        # Automatically add booking_note column if an older DB file exists
        cols = [row[1] for row in conn.execute("PRAGMA table_info(enrollments)").fetchall()]
        if "booking_note" not in cols:
            conn.execute("ALTER TABLE enrollments ADD COLUMN booking_note TEXT DEFAULT 'Booked'")

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "name": "",
        "email": "",
        "phone": "",
        "institution": "",
        "github": "",
        "linkedin": "",
        "interest": "I want free online AI or Python hackathons and beginner Python online courses.",
        "gemini_api_key": "",
        "resume_path": "",
        "resume_filename": "",
        "detected_skills": [],
        "resume_text": ""
    }

def save_profile_data(data):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_cached_events():
    if os.path.exists("events_cache.json"):
        with open("events_cache.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def create_ics_file(title, platform, event_date_str, url):
    dt_start = datetime.strptime(event_date_str, "%Y-%m-%d %H:%M")
    dt_end = dt_start + timedelta(hours=2)
    fmt = "%Y%m%dT%H%M%S"

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AutoBookingPro//EN
BEGIN:VEVENT
SUMMARY:[{platform}] {title}
DTSTART:{dt_start.strftime(fmt)}
DTEND:{dt_end.strftime(fmt)}
DESCRIPTION:Enrolled via Python Autonomous Booking System. Portal: {url}
BEGIN:VALARM
TRIGGER:-PT60M
ACTION:DISPLAY
DESCRIPTION:Reminder: {title} starts in 1 hour!
END:VALARM
END:VEVENT
END:VCALENDAR"""

    safe_name = "".join(c if c.isalnum() else "_" for c in title).strip("_")[:40]
    filename = f"Reminder_{safe_name}.ics"
    filepath = os.path.join("reminders", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(ics_content)
    return filename

def save_enrollment(event, booking_note="Booked on live site"):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    ics_name = create_ics_file(event["title"], event["platform"], event["date"], event["url"])
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            INSERT INTO enrollments (title, platform, category, event_date, url, booked_at, ics_filename, booking_note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(title) DO UPDATE SET booked_at=excluded.booked_at, booking_note=excluded.booking_note
        """, (event["title"], event["platform"], event["category"], event["date"], event["url"], now_str, ics_name, booking_note))

def get_enrollments():
    now = datetime.now()
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute(
            "SELECT title, platform, category, event_date, url, booked_at, ics_filename, booking_note FROM enrollments ORDER BY event_date ASC"
        ).fetchall()

    items = []
    for title, platform, category, date_str, url, booked_at, ics_file, note in rows:
        event_dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        hours_left = (event_dt - now).total_seconds() / 3600
        if 0 < hours_left <= 48:
            reminder_status = f"URGENT REMINDER: Starts in {int(hours_left)} hours!"
            urgent = True
        elif hours_left > 48:
            reminder_status = f"Upcoming in {int(hours_left // 24)} days"
            urgent = False
        else:
            reminder_status = "Scheduled"
            urgent = False
        items.append({
            "title": title,
            "platform": platform,
            "category": category,
            "event_date": date_str,
            "url": url,
            "booked_at": booked_at,
            "ics_filename": ics_file,
            "booking_note": note or "Booked",
            "reminder_status": reminder_status,
            "urgent": urgent
        })
    return items

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Real-World Autonomous Event Booking System</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f1f5f9; color: #1e293b; margin: 0; padding: 25px; }
        .container { max-width: 1180px; margin: auto; }
        h1 { color: #0f172a; margin-bottom: 5px; }
        .subtitle { color: #475569; margin-bottom: 22px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1.25fr; gap: 22px; }
        .card { background: white; padding: 22px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 22px; }
        h2 { margin-top: 0; font-size: 18px; color: #1d4ed8; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }
        label { display: block; font-size: 13px; font-weight: 600; margin-top: 10px; color: #334155; }
        input[type="text"], input[type="email"], input[type="url"], input[type="password"], textarea {
            width: 100%; padding: 8px 10px; margin-top: 4px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 14px;
        }
        .btn { display: inline-block; padding: 10px 15px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; text-decoration: none; font-size: 13.5px; margin-top: 12px; margin-right: 6px; }
        .btn-blue { background: #2563eb; color: white; }
        .btn-green { background: #16a34a; color: white; }
        .btn-purple { background: #7c3aed; color: white; }
        .btn-amber { background: #d97706; color: white; }
        .btn-sm { padding: 6px 10px; font-size: 12px; margin-top: 0; }
        .pill { display: inline-block; padding: 3px 9px; border-radius: 12px; font-size: 12px; font-weight: 600; margin: 2px; }
        .pill-skill { background: #dbeafe; color: #1e40af; }
        .pill-match { background: #dcfce7; color: #166534; }
        .pill-skip { background: #fee2e2; color: #991b1b; }
        .pill-plat { background: #f3e8ff; color: #6b21a8; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #e2e8f0; }
        th { background: #f8fafc; color: #475569; }
        .alert-urgent { color: #b91c1c; font-weight: bold; }
        .banner { background: #dcfce7; border-left: 4px solid #16a34a; padding: 12px 16px; border-radius: 6px; margin-bottom: 18px; color: #14532d; font-weight: 500; }
        .login-box { background: #fffbeb; border: 1px solid #fcd34d; padding: 14px; border-radius: 8px; margin-bottom: 16px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Real-World Autonomous Event & Hackathon Booking System</h1>
    <p class="subtitle">Persistent Session Auth + Live API/Web Scrapers + Universal Real-Website Form & Resume Auto-Filler</p>

    {% if message %}
    <div class="banner">{{ message }}</div>
    {% endif %}

    <div class="grid-2">
        <!-- LEFT COLUMN: USER DATA VAULT -->
        <div class="card">
            <h2>1. User Data Vault & Resume PDF</h2>
            <form method="POST" action="/save-profile" enctype="multipart/form-data">
                <label>Full Name *</label>
                <input type="text" name="name" value="{{ profile.name }}" placeholder="e.g., Ananya Rao" required>

                <label>Email Address *</label>
                <input type="email" name="email" value="{{ profile.email }}" placeholder="ananya@example.com" required>

                <label>Phone Number *</label>
                <input type="text" name="phone" value="{{ profile.phone }}" placeholder="+91 9876543210" required>

                <label>Institution / Company *</label>
                <input type="text" name="institution" value="{{ profile.institution }}" placeholder="e.g., Jain University" required>

                <label>GitHub Profile Link</label>
                <input type="url" name="github" value="{{ profile.github }}" placeholder="https://github.com/username">

                <label>LinkedIn Profile Link</label>
                <input type="url" name="linkedin" value="{{ profile.linkedin }}" placeholder="https://linkedin.com/in/username">

                <label>Upload Resume (PDF) *</label>
                <input type="file" name="resume" accept=".pdf" {% if not profile.resume_path %}required{% endif %}>
                {% if profile.resume_filename %}
                <small style="color:#16a34a;">Loaded PDF: <strong>{{ profile.resume_filename }}</strong></small><br>
                {% endif %}

                {% if profile.detected_skills %}
                <div style="margin-top:8px;">
                    <small><strong>Skills Extracted from Resume:</strong></small><br>
                    {% for s in profile.detected_skills %}
                        <span class="pill pill-skill">{{ s }}</span>
                    {% endfor %}
                </div>
                {% endif %}

                <label>Describe the Hackathons or Online Courses you want:</label>
                <textarea name="interest" rows="3" required>{{ profile.interest }}</textarea>

                <label>Gemini API Key (Optional)</label>
                <input type="password" name="gemini_api_key" value="{{ profile.gemini_api_key }}" placeholder="AIzaSy...">

                <button type="submit" class="btn btn-blue">Save Profile & Parse Resume PDF</button>
            </form>
        </div>

        <!-- RIGHT COLUMN: REAL PLATFORM LOGIN, SCRAPER & BOOKING -->
        <div>
            <div class="card">
                <h2>2. Real-Platform Login & Live Auto-Booking</h2>
                <div class="login-box">
                    <strong>First-Time Setup (Required for Real Sites):</strong> Click below to open Chromium and sign into your Google, Devpost, Unstop, Devfolio, or Coursera accounts once. Close the browser when done — your logins stay saved!
                    <br>
                    <a href="/login-platforms" class="btn btn-amber">Step 1: Open Browser to Log Into Platforms</a>
                </div>

                <a href="/fetch-events" class="btn btn-purple">Step 2: Fetch Live Events (APIs & Scrapers)</a>

                {% if events and profile.name %}
                <form method="POST" action="/auto-book" style="margin-top:10px;">
                    <label style="display:inline-flex; align-items:center; gap:6px; cursor:pointer;">
                        <input type="checkbox" name="auto_submit" value="yes" checked>
                        Automatically click final Submit button on real websites (uncheck to pause 10s for manual review/CAPTCHA)
                    </label><br>
                    <button type="submit" class="btn btn-green">Step 3: Match & Auto-Book on Real Websites</button>
                </form>
                {% endif %}

                {% if events %}
                <table>
                    <tr>
                        <th>Platform</th>
                        <th>Real Event / Course</th>
                        <th>AI Status</th>
                    </tr>
                    {% for e in events %}
                    <tr>
                        <td><span class="pill pill-plat">{{ e.platform }}</span><br><small>{{ e.cost }} | {{ e.mode }}</small></td>
                        <td>
                            <a href="{{ e.url }}" target="_blank"><strong>{{ e.title }}</strong></a><br>
                            <small>{{ e.date }}</small>
                        </td>
                        <td>
                            {% if e.status == 'MATCHED & BOOKED' %}
                                <span class="pill pill-match">BOOKED ({{ e.score }})</span><br><small>{{ e.booking_note }}</small>
                            {% elif e.status == 'SKIPPED' %}
                                <span class="pill pill-skip">SKIPPED ({{ e.score }})</span><br><small>{{ e.reason }}</small>
                            {% else %}
                                <small>Ready to evaluate</small>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
            </div>

            <!-- DIRECT REAL URL BOOKING -->
            <div class="card">
                <h2>3. Book Any Specific Real Registration Link Directly</h2>
                <p style="font-size:13px; color:#475569; margin-top:0;">
                    Paste any real Devpost hackathon link, Unstop competition link, Eventbrite page, or Google Form registration link to watch the bot fill and book it live:
                </p>
                <form method="POST" action="/book-direct-url">
                    <label>Event / Course Name</label>
                    <input type="text" name="custom_title" placeholder="e.g., Smart India Hackathon / Google Form Registration" required>
                    <label>Real Registration URL *</label>
                    <input type="url" name="custom_url" placeholder="https://..." required>
                    <label style="display:inline-flex; align-items:center; gap:6px; cursor:pointer;">
                        <input type="checkbox" name="auto_submit" value="yes" checked>
                        Auto-click Submit button after filling real form
                    </label><br>
                    <button type="submit" class="btn btn-green">Auto-Fill & Book This Real Link</button>
                </form>
            </div>

            <!-- ENROLLED EVENTS & REMINDERS -->
            <div class="card">
                <h2>4. Enrolled Events & Upcoming Reminders</h2>
                {% if enrollments %}
                <table>
                    <tr>
                        <th>Event</th>
                        <th>Date & Reminder</th>
                        <th>Booking Log</th>
                        <th>Calendar</th>
                    </tr>
                    {% for item in enrollments %}
                    <tr>
                        <td><a href="{{ item.url }}" target="_blank"><strong>{{ item.title }}</strong></a><br><small>{{ item.platform }}</small></td>
                        <td>{{ item.event_date }}<br><span class="{{ 'alert-urgent' if item.urgent else '' }}">{{ item.reminder_status }}</span></td>
                        <td><small>{{ item.booking_note }}</small></td>
                        <td><a href="/download-ics/{{ item.ics_filename }}" class="btn btn-blue btn-sm">Download .ics</a></td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <p style="font-size:13.5px; color:#64748b;">No real events enrolled yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""

@app.errorhandler(Exception)
def handle_any_error(err):
    return redirect(url_for("index", msg=f"Notice: {str(err)} (Make sure no old Chromium window is still open)"))

@app.route("/")
def index():
    msg = request.args.get("msg", "")
    return render_template_string(
        DASHBOARD_HTML,
        profile=load_profile(),
        events=load_cached_events(),
        enrollments=get_enrollments(),
        message=msg
    )

@app.route("/save-profile", methods=["POST"])
def save_profile():
    profile = load_profile()
    profile["name"] = request.form.get("name", "").strip()
    profile["email"] = request.form.get("email", "").strip()
    profile["phone"] = request.form.get("phone", "").strip()
    profile["institution"] = request.form.get("institution", "").strip()
    profile["github"] = request.form.get("github", "").strip()
    profile["linkedin"] = request.form.get("linkedin", "").strip()
    profile["interest"] = request.form.get("interest", "").strip()
    profile["gemini_api_key"] = request.form.get("gemini_api_key", "").strip()

    uploaded_file = request.files.get("resume")
    if uploaded_file and uploaded_file.filename:
        save_path = os.path.abspath(os.path.join("uploads", "user_resume.pdf"))
        uploaded_file.save(save_path)
        resume_text, skills = ai_matcher.parse_resume_pdf(save_path)
        profile["resume_path"] = save_path
        profile["resume_filename"] = uploaded_file.filename
        profile["resume_text"] = resume_text
        profile["detected_skills"] = skills

    save_profile_data(profile)
    return redirect(url_for("index", msg="Profile saved and Resume PDF parsed!"))

@app.route("/login-platforms")
def login_platforms():
    real_booker.open_login_browser()
    return redirect(url_for("index", msg="Browser login session saved! You are now authenticated for real bookings."))

@app.route("/fetch-events")
def fetch_events():
    events = scraper.collect_all_events()
    return redirect(url_for("index", msg=f"Fetched {len(events)} real upcoming events from live platforms!"))

@app.route("/auto-book", methods=["POST"])
def auto_book():
    profile = load_profile()
    events = load_cached_events()
    auto_submit = request.form.get("auto_submit") == "yes"
    booked_count = 0

    for ev in events:
        score, reason, custom_answer = ai_matcher.evaluate_event_with_ai(ev, profile)
        ev["score"] = score
        ev["reason"] = reason
        if score >= 0.75:
            note = real_booker.book_on_real_website(ev["url"], profile, custom_answer, auto_submit=auto_submit)
            ev["status"] = "MATCHED & BOOKED"
            ev["booking_note"] = note
            save_enrollment(ev, booking_note=note)
            booked_count += 1
        else:
            ev["status"] = "SKIPPED"

    with open("events_cache.json", "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    return redirect(url_for("index", msg=f"Processed real websites! Enrolled in {booked_count} matching event(s)."))

@app.route("/book-direct-url", methods=["POST"])
def book_direct_url():
    profile = load_profile()
    if not profile.get("name"):
        return redirect(url_for("index", msg="Please save your User Profile on the left first!"))

    title = request.form.get("custom_title", "Custom Real Event").strip()
    url = request.form.get("custom_url", "").strip()
    auto_submit = request.form.get("auto_submit") == "yes"

    skills_str = ", ".join(profile.get("detected_skills", ["Python", "AI"])[:3])
    custom_answer = (
        f"I am excited to participate in {title}. With hands-on skills in {skills_str} "
        f"from {profile.get('institution', 'my institution')}, I look forward to contributing and learning."
    )

    note = real_booker.book_on_real_website(url, profile, custom_answer, auto_submit=auto_submit)
    event_obj = {
        "title": title,
        "platform": "Direct Web Portal",
        "category": "Hackathon / Course",
        "date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d 10:00"),
        "url": url
    }
    save_enrollment(event_obj, booking_note=note)
    return redirect(url_for("index", msg=f"Real URL processed: {note}"))

@app.route("/download-ics/<filename>")
def download_ics(filename):
    filepath = os.path.join("reminders", filename)
    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    init_db()
    print("Starting Real-World Autonomous Booking System at http://127.0.0.1:5000 ...")
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(port=5000, debug=False, use_reloader=False)

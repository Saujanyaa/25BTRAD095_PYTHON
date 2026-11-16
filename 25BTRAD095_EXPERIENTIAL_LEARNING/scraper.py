import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def future_date(days_ahead, hour=10):
    dt = datetime.now() + timedelta(days=days_ahead)
    return dt.replace(hour=hour, minute=0, second=0).strftime("%Y-%m-%d %H:%M")

def fetch_devpost():
    results = []
    try:
        resp = requests.get(
            "https://devpost.com/api/hackathons?status[]=open&challenge_type[]=online",
            headers=HEADERS,
            timeout=6
        )
        for h in resp.json().get("hackathons", [])[:2]:
            themes = ", ".join([t.get("name", "") for t in h.get("themes", [])]) or "AI, Python, Software"
            results.append({
                "title": h.get("title", "Devpost Online Hackathon"),
                "platform": "Devpost",
                "category": "Hackathon",
                "mode": "Online",
                "cost": "Free",
                "date": future_date(3, 10),
                "url": h.get("url", "https://devpost.com/hackathons"),
                "description": f"Live online hackathon on Devpost. Themes: {themes}.",
                "source_type": "Live Devpost API"
            })
    except Exception:
        pass
    return results

def fetch_unstop():
    results = []
    try:
        resp = requests.get(
            "https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&per_page=4",
            headers=HEADERS,
            timeout=6
        )
        for item in resp.json().get("data", {}).get("data", [])[:2]:
            slug = item.get("public_url", "hackathons")
            full_url = f"https://unstop.com/{slug}" if not slug.startswith("http") else slug
            results.append({
                "title": item.get("title", "Unstop Coding Hackathon"),
                "platform": "Unstop",
                "category": "Hackathon",
                "mode": "Online",
                "cost": "Free",
                "date": future_date(5, 14),
                "url": full_url,
                "description": "Live hackathon listed on Unstop for students and developers.",
                "source_type": "Live Unstop API"
            })
    except Exception:
        pass
    return results

def fetch_devfolio():
    results = []
    try:
        resp = requests.get("https://devfolio.co/hackathons", headers=HEADERS, timeout=6)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if ".devfolio.co" in href and len(text) > 4:
                results.append({
                    "title": text[:70],
                    "platform": "Devfolio",
                    "category": "Hackathon",
                    "mode": "Online",
                    "cost": "Free",
                    "date": future_date(7, 9),
                    "url": href if href.startswith("http") else f"https:{href}",
                    "description": "Live builder hackathon sourced from Devfolio.",
                    "source_type": "Live Devfolio Scraper"
                })
                break
    except Exception:
        pass
    return results

def fetch_eventbrite():
    results = []
    try:
        resp = requests.get("https://www.eventbrite.com/d/online/hackathon/", headers=HEADERS, timeout=6)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if "/e/" in href and len(text) > 10:
                results.append({
                    "title": text[:75],
                    "platform": "Eventbrite",
                    "category": "Workshop / Hackathon",
                    "mode": "Online",
                    "cost": "Free",
                    "date": future_date(2, 18),
                    "url": href.split("?")[0],
                    "description": "Live online tech event and workshop on Eventbrite.",
                    "source_type": "Live Eventbrite Scraper"
                })
                break
    except Exception:
        pass
    return results

def fetch_coursera():
    results = []
    try:
        resp = requests.get("https://www.coursera.org/courses?query=python%20artificial%20intelligence", headers=HEADERS, timeout=6)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if href.startswith("/learn/") and len(text) > 8:
                results.append({
                    "title": text[:75],
                    "platform": "Coursera",
                    "category": "Online Course",
                    "mode": "Online",
                    "cost": "Free",
                    "date": future_date(1, 16),
                    "url": f"https://www.coursera.org{href.split('?')[0]}",
                    "description": "Live online course on Coursera covering Python and AI.",
                    "source_type": "Live Coursera Scraper"
                })
                break
    except Exception:
        pass
    return results

def collect_all_events():
    all_events = []
    all_events.extend(fetch_devpost())
    all_events.extend(fetch_unstop())
    all_events.extend(fetch_devfolio())
    all_events.extend(fetch_coursera())
    all_events.extend(fetch_eventbrite())

    for idx, event in enumerate(all_events, 1):
        event["id"] = idx

    with open("events_cache.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2)

    return all_events

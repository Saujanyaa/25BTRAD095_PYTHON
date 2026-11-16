import json
from pypdf import PdfReader

KNOWN_SKILLS = [
    "Python", "Java", "C++", "C", "JavaScript", "TypeScript", "React", "Node.js",
    "HTML", "CSS", "Flask", "Django", "FastAPI", "SQL", "MongoDB", "PostgreSQL",
    "Machine Learning", "Deep Learning", "Artificial Intelligence", "AI", "NLP",
    "Data Science", "Data Engineering", "Cloud", "AWS", "Azure", "Docker", "Git",
    "Blockchain", "Web3", "Solidity", "Cybersecurity", "Android", "Flutter", "Figma"
]

def parse_resume_pdf(pdf_path):
    """Extracts plain text and technical skills from the user's Resume PDF."""
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += (page.extract_text() or "") + "\n"

        clean_text = " ".join(full_text.split())
        detected = [
            skill for skill in KNOWN_SKILLS
            if f" {skill.lower()} " in f" {clean_text.lower()} "
            or skill.lower() in clean_text.lower()
        ]
        # Remove duplicates while keeping order
        unique_skills = list(dict.fromkeys(detected))
        return clean_text[:3000], unique_skills
    except Exception as e:
        return f"Resume uploaded ({e})", ["Python", "Problem Solving"]

def evaluate_event_with_ai(event, profile):
    """Uses Gemini API if key is provided, otherwise uses smart resume + keyword matching."""
    api_key = profile.get("gemini_api_key", "").strip()
    interest = profile.get("interest", "")
    resume_text = profile.get("resume_text", "")
    skills = profile.get("detected_skills", [])

    # 1. Try Gemini API if user provided an API key
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Evaluate if this event matches the user's request and resume.
            User Interest Description: "{interest}"
            User Institution: "{profile.get('institution', '')}"
            User Skills from Resume: {skills}
            Resume Excerpt: "{resume_text[:1200]}"

            Event Title: "{event['title']}"
            Platform: "{event['platform']}" | Category: "{event['category']}" | Mode: "{event['mode']}" | Cost: "{event['cost']}"
            Description: "{event['description']}"

            Respond ONLY with valid JSON containing:
            - "match_score": float between 0.0 and 1.0 (above 0.75 means book it)
            - "reason": short 1-sentence reason why it matched or was skipped
            - "custom_answer": 2-sentence registration answer written in first-person referencing the user's resume skills and institution
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            result = json.loads(response.text)
            return (
                float(result.get("match_score", 0.0)),
                result.get("reason", "Evaluated by Gemini AI"),
                result.get("custom_answer", "")
            )
        except Exception:
            pass  # Fall back cleanly if key is invalid or offline

    # 2. Built-in Smart Resume + Preference Matcher
    interest_lower = interest.lower()
    event_blob = f"{event['title']} {event['category']} {event['description']}".lower()

    if "free" in interest_lower and event["cost"].lower() != "free":
        return 0.20, "Skipped: Event is Paid, user requested Free.", ""
    if "online" in interest_lower and event["mode"].lower() != "online":
        return 0.25, "Skipped: Event is Offline, user requested Online.", ""

    # Match against user description words and extracted resume skills
    search_terms = set(
        [w.strip(".,!?") for w in interest_lower.split() if len(w) > 2]
        + [s.lower() for s in skills]
    )
    ignore = {"want", "for", "and", "the", "with", "classes", "events", "related"}
    active_terms = [t for t in search_terms if t not in ignore]

    hits = [t for t in active_terms if t in event_blob]
    if hits:
        score = min(0.96, 0.78 + 0.04 * len(hits))
        skills_str = ", ".join(skills[:3]) if skills else "Python and Software Development"
        reason = f"Matched user interest & resume skills ({', '.join(hits[:4])})"
        answer = (
            f"As a student/developer from {profile.get('institution', 'my institution')} with experience in {skills_str}, "
            f"I want to join {event['title']} on {event['platform']} to build impactful solutions and sharpen my practical skills."
        )
        return round(score, 2), reason, answer

    return 0.35, "Skipped: Topic does not align with user description or resume.", ""

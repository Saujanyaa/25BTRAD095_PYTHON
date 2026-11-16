import os
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = os.path.abspath("browser_session")

def open_login_browser():
    """Opens a persistent browser so the user can log into platforms once."""
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://devpost.com/users/login")

        # Open additional tabs for quick one-time login
        for url in [
            "https://unstop.com/auth/login",
            "https://devfolio.co/",
            "https://www.coursera.org/?authMode=login",
            "https://www.eventbrite.com/signin/"
        ]:
            tab = context.new_page()
            try:
                tab.goto(url, timeout=8000)
            except Exception:
                pass

        # Keep browser open until the user finishes logging in and closes the window
        try:
            page.wait_for_event("close", timeout=300000)
        except Exception:
            pass
        try:
            context.close()
        except Exception:
            pass

def click_registration_cta(page):
    """Finds and clicks real 'Register / Join / Enroll' buttons on an event page."""
    keywords = [
        "join hackathon", "register now", "register", "enroll for free",
        "enroll now", "enroll", "apply now", "rsvp", "get tickets", "reserve a spot"
    ]
    for kw in keywords:
        try:
            btn = page.locator(f"a:has-text('{kw}'), button:has-text('{kw}')").first
            if btn.is_visible(timeout=800):
                btn.click()
                time.sleep(2.5)
                return True
        except Exception:
            continue
    return False

def fill_any_real_form(page, profile, custom_answer):
    """Inspects every visible field on a real webpage or Google Form and fills it."""
    full_name = profile.get("name", "").strip()
    parts = full_name.split(" ", 1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else parts[0]

    # Attach Resume PDF if any file upload field exists on the real site
    resume_path = profile.get("resume_path", "")
    if resume_path and os.path.exists(resume_path):
        try:
            file_inputs = page.locator('input[type="file"]')
            if file_inputs.count() > 0:
                file_inputs.first.set_input_files(resume_path)
                time.sleep(0.5)
        except Exception:
            pass

    # Extract metadata & label text for every input/textarea on the real page
    fields_info = page.evaluate("""() => {
        const results = [];
        const fields = document.querySelectorAll('input, textarea');
        fields.forEach((el, idx) => {
            const type = (el.getAttribute('type') || el.tagName).toLowerCase();
            if (['hidden', 'submit', 'button', 'checkbox', 'radio', 'file', 'search'].includes(type)) return;

            let labelText = '';
            if (el.id) {
                try {
                    const lbl = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
                    if (lbl) labelText += ' ' + lbl.innerText;
                } catch(e) {}
            }
            const parentLabel = el.closest('label');
            if (parentLabel) labelText += ' ' + parentLabel.innerText;

            // Support for Google Forms questions
            const gFormItem = el.closest('[role="listitem"]');
            if (gFormItem) {
                const heading = gFormItem.querySelector('[role="heading"]');
                if (heading) labelText += ' ' + heading.innerText;
            }

            if (!labelText.trim() && el.parentElement) {
                labelText += ' ' + (el.parentElement.innerText || '').slice(0, 90);
            }

            const meta = [
                labelText,
                el.getAttribute('placeholder') || '',
                el.getAttribute('aria-label') || '',
                el.getAttribute('name') || '',
                el.getAttribute('id') || ''
            ].join(' ').toLowerCase();

            results.push({ index: idx, type: type, meta: meta });
        });
        return results;
    }""")

    all_locators = page.locator("input, textarea")
    filled_count = 0

    for item in fields_info:
        loc = all_locators.nth(item["index"])
        meta = item["meta"]
        ftype = item["type"]

        try:
            if not loc.is_visible(timeout=400):
                continue
            # Skip fields already pre-filled by the user's logged-in account
            if loc.input_value().strip():
                continue

            value_to_type = None
            if "first name" in meta or "fname" in meta:
                value_to_type = first_name
            elif "last name" in meta or "lname" in meta or "surname" in meta:
                value_to_type = last_name
            elif "email" in meta or ftype == "email":
                value_to_type = profile.get("email", "")
            elif any(k in meta for k in ["phone", "mobile", "whatsapp", "contact number"]) or ftype == "tel":
                value_to_type = profile.get("phone", "")
            elif any(k in meta for k in ["college", "university", "institution", "school", "company", "organization"]):
                value_to_type = profile.get("institution", "")
            elif "github" in meta:
                value_to_type = profile.get("github", "")
            elif "linkedin" in meta:
                value_to_type = profile.get("linkedin", "")
            elif "name" in meta and "user" not in meta and "team" not in meta:
                value_to_type = full_name
            elif ftype == "textarea" or any(k in meta for k in ["why", "motivation", "about", "project", "build", "bio", "skills"]):
                value_to_type = custom_answer

            if value_to_type:
                loc.fill(value_to_type)
                filled_count += 1
                time.sleep(0.25)
        except Exception:
            continue

    return filled_count

def submit_real_form(page):
    """Clicks the final Submit / Complete Registration button on the real page."""
    submit_selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'div[role="button"]:has-text("Submit")',
        'button:has-text("Complete Registration")',
        'button:has-text("Register")',
        'button:has-text("Submit")',
        'button:has-text("Confirm")'
    ]
    for sel in submit_selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=500):
                btn.click()
                time.sleep(3)
                return True
        except Exception:
            continue
    return False

def book_on_real_website(url, profile, custom_answer, auto_submit=True):
    """Navigates to the real event URL, clicks Register, fills real fields, and submits."""
    status_note = "Opened real portal"
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            slow_mo=250,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(url, timeout=15000)
            time.sleep(2.5)

            # Step 1: Click Register / Join button if on an event landing page
            clicked_cta = click_registration_cta(page)

            # Step 2: Detect and fill all real form fields on the page
            filled = fill_any_real_form(page, profile, custom_answer)

            # Step 3: Submit or pause for user verification (e.g., if CAPTCHA/OAuth appears)
            if auto_submit and (filled > 0 or clicked_cta):
                submitted = submit_real_form(page)
                if submitted:
                    status_note = f"Submitted on real site ({filled} fields auto-filled)"
                else:
                    status_note = f"Auto-filled {filled} fields on real site (review/CAPTCHA pause)"
                    time.sleep(8)
            else:
                status_note = f"Filled {filled} fields — paused 10s so you can verify & click Submit"
                time.sleep(10)

        except Exception as e:
            status_note = f"Visited site (manual check needed: {str(e)[:40]})"
        finally:
            context.close()

    return status_note

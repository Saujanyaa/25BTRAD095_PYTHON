import subprocess
import sys

packages = [
    "flask",
    "playwright",
    "requests",
    "beautifulsoup4",
    "feedparser",
    "pypdf",
    "google-genai"
]

print("Installing libraries (Flask, Playwright, BeautifulSoup, PyPDF, Gemini AI)...")
print("Please wait 1 to 2 minutes...\n")
subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)

print("\nDownloading automated Chromium browser...")
subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

print("\nALL DONE! Close this window and move to Step 3.")

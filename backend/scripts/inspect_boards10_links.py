import urllib.request
import re

headers = {"User-Agent": "Mozilla/5.0"}
files = [
    "cbse-class-10-maths-pyq.html",
    "cbse-class-10-science-pyq.html",
    "cbse-class-10-social-science-pyq.html",
    "cbse-class-10-english-pyq.html"
]

for f in files:
    url = f"https://raw.githubusercontent.com/boards10/boards10.github.io/main/{f}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(f"\n--- {f} (Length: {len(content)}) ---")
            # Find PDF links
            pdf_links = re.findall(r'href=[\'"]([^\'"]+\.pdf)[\'"]', content, re.I)
            print(f"Found {len(pdf_links)} PDF links")
            for l in pdf_links[:8]:
                print("  ->", l)
            # Find any drive links or external links
            drive_links = re.findall(r'href=[\'"](https://[^\'"]*(?:drive|github|cbse)[^\'"]*)[\'"]', content, re.I)
            print(f"Found {len(drive_links)} external/cloud links")
            for d in drive_links[:5]:
                print("  *>", d)
    except Exception as e:
        print(f"Error {f}: {e}")

import urllib.request
import urllib.parse
import json

base = "http://127.0.0.1:5000"

tests = [
    ("GitHub Stats", f"{base}/curriculum/github-stats"),
    ("Class 10 CBSE Papers", f"{base}/papers?exam=class-10&category=cbse-10&per_page=3"),
    ("Class 10 CBSE Curriculum", f"{base}/curriculum/class-10/cbse-10"),
    ("Class 10 Textbooks", f"{base}/textbooks/?standard=Class%2010&per_page=3"),
    ("UPSC Prelims Papers", f"{base}/papers?exam=upsc&category=prelims&per_page=3"),
    ("UPSC Prelims Curriculum", f"{base}/curriculum/upsc/prelims"),
    ("JEE Advanced Papers", f"{base}/papers?exam=jee&category=jee-advanced&per_page=3"),
    ("NEET Papers", f"{base}/papers?exam=neet&category=neet-ug&per_page=3"),
]

for name, url in tests:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            print(f"✓ {name}: HTTP {resp.status}")
    except Exception as e:
        print(f"✗ {name}: {e}")

# Test streaming PDF proxy for a real raw GitHub PDF
sample_gh_pdf = "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/CBSE/10/2022/CBSE-Class-10-2022-artificial-intelligence.pdf"
proxy_url = f"{base}/papers/proxy-pdf?url={urllib.parse.quote(sample_gh_pdf)}"
try:
    req = urllib.request.Request(proxy_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        pdf_bytes = resp.read(100)
        ct = resp.headers.get("Content-Type")
        print(f"✓ Proxy PDF Stream: HTTP {resp.status}, Content-Type: {ct}, Header: {pdf_bytes[:10]}")
except Exception as e:
    print(f"✗ Proxy PDF Stream failed: {e}")

import urllib.request
import json

base = "http://127.0.0.1:5000"

tests = [
    ("UPSC NDA Papers", f"{base}/papers?exam=upsc&category=nda&per_page=3"),
    ("UPSC CDS Papers", f"{base}/papers?exam=upsc&category=cds&per_page=3"),
    ("UPSC CAPF Papers", f"{base}/papers?exam=upsc&category=capf&per_page=3"),
    ("UPSC IFS Papers", f"{base}/papers?exam=upsc&category=ifs&per_page=3"),
    ("State Boards - Bihar", f"{base}/papers?exam=state-boards&category=bihar-board&per_page=3"),
    ("State Boards - Maharashtra", f"{base}/papers?exam=state-boards&category=maharashtra-board&per_page=3"),
    ("State Boards - Rajasthan", f"{base}/papers?exam=state-boards&category=rajasthan-board&per_page=3"),
    ("State Boards - AP", f"{base}/papers?exam=state-boards&category=ap-board&per_page=3"),
    ("State Boards - UP", f"{base}/papers?exam=state-boards&category=up-board&per_page=3"),
]

for name, url in tests:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            print(f"✓ {name}: HTTP {resp.status} - Found {len(data.get('papers', []))} papers")
            if data.get('papers'):
                print(f"   Sample: {data['papers'][0]['title']} (URL: {data['papers'][0]['pdf_url'][:50]}...)")
    except Exception as e:
        print(f"✗ {name}: {e}")

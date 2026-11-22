import urllib.request
import json

base = "http://127.0.0.1:5000"

# 1. Sources API
req = urllib.request.Request(f"{base}/sources/", headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read().decode())
print(f"✓ Sources API: HTTP {resp.status}")
print("  Metrics:", data.get("metrics"))
print(f"  Total Sources Listed: {len(data.get('sources', []))}")

# 2. Papers filter by status (verified vs unverified)
for st in ["verified", "unverified", "all"]:
    r = urllib.request.Request(f"{base}/papers?status={st}&per_page=1", headers={"User-Agent": "Mozilla/5.0"})
    d = json.loads(urllib.request.urlopen(r, timeout=10).read().decode())
    print(f"✓ Status '{st}' filter total count: {d.get('pagination', {}).get('total')}")

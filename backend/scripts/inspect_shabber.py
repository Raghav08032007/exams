import urllib.request
import re

url = "https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/CBSE/10"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=5) as r:
        html = r.read().decode("utf-8", errors="ignore")
        matches = re.findall(r'/Shabber10/ALL-PYQ-Papers/tree/main/Boards/CBSE/10/([^"/?#]+)', html)
        print("Years/folders in Shabber10 CBSE 10:", sorted(list(set(matches))))
except Exception as e:
    print("ERR:", e)

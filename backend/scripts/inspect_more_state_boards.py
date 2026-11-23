import urllib.request
import re

for b in ['Bihar', 'Rajasthan', 'Madhya_Pradesh', 'Telangana']:
    u = f"https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/{b}"
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            html = r.read().decode('utf-8', errors='ignore')
            sub = re.findall(rf'/Shabber10/ALL-PYQ-Papers/tree/main/Boards/{b}/([^"/?#]+)', html)
            print(f"{b} subfolders:", sorted(list(set(sub))))
    except Exception as e:
        print(f"{b} error:", e)

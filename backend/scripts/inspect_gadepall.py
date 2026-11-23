import urllib.request
import re

url = "https://github.com/gadepall/cbse-papers/tree/main/papers"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=5) as r:
        html = r.read().decode("utf-8", errors="ignore")
        matches = re.findall(r'/gadepall/cbse-papers/tree/main/papers/([^"/?#]+)', html)
        print("Subject folders in gadepall/cbse-papers/papers:", sorted(list(set(matches))))
except Exception as e:
    print("ERR:", e)

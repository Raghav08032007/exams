import urllib.request
import re

def fetch_links(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            return html
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

for board in ['Tamil_Nadu', 'Maharashtra', 'ICSE', 'Uttar_Pradesh', 'Kerala', 'West_Bengal']:
    u = f"https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/{board}"
    html = fetch_links(u)
    sub = re.findall(rf'/Shabber10/ALL-PYQ-Papers/tree/main/Boards/{board}/([^"/?#]+)', html)
    print(f"Subfolders in {board}:", sorted(list(set(sub))))

# Check gadepall cbse-papers for math & physics
for sub in ['math', 'physics', 'chemistry', 'cs']:
    u = f"https://github.com/gadepall/cbse-papers/tree/main/papers/{sub}"
    html = fetch_links(u)
    years = re.findall(rf'/gadepall/cbse-papers/tree/main/papers/{sub}/([^"/?#]+)', html)
    print(f"Years/folders in gadepall {sub}:", sorted(list(set(years))))

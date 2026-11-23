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

# Check CBSE 12 years in Shabber10
html_cbse12 = fetch_links("https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/CBSE/12")
years_cbse12 = re.findall(r'/Shabber10/ALL-PYQ-Papers/tree/main/Boards/CBSE/12/([^"/?#]+)', html_cbse12)
print("Years in Shabber10 CBSE 12:", sorted(list(set(years_cbse12))))

# Check what other boards have in Shabber10
html_boards = fetch_links("https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards")
boards = re.findall(r'/Shabber10/ALL-PYQ-Papers/tree/main/Boards/([^"/?#]+)', html_boards)
print("Boards in Shabber10:", sorted(list(set(boards))))

# Check Tamil Nadu in Shabber10
html_tn = fetch_links("https://github.com/Shabber10/ALL-PYQ-Papers/tree/main/Boards/TamilNadu")
tn_sub = re.findall(r'/Shabber10/ALL-PYQ-Papers/tree/main/Boards/TamilNadu/([^"/?#]+)', html_tn)
print("Tamil Nadu folders in Shabber10:", sorted(list(set(tn_sub))))

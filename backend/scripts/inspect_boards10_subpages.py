import urllib.request, re

base = "https://boards10.github.io/"
pages = [
    "cbse-class-10-maths-pyq.html",
    "cbse-class-10-science-pyq.html",
    "cbse-class-10-social-science-pyq.html",
    "cbse-class-10-english-pyq.html",
    "cbse-class-10-hindi-a-pyq.html",
    "cbse-class-10-hindi-b-pyq.html"
]

all_pdfs = {}
for p in pages:
    url = base + p
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            pdfs = re.findall(r'href=[\'"]([^\'"]+\.pdf)[\'"]', html, re.I)
            print(f"Page '{p}': {len(pdfs)} PDF links found")
            for pdf in pdfs[:5]:
                print(f"   {pdf}")
            all_pdfs[p] = pdfs
    except Exception as e:
        print(f"Error on {p}: {e}")

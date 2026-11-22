import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        return urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

# Let's check Kalvisolai archives for 10th and 12th public exam question papers
print("Fetching Kalvisolai...")
html_k = fetch("https://www.kalvisolai.com/p/10th-public-exam-question-papers-and.html")
if not html_k:
    html_k = fetch("https://www.kalvisolai.com/search?q=10th+public+exam+question+paper")

pdf_links_k = re.findall(r'href=[\'"](https?://[^\'"]+\.pdf)[\'"]', html_k)
print(f"Kalvisolai PDF links found: {len(pdf_links_k)}")
for p in pdf_links_k[:10]:
    print(" ", p)

# Also check Padasalai
print("\nFetching Padasalai...")
html_p = fetch("https://www.padasalai.net/search?q=10th+public+exam+original+question+paper")
pdf_links_p = re.findall(r'href=[\'"](https?://[^\'"]+\.pdf)[\'"]', html_p)
print(f"Padasalai PDF links found: {len(pdf_links_p)}")
for p in pdf_links_p[:10]:
    print(" ", p)

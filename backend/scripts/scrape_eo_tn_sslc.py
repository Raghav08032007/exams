import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.educationobserver.com/previous-11-year-solved-question-papers-of-tamil-nadu-sslc-exam/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    # Find all pdf links or drive links
    links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html)
    pdf_links = [l for l in links if '.pdf' in l.lower() or 'drive.google.com' in l.lower() or 'educationobserver.com' in l.lower()]
    print(f"Found {len(pdf_links)} links:")
    for l in pdf_links[:25]:
        print(" ", l)
except Exception as e:
    print(f"Error: {e}")

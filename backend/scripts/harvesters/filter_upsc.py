import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = 'https://www.upsc.gov.in/archived-exam-documents/question-papers/'
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8', errors='ignore')

pdf_urls = set(re.findall(r'https?://[^\s"\'<>]+\.pdf', html))
csp_csm = [p for p in pdf_urls if any(k in p.upper() for k in ['CSP', 'CSM', 'CIVIL', 'PRELIM', 'GS1', 'GS2', 'CSAT'])]
print(f"Found {len(csp_csm)} UPSC Civil Services papers:")
for p in sorted(csp_csm):
    print(" ", p)

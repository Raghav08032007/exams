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
print(f"Total PDF URLs found: {len(pdf_urls)}")
for p in sorted(pdf_urls):
    print(" ", p)

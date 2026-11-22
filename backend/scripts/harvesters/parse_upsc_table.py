import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://www.upsc.gov.in/archived-exam-documents/question-papers/'
html = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=10, context=ctx).read().decode('utf-8', errors='ignore')

# Match table cells or text near PDF links
items = re.findall(r'<a[^>]+href=["\']([^"\']+\.pdf)["\'][^>]*>([\s\S]*?)</a>', html)
for href, text in items:
    clean_text = re.sub(r'<[^>]+>', '', text).strip()
    clean_text = re.sub(r'\s+', ' ', clean_text)
    if any(k in href.lower() or k in clean_text.lower() for k in ['general', 'prelim', 'civil', 'essay', 'studies', 'csat']):
        print(f"[{clean_text}] -> {href}")

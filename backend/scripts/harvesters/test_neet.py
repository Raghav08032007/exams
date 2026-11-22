import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://neet.nta.nic.in/archive/'
try:
    req = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8', errors='ignore')
    pdfs = re.findall(r'href=["\']([^"\']+\.pdf)["\']', html)
    print(f"Found {len(pdfs)} on neet archive:")
    for p in pdfs[:10]:
        print(" ", p)
except Exception as e:
    print("Error:", e)

import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

urls = [
    "https://cbseacademic.nic.in/SQP_CLASSX_2022-23.html",
    "https://cbseacademic.nic.in/SQP_CLASSXII_2022-23.html",
    "https://cbseacademic.nic.in/SQP_CLASSX_2020-21.html",
    "https://cbseacademic.nic.in/SQP_CLASSXII_2020-21.html"
]
for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            pdfs = re.findall(r'href=["\']([^"\']+\.pdf)["\']', html)
            print(f"{u} -> {len(pdfs)} PDFs")
            for p in pdfs[:4]:
                print("   ", p)
    except Exception as e:
        print(f"{u} -> Error: {e}")

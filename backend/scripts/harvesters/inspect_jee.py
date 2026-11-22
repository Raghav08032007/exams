import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

req = urllib.request.Request('https://jeeadv.ac.in/archive.html', headers=headers)
html = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8', errors='ignore')
for p in re.findall(r'href=["\']([^"\']+\.pdf)["\']', html):
    print(p)

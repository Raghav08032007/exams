import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
req = urllib.request.Request('https://www.selfstudys.com/show-pdf/0XreMO9qWAnq7vyVoUwg.pdf', headers=headers)
html = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8', errors='ignore')
pdfs = re.findall(r'https?://[^\s"\'<>]+\.pdf', html)
print('PDFs inside show-pdf:', pdfs)

# Also check any file or download URLs or asset URLs
other_links = re.findall(r'https?://[^\s"\'<>]+(?:download|asset|storage|pdf|media|file)[^\s"\'<>]*', html, re.I)
print('Other interesting links:', other_links[:10])

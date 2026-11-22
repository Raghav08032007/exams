import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://www.upsc.gov.in/archived-exam-documents/question-papers/'
html = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=10, context=ctx).read().decode('utf-8', errors='ignore')
matches = [m for m in re.findall(r'https?://[^\s"\'<>]+\.pdf', html) if 'QP-' in m or 'CSP' in m or 'CSM' in m]
for m in sorted(set(matches)):
    print(m)

import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://www.upsc.gov.in/archived-exam-documents/question-papers/'
html = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=10, context=ctx).read().decode('utf-8', errors='ignore')

idx = html.find('QP-CSP-18-GS-I-C.pdf')
if idx != -1:
    print(html[max(0, idx - 400): idx + 400])
else:
    print("Not found")

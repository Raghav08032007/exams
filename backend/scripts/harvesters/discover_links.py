import urllib.request
import ssl
import re
from urllib.parse import urljoin

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def check_url(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href=["\']([^"\']+)["\']', html)
            pdfs = [urljoin(url, l) for l in links if re.search(r'\.pdf', l, re.I)]
            return resp.status, len(pdfs), pdfs[:5]
    except Exception as e:
        return str(e), 0, []

test_urls = [
    # UPSC URLs
    "https://upsc.gov.in/examinations/previous-question-papers",
    "https://upsc.gov.in/examinations/previous-question-papers?field_exam_name_value=Civil+Services",
    "https://www.upsc.gov.in/examinations/previous-question-papers",
    # CBSE URLs
    "https://www.cbse.gov.in/cbsenew/question-paper.html",
    "https://cbseacademic.nic.in/SQP_CLASSX_2023-24.html",
    "https://cbseacademic.nic.in/SQP_CLASSXII_2023-24.html",
    # NTA NEET & JEE Main URLs
    "https://nta.ac.in/Downloads",
    "https://jeemain.nta.nic.in/",
]

for u in test_urls:
    status, count, sample = check_url(u)
    print(f"URL: {u}\n  Status: {status} | PDFs: {count}")
    for s in sample:
        print(f"    {s}")

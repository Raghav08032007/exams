import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://www.upsc.gov.in/archived-exam-documents/question-papers/'
html = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=10, context=ctx).read().decode('utf-8', errors='ignore')

# Match examName, year, and documents
exam_blocks = re.findall(r'\{\\"id\\":\\"\d+\\",\\"examName\\":\\"([^\\"]+)\\",\\"year\\":\\"(\d+)\\"[\s\S]*?\\"documents\\":\[([\s\S]*?)\]\}', html)
print(f"Total exam blocks: {len(exam_blocks)}")

for name, year, docs in exam_blocks:
    if "civil services" in name.lower():
        print(f"\n=== {name} ({year}) ===")
        doc_matches = re.findall(r'\\"title\\":\\"([^\\"]+)\\"[\s\S]*?\\"url\\":\\"(https://www\.upsc\.gov\.in/uploads/[^\\"]+\.pdf)\\"', docs)
        for t, u in doc_matches:
            if any(k in t.lower() for k in ["general studies", "essay", "csat"]):
                print(f"  * {t} -> {u}")

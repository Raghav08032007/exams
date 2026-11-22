import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    ("2024", "https://www.educationobserver.com/tamilnadu-class-10-sslc-public-exam-2024-question-papers-answer-keys/"),
    ("2023", "https://www.educationobserver.com/tnsslc-public-exam-2023-question-papers-answer-keys/"),
    ("2022", "https://www.educationobserver.com/previous-question-papers-keys-tn-sslc-board-exam-2022/"),
]

for year, url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        matches = re.findall(r'<a\s+(?:[^>]*?\s+)?href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', html, re.I | re.S)
        print(f"\n=== TN SSLC {year} Links ===")
        for href, text in matches:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            if any(w in (href + clean_text).lower() for w in ['.pdf', 'drive.google', 'tamil', 'english', 'math', 'science', 'social']):
                print(f"  {clean_text[:40]} -> {href}")
    except Exception as e:
        print(f"Error {year}: {e}")

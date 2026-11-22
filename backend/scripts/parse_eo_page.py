import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.educationobserver.com/tamilnadu-sslc-exam-previous-model-question-answer/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        
    # Extract links with text
    matches = re.findall(r'<a\s+(?:[^>]*?\s+)?href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', html, re.I | re.S)
    print(f"Total links on page: {len(matches)}")
    sslc_links = []
    for href, text in matches:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        if any(w in (href + clean_text).lower() for w in ['question', 'paper', 'math', 'tamil', 'science', 'english', 'social', 'sslc', '10th']):
            sslc_links.append((clean_text, href))
            
    print(f"Relevant links: {len(sslc_links)}")
    for txt, href in sslc_links[:35]:
        print(f"  {txt[:50]} -> {href}")
except Exception as e:
    print("Error:", e)

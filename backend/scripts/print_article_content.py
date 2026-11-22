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
    
    # Extract entry-content
    match = re.search(r'<div class="entry-content[^"]*">(.*?)</div>\s*<!-- \.entry-content -->', html, re.S)
    if not match:
        match = re.search(r'<article[^>]*>(.*?)</article>', html, re.S)
    
    if match:
        content = match.group(1)
        # Find all a tags
        links = re.findall(r'<a\s+(?:[^>]*?\s+)?href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', content, re.I | re.S)
        print(f"Links in article content: {len(links)}")
        for href, text in links:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            print(f"  {clean_text[:60]} -> {href}")
    else:
        print("Could not isolate article content")
except Exception as e:
    print("Error:", e)

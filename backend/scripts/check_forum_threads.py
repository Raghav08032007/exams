import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://www.educationobserver.com/forum/forumdisplay.php?fid=128", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    threads = re.findall(r'<a\s+(?:[^>]*?\s+)?href=[\'"]([^\'"]*showthread\.php\?tid=\d+)[^\'"]*[\'"][^>]*>(.*?)</a>', html, re.I | re.S)
    print(f"Total threads in forum: {len(threads)}")
    for href, title in threads:
        clean = re.sub(r'<[^>]+>', '', title).strip()
        if any(w in clean.lower() for w in ['2021', '2020', '2022', '2023', '2024', '10th', 'sslc']):
            print(f"  {clean} -> {href}")
except Exception as e:
    print("Error:", e)

import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

threads = [
    ("Tamil", "https://www.educationobserver.com/forum/showthread.php?tid=24295"),
    ("English", "https://www.educationobserver.com/forum/showthread.php?tid=24297"),
    ("Maths", "https://www.educationobserver.com/forum/showthread.php?tid=24293"),
    ("Science", "https://www.educationobserver.com/forum/showthread.php?tid=24296"),
    ("Social", "https://www.educationobserver.com/forum/showthread.php?tid=24298"),
]

for sub, url in threads:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        atts = re.findall(r'href=[\'"]([^\'"]*attachment\.php\?aid=(\d+))[^\'"]*[\'"][^>]*>(.*?)</a>', html, re.I | re.S)
        print(f"\n{sub}: {len(atts)} attachments")
        for href, aid, text in atts:
            clean = re.sub(r'<[^>]+>', '', text).strip()
            print(f"  [{aid}] {clean}")
    except Exception as e:
        print(f"Error {sub}: {e}")

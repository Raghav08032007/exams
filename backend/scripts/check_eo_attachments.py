import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

threads = [
    ("2023 Tamil", "https://www.educationobserver.com/forum/showthread.php?tid=28098"),
    ("2023 English", "https://www.educationobserver.com/forum/showthread.php?tid=28108"),
    ("2023 Maths", "https://www.educationobserver.com/forum/showthread.php?tid=28116"),
    ("2023 Science", "https://www.educationobserver.com/forum/showthread.php?tid=28127"),
    ("2023 Social", "https://www.educationobserver.com/forum/showthread.php?tid=28128"),
    ("Older tid=21844", "https://www.educationobserver.com/forum/showthread.php?tid=21844"),
    ("Older tid=18002", "https://www.educationobserver.com/forum/showthread.php?tid=18002")
]

for title, url in threads:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        # Look for attachment links
        att = re.findall(r'href=[\'"]([^\'"]*(?:attachment\.php\?aid=\d+|[^\'"]+\.pdf))[^\'"]*[\'"]', html, re.I)
        print(f"\n{title} ({url}):")
        for a in att[:5]:
            print("  Attachment/PDF:", a)
    except Exception as e:
        print(f"Error {title}: {e}")

import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

threads_2024 = [
    ("2024", "https://www.educationobserver.com/forum/showthread.php?tid=29233"),
    ("2024", "https://www.educationobserver.com/forum/showthread.php?tid=29236"),
    ("2024", "https://www.educationobserver.com/forum/showthread.php?tid=29240"),
    ("2024", "https://www.educationobserver.com/forum/showthread.php?tid=29379"),
    ("2024", "https://www.educationobserver.com/forum/showthread.php?tid=31632")
]

for year, url in threads_2024:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # Get thread title
        t_match = re.search(r'<title>(.*?)</title>', html, re.I)
        title = t_match.group(1) if t_match else "No Title"
        print(f"\nThread: {title} ({url})")
        
        attachments = re.findall(r'href=[\'"]([^\'"]*(?:attachment\.php\?aid=\d+|[^\'"]+\.pdf))[^\'"]*[\'"][^>]*>(.*?)</a>', html, re.I | re.S)
        for att, atitle in attachments:
            clean_title = re.sub(r'<[^>]+>', '', atitle).strip()
            print(f"  {clean_title} -> {att}")
    except Exception as e:
        print(f"Error {url}: {e}")

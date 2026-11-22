import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Threads from Education Observer for TN SSLC
threads = [
    ("2024", "https://www.educationobserver.com/tamilnadu-class-10-sslc-public-exam-2024-question-papers-answer-keys/"),
    ("2023", "https://www.educationobserver.com/tnsslc-public-exam-2023-question-papers-answer-keys/"),
    ("2022", "https://www.educationobserver.com/previous-question-papers-keys-tn-sslc-board-exam-2022/"),
    ("2020", "https://www.educationobserver.com/tamilnadu-sslc-exam-2020-revision-question-papers/"),
    ("2019", "https://www.educationobserver.com/forum/showthread.php?tid=23265"),
    ("2018", "https://www.educationobserver.com/forum/showthread.php?tid=21844"),
    ("2017", "https://www.educationobserver.com/forum/showthread.php?tid=21102"),
    ("2016", "https://www.educationobserver.com/forum/showthread.php?tid=21110"),
    ("2015", "https://www.educationobserver.com/forum/showthread.php?tid=18002"),
]

for year, url in threads:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # Check for sub-threads or attachments
        sub_threads = re.findall(r'href=[\'"]([^\'"]*showthread\.php\?tid=\d+)[^\'"]*[\'"][^>]*>(.*?)</a>', html, re.I | re.S)
        attachments = re.findall(r'href=[\'"]([^\'"]*attachment\.php\?aid=\d+|[^\'"]+\.pdf)[^\'"]*[\'"][^>]*>(.*?)</a>', html, re.I | re.S)
        
        print(f"\n=== Year {year} ({url}) ===")
        print(f"  Sub-threads found: {len(sub_threads)}")
        for st, title in sub_threads[:5]:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            print(f"    sub-thread: {clean_title} -> {st}")
        print(f"  Attachments found: {len(attachments)}")
        for att, title in attachments[:5]:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            print(f"    attachment: {clean_title} -> {att}")
    except Exception as e:
        print(f"Error {year}: {e}")

import urllib.request
import re

url = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/cbse-class-10-maths-pyq.html"
headers = {"User-Agent": "Mozilla/5.0"}
content = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read().decode('utf-8', errors='ignore')
print(content[:2500])

# Find all <a> tags
links = re.findall(r'<a\s+[^>]*href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', content, re.I)
print(f"\nTotal <a> links: {len(links)}")
for href, text in links[:15]:
    print(f"  {text.strip()} -> {href}")

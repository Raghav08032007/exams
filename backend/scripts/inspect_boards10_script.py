import urllib.request
import re

url = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/cbse-class-10-maths-pyq.html"
headers = {"User-Agent": "Mozilla/5.0"}
content = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read().decode('utf-8', errors='ignore')

scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
print(f"Found {len(scripts)} scripts")
for i, s in enumerate(scripts):
    print(f"\n--- Script {i} ({len(s)} chars) ---")
    print(s[:1000])

# Also check for script src
srcs = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', content)
print("\nScript sources:", srcs)

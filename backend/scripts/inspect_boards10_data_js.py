import urllib.request
import re

url = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/data.js"
headers = {"User-Agent": "Mozilla/5.0"}
content = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read().decode('utf-8', errors='ignore')
print(f"data.js length: {len(content)}")
print("Sample content:")
print(content[:1500])

# Check keys in DATA
keys = re.findall(r'(\w+):\s*\[', content)
print("Keys in DATA:", keys[:15])

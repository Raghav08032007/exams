import urllib.request
import json
import re

url = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/data.js"
headers = {"User-Agent": "Mozilla/5.0"}
content = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read().decode('utf-8', errors='ignore')

# data.js starts with 'const DATA = ' and ends with ';'
raw_json = re.sub(r'^\s*const\s+DATA\s*=\s*', '', content).rstrip(';\n ')
try:
    data = json.loads(raw_json)
    print("Parsed JSON successfully!")
    print(f"Total subjects in boards10: {len(data)}")
    for subj, papers in data.items():
        print(f"\n--- Subject: {subj} ({len(papers)} papers) ---")
        years = set(p.get("year") for p in papers)
        sets = set(p.get("set") for p in papers)
        types = set(p.get("type") for p in papers)
        print(f"  Years: {sorted(list(years))[:10]} ... {sorted(list(years))[-3:]}")
        print(f"  Sets: {sets}")
        print(f"  Sample file: {papers[0].get('file')}")
except Exception as e:
    print("Error parsing JSON:", e)

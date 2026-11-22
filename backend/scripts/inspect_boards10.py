import urllib.request
import json
import re

c = urllib.request.urlopen('https://raw.githubusercontent.com/boards10/boards10.github.io/main/data.js').read().decode('utf-8')
raw_json = re.sub(r'^\s*const\s+DATA\s*=\s*', '', c).rstrip(';\n ')
d = json.loads(raw_json)

total = sum(len(v) for v in d.values())
print('Total papers in data.js:', total)
for subj, items in d.items():
    print(f"Subject '{subj}': {len(items)} items. Example: {items[0]}")
    if len(items) > 1:
        print(f"  Second: {items[1]}")

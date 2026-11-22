import urllib.request
import json
import re

c = urllib.request.urlopen('https://raw.githubusercontent.com/boards10/boards10.github.io/main/data.js').read().decode('utf-8')
raw_json = re.sub(r'^\s*const\s+DATA\s*=\s*', '', c).rstrip(';\n ')
d = json.loads(raw_json)

for subj, items in d.items():
    years = sorted(list(set(x['year'] for x in items)))
    sets = sorted(list(set(str(x.get('set','')) for x in items)))
    print(f"{subj}: {len(items)} files, years: {years}, sets: {sets}")

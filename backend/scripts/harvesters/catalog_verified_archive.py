import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
data = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=headers), context=ctx).read())

all_pdfs = [x['path'] for x in data.get('tree', []) if x['path'].endswith('.pdf')]

# Catalog Tamil Nadu
tn_files = [p for p in all_pdfs if p.startswith('Boards/Tamil_Nadu/')]
print(f"Total Boards/Tamil_Nadu files: {len(tn_files)}")
for p in tn_files:
    print(" ", p)

# Catalog NEET
neet_files = [p for p in all_pdfs if p.startswith('NEET/')]
print(f"\nTotal NEET files: {len(neet_files)}")
for p in neet_files:
    print(" ", p)

# Catalog JEE Main
jee_main_files = [p for p in all_pdfs if p.startswith('JEE/Main/')]
print(f"\nTotal JEE/Main files: {len(jee_main_files)}")
for p in jee_main_files[:25]:
    print(" ", p)

# Catalog CBSE
cbse_10 = [p for p in all_pdfs if p.startswith('Boards/CBSE/10/')]
cbse_12 = [p for p in all_pdfs if p.startswith('Boards/CBSE/12/')]
print(f"\nTotal CBSE 10: {len(cbse_10)}, CBSE 12: {len(cbse_12)}")
# Sample core subjects
core_subjs = ['math', 'science', 'social', 'physics', 'chemistry', 'biology', 'english']
cbse_10_core = [p for p in cbse_10 if any(s in p.lower() for s in core_subjs)]
cbse_12_core = [p for p in cbse_12 if any(s in p.lower() for s in core_subjs)]
print(f"CBSE 10 core subjects: {len(cbse_10_core)}")
for p in cbse_10_core[:15]:
    print(" ", p)
print(f"CBSE 12 core subjects: {len(cbse_12_core)}")
for p in cbse_12_core[:15]:
    print(" ", p)

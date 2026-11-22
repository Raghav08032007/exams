import urllib.request
import json

url = 'http://localhost:5000/papers/?exam=class-10&category=cbse-10&per_page=100'
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode('utf-8'))

print('Total papers in category:', d.get('pagination', {}).get('total'))
papers = d.get('papers', [])
print('Papers returned in response:', len(papers))

# Check Math papers across all years in this category
years_math = {}
for p in papers:
    is_math = any(s.get('name') == 'Mathematics' for s in p.get('subjects', []))
    if is_math:
        yr = p.get('year')
        years_math.setdefault(yr, []).append(p)

print(f"\nMath papers found in first 100 results: {sum(len(v) for v in years_math.values())}")
for yr in sorted(years_math.keys(), reverse=True):
    print(f"  Year {yr}: {len(years_math[yr])} papers")

# Now let's query specifically for subject=Mathematics
url2 = 'http://localhost:5000/papers/?exam=class-10&category=cbse-10&subject=Mathematics&per_page=100'
with urllib.request.urlopen(urllib.request.Request(url2)) as resp2:
    d2 = json.loads(resp2.read().decode('utf-8'))

print(f"\nExplicit query for subject=Mathematics total: {d2.get('pagination', {}).get('total')}")
papers2 = d2.get('papers', [])
years_math2 = {}
for p in papers2:
    yr = p.get('year')
    years_math2.setdefault(yr, []).append(p)

for yr in sorted(years_math2.keys(), reverse=True):
    print(f"  Year {yr}: {len(years_math2[yr])} papers")

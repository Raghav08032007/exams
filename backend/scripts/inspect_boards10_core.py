import urllib.request, json

url = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/final_meta.json"
req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))

for subj in ['math', 'science', 'social', 'english']:
    papers = data.get(subj, [])
    sample_papers = [p for p in papers if p.get('type') == 'Sample']
    print(f"Subject '{subj}': total {len(papers)} papers (Sample: {len(sample_papers)})")
    years = sorted(list(set(p['year'] for p in papers)), reverse=True)
    print(f"  Years: {years[:12]}")

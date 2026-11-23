import urllib.request, json

url = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/final_meta.json"
req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))

print("Total subjects in final_meta.json:", list(data.keys()))
for subj in ['hindi_a', 'hindi_b', 'ait']:
    papers = data.get(subj, [])
    print(f"Subject '{subj}': {len(papers)} papers")
    years = sorted(list(set(p['year'] for p in papers)), reverse=True)
    print(f"  Years for {subj}: {years[:12]}")
    if papers:
        print(f"  Sample file: {papers[0]['file']} ({papers[0]['size']} bytes)")

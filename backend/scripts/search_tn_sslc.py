import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

queries = [
    "tamilnadu+sslc+question+paper",
    "tn+sslc+pyq",
    "tamil+10th+question+paper",
    "samacheer+kalvi+10th+question+paper"
]

for q in queries:
    res = fetch_json(f'https://api.github.com/search/repositories?q={q}')
    if res and res.get('items'):
        print(f"\nQuery: {q} found {res['total_count']} repos:")
        for r in res['items'][:4]:
            print(f"  {r['full_name']} - {r['html_url']}")

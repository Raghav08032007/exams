import urllib.request
import urllib.parse
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_repos(q):
    url = f'https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&sort=stars&order=desc'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            items = json.loads(r.read().decode('utf-8')).get('items', [])
            print(f"Query: {q} -> Found {len(items)} repos")
            for it in items[:6]:
                name = it.get('full_name')
                stars = it.get('stargazers_count')
                desc = (it.get('description') or '')[:80]
                print(f"  {name} ({stars}*) - {desc}")
    except Exception as e:
        print(f"Error searching {q}: {e}")

search_repos('cbse class 10 question papers')
search_repos('tamil nadu sslc question papers')
search_repos('cbse papers')
search_repos('pyq cbse')

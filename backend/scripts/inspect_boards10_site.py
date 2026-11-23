import urllib.request, re

def check_boards10():
    url = "https://boards10.github.io/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href=[\'"]([^\'"]+\.pdf)[\'"]', html, re.I)
            all_links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html, re.I)
            print(f"Boards10 root returned {len(html)} bytes, {len(links)} PDF links, {len(all_links)} total links.")
            for l in links[:20]:
                print("  PDF:", l)
            internal_pages = [l for l in all_links if not l.startswith('http') and not l.startswith('#')]
            print("  Internal links:", internal_pages[:20])
    except Exception as e:
        print("Boards10 error:", e)

check_boards10()

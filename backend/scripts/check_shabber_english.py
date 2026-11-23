import urllib.request

for yr in range(2015, 2027):
    url = f"https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/CBSE/10/{yr}/CBSE-Class-10-{yr}-english.pdf"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"Year {yr} English exists! Size: {resp.length or len(resp.read())}")
    except Exception as e:
        print(f"Year {yr} English not found: {e}")

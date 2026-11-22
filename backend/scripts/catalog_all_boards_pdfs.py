import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as resp:
    tree = json.loads(resp.read().decode('utf-8')).get('tree', [])

board_files = [x['path'] for x in tree if x['path'].startswith('Boards/') and x['path'].endswith('.pdf')]
print(f"Total PDFs in Boards/: {len(board_files)}")

boards_map = {}
for bf in board_files:
    parts = bf.split('/')
    board = parts[1]
    boards_map.setdefault(board, []).append(bf)

for b, flist in sorted(boards_map.items()):
    print(f"\n--- {b} ({len(flist)} files) ---")
    for f in flist[:8]:
        print(" ", f)

import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

redirect_url = "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6QLVS5t2WR-JjnDpWNver07vk__qwYPdHhii6YQIhCb0HzkEVq1NJxDRNeMWFWE8K0sDR3FR0PzbVGHvYvolBLblgnWz6OBpOD6qVOyWwfIBYK6hUzAATO8ToCbBMyvfVxsvJp_ZX5-D2kDKKd-YpDp1Hop9jZd94QZqtvlZxT6gdrU5jiy1ZB57A"

req = urllib.request.Request(redirect_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        print("Final URL:", resp.geturl())
        html = resp.read().decode('utf-8', errors='ignore')
        import re
        links = re.findall(r'href=[\'"]([^\'"]+\.pdf[^\'"]*)[\'"]', html, re.I)
        print(f"Found {len(links)} PDF links:")
        for l in links[:15]:
            print(" ", l)
except Exception as e:
    print("Error:", e)

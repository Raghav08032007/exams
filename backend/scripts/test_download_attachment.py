import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.educationobserver.com/forum/attachment.php?aid=64603"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        content_type = resp.headers.get('Content-Type')
        content_disp = resp.headers.get('Content-Disposition')
        data = resp.read()
        print(f"Status: {resp.status}")
        print(f"Content-Type: {content_type}")
        print(f"Content-Disposition: {content_disp}")
        print(f"Downloaded bytes: {len(data)}")
        print(f"PDF Header: {data[:10]}")
except Exception as e:
    print("Download error:", e)

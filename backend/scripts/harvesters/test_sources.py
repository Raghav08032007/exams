import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

test_urls = [
    # UPSC 2024 Prelims
    ("UPSC 2024 Prelims GS1", "https://upsc.gov.in/sites/default/files/CSP-24-GS-P1.pdf"),
    ("UPSC 2024 Prelims CSAT", "https://upsc.gov.in/sites/default/files/CSP-24-CSAT-P2.pdf"),
    ("UPSC 2024 Prelims GS1 alt", "https://www.upsc.gov.in/sites/default/files/CSP-24-Paper-I-020724.pdf"),
    
    # CBSE 2020 / 2019
    ("CBSE 10 Maths 2020", "https://cbseacademic.nic.in/web_material/SQP/ClassX_2019_20/Maths-Standard-SQP.pdf"),
    ("CBSE 10 Science 2020", "https://cbseacademic.nic.in/web_material/SQP/ClassX_2019_20/Science-SQP.pdf"),
    ("CBSE 12 Physics 2020", "https://cbseacademic.nic.in/web_material/SQP/ClassXII_2019_20/Physics_SQP.pdf"),
    ("CBSE 12 Chemistry 2020", "https://cbseacademic.nic.in/web_material/SQP/ClassXII_2019_20/Chemistry_SQP.pdf"),
    
    # TN DGE / Kalvisolai / Padasalai
    ("TN DGE Portal", "https://dge.tn.gov.in"),
    ("Kalvisolai Portal", "https://www.kalvisolai.com"),
    ("Padasalai Portal", "https://www.padasalai.net"),
]

for name, url in test_urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            content_type = resp.headers.get('Content-Type', '')
            status = resp.status
            head = resp.read(16)
            is_pdf = head.startswith(b'%PDF')
            print(f"[OK {status}] {name} | type={content_type} | %PDF={is_pdf} | url={url}")
    except Exception as e:
        print(f"[ERR] {name} -> {e}")

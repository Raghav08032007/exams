import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

test_upsc = [
    # 2024 Prelims
    'https://www.upsc.gov.in/uploads/2026/06/CSP-2024-GS-P1.pdf',
    'https://www.upsc.gov.in/uploads/2026/06/CSP-2024-GS-P2.pdf',
    'https://www.upsc.gov.in/uploads/2026/06/GS-Paper-I.pdf',
    'https://www.upsc.gov.in/uploads/2026/06/CSAT-Paper-II.pdf',
    # 2023 Prelims & Mains
    'https://www.upsc.gov.in/uploads/2026/05/CSP-2023-GS-P1.pdf',
    'https://www.upsc.gov.in/uploads/2026/07/QP-CSM-23-ESSAY.pdf',
    'https://www.upsc.gov.in/uploads/2026/07/QP-CSM-23-GS-I.pdf',
    'https://www.upsc.gov.in/uploads/2026/07/QP-CSM-23-GS-II.pdf',
    'https://www.upsc.gov.in/uploads/2026/07/QP-CSM-23-GS-III.pdf',
    'https://www.upsc.gov.in/uploads/2026/07/QP-CSM-23-GS-IV.pdf',
    # 2022 Prelims & Mains
    'https://www.upsc.gov.in/uploads/2026/07/QP-CSM-22-GS-I.pdf',
    'https://www.upsc.gov.in/uploads/2026/07/QP-CSM-22-GS-II.pdf',
    'https://www.upsc.gov.in/uploads/2026/07/QP-CSM-22-GS-III.pdf',
    'https://www.upsc.gov.in/uploads/2026/07/QP-CSM-22-GS-IV.pdf',
    # 2018 Prelims
    'https://www.upsc.gov.in/uploads/2026/09/QP-CSP-18-GS-I-C.pdf',
    'https://www.upsc.gov.in/uploads/2026/09/QP-CSP-18-GS-II-C.pdf',
]

for u in test_upsc:
    req = urllib.request.Request(u, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
            print(f"200 OK: {u} (size: {r.headers.get('Content-Length')})")
    except Exception as e:
        # print(f"Error {u}: {e}")
        pass

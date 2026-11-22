import urllib.request
import ssl

ctx = ssl._create_unverified_context()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

urls = [
    ("NCERT Class 10 Maths Ch 1", "https://ncert.nic.in/textbook/pdf/jemh101.pdf"),
    ("NCERT Class 10 Science Ch 1", "https://ncert.nic.in/textbook/pdf/jesc101.pdf"),
    ("NCERT Class 12 Physics Ch 1", "https://ncert.nic.in/textbook/pdf/leph101.pdf"),
    ("NCERT Class 12 Chemistry Ch 1", "https://ncert.nic.in/textbook/pdf/lech101.pdf"),
    ("NCERT Class 12 Biology Ch 1", "https://ncert.nic.in/textbook/pdf/lebo101.pdf"),
    ("NCERT Class 6 Science Ch 1", "https://ncert.nic.in/textbook/pdf/fesc101.pdf"),
]

for name, url in urls:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read(2048)
            is_pdf = b"%PDF" in data[:100]
            print(f" {name}: Status {resp.status} | Is PDF: {is_pdf} | Bytes read: {len(data)}")
    except Exception as e:
        print(f" {name}: Error {e}")

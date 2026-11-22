import urllib.request
import ssl
from pypdf import PdfReader
import io

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

test_paths = [
    "Boards/Tamil_Nadu/2015/Tamil_Nadu-2015-physics.pdf",
    "Boards/Tamil_Nadu/2017/Tamil_Nadu-2017-mathematics.pdf",
    "NEET/2018/main/NEET-2018-main-question.pdf",
    "NEET/2018/main/NEET-2018-main-solution.pdf",
    "JEE/Advanced/2019/Paper 2/jee-advanced-2019-question-paper-2.pdf",
    "Boards/CBSE/10/2022/CBSE-Class-10-2022-computer-applications.pdf",
    "Boards/CBSE/12/2022/CBSE-Class-12-2022-chemistry.pdf"
]

for p in test_paths:
    # URL encode spaces
    url = "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/" + urllib.parse.quote(p)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read()
            is_pdf = data.startswith(b'%PDF')
            reader = PdfReader(io.BytesIO(data))
            text = ""
            for page in reader.pages[:2]:
                text += page.extract_text() or ""
            print(f"[OK] {p} | Size: {len(data)} | Pages: {len(reader.pages)} | %PDF: {is_pdf}")
            print(f"     Excerpt: {' '.join(text.split()[:20])}")
    except Exception as e:
        print(f"[ERR] {p} -> {e}")

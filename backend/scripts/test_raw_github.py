import urllib.request
import urllib.parse

urls = [
    "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/JEE/Advanced/2023/Paper%201/jee-advanced-2023-question-paper-1.pdf",
    "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/CBSE/10/2022/CBSE-Class-10-2022-artificial-intelligence.pdf",
    "https://raw.githubusercontent.com/avallark/NCERT-TextBooks/master/10/10th-Mathematics.pdf",
    "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/NEET/2017/A/NEET-2017-A-question.pdf"
]

headers = {"User-Agent": "Mozilla/5.0"}
for url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read(200)
            print("OK:", resp.status, len(data), "bytes, header:", data[:10], "URL:", url.split('/')[-1])
    except Exception as e:
        print("FAIL:", e, url)

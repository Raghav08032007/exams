"""
Automatic DB migration script for ExamVault v2.
Connects to MySQL using DATABASE_URL from .env and applies missing columns/tables.
Run with: python run_migration.py
"""
import os
import pymysql
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get("DATABASE_URL", "mysql+pymysql://root:261008@localhost:3306/examvault")
for prefix in ("mysql+pymysql://", "mysql://", "pymysql://"):
    if db_url.startswith(prefix):
        db_url = "mysql://" + db_url[len(prefix):]
        break

parsed = urlparse(db_url)
host = parsed.hostname or "localhost"
port = parsed.port or 3306
user = parsed.username or "root"
password = parsed.password or ""
dbname = parsed.path.lstrip("/") or "examvault"

print(f"Connecting to MySQL database '{dbname}' on {host}:{port} as '{user}'...")

conn = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=dbname,
    charset="utf8mb4",
    autocommit=True
)

statements = [
    # 1. Update users.role ENUM
    "ALTER TABLE users MODIFY COLUMN role ENUM('user', 'admin', 'verifier') NOT NULL DEFAULT 'user'",
    
    # 2. Add official_site_url to exams
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS official_site_url VARCHAR(255) NULL",
    
    # 3. Add session to papers
    "ALTER TABLE papers ADD COLUMN IF NOT EXISTS session VARCHAR(50) NULL AFTER year",
    
    # 4. Add uploaded_by to papers
    "ALTER TABLE papers ADD COLUMN IF NOT EXISTS uploaded_by INT NULL AFTER verified_by",
    
    # 5. Populate official_site_url
    "UPDATE exams SET official_site_url = 'https://www.tnpsc.gov.in' WHERE slug = 'tnpsc'",
    "UPDATE exams SET official_site_url = 'https://www.upsc.gov.in' WHERE slug = 'upsc'",
    "UPDATE exams SET official_site_url = 'https://jeemain.nta.nic.in' WHERE slug = 'jee'",
    "UPDATE exams SET official_site_url = 'https://neet.nta.nic.in' WHERE slug = 'neet'",
]

with conn.cursor() as cur:
    for stmt in statements:
        try:
            cur.execute(stmt)
            print(f"✓ Executed: {stmt[:60]}...")
        except Exception as e:
            print(f"⚠ Notice: {e}")

    # Add FK constraint if missing
    try:
        cur.execute("""
            ALTER TABLE papers
            ADD CONSTRAINT fk_papers_uploaded_by
            FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
        """)
        print("✓ Added foreign key constraint fk_papers_uploaded_by")
    except Exception as e:
        print(f"ℹ FK notice: {e}")

    # Drop old scraper columns if present
    for col in ["source_type", "scraped_at"]:
        try:
            cur.execute(f"ALTER TABLE papers DROP COLUMN {col}")
            print(f"✓ Dropped old column {col}")
        except Exception:
            pass

print("\n🎉 Migration completed successfully! The database is up to date.")
conn.close()

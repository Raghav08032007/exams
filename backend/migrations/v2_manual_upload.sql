-- ExamVault Migration v2 — Manual Upload Overhaul
-- Safe to run on an existing database — no data loss for verified papers.
-- Run this in MySQL Workbench or terminal: mysql -u root -p examvault < v2_manual_upload.sql

USE examvault;

-- ── 1. Extend users.role ENUM to add 'verifier' ──────────────────────────────
ALTER TABLE users
  MODIFY COLUMN role ENUM('user', 'admin', 'verifier') NOT NULL DEFAULT 'user';

-- ── 2. Add official_site_url to exams ────────────────────────────────────────
ALTER TABLE exams
  ADD COLUMN IF NOT EXISTS official_site_url VARCHAR(255) NULL;

-- ── 3. Add session to papers ─────────────────────────────────────────────────
ALTER TABLE papers
  ADD COLUMN IF NOT EXISTS session VARCHAR(50) NULL
    COMMENT 'e.g. "January Session 1", NULL for exams without sessions'
  AFTER year;

-- ── 4. Add uploaded_by to papers ─────────────────────────────────────────────
ALTER TABLE papers
  ADD COLUMN IF NOT EXISTS uploaded_by INT NULL
    COMMENT 'FK to users — who uploaded this paper'
  AFTER verified_by;

-- Add FK constraint for uploaded_by if it doesn't already exist
-- (MySQL doesn't support IF NOT EXISTS for constraints, so we check first)
SET @fk_exists = (
  SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
  WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'papers'
    AND CONSTRAINT_NAME = 'fk_papers_uploaded_by'
);
SET @sql = IF(@fk_exists = 0,
  'ALTER TABLE papers ADD CONSTRAINT fk_papers_uploaded_by FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL',
  'SELECT ''FK already exists'' AS info'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ── 5. Add index on session for fast year+session queries ─────────────────────
-- (safe to re-run — MySQL silently ignores duplicate index names if you use CREATE INDEX IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS ix_papers_session ON papers(session);

-- ── 6. Populate official_site_url for all 4 exams ────────────────────────────
UPDATE exams SET official_site_url = 'https://www.tnpsc.gov.in'    WHERE slug = 'tnpsc' AND (official_site_url IS NULL OR official_site_url = '');
UPDATE exams SET official_site_url = 'https://www.upsc.gov.in'     WHERE slug = 'upsc'  AND (official_site_url IS NULL OR official_site_url = '');
UPDATE exams SET official_site_url = 'https://jeemain.nta.nic.in'  WHERE slug = 'jee'   AND (official_site_url IS NULL OR official_site_url = '');
UPDATE exams SET official_site_url = 'https://neet.nta.nic.in'     WHERE slug = 'neet'  AND (official_site_url IS NULL OR official_site_url = '');

-- ── 7. Remove scraping columns (safe — data in these cols is no longer used) ─
-- Using IF EXISTS to avoid errors if already removed
ALTER TABLE papers DROP COLUMN IF EXISTS source_type;
ALTER TABLE papers DROP COLUMN IF EXISTS scraped_at;
-- source_url can stay if it has data — it's just a reference URL field
-- ALTER TABLE papers DROP COLUMN IF EXISTS source_url;  -- uncomment if desired

-- ── Verification ─────────────────────────────────────────────────────────────
-- Check all 4 exams have official_site_url
SELECT name, slug, official_site_url FROM exams;
-- Check papers table structure
DESCRIBE papers;
-- Check users role enum
SHOW COLUMNS FROM users LIKE 'role';

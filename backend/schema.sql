-- ExamVault Database Schema v2
-- Managed via MySQL Workbench — run this against a fresh database.
-- For existing databases, use migrations/v2_manual_upload.sql instead.

CREATE DATABASE IF NOT EXISTS examvault CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE examvault;

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS paper_subjects;
DROP TABLE IF EXISTS bookmarks;
DROP TABLE IF EXISTS papers;
DROP TABLE IF EXISTS exam_categories;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS exams;

-- 1. Exams Table
CREATE TABLE exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    accent_color_hex VARCHAR(7) NOT NULL,
    official_site_url VARCHAR(255) NULL,
    INDEX ix_exams_slug (slug)
);

-- 2. Subjects Table
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 3. Users Table (role now includes 'verifier')
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin', 'verifier') NOT NULL DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_users_email (email)
);

-- 4. Exam Categories Table
CREATE TABLE exam_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    UNIQUE uq_category_exam_slug (exam_id, slug),
    INDEX ix_exam_categories_exam_id (exam_id)
);

-- 5. Papers Table (no source_type/scraped_at; adds session + uploaded_by)
CREATE TABLE papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_category_id INT NOT NULL,
    year SMALLINT NOT NULL,
    session VARCHAR(50) NULL COMMENT 'e.g. "January Session 1", NULL for exams without sessions',
    title VARCHAR(255) NOT NULL,
    language VARCHAR(50) DEFAULT 'English',
    pdf_url VARCHAR(500),
    file_size INT,
    has_answer_key BOOLEAN NOT NULL DEFAULT 0,
    answer_key_pdf_url VARCHAR(500),
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    download_count INT NOT NULL DEFAULT 0,
    source_url VARCHAR(500) NULL,
    source_name VARCHAR(100) NULL,
    answer_key_source_url VARCHAR(500) NULL,
    paper_type VARCHAR(20) NOT NULL DEFAULT 'original' COMMENT '"original" or "sample"',
    verification_status VARCHAR(20) NOT NULL DEFAULT 'unverified',
    verified_by INT NULL,
    uploaded_by INT NULL COMMENT 'FK to users — who uploaded this paper',
    rejection_note TEXT NULL,
    FOREIGN KEY (exam_category_id) REFERENCES exam_categories(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX ix_papers_exam_category_id (exam_category_id),
    INDEX ix_papers_year (year),
    INDEX ix_papers_paper_type (paper_type),
    INDEX ix_papers_verification_status (verification_status),
    INDEX ix_papers_session (session)
);

-- 6. Bookmarks Table
CREATE TABLE bookmarks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    paper_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    UNIQUE uq_user_paper_bookmark (user_id, paper_id),
    INDEX ix_bookmarks_user_id (user_id),
    INDEX ix_bookmarks_paper_id (paper_id)
);

-- 7. Paper Subjects (Many-to-Many)
CREATE TABLE paper_subjects (
    paper_id INT NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (paper_id, subject_id),
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- 8. Textbooks Table (Curriculum Books for Classes 1 to 12 & Competitive Exams)
CREATE TABLE textbooks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    standard_level VARCHAR(20) NOT NULL COMMENT 'e.g. "Class 1" to "Class 12"',
    board VARCHAR(50) NOT NULL COMMENT 'e.g. "CBSE / NCERT", "Tamil Nadu State Board"',
    subject_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    edition_year SMALLINT NULL DEFAULT 2024,
    language VARCHAR(50) NOT NULL DEFAULT 'English',
    pdf_url VARCHAR(500) NOT NULL,
    cover_image_url VARCHAR(500) NULL,
    chapter_number TINYINT NULL,
    chapter_title VARCHAR(255) NULL,
    source_url VARCHAR(500) NULL,
    source_name VARCHAR(100) NULL,
    download_count INT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    INDEX ix_textbooks_standard (standard_level),
    INDEX ix_textbooks_board (board),
    INDEX ix_textbooks_subject_id (subject_id),
    INDEX ix_textbooks_language (language)
);

-- ── Seed Data ─────────────────────────────────────────────────────────────────

-- Default exams with official site URLs and light-theme pastel accent colors
INSERT INTO exams (name, slug, description, accent_color_hex, official_site_url) VALUES
('TNPSC',
 'tnpsc',
 'Tamil Nadu Public Service Commission — Group 1, 2A, 2, 4, and VAO examinations for state government positions.',
 '#E8998D',
 'https://www.tnpsc.gov.in'),
('UPSC',
 'upsc',
 'Union Public Service Commission — Civil Services Examination (Prelims & Mains) and other central government recruitment.',
 '#8FB9A8',
 'https://www.upsc.gov.in'),
('JEE',
 'jee',
 'Joint Entrance Examination — JEE Main (multiple sessions) and JEE Advanced for engineering college admissions.',
 '#8FB8E0',
 'https://jeemain.nta.nic.in'),
('NEET',
 'neet',
 'National Eligibility cum Entrance Test — undergraduate medical (MBBS/BDS) admissions across India.',
 '#C3A8D9',
 'https://neet.nta.nic.in');

-- Default exam categories
INSERT INTO exam_categories (exam_id, name, slug) VALUES
-- TNPSC categories
((SELECT id FROM exams WHERE slug='tnpsc'), 'Group 1', 'group-1'),
((SELECT id FROM exams WHERE slug='tnpsc'), 'Group 2A', 'group-2a'),
((SELECT id FROM exams WHERE slug='tnpsc'), 'Group 2', 'group-2'),
((SELECT id FROM exams WHERE slug='tnpsc'), 'Group 4', 'group-4'),
((SELECT id FROM exams WHERE slug='tnpsc'), 'VAO', 'vao'),
-- UPSC categories
((SELECT id FROM exams WHERE slug='upsc'), 'Prelims', 'prelims'),
((SELECT id FROM exams WHERE slug='upsc'), 'Mains', 'mains'),
-- JEE categories
((SELECT id FROM exams WHERE slug='jee'), 'JEE Main', 'jee-main'),
((SELECT id FROM exams WHERE slug='jee'), 'JEE Advanced', 'jee-advanced'),
-- NEET categories
((SELECT id FROM exams WHERE slug='neet'), 'NEET UG', 'neet-ug');

-- Default admin user (password: Admin@1234 — change in production!)
-- bcrypt hash of "Admin@1234"
INSERT INTO users (name, email, password_hash, role)
VALUES ('Admin', 'admin@examvault.in',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQyCgRbDExgr5VhVcH9yDFMhS',
        'admin');

-- Note: Run migrations/v2_manual_upload.sql against an existing database
-- instead of re-running this full schema (which drops all data).

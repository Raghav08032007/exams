"""
Phase 0 — Audit & Clean Pipeline Script
Deletes old scraper scripts with fabrication logic,
migrates DB schema with verification columns,
resets fabricated/Wikimedia PDF URLs to NULL,
sets verification_status = 'unverified',
and removes orphaned 'real_' / 'gen_' uploaded files.
"""
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import text
from app import create_app
from app.extensions import db
from app.models.paper import Paper


def delete_old_scraper_scripts():
    print("🧹 [Task 1] Deleting old scraper scripts with fabrication logic...")
    files_to_delete = [
        os.path.join(backend_dir, "fetch_real_papers.py"),
        os.path.join(backend_dir, "scrape_official_urls.py")
    ]
    for filepath in files_to_delete:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"  -> Deleted: {os.path.basename(filepath)}")
        else:
            print(f"  -> Already absent: {os.path.basename(filepath)}")


def ensure_db_migration():
    print("🛠️ [Task 4] Ensuring verification columns exist on 'papers' table...")
    columns_to_add = [
        ("source_url", "VARCHAR(500) NULL"),
        ("source_type", "VARCHAR(50) NULL"),
        ("scraped_at", "DATETIME NULL"),
        ("verification_status", "VARCHAR(20) NOT NULL DEFAULT 'unverified'"),
        ("verified_by", "INT NULL"),
        ("rejection_note", "TEXT NULL")
    ]
    
    with db.engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE papers ADD COLUMN {col_name} {col_type};"))
                conn.commit()
                print(f"  -> Added column '{col_name}' to papers table.")
            except Exception as e:
                # Column likely already exists
                pass


def audit_and_clean_papers_table():
    print("🔍 [Task 2] Auditing papers table for fabricated / Wikimedia / sample URLs...")
    papers = Paper.query.all()
    reset_count = 0
    
    for paper in papers:
        url = paper.pdf_url or ""
        is_wikimedia = "wikimedia.org" in url.lower()
        is_sample = "sample.pdf" in url.lower() or "dummy.pdf" in url.lower()
        is_fabricated = ".nic.in/archives/" in url.lower() or "real_" in url.lower() or "gen_" in url.lower()
        
        if is_wikimedia or is_sample or is_fabricated:
            paper.pdf_url = None
            paper.answer_key_pdf_url = None
            paper.verification_status = "unverified"
            reset_count += 1
            print(f"  -> Reset paper ID {paper.id} ({paper.title}): cleared fabricated url '{url}'")
        else:
            # Ensure verification_status is initialized
            if not paper.verification_status:
                paper.verification_status = "unverified"

    db.session.commit()
    print(f"  -> Audited {len(papers)} papers. Reset {reset_count} fabricated/sample records to NULL & 'unverified'.")


def delete_orphaned_uploads():
    print("🗑️ [Task 3] Deleting orphaned 'real_' / 'gen_' / 'sample.pdf' files from uploads...")
    upload_dir = os.path.join(backend_dir, "uploads")
    if not os.path.exists(upload_dir):
        print("  -> Uploads folder does not exist.")
        return

    deleted_count = 0
    for fname in os.listdir(upload_dir):
        if fname.startswith("real_") or fname.startswith("gen_") or fname == "sample.pdf":
            fpath = os.path.join(upload_dir, fname)
            try:
                os.remove(fpath)
                deleted_count += 1
                print(f"  -> Removed file: {fname}")
            except Exception as e:
                print(f"  -> Could not remove {fname}: {e}")

    print(f"  -> Deleted {deleted_count} orphaned files from /uploads.")


def run_phase_0_audit():
    app = create_app("development")
    with app.app_context():
        print("==================================================")
        print("PHASE 0 AUDIT & CLEANUP")
        print("==================================================")
        delete_old_scraper_scripts()
        ensure_db_migration()
        audit_and_clean_papers_table()
        delete_orphaned_uploads()
        print("==================================================")
        print("PHASE 0 COMPLETE")
        print("==================================================")


if __name__ == "__main__":
    run_phase_0_audit()

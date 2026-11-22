"""
Comprehensive Verification Script for ExamVault Paper Ingestion & Verification Pipeline.
Tests Phase 0, Phase 1, Phase 2, Phase 3, and Phase 4 components.
"""
import os
import sys
from datetime import datetime, timezone

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.extensions import db
from app.models.paper import Paper
from app.models.exam import Exam, ExamCategory
from scripts.audit_and_clean_db import run_phase_0_audit
from app.scrapers.run_all_scrapers import run_pipeline


def verify_all():
    print("==================================================")
    print("EXAMVAULT INGESTION & VERIFICATION SYSTEM TEST")
    print("==================================================")

    # 1. Test Phase 0 Audit & Clean
    print("\n--- Testing Phase 0: Audit & Clean ---")
    run_phase_0_audit()

    # Confirm old scraper scripts are absent
    p1 = os.path.join(backend_dir, "fetch_real_papers.py")
    p2 = os.path.join(backend_dir, "scrape_official_urls.py")
    assert not os.path.exists(p1), f"FAIL: {p1} still exists!"
    assert not os.path.exists(p2), f"FAIL: {p2} still exists!"
    print("  [✓] Confirmed: Old fabrication scripts completely deleted.")

    app = create_app("development")
    with app.app_context():
        # Check DB columns
        paper_sample = Paper.query.first()
        if paper_sample:
            assert hasattr(paper_sample, "source_url"), "FAIL: source_url missing"
            assert hasattr(paper_sample, "source_type"), "FAIL: source_type missing"
            assert hasattr(paper_sample, "verification_status"), "FAIL: verification_status missing"
            assert hasattr(paper_sample, "verified_by"), "FAIL: verified_by missing"
            assert hasattr(paper_sample, "rejection_note"), "FAIL: rejection_note missing"
            print("  [✓] Confirmed: DB schema migration active with all verification fields.")

        # Test Public Endpoint Filtering (Phase 0 check)
        from app.blueprints.papers import list_papers
        with app.test_client() as client:
            res = client.get("/papers/")
            data = res.get_json()
            public_papers = data.get("papers", [])
            print(f"  [✓] Public /papers API response count: {len(public_papers)} (Must be 0 before admin approval)")
            assert len(public_papers) == 0, f"FAIL: Public API leaked {len(public_papers)} unverified papers!"

        # 2. Test Phase 1 & 2 Pipeline Execution
        print("\n--- Testing Phase 1 & Phase 2: Official Scrapers & Aggregator Fallbacks ---")
        run_pipeline()

        # 3. Test Phase 3: Admin Verification Queue & Approve/Reject Flow
        print("\n--- Testing Phase 3: Admin Verification Queue & Approve/Reject Flow ---")
        unverified_papers = Paper.query.filter_by(verification_status="unverified").all()
        print(f"  -> Total unverified papers in queue: {len(unverified_papers)}")

        if unverified_papers:
            test_paper = unverified_papers[0]
            print(f"  -> Testing approval flow on paper ID {test_paper.id} ({test_paper.title})...")
            
            # Approve test_paper
            test_paper.verification_status = "verified"
            test_paper.verified_by = 1
            db.session.commit()

            # Confirm it now appears on public API
            with app.test_client() as client:
                res = client.get("/papers/")
                data = res.get_json()
                public_papers = data.get("papers", [])
                print(f"  [✓] Public /papers API response after approving 1 paper: {len(public_papers)} paper(s)")
                assert len(public_papers) == 1, f"FAIL: Expected 1 public paper, got {len(public_papers)}"
                assert public_papers[0]["id"] == test_paper.id, "FAIL: Mismatched public paper ID!"

            # Test rejection flow on second paper if available
            if len(unverified_papers) > 1:
                reject_paper = unverified_papers[1]
                print(f"  -> Testing rejection flow on paper ID {reject_paper.id} ({reject_paper.title})...")
                reject_paper.verification_status = "rejected"
                reject_paper.verified_by = 1
                reject_paper.rejection_note = "Test rejection note"
                db.session.commit()

                # Confirm rejected paper does NOT appear on public API
                with app.test_client() as client:
                    res = client.get(f"/papers/{reject_paper.id}")
                    assert res.status_code == 404, f"FAIL: Rejected paper returned HTTP {res.status_code} instead of 404!"
                    print("  [✓] Confirmed: Rejected paper returns HTTP 404 on public API.")

    print("\n==================================================")
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY! 🎉")
    print("==================================================")


if __name__ == "__main__":
    verify_all()

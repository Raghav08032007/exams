"""
Quick DB status check - shows current paper counts by verification status.
"""
import os, sys
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.extensions import db
from app.models.paper import Paper
from app.models.exam import Exam, ExamCategory

app = create_app("development")
with app.app_context():
    total = Paper.query.count()
    verified = Paper.query.filter_by(verification_status='verified').count()
    unverified = Paper.query.filter_by(verification_status='unverified').count()
    rejected = Paper.query.filter_by(verification_status='rejected').count()
    no_pdf = Paper.query.filter(Paper.pdf_url == None).count()

    print(f"\n📊 DB Status:")
    print(f"  Total papers:     {total}")
    print(f"  ✓ Verified:       {verified}  (public)")
    print(f"  ⏳ Unverified:    {unverified}  (admin queue)")
    print(f"  ✗ Rejected:       {rejected}")
    print(f"  ⚠ No PDF at all:  {no_pdf}")

    if unverified == 0 and total > 0:
        print("\n  ⚠ All papers are verified or rejected - none in queue.")
    elif total == 0:
        print("\n  ⚠ No papers in DB at all - run seed.py first.")
    else:
        print(f"\n  ✅ {unverified} papers are waiting in admin queue for approval.")

    # Show a sample
    papers = Paper.query.limit(5).all()
    print("\n  Sample papers:")
    for p in papers:
        print(f"    ID={p.id} | {p.title} ({p.year}) | status={p.verification_status} | pdf={'YES' if p.pdf_url else 'NULL'}")

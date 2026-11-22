"""
Paper, Subject, and the paper_subjects association table.
"""
from datetime import datetime, timezone
from ..extensions import db

# Many-to-many association table between papers and subjects
paper_subjects = db.Table(
    "paper_subjects",
    db.Column("paper_id", db.Integer, db.ForeignKey("papers.id"), primary_key=True),
    db.Column("subject_id", db.Integer, db.ForeignKey("subjects.id"), primary_key=True),
)


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}

    def __repr__(self):
        return f"<Subject {self.name}>"


class Paper(db.Model):
    __tablename__ = "papers"

    id = db.Column(db.Integer, primary_key=True)
    exam_category_id = db.Column(
        db.Integer,
        db.ForeignKey("exam_categories.id"),
        nullable=False,
        index=True,
    )
    year = db.Column(db.SmallInteger, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(50), default="English")
    pdf_url = db.Column(db.String(500))
    file_size = db.Column(db.Integer)  # stored in bytes
    has_answer_key = db.Column(db.Boolean, default=False, nullable=False)
    answer_key_pdf_url = db.Column(db.String(500), nullable=True)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    download_count = db.Column(db.Integer, default=0, nullable=False)
    source_url = db.Column(db.String(500), nullable=True)
    source_type = db.Column(db.String(50), nullable=True)
    scraped_at = db.Column(db.DateTime, nullable=True)
    verification_status = db.Column(db.String(20), default="unverified", nullable=False, index=True)
    verified_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    rejection_note = db.Column(db.Text, nullable=True)

    subjects = db.relationship(
        "Subject",
        secondary=paper_subjects,
        lazy="subquery",
        backref=db.backref("papers", lazy=True),
    )
    bookmarks = db.relationship(
        "Bookmark",
        backref="paper",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self, include_category=False):
        data = {
            "id": self.id,
            "exam_category_id": self.exam_category_id,
            "year": self.year,
            "title": self.title,
            "language": self.language,
            "pdf_url": self.pdf_url,
            "file_size": self.file_size,
            "has_answer_key": self.has_answer_key,
            "answer_key_pdf_url": self.answer_key_pdf_url,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "download_count": self.download_count,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "verification_status": self.verification_status,
            "verified_by": self.verified_by,
            "rejection_note": self.rejection_note,
            "subjects": [s.to_dict() for s in self.subjects],
        }
        if include_category and self.category:
            data["category"] = self.category.to_dict()
            data["exam"] = self.category.exam.to_dict()
        return data

    def __repr__(self):
        return f"<Paper {self.title} ({self.year})>"

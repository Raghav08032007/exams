"""
Exam and ExamCategory models.
Each Exam (TNPSC, UPSC, JEE, NEET) has multiple categories (e.g. Group 1, Prelims, JEE Main).
"""
from ..extensions import db


class Exam(db.Model):
    __tablename__ = "exams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    accent_color_hex = db.Column(db.String(7), nullable=False)

    categories = db.relationship(
        "ExamCategory",
        backref="exam",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="ExamCategory.name",
    )

    def to_dict(self, include_categories=False):
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "accent_color_hex": self.accent_color_hex,
        }
        if include_categories:
            data["categories"] = [c.to_dict() for c in self.categories]
        return data

    def __repr__(self):
        return f"<Exam {self.name}>"


class ExamCategory(db.Model):
    __tablename__ = "exam_categories"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)

    papers = db.relationship(
        "Paper",
        backref="category",
        lazy=True,
        order_by="Paper.year.desc()",
    )

    __table_args__ = (
        db.UniqueConstraint("exam_id", "slug", name="uq_category_exam_slug"),
    )

    def to_dict(self, include_exam=False):
        data = {
            "id": self.id,
            "exam_id": self.exam_id,
            "name": self.name,
            "slug": self.slug,
        }
        if include_exam:
            data["exam"] = self.exam.to_dict()
        return data

    def __repr__(self):
        return f"<ExamCategory {self.name}>"

"""
Bookmark model — links a user to a saved paper.
Unique constraint prevents duplicate bookmarks.
"""
from datetime import datetime, timezone
from ..extensions import db


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    paper_id = db.Column(db.Integer, db.ForeignKey("papers.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("user_id", "paper_id", name="uq_user_paper_bookmark"),
    )

    def to_dict(self, include_paper=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "paper_id": self.paper_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_paper and self.paper:
            data["paper"] = self.paper.to_dict(include_category=True)
        return data

    def __repr__(self):
        return f"<Bookmark user={self.user_id} paper={self.paper_id}>"

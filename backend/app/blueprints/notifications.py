"""
/notifications blueprint — fetch notifications, unread counts, and mark as read.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..db import get_db

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/", methods=["GET"])
@jwt_required()
def get_notifications():
    """
    GET /notifications/
    Returns the latest 20 broadcast/user notifications with unread counts for regular users.
    """
    user_id = get_jwt_identity()
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        user_row = cur.fetchone()

        # Only serve paper notifications for regular users (role == 'user')
        if not user_row or user_row.get("role") in ("admin", "verifier"):
            return jsonify({"notifications": [], "unread_count": 0}), 200

        cur.execute(
            """
            SELECT n.id, n.title, n.message, n.paper_id, n.exam_slug, n.created_at,
                   (CASE WHEN r.read_at IS NOT NULL THEN 1 ELSE 0 END) AS is_read
            FROM notifications n
            LEFT JOIN user_notification_reads r ON r.notification_id = n.id AND r.user_id = %s
            WHERE n.user_id IS NULL OR n.user_id = %s
            ORDER BY n.created_at DESC
            LIMIT 20
            """,
            (user_id, user_id),
        )
        rows = cur.fetchall()

    notifications = []
    unread_count = 0
    for r in rows:
        is_read = bool(r["is_read"])
        if not is_read:
            unread_count += 1
        notifications.append(
            {
                "id": r["id"],
                "title": r["title"],
                "message": r["message"],
                "paper_id": r["paper_id"],
                "exam_slug": r["exam_slug"],
                "is_read": is_read,
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
        )

    return jsonify({"notifications": notifications, "unread_count": unread_count}), 200


@notifications_bp.route("/<int:notif_id>/read", methods=["POST"])
@jwt_required()
def mark_read(notif_id):
    """
    POST /notifications/<id>/read
    Marks a notification as read by the current user.
    """
    user_id = get_jwt_identity()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO user_notification_reads (user_id, notification_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE read_at = CURRENT_TIMESTAMP
            """,
            (user_id, notif_id),
        )
        conn.commit()

    return jsonify({"message": "Notification marked as read"}), 200

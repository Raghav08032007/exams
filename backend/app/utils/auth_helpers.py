"""
Auth helper decorators for JWT + role enforcement.
Uses raw PyMySQL queries — no ORM.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..db import get_db


def _get_user_by_id(user_id) -> dict | None:
    """Fetch a single user row by ID. Returns a dict or None."""
    if user_id is None:
        return None
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, email, role FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()


def admin_required(fn):
    """
    Decorator: requires a valid JWT AND role = 'admin'.
    Usage: @admin_required above any route function.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = _get_user_by_id(user_id)
        if not user or user["role"] != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def verifier_or_admin_required(fn):
    """
    Decorator: requires a valid JWT AND role in ('admin', 'verifier').
    Used for paper upload endpoints — both admins and verifiers can upload.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = _get_user_by_id(user_id)
        if not user or user["role"] not in ("admin", "verifier"):
            return jsonify({"error": "Admin or verifier access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def get_current_user() -> dict | None:
    """Return the current authenticated user dict, or None."""
    try:
        user_id = get_jwt_identity()
        return _get_user_by_id(user_id)
    except Exception:
        return None

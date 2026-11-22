"""
/auth blueprint — register, login, and current-user endpoints.
Uses raw PyMySQL queries — no ORM.
JWT tokens are returned on successful login/register.
"""
import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..db import get_db

auth_bp = Blueprint("auth", __name__)


def _user_to_dict(row: dict) -> dict:
    """Serialize a user DB row to a safe public dict."""
    return {
        "id":         row["id"],
        "name":       row["name"],
        "email":      row["email"],
        "role":       row["role"],
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
    }


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    POST /auth/register
    Body: { "name": str, "email": str, "password": str }
    Returns: { "message": str, "access_token": str, "user": {...} }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name:
        return jsonify({"error": "Name is required"}), 400
    if not email or "@" not in email:
        return jsonify({"error": "Valid email is required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify({"error": "An account with this email already exists"}), 409

        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, 'user')",
            (name, email, pw_hash),
        )
        user_id = cur.lastrowid
        conn.commit()

        cur.execute(
            "SELECT id, name, email, role, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        user = cur.fetchone()

    access_token = create_access_token(identity=str(user_id))
    return jsonify({
        "message":      "Account created successfully",
        "access_token": access_token,
        "user":         _user_to_dict(user),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /auth/login
    Body: { "email": str, "password": str }
    Returns: { "access_token": str, "user": {...} }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, email, password_hash, role, created_at FROM users WHERE email = %s",
            (email,),
        )
        user = cur.fetchone()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user["id"]))
    return jsonify({
        "access_token": access_token,
        "user":         _user_to_dict(user),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    GET /auth/me
    Headers: Authorization: Bearer <token>
    Returns: { "user": {...} }
    """
    user_id = get_jwt_identity()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, email, role, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        user = cur.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": _user_to_dict(user)}), 200


@auth_bp.route("/google", methods=["POST"])
def google_auth():
    """
    POST /auth/google
    Body: { "email": str, "name": str, "google_id": optional str }
    Creates or logs in a Google user, returning access_token and user dict.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip()

    if not email or "@" not in email:
        return jsonify({"error": "Valid Google email is required"}), 400

    if not name:
        name = email.split("@")[0].capitalize()

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, email, role, created_at FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            dummy_hash = bcrypt.hashpw(os.urandom(16), bcrypt.gensalt()).decode("utf-8")
            cur.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, 'user')",
                (name, email, dummy_hash),
            )
            conn.commit()
            user_id = cur.lastrowid
            cur.execute("SELECT id, name, email, role, created_at FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()

    access_token = create_access_token(identity=str(user["id"]))
    return jsonify({
        "message": "Google sign-in successful",
        "access_token": access_token,
        "user": _user_to_dict(user),
    }), 200

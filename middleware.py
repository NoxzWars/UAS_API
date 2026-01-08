from flask import request, jsonify, g, current_app
import jwt
import time
from collections import defaultdict, deque

# ========== RATE LIMIT STORAGE SEDERHANA ==========
REQUEST_LOG = defaultdict(lambda: deque())
LOGIN_LOG   = defaultdict(lambda: deque())

MAX_REQ_PER_MINUTE = 60      # 60 request/menit per user
MAX_LOGIN_PER_MIN  = 5       # 5 percobaan login/menit

# ========== ROLE PROTECTION ==========
PROTECTED_ROUTES = {
    ("POST",   "/kota"):  "admin",
    ("PATCH",  "/kota"):  "admin",
    ("DELETE", "/kota"):  "admin",

    ("POST",   "/cuaca"): "admin",
    ("PATCH",  "/cuaca"): "admin",
    ("DELETE", "/cuaca"): "admin",
}


def _check_rate_limit(log_store, key, limit, window=60):
    """Sliding window rate limit sederhana."""
    now = time.time()
    q = log_store[key]

    while q and now - q[0] > window:
        q.popleft()

    if len(q) >= limit:
        return False

    q.append(now)
    return True


def init_middleware(app):

    @app.before_request
    def global_auth_middleware():

        # ================= PRE-FLIGHT CORS =================
        if request.method == "OPTIONS":
            return jsonify({"message": "OK"}), 200

        # ================= SWAGGER / DOKUMENTASI (PUBLIC) =================
        if (
            request.path.startswith("/apidocs")
            or request.path.startswith("/apispec.json")
            or request.path.startswith("/flasgger_static")
            or request.path == "/favicon.ico"
        ):
            return

        path = request.path
        method = request.method

        # ================= LOGIN (RATE LIMIT KHUSUS) =================
        if path == "/login":
            ip = request.remote_addr or "unknown"
            if not _check_rate_limit(LOGIN_LOG, ip, MAX_LOGIN_PER_MIN):
                return jsonify({
                    "message": "Terlalu banyak percobaan login, coba beberapa saat lagi"
                }), 429
            return  # login tidak butuh JWT

        # ================= ENDPOINT PUBLIC =================
        if path in ["/register"]:
            return

        # ================= JWT AUTH =================
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"message": "Token tidak ditemukan"}), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Format token harus: Bearer <token>"}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            decoded = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
            g.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token kedaluwarsa"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token tidak valid"}), 401

        # ================= RATE LIMIT UMUM (PER USER) =================
        user_key = f"user:{g.user.get('user_id', 'unknown')}"
        if not _check_rate_limit(REQUEST_LOG, user_key, MAX_REQ_PER_MINUTE):
            return jsonify({
                "message": "Terlalu banyak permintaan, coba lagi nanti"
            }), 429

        # ================= ROLE CHECK =================
        for (m, p), role in PROTECTED_ROUTES.items():
            if method == m and path.startswith(p):
                if role == "admin" and g.user.get("role") != "admin":
                    return jsonify({
                        "message": "Hanya admin yang boleh mengakses endpoint ini"
                    }), 403
                break

        # ================= LANJUT KE ENDPOINT =================
        return

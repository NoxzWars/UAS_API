from flask import request, jsonify, g, current_app
import jwt
import time
from collections import defaultdict, deque

# ========== RATE LIMIT STORAGE SEDERHANA ==========
# key: user_id atau IP, value: deque timestamp
REQUEST_LOG = defaultdict(lambda: deque())
LOGIN_LOG   = defaultdict(lambda: deque())

MAX_REQ_PER_MINUTE = 60      # misal 60 request/menit per user/IP
MAX_LOGIN_PER_MIN  = 5       # 5 kali percobaan login/menit

# PETA ROLE: path + method → role minimal
PROTECTED_ROUTES = {
    # hanya admin boleh ubah data
    ("POST",   "/kota"):  "admin",
    ("PATCH",  "/kota"):  "admin",
    ("DELETE", "/kota"):  "admin",

    ("POST",   "/cuaca"): "admin",
    ("PATCH",  "/cuaca"): "admin",
    ("DELETE", "/cuaca"): "admin",
    # GET kota/cuaca boleh semua user yang sudah login
}


def _check_rate_limit(log_store, key, limit, window=60):
    """log_store = REQUEST_LOG atau LOGIN_LOG, sliding window sederhana."""
    now = time.time()
    q = log_store[key]

    # buang yg lebih tua dari window detik
    while q and now - q[0] > window:
        q.popleft()

    if len(q) >= limit:
        return False  # sudah melewati limit

    q.append(now)
    return True


def init_middleware(app):

    @app.before_request
    def global_auth_middleware():
        # 1) izinkan preflight CORS
        if request.method == "OPTIONS":
            return jsonify({"message": "OK"}), 200

        path = request.path
        method = request.method

        public_paths = ['/login', '/register']

        # 2) rate limit khusus endpoint login (berdasarkan IP)
        if path == "/login":
            ip = request.remote_addr or "unknown"
            if not _check_rate_limit(LOGIN_LOG, ip, MAX_LOGIN_PER_MIN):
                return jsonify({
                    "message": "Terlalu banyak percobaan login, coba beberapa saat lagi"
                }), 429
            # login tidak butuh token / role, jadi langsung return (biarkan view function jalan)
            return

        # 3) endpoint public lain (register)
        if path in public_paths:
            return

        # 4) Auth: semua endpoint lain wajib punya JWT
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization', '')
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
            else:
                return jsonify({'message': 'Gunakan format Authorization: Bearer <token>'}), 401

        if not token:
            return jsonify({'message': 'Token tidak ditemukan'}), 401

        try:
            decoded = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
            g.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token kedaluwarsa'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token tidak valid'}), 401

        # 5) rate limit umum per user (setelah sukses decode)
        user_key = f"user:{g.user.get('user_id','unknown')}"
        if not _check_rate_limit(REQUEST_LOG, user_key, MAX_REQ_PER_MINUTE):
            return jsonify({
                "message": "Terlalu banyak permintaan, coba lagi nanti"
            }), 429

        # 6) cek role berdasarkan PROTECTED_ROUTES
        required_role = None
        for (m, p), role in PROTECTED_ROUTES.items():
            if method == m and path.startswith(p):
                required_role = role
                break

        if required_role == "admin" and g.user.get("role") != "admin":
            return jsonify({'message': 'Hanya admin yang boleh mengakses endpoint ini'}), 403

        # kalau tidak ada required_role atau sudah lolos, lanjut ke endpoint
        return

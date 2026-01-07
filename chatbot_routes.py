from flask import Blueprint, request, jsonify
from db import get_db_connection

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json() or {}
    pesan = data.get("message", "").lower()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Cari nama kota di pesan user
    cursor.execute("SELECT nama_kota FROM kota")
    daftar_kota = [k["nama_kota"].lower() for k in cursor.fetchall()]

    kota_dipilih = None
    for kota in daftar_kota:
        if kota in pesan:
            kota_dipilih = kota
            break

    if kota_dipilih:
        cursor.execute("""
            SELECT k.nama_kota, c.suhu, c.kelembapan, c.kondisi
            FROM cuaca c
            JOIN kota k ON c.kota_id = k.kota_id
            WHERE LOWER(k.nama_kota) = %s
            ORDER BY c.tanggal_input DESC
            LIMIT 1
        """, (kota_dipilih,))
    else:
        cursor.execute("""
            SELECT k.nama_kota, c.suhu, c.kelembapan, c.kondisi
            FROM cuaca c
            JOIN kota k ON c.kota_id = k.kota_id
            ORDER BY c.tanggal_input DESC
            LIMIT 1
        """)

    cuaca = cursor.fetchone()
    conn.close()

    if not cuaca:
        return jsonify({"reply": "Data cuaca belum tersedia."}), 200

    # RULE BASE RESPONSE
    if "halo" in pesan or "hai" in pesan:
        reply = "Halo! Saya chatbot cuaca. Tanyakan cuaca kota tertentu."

    elif "cuaca" in pesan or "hari ini" in pesan:
        reply = (
            f"Cuaca di {cuaca['nama_kota']} saat ini {cuaca['kondisi']} "
            f"dengan suhu {cuaca['suhu']}°C dan kelembapan {cuaca['kelembapan']}%."
        )

    elif "aman" in pesan or "keluar" in pesan:
        reply = (
            "Disarankan membawa payung."
            if cuaca["kondisi"].lower().startswith("hujan")
            else "Cuaca relatif aman untuk aktivitas luar ruangan."
        )

    elif "suhu" in pesan:
        reply = f"Suhu di {cuaca['nama_kota']} sekitar {cuaca['suhu']}°C."

    else:
        reply = (
            "Saya bisa membantu informasi cuaca, suhu, "
            "atau keamanan aktivitas di luar ruangan."
        )

    return jsonify({
        "reply": reply,
        "tipe": "Rule-Based Chatbot"
    }), 200

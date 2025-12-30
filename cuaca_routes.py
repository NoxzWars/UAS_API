from flask import Blueprint, request, jsonify, g
from db import get_db_connection

cuaca_bp = Blueprint('cuaca', __name__)

@cuaca_bp.route('/cuaca', methods=['GET'])
def get_cuaca():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    nama_kota = request.args.get('kota') or None
    kondisi   = request.args.get('kondisi') or None
    suhu_min  = request.args.get('suhu_min')
    suhu_max  = request.args.get('suhu_max')

    suhu_min = float(suhu_min) if suhu_min else None
    suhu_max = float(suhu_max) if suhu_max else None

    cursor.callproc('get_cuaca_filtered', [nama_kota, kondisi, suhu_min, suhu_max])

    result = None
    for rs in cursor.stored_results():
        result = rs.fetchall()

    conn.close()

    if not result:
        return jsonify({'message': 'Data tidak ditemukan'}), 404
    return jsonify(result), 200


@cuaca_bp.route('/cuaca', methods=['POST'])
def tambah_cuaca():
    # Middleware sudah cek admin
    data = request.get_json() or {}
    required_fields = ['kota_id', 'suhu', 'kelembapan', 'kondisi']

    if not all(f in data for f in required_fields):
        return jsonify({'message': 'Parameter salah'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.callproc('add_cuaca', [
        data['kota_id'],
        g.user['user_id'],
        data['suhu'],
        data['kelembapan'],
        data['kondisi']
    ])

    conn.commit()
    conn.close()

    return jsonify({'message': 'Data cuaca berhasil ditambahkan'}), 201


@cuaca_bp.route('/cuaca/<int:cuaca_id>', methods=['PATCH'])
def ubah_cuaca(cuaca_id):
    # Middleware sudah cek admin
    data = request.get_json() or {}

    if not any(k in data for k in ['suhu', 'kelembapan', 'kondisi']):
        return jsonify({'message': 'Tidak ada data yang diubah'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cuaca WHERE cuaca_id = %s", (cuaca_id,))
    current = cursor.fetchone()

    if not current:
        conn.close()
        return jsonify({'message': 'Data tidak ditemukan'}), 404

    suhu = data.get('suhu', current['suhu'])
    kelembapan = data.get('kelembapan', current['kelembapan'])
    kondisi = data.get('kondisi', current['kondisi'])

    cursor = conn.cursor()
    cursor.callproc('update_cuaca', [cuaca_id, suhu, kelembapan, kondisi])
    conn.commit()
    conn.close()

    return jsonify({'message': 'Data cuaca berhasil diperbarui'}), 200


@cuaca_bp.route('/cuaca/<int:cuaca_id>', methods=['DELETE'])
def hapus_cuaca(cuaca_id):
    # Middleware sudah cek admin
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.callproc('delete_cuaca', [cuaca_id])
    conn.commit()
    conn.close()

    return jsonify({'message': 'Data cuaca berhasil dihapus'}), 200

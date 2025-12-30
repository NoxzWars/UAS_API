from flask import Blueprint, request, jsonify
from db import get_db_connection
import mysql.connector

kota_bp = Blueprint('kota', __name__)

@kota_bp.route('/kota', methods=['GET'])
def get_kota():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.callproc('get_kota')
    result = None
    for rs in cursor.stored_results():
        result = rs.fetchall()

    conn.close()
    return jsonify(result), 200


@kota_bp.route('/kota', methods=['POST'])
def add_kota():
    # Role admin sudah dicek oleh middleware
    data = request.get_json() or {}
    nama_kota = data.get('nama_kota')

    if not nama_kota:
        return jsonify({'message': 'Parameter salah'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.callproc('add_kota', [nama_kota])
        conn.commit()
    except mysql.connector.IntegrityError:
        conn.rollback()
        return jsonify({'message': 'Kota sudah ada'}), 400
    finally:
        conn.close()

    return jsonify({'message': f'Kota {nama_kota} berhasil ditambahkan'}), 201


@kota_bp.route('/kota/<int:kota_id>', methods=['PATCH'])
def edit_kota(kota_id):
    # Middleware sudah cek admin
    data = request.get_json() or {}
    nama_kota = data.get('nama_kota')

    if not nama_kota:
        return jsonify({'message': 'Parameter salah'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.callproc('update_kota', [kota_id, nama_kota])
    conn.commit()
    conn.close()

    return jsonify({'message': 'Nama kota berhasil diperbarui'}), 200


@kota_bp.route('/kota/<int:kota_id>', methods=['DELETE'])
def hapus_kota(kota_id):
    # Middleware sudah cek admin
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.callproc('delete_kota', [kota_id])
    conn.commit()
    conn.close()

    return jsonify({'message': 'Kota berhasil dihapus'}), 200

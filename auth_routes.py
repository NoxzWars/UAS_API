from flask import Blueprint, request, jsonify, current_app
from db import get_db_connection
import jwt
import datetime
import mysql.connector
import time


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Parameter salah'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # pakai stored procedure add_user
        cursor.callproc('add_user', [username, password])
        conn.commit()
    except mysql.connector.IntegrityError:
        conn.rollback()
        return jsonify({'message': 'Username sudah digunakan'}), 400
    finally:
        conn.close()

    return jsonify({'message': f'User {username} berhasil diregistrasi'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Parameter salah'}), 400

    time.sleep(1.5)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # panggil stored procedure login_user
    cursor.callproc('login_user', [username, password])

    user = None
    for result in cursor.stored_results():
        user = result.fetchone()

    conn.close()

    if not user:
        return jsonify({'message': 'Username atau password salah'}), 401

    token = jwt.encode({
        'user_id': user['user_id'],
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token, 'role': user['role'], 'username': user['username']}), 200

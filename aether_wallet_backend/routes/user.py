from models.user import User, users_collection
from flask import Blueprint, request, jsonify
from models.report import expense_reports_collection
from models.category import category_collection
from models.balance import balance_collection
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def signup():
    data = request.json

    user = User.find_by_email(data['email'])
    if user:
        return jsonify({'message': 'User already exists'}), 400

    token = secrets.token_hex(32)

    user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        mobile_no=data['mobile_no'],
        user_image=data['user_image'],
        token=token
    )
    user.save()

    return jsonify({'message': 'User created successfully', 'token': token}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    if 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.find_by_email(data['email'])
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not User.check_password(user['password'], data['password']):
        return jsonify({'message': 'Invalid password'}), 400

    new_token = secrets.token_hex(32)

    users_collection.update_one({'_id': user['_id']}, {'$set': {'token': new_token}})

    return jsonify({
        "message": "Login successful",
        "token": new_token
    }), 200

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400

    token = auth_header.split(" ")[1] if " " in auth_header else auth_header

    user = User.find_by_token(token)
    if not user:
        return jsonify({'message': 'Invalid token or user not found'}), 401

    return jsonify(User.to_dict(user)), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400

    token = auth_header.split(" ")[1] if " " in auth_header else auth_header

    user = User.find_by_token(token)
    if not user:
        return jsonify({'message': 'Invalid token or user not found'}), 401

    user['token'] = None
    users_collection.update_one({'_id': user['_id']}, {'$set': {'token': None}})
    
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/delete_account', methods=['DELETE'])
def delete_account():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    user = User.find_by_token(token)
    if not user:
        return jsonify({'message': 'Invalid token or user not found'}), 401

    expense_reports_collection.delete_many({'user_id': user['_id']})
    category_collection.delete_many({'user_id': user['_id']})

    balance_collection.delete_many({'user_id': user['_id']})

    users_collection.delete_one({'_id': user['_id']})

    return jsonify({'message': 'Account and all associated data deleted successfully'}), 200

@auth_bp.route('/update', methods=['PUT'])
def update_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400

    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    user = User.find_by_token(token)
    if not user:
        return jsonify({'message': 'Invalid token or user not found'}), 401

    data = request.json

    # Update fields only if provided
    updated_fields = {}
    if 'name' in data:
        updated_fields['name'] = data['name']
    if 'email' in data:
        existing_user = User.find_by_email(data['email'])
        if existing_user and str(existing_user['_id']) != str(user['_id']):
            return jsonify({'message': 'Email already in use'}), 409
        updated_fields['email'] = data['email']
    if 'password' in data:
        updated_fields['password'] = User.hash_password(data['password'])
    if 'mobile_no' in data:
        updated_fields['mobile_no'] = data['mobile_no']
    if 'user_image' in data:
        updated_fields['user_image'] = data['user_image']

    # Update the user document in MongoDB
    users_collection.update_one({'_id': user['_id']}, {'$set': updated_fields})

    return jsonify({'message': 'User updated successfully'}), 200

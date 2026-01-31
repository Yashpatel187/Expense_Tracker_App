from models import user
from models.balance import Balance, balance_collection  
from flask import Blueprint, request, jsonify
from models.user import User
from bson import ObjectId

balance_bp = Blueprint('balance', __name__)

@balance_bp.route('/balance', methods=['GET'])
def get_balance():
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400
    
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    
    user = User.find_by_token(token)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    balance = balance_collection.find_one({"user_id": user['_id']})
    
    if not balance:
        return jsonify({'message': 'Balance not found'}), 404
    
    return jsonify({'balance': balance['balance']}), 200


@balance_bp.route('/balance', methods=['POST'])
def add_balance():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400
    
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    current_user = User.find_by_token(token) 
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.json
    balance = Balance(
        balance=data['balance'],
        user_id=current_user['_id']
    )
    balance.save()
    
    return jsonify({'message': 'Balance added successfully'}), 201

@balance_bp.route('/balance', methods=['PUT'])
def update_balance():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400
    
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    user = User.find_by_token(token)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.json
    new_balance = data.get('balance')
    
    balance = balance_collection.find_one({"user_id": user['_id']})
    if not balance:
        return jsonify({'message': 'Balance not found'}), 404
    
    balance_collection.update_one(
        {"_id": balance['_id']},
        {"$set": {"balance": new_balance}}
    )
    
    return jsonify({'message': 'Balance updated successfully'}), 200

@balance_bp.route('/balance', methods=['DELETE'])
def delete_balance():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400
    
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    user = User.find_by_token(token)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    balance = balance_collection.find_one({"user_id": user['_id']})
    if not balance:
        return jsonify({'message': 'Balance not found'}), 404
    
    balance_collection.delete_one({"_id": balance['_id']})
    
    return jsonify({'message': 'Balance deleted successfully'}), 200

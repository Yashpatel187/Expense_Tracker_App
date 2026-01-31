from models import category
from models.category import Category, category_collection
from flask import Blueprint, request, jsonify
from models.user import User
from bson import ObjectId

category_bp = Blueprint('category', __name__)

@category_bp.route('/category', methods=['GET'])
def get_categories():
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400
    
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    
    user = User.find_by_token(token)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    categories = Category.find_by_user_id(user['_id'])
    
    categories_list = []
    for category in categories:
        category['_id'] = str(category['_id'])
        category['user_id'] = str(category['user_id'])
        categories_list.append(category)
    
    return jsonify({'categories': categories_list}), 200

@category_bp.route('/category', methods=['POST'])
def add_category():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400
    
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    current_user = User.find_by_token(token) 
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.json
    
    existing_category = category_collection.find_one({
        'name': data['name'], 
        'user_id': current_user['_id']
    })
    if existing_category:
        return jsonify({'message': f"Category '{data['name']}' already exists"}), 400
    
    # Proceed to create the category if it does not exist
    new_category = {
        'name': data['name'],
        'type': data['type'],
        'icon': data['icon'],
        'color': data['color'],
        'user_id': current_user['_id']
    }
    category_collection.insert_one(new_category)
    
    return jsonify({'message': 'Category added successfully'}), 201

@category_bp.route('/category', methods=['DELETE'])
def delete_category():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token missing in the Authorization header'}), 400
    
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    user = User.find_by_token(token)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.json
    category = Category.find_by_id(data['category_id'])
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    Category.delete_category(category['_id'])
    
    return jsonify({'message': 'Category deleted successfully'}), 200


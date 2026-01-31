from flask import Blueprint, request, jsonify
from models.lending_transiction import LendingTransaction
from models.user import User
from models.contact import Contact
from bson import ObjectId
from datetime import datetime

lending_bp = Blueprint('lending', __name__)

# Helper function to verify user token
def verify_token(auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    return User.find_by_token(token)

# API to Add a New Lending Transaction
@lending_bp.route('/lending', methods=['POST'])
def add_lending_transaction():
    data = request.get_json()
    auth_header = request.headers.get('Authorization')

    try:
        # Verify the user token
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Extract and validate required fields
        contact_id = data.get('contact_id')
        amount = data.get('amount')
        transaction_type = data.get('type')  # 'given' or 'received'
        description = data.get('description')

        if not all([contact_id, amount, transaction_type]) or transaction_type not in ['given', 'received']:
            return jsonify({'error': 'Contact ID, amount, and valid type ("given" or "received") are required'}), 400

        # Check if contact exists
        contact = Contact.find_by_id(contact_id)
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404

        # Create and save the lending transaction
        transaction = LendingTransaction(
            user_id=str(user['_id']),
            contact_id=contact_id,
            amount=float(amount),
            type=transaction_type,
            description=description
        )
        transaction_id = transaction.save()

        return jsonify({
            'message': 'Lending transaction added successfully, and contact balance updated!',
            'transaction_id': transaction_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API to Get All Lending Transactions for the Authenticated User
@lending_bp.route('/lending-transactions', methods=['POST'])
def get_transactions_by_contact():
    auth_header = request.headers.get('Authorization')
    contact_id = request.headers.get('Contact-ID')  # Extract contact ID from headers

    try:
        # Verify the token
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Validate contact ID
        if not contact_id:
            return jsonify({'error': 'Missing Contact-ID in header'}), 400

        # Fetch transactions for the specified contact
        transactions = LendingTransaction.find_by_contact(contact_id)

        # Convert transactions to a list of dictionaries
        transactions_list = [
            LendingTransaction.to_dict(transaction)
            for transaction in transactions
        ]

        # Return empty list if no transactions are found
        return jsonify({'transactions': transactions_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API to Update a Lending Transaction
@lending_bp.route('/lending/<transaction_id>', methods=['PUT'])
def update_lending_transaction(transaction_id):
    data = request.get_json()
    auth_header = request.headers.get('Authorization')

    try:
        # Verify the user token
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Find the transaction by ID
        transaction = LendingTransaction.find_by_id(transaction_id)
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404

        # Check if the user is the owner of the transaction
        if str(transaction['user_id']) != str(user['_id']):
            return jsonify({'error': 'Unauthorized: You cannot update this transaction'}), 403

        # Update fields
        update_data = {
            "contact_id": ObjectId(data.get('contact_id', transaction['contact_id'])),
            "amount": float(data.get('amount', transaction['amount'])),
            "type": data.get('type', transaction['type']),
            "description": data.get('description', transaction['description']),
            "status": data.get('status', transaction['status']),
            "due_date": data.get('due_date', transaction.get('due_date')),
            "settled_date": data.get('settled_date', transaction.get('settled_date')),
            "bill_image": data.get('bill_image', transaction.get('bill_image'))
        }

        LendingTransaction.update(transaction_id, update_data)

        return jsonify({'message': 'Lending transaction updated successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

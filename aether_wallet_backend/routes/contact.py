from flask import Blueprint, request, jsonify
from models.contact import Contact, contacts_collection
from models.user import User
from bson import ObjectId
from models.lending_transiction import LendingTransaction

contact_bp = Blueprint('contact', __name__)

def verify_token(auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        print("Missing or invalid token")
        return None
    token = auth_header.split(" ")[1]
    user = User.find_by_token(token)
    if not user:
        print("Invalid token")
    return user


@contact_bp.route('/contact', methods=['POST'])
def add_contact():
    data = request.get_json()
    auth_header = request.headers.get('Authorization')

    try:
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        name = data.get('name')
        mobile_no = data.get('mobile_no')
        user_image = data.get('user_image')

        if not all([name, mobile_no, user_image]):
            return jsonify({'error': 'Name, mobile number, and user image are required'}), 400

        existing_contact = contacts_collection.find_one({
            "user_id": str(user['_id']),
            "mobile_no": mobile_no
        })

        if existing_contact:
            return jsonify({'error': 'A contact with this mobile number already exists'}), 409

        # Add the contact to the database with the correct user_id
        contact = Contact(
            user_id=str(user['_id']),
            name=name,
            mobile_no=mobile_no,
            user_image=user_image
        )
        contact.save()

        return jsonify({
            'message': 'Contact added successfully!',
            'contact_id': str(contact._id)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contact_bp.route('/contacts', methods=['GET'])
def get_all_contacts():
    auth_header = request.headers.get('Authorization')

    try:
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Log the user_id for debugging
        print(f"Authenticated user_id: {user['_id']}")

        # Query for contacts using ObjectId to match user_id
        contacts = contacts_collection.find({"user_id": ObjectId(user['_id'])})

        # Convert cursor to list
        contacts_list = list(contacts)


        contact_list = [
            {
                'id': str(contact['_id']),
                'name': contact.get('name'),
                'mobile_no': contact.get('mobile_no'),
                'amount': contact.get('net_balance'),
                'user_image': contact.get('user_image'),
                'created_at': contact.get('created_at')
            }
            for contact in contacts_list
        ]

        # Always return the contacts list, even if it's empty
        return jsonify({'contacts': contact_list}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API to Update a Contact
@contact_bp.route('/contact/<contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data = request.get_json()
    auth_header = request.headers.get('Authorization')

    try:
        # Verify user token
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Find the contact by ID, ensure the contact exists and check its user_id
        contact = contacts_collection.find_one({"_id": ObjectId(contact_id)})
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404

        # Check if the user is the owner of the contact
        if str(contact['user_id']) != str(user['_id']):
            return jsonify({'error': 'Unauthorized: You cannot update this contact'}), 403

        # Update fields with data from the request body
        name = data.get('name', contact['name'])
        mobile_no = data.get('mobile_no', contact['mobile_no'])
        user_image = data.get('user_image', contact.get('user_image'))

        # Update the contact in the database
        contacts_collection.update_one(
            {"_id": ObjectId(contact_id)},
            {"$set": {"name": name, "mobile_no": mobile_no, "user_image": user_image}}
        )

        return jsonify({
            'message': 'Contact updated successfully!',
            'contact': {
                'id': contact_id,
                'name': name,
                'mobile_no': mobile_no,
                'user_image': user_image
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API to Delete a Contact
# API to Delete a Contact and all associated transactions
@contact_bp.route('/contact/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    auth_header = request.headers.get('Authorization')

    try:
        # Verify user token
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Find the contact by ID
        contact = contacts_collection.find_one({"_id": ObjectId(contact_id)})
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404

        # Check if the user is the owner of the contact
        if str(contact['user_id']) != str(user['_id']):
            return jsonify({'error': 'Unauthorized: You cannot delete this contact'}), 403
        LendingTransaction.delete_by_contact(contact_id)

        # Delete the contact from the collection
        contacts_collection.delete_one({"_id": ObjectId(contact_id)})

        return jsonify({'message': 'Contact and associated transactions deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@contact_bp.route('/contact', methods=['GET'])
def get_contact_by_id():
    auth_header = request.headers.get('Authorization')
    contact_id = request.headers.get('Contact-ID')  # Extract contact ID from headers

    try:
        # Verify the token
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Validate the Contact-ID
        if not contact_id:
            return jsonify({'error': 'Missing Contact-ID in header'}), 400

        # Fetch the contact using Contact-ID
        contact = contacts_collection.find_one({"_id": ObjectId(contact_id)})

        if not contact:
            return jsonify({'error': 'Contact not found'}), 404

        # Check if the contact belongs to the authenticated user
        if str(contact['user_id']) != str(user['_id']):
            return jsonify({'error': 'Unauthorized: You cannot access this contact'}), 403

        # Convert the contact to a dictionary
        contact_data = {
            'id': str(contact['_id']),
            'name': contact.get('name'),
            'mobile_no': contact.get('mobile_no'),
            'net_balance': contact.get('net_balance', 0.0),  # Default to 0.0 if not set
            'created_at': contact.get('created_at'),
            'user_image': contact.get('user_image'),
        }

        return jsonify({'contact': contact_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

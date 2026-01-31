from datetime import datetime
from bson.objectid import ObjectId
from database import db
from decimal import Decimal

# Use collections from the database
contacts_collection = db['contacts']

class Contact:
    def __init__(self, user_id=None, name=None, mobile_no=None, user_image=None):
        self._id = None
        self.user_id = user_id
        self.name = name
        self.mobile_no = mobile_no
        self.user_image = user_image
        self.net_balance = Decimal('0.00')
        self.created_at = datetime.now()

    def save(self):
        result = contacts_collection.insert_one({
            'user_id': ObjectId(self.user_id),
            'name': self.name,
            'mobile_no': self.mobile_no,
            'user_image': self.user_image,
            'net_balance': float(self.net_balance),
            'created_at': self.created_at
        })
        self._id = result.inserted_id
        return str(result.inserted_id)

    @staticmethod
    def find_by_id(contact_id):
        return contacts_collection.find_one({"_id": ObjectId(contact_id)})

    @staticmethod
    def find_by_user_mobile(user_id, mobile_no):
        return contacts_collection.find_one({
            "user_id": ObjectId(user_id),
            "mobile_no": mobile_no
        })

    @staticmethod
    def find_all_by_user(user_id, search_query=None):
        query = {"user_id": ObjectId(user_id)}
        if search_query:
            query["$or"] = [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"mobile_no": {"$regex": search_query, "$options": "i"}}
            ]
        return contacts_collection.find(query).sort("name", 1)

    @staticmethod
    def update(contact_id, update_data):
        return contacts_collection.update_one(
            {"_id": ObjectId(contact_id)},
            {"$set": update_data}
        )

    @staticmethod
    def delete(contact_id):
        return contacts_collection.delete_one({"_id": ObjectId(contact_id)})

    @staticmethod
    def update_balance(contact_id, amount):
        return contacts_collection.update_one(
            {"_id": ObjectId(contact_id)},
            {"$inc": {"net_balance": float(amount)}}
        )

    @staticmethod
    def to_dict(contact):
        return {
            'id': str(contact['_id']),
            'user_id': str(contact['user_id']),
            'name': contact['name'],
            'mobile_no': contact['mobile_no'],
            'user_image': contact['user_image'],
            'net_balance': float(contact['net_balance']),
            'created_at': contact['created_at']
        }
from datetime import datetime
from bson.objectid import ObjectId
from database import db
from models.contact import Contact

lending_transactions_collection = db['lending_transactions']

class LendingTransaction:
    def __init__(self, user_id=None, contact_id=None, amount=None, type=None, description=None):
        self._id = None
        self.user_id = user_id
        self.contact_id = contact_id
        self.amount = amount
        self.type = type
        self.description = description
        self.date = datetime.now()
        self.created_at = datetime.now()

    def save(self):
        result = lending_transactions_collection.insert_one({
            'user_id': ObjectId(self.user_id),
            'contact_id': ObjectId(self.contact_id),
            'amount': float(self.amount),
            'type': self.type,
            'description': self.description,
            'date': self.date,
            'created_at': self.created_at,
        })
        self._id = result.inserted_id

        # Update contact balance
        amount = float(self.amount) if self.type == 'given' else -float(self.amount)
        Contact.update_balance(self.contact_id, amount)

        return str(result.inserted_id)

    @staticmethod
    def find_by_id(transaction_id):
        return lending_transactions_collection.find_one({"_id": ObjectId(transaction_id)})
    
    @staticmethod
    def find_by_user(user_id, status=None):
        query = {"user_id": ObjectId(user_id)}
        if status:  # Add status to the query only if it's provided
            query["status"] = status
        return lending_transactions_collection.find(query).sort("date", -1)


    @staticmethod
    def find_by_contact(contact_id):
        return lending_transactions_collection.find(
            {"contact_id": ObjectId(contact_id)}
        ).sort("date", -1)
    
    @staticmethod
    def delete_by_contact(contact_id):
        lending_transactions_collection.delete_many({"contact_id": ObjectId(contact_id)})

    @staticmethod
    def find_by_user(user_id):
        return lending_transactions_collection.find({"user_id": ObjectId(user_id)}).sort("date", -1)

    @staticmethod
    def update(transaction_id, update_data):
        return lending_transactions_collection.update_one(
            {"_id": ObjectId(transaction_id)},
            {"$set": update_data}
        )

    @staticmethod
    def delete(transaction_id):
        transaction = LendingTransaction.find_by_id(transaction_id)
        if transaction:
            # Reverse the balance effect
            amount = -float(transaction['amount']) if transaction['type'] == 'given' else float(transaction['amount'])
            Contact.update_balance(transaction['contact_id'], amount)

            return lending_transactions_collection.delete_one({"_id": ObjectId(transaction_id)})
        return None

    @staticmethod
    def to_dict(transaction):
        return {
            'id': str(transaction['_id']),
            'user_id': str(transaction['user_id']),
            'contact_id': str(transaction['contact_id']),
            'amount': float(transaction['amount']),
            'type': transaction['type'],
            'description': transaction['description'],
            'date': transaction['date'],
            'created_at': transaction['created_at'],
        }

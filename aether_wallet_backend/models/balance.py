from database import db

balance_collection = db['balance']

class Balance:
    def __init__(self, balance, user_id):
        self.balance = balance
        self.user_id = user_id

    def save(self):
        balance_collection.insert_one({
            "balance": self.balance,
            "user_id": self.user_id
        })

    @staticmethod
    def find_by_user_id(user_id):
        return balance_collection.find_one({"user_id": user_id})
    
    def update_balance(self, balance):
        balance_collection.update_one({"_id": self._id}, {"$set": {"balance": balance}})

    @staticmethod
    def to_dict(self):
        return {
            "balance": self.balance,
            "user_id": str(self.user_id)
        }
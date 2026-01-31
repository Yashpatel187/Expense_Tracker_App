from database import db
from bson.objectid import ObjectId

category_collection = db['category']

class Category:
    def __init__(self, name, type, icon, color, user_id):
        self.name = name
        self.type = type
        self.icon = icon
        self.color = color
        self.user_id = user_id

    def save(self):
        category_collection.insert_one({
            "name": self.name,
            "type": self.type,
            "icon": self.icon,
            "color": self.color,
            "user_id": self.user_id
        })

    @staticmethod
    def find_by_user_id(user_id):
        return category_collection.find({"user_id": user_id})
    
    @staticmethod
    def find_by_id(category_id):
        return category_collection.find_one({'_id': ObjectId(category_id)})

    
    def update_category(self, name, type, icon, color):
        category_collection.update_one({"_id": self._id}, {"$set": {"name": name, "type": type, "icon": icon, "color": color}})

    @staticmethod
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "icon": self.icon,
            "color": self.color,
            "user_id": str(self.user_id)
        }
    
    @staticmethod
    def delete_category(category_id):
        category_collection.delete_one({"_id": category_id})

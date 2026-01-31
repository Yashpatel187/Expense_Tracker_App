from datetime import datetime
from bson.objectid import ObjectId
from database import db
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash

# Use the 'users' collection from the database
users_collection = db['users']

class User:

    def __init__(self, name=None, email=None, password=None, mobile_no=None, user_image=None, token=None):
        self._id = None
        self.name = name
        self.email = email
        self.password = password
        self.mobile_no = mobile_no
        self.user_image = user_image
        self.token = token
        self.created_at = datetime.utcnow()

    def save(self):
        hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())
        result = users_collection.insert_one({
            'name': self.name,
            'email': self.email,
            'password': hashed_password,
            'mobile_no': self.mobile_no,
            'user_image': self.user_image,
            'token': self.token,
            'created_at': self.created_at
        })
        self._id = result.inserted_id
        return str(result.inserted_id)

    @staticmethod
    def find_by_email(email):
        return users_collection.find_one({"email": email})
    
    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    @staticmethod
    def find_by_id(user_id):
        return users_collection.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def find_by_token(token):
        return users_collection.find_one({"token": token})

    @staticmethod
    def check_password(stored_password, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

    def update_token(self, token):
        users_collection.update_one({"_id": ObjectId(self._id)}, {"$set": {"token": token}})

    @staticmethod
    def to_dict(user):
        return {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'mobile_no': user['mobile_no'],
            'user_image': user['user_image'],
            'created_at': user['created_at'],
            'token': user['token']
        }

from pymongo import MongoClient

# Replace <your_connection_string> with your MongoDB Atlas connection string
client = MongoClient("mongodb+srv://dev:dev@cluster0.mgy7e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client['AetherWallet']
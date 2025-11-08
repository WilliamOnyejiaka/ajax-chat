from bson import ObjectId
from src.config.db import db

class UserRepository:

    def __init__(self):
        self.collection = db.get_collection("users")

    def create_user(self, data: dict):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def get_user(self, user_id: str):
        user = self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def list_users(self):
        users = []
        for doc in self.collection.find({}):
            doc["_id"] = str(doc["_id"])
            users.append(doc)
        return users

    def create_indexes(self):
        self.collection.create_index("email", unique=True)
        # self.collection.create_index([("book_id", 1)])

from bson import ObjectId
from src.config.db import db

class ChatRepository:

    def __init__(self):
        self.collection = db.get_collection("chats")

    def create_chat(self, data: dict):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def chat_with_messages(self,chat_id: str):
        pipeline = [
            {"$match": {"_id": ObjectId(chat_id)}},  # select the chat
            {
                "$lookup": {
                    "from": "messages",  # collection to join
                    "localField": "_id",  # field in chats
                    "foreignField": "chat_id",  # field in messages
                    "as": "messages"  # output array
                }
            },
            {"$unwind": {"path": "$messages", "preserveNullAndEmptyArrays": True}},
            # {"$sort": {"messages.created_at": -1}},  # most recent first
            {"$group": {
                "_id": "$_id",
                "title": {"$first": "$title"},
                "created_at": {"$first": "$created_at"},
                "updated_at": {"$first": "$updated_at"},
                "messages": {"$push": "$messages"}
            }}
        ]

        result = list(self.collection.aggregate(pipeline))
        return result

    def create_indexes(self):
        self.collection.create_index([("user_id", 1)])

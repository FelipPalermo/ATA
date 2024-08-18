from pymongo.mongo_client import MongoClient
from datetime import datetime
import os 
import certifi 

Uri = os.getenv("MongoDB_URI")
Client = MongoClient(Uri, tlsCAFile=certifi.where())["Alan_the_Alarm"]


@staticmethod
def insert_timer(Discord_ID, date_to_send, message) : 

    Discord_ID = str(Discord_ID)

    now = datetime.now()
    collection_name = Discord_ID
    document = {
        "Discord_ID": Discord_ID,
        "Hour_to_Send": date_to_send,
        "Created_At": now.strftime("%d-%m-%Y-%H:%M"),
        "Message": message,
        "Mailed": False
    }
    
    if collection_name in Client.list_collection_names():
        result = Client[collection_name].insert_one(document)
    else:
        result = Client["An_Timers"].insert_one(document)
    
    return result.inserted_id

a = insert_timer("350364616657862679", "2024-08-18T17:00:10.824+00:00", "Message")
b = Client["An_Timers"].find_one({
    "_id" : a
})

print(b)
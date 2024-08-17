import certifi
from pymongo.mongo_client import MongoClient
from datetime import datetime
import os

# ----- /// MongoDB Connector /// -----
Uri = os.getenv("MongoDB_URI")
Client = MongoClient(Uri, tlsCAFile=certifi.where())["Alan_the_Timer"]

now = datetime.now()

class mongo_ATA :  

    @staticmethod
    def insert_timer(Discord_ID, date_to_send, message) : 

        if str(Discord_ID) in Client.list_collection_names() : 

            Client[str(Discord_ID)].insert_one({
                "Discord_ID" : Discord_ID,
                "Date_to_send" : date_to_send, 
                "Created_At" : now.strftime("%d-%m-%Y-%H:%M"),
                "Message" : message,
                "Mailed" : False }) 
        else : 
            Client["Anonymous_Timers"].insert_one({
                "Discord_ID" : Discord_ID,
                "Date_to_send" : date_to_send, 
                "Created_At" : now.strftime("%d-%m-%Y-%H:%M"),
                "Message" : message,
                "Mailed" : False }) 

    @staticmethod
    def create_profile(Discord_ID, email) : 

        Signed_Users = Client.list_collection_names()

        if str(Discord_ID) not in Signed_Users : 

            Client[str(Discord_ID)].insert_one({
                "_id" : Discord_ID,
                "Email" : email
            })
            
        else : 

            #TODO colocar para o bot falar que já existe um registro para esse ID de discord
            print("Esse registro já existe")

    @staticmethod
    def Change_Email(Discord_ID, email) : 
        if str(Discord_ID) in Client.list_collection_names() : 
            Client[str(Discord_ID)].update_one({"_id" : Discord_ID}, {"$set" : {"Email" : email}} )

    @staticmethod
    def Anonymous_send_not_mailed() -> None : 
        
        db = Client
        Anonymous_documents = db["Anonymous_Timers"].find()

        for document in Anonymous_documents:
            if not document.get("Mailed", True):
                db["Anonymous_Timers"].delete_one({"_id": document["_id"]})

    @staticmethod
    def Signed_send_not_mailed() -> None : 
        
        db = Client
        Signed_Users = db.list_collection_names()
        
        for collection_name in Signed_Users: 
            
            if collection_name != "Anonymous_Timers":
                signed_users_document = db[collection_name].find()
                
                for document in signed_users_document: 
                    
                    if not document.get("Mailed", True): 
                        db[collection_name].delete_one({"_id": document["_id"]})



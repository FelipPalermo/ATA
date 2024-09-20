from xml.dom.minidom import Document
from more_itertools import last
from pymongo.mongo_client import MongoClient
from datetime import datetime
import os
from typing import Union
from datetime import timedelta
from message_cryptography import  Cryptography
import certifi
import ssl

# ----- /// MongoDB Connector /// -----
Uri = os.getenv("MONGODB_URI")
ssl_context = ssl.create_default_context(cafile=certifi.where())
Client = MongoClient(Uri, tlsCAFile=certifi.where())["Alan_the_Alarm"] 

now = datetime.now()

class mongo_ATA :  

    @staticmethod
    def insert_timer(Discord_ID, date_to_send, message) : 

        Discord_ID = str(Discord_ID)

        now = datetime.now()
        collection_name = Discord_ID
        document = {
            "Discord_ID": Discord_ID,
            "Date_to_Send": date_to_send,
            "Created_At": now.strftime("%d-%m-%Y %H:%M"),
            "Message": Cryptography.encrypt(message),
            "Mailed": False,
            "Late" : "" 
        }
        
        if collection_name in Client.list_collection_names():
            result = Client[collection_name].insert_one(document)
        else:
            result = Client["An_Timers"].insert_one(document)
        
        return result.inserted_id
        
    @staticmethod
    def create_profile(Discord_ID, email) : 

        Discord_ID = str(Discord_ID)
        Signed_Users = Client.list_collection_names()

        if Discord_ID not in Signed_Users : 

            Client[Discord_ID].insert_one({
                "Discord_ID" : Discord_ID,
                "Email" : email
            })
            
        else : 
            #TODO colocar para o bot falar que já existe um registro para esse ID de discord
            print("Esse registro já existe")

    @staticmethod
    def Change_Email(Discord_ID, email) : 
        Discord_ID = str(Discord_ID)
        if Discord_ID in Client.list_collection_names() : 
            Client[Discord_ID].update_one({"_id" : Discord_ID}, {"$set" : {"Email" : email}} )

    @staticmethod
    def Anonymous_send_not_mailed() -> None : 
        
        db = Client
        Anonymous_documents = db["An_Timers"].find()

        for document in Anonymous_documents:
            if not document.get("Mailed", True):
                db["An_Timers"].delete_one({"_id": document["_id"]})

    @staticmethod
    def Signed_send_not_mailed() -> None : 
       # SIGNED = PEOPLE WHO HAVE EMAIL IN THE BOT 

        db = Client
        Signed_Users = db.list_collection_names()
        
        for collection_name in Signed_Users: 
            
            if collection_name != "An_Timers":
                signed_users_document = db[collection_name].find()
                
                for document in signed_users_document: 
                    
                    if not document.get("Mailed", True): 
                        db[collection_name].delete_one({"_id": document["_id"]})


    @staticmethod
    def Return_Time_to_Send(Discord_ID : str, Document_ID) -> str : # type: ignore  

        Discord_ID = str(Discord_ID)

        last_message = Client["An_Timers"].find_one({
                "_id" : Document_ID,
                "Mailed" : False     
            })

        try : 
            if last_message : 

                last_message = str(last_message["Date_to_Send"])
                return last_message # type: ignore

        except Exception as err :  

            Client["Errors"].insert_one({
                "Error_Code" : 2, 
                "Error" : err,
                "Discord_ID" : Discord_ID,
            })

            raise TypeError("Could not complete transaction due incorrect input")

        # Implementar verificacao de tipo junto com a classeu
        # para nao interromper o tempo de execucao 
        """
        a = Return_Time_to_Send("350364616657862679") if isinstance(Return_Time_to_Send("350364616657862679"), dict) else None  
        if isinstance(a, dict) : 
            ...
        else : 
            print("Nao")
        """
        # ----- /// -----


    @staticmethod
    def true_mailed(Discord_ID, time, Document_ID) -> Union[dict, None]:  # type: ignore
        Discord_ID = str(Discord_ID)
        send_at = None  # Inicializando send_at para garantir que ela existe

        try:
            send_at_str = mongo_ATA.Return_Time_to_Send(Discord_ID, Document_ID)  # type: ignore

            if send_at_str:
                send_at = datetime.strptime(send_at_str, "%d/%m/%Y %H:%M:%S")
            else:
                raise ValueError("No valid send time found for this document.")

            last_message = Client["An_Timers"].find_one({
                "_id": Document_ID,
                "Discord_ID": Discord_ID,
                "Mailed": False
            })

            if last_message:
                current_time = datetime.now()
                treshold = timedelta(seconds=5)

                if not (send_at - treshold <= current_time <= send_at + treshold):
                    Client["An_Timers"].update_one(
                        {"_id": Document_ID},
                        {"$set": {"Mailed": True, "Late": False}}
                    )
                else:
                    Client["Errors"].insert_one({
                        "Error_Code": 3,
                        "Error": "Too late",
                        "Discord_ID": Discord_ID,
                        "Late": datetime.strftime(send_at, "%d/%m/%Y %H:%M:%S")}  # type: ignore
                    )

                    Client["An_Timers"].update_one(
                        {"_id": Document_ID, "Discord_ID": Discord_ID},
                        {"$set": {"Mailed": True, "Late": datetime.strftime(send_at, "%d/%m/%Y %H:%M:%S")}}  # type: ignore
                    )

        except ValueError as ve:
            print(f"ValueError: {ve}")
            Client["Errors"].insert_one({
                "Error_Code": 2,
                "Error": str(ve),
                "Discord_ID": Discord_ID,
                "Late": datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Registro do erro com hora atual
            })

        except Exception as e:
            print(f"Error: {e}")
            Client["Errors"].insert_one({
                "Error_Code": "Unknown",
                "Error": str(e),
                "Error_on": Document_ID,
                "Discord_ID": Discord_ID,
                "Late": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}  # type: ignore
            )

        return None

    @staticmethod
    def active_alarms(Discord_ID) : 
        alarms = Client["An_Timers"].find({
        "Discord_ID" :str(Discord_ID),
        "Mailed" : False 
        })

        return alarms

    @staticmethod
    def active_anonymous_alarms() : 
        alarms = Client["An_Timers"].find({
        "Mailed" : False 
        })

        return alarms

    
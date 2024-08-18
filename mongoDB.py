import certifi
from pymongo.mongo_client import MongoClient
from datetime import datetime
import os
from typing import Union


# ----- /// MongoDB Connector /// -----
Uri = os.getenv("MongoDB_URI")
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
            "Message": message,
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
                "_id" : Discord_ID,
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
    def Return_Time_to_Send(Discord_ID : str, Document_ID) -> Union[dict, None] : # type: ignore  

        Discord_ID = str(Discord_ID)

        last_message = Client["An_Timers"].find_one({
                "_id" : Document_ID,
                "Mailed" : False     
            })

        try : 
            print("dentro do try return_time")
            if last_message : 

                print("last message exist")
                last_message = str(last_message["Date_to_Send"])
                last_message = datetime.strptime(last_message, "%d/%m %H:%M:%S")

                print(last_message)

                return last_message # type: ignore

            else : 

                print("No Messages to Mail from this ID")
                Client["Errors"].insert_one({
                    "Discord_ID" : Discord_ID,
                    "Error_Code" : 1,
                    "Error" : "No messages to mail from this Discord_ID"
                })

                return None 

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
    def true_mailed(Discord_ID, time, Document_ID) -> Union[dict, None] : # type: ignore  

        Discord_ID = str(Discord_ID)

        try : 
            print("Dentro do try")

            send_at = mongo_ATA.Return_Time_to_Send(Discord_ID, Document_ID) # type: ignore
            print('\n\n\n\n\n\n\n ----------------')

            print(type(send_at))

            print(send_at)

            last_message = Client["An_Timers"].find_one({
                    "_id" : Document_ID, 
                    "Discord_ID" : Discord_ID,
                    "Mailed" : False
                    })

            print("last message")#  

            if last_message : 

                print("Dentro do IF last_message") 

                time = datetime.now()
                time = datetime.strftime(time, "%d/%m %H:%M:%S")
                 
                if str(send_at) != time :   

                    Client["Errors"].insert_one({
                        "Error_Code" : 3, 
                        "Error" : "Too late" ,
                        "Discord_ID" : Discord_ID,
                        "Late" : datetime.strftime(send_at, "%d/%m %H:%M:%S")}  # type: ignore
                    )

                    Client["An_Timers"].update_one(
                        {"_id" : Document_ID,
                         "Discord_ID" : Discord_ID}, 

                        {"$set" : {"Mailed" : True, 
                                   "Late" : datetime.strftime(send_at, "%d/%m %H:%M:%S")}  # type: ignore
                                })

                    print("if send_at") 

                else : 
                    print("Else") 
                    Client["An_Timers"].update_one(
                        {"_id" : Document_ID}, 
                        {"$set" : {"Mailed" : True, 
                                  "Late" : "False"}
                                })
                
                    print("Documento atualizado")

        except Exception as e: 
            print(f"Error : {e}")
            Client["Errors"].insert_one({
                        "Error_Code" : "Unknow", 
                        "Error" : e,
                        "Error_on" : Document_ID,
                        "Discord_ID" : Discord_ID,
                        "Late" : datetime.strftime(send_at, "%d/%m %H:%M:%S")} # type: ignore
                    )

            return None 

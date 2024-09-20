from xml.dom.minidom import Document
import bson
from more_itertools import last
from pymongo.mongo_client import MongoClient
from datetime import datetime
import os
from typing import Union
from datetime import timedelta
from message_cryptography import  Cryptography
import certifi
import ssl
import pytz

# ----- /// MongoDB Connector /// -----
Uri = os.getenv("MONGODB_URI")
ssl_context = ssl.create_default_context(cafile=certifi.where())
Client = MongoClient(Uri, tlsCAFile=certifi.where())["Alan_the_Alarm"] 

now = datetime.now()

# banco de alarmes ["Alarms"] 
# banco de registros ["User_Info"]


class mongo_ATA :  

    # ----- /// Create User /// -----
    @staticmethod
    def create_user(Discord_ID : str, GMT : str) -> Union[None, str]  : 

       if Client["User_Info"].find_one({
           "Discord_ID" : Discord_ID
       }) is None : 

        document = {
            "Discord_ID" : Discord_ID,
            "GMT" : GMT, 
            "Alarm_Sound" : ""
        } 

        Client["User_Info"].insert_one(document)

       else : 
            return "Already registred"


    # ----- /// Insert timer /// -----  
    @staticmethod
    def insert_timer(Discord_ID, date_to_send, message) : 

        Discord_ID = str(Discord_ID)
        now = datetime.now()

        document = {
            "Discord_ID": Discord_ID,
            "Date_to_Send": date_to_send,
            "Created_At": now.strftime("%d-%m-%Y %H:%M"),
            "GMT" : None,
            "Message": Cryptography.encrypt(message),
            "Mailed": False,
            "Late" : "" 
        }
        
        result = Client["Alarms"].insert_one(document)
        return result.inserted_id
        

    @staticmethod
    def Anonymous_send_not_mailed() -> None : 
        
        db = Client
        Anonymous_documents = db["An_Timers"].find()

        for document in Anonymous_documents:
            if not document.get("Mailed", True):
                db["An_Timers"].delete_one({"_id": document["_id"]})


    # ----- /// Return time to send /// ----
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


    # ----- /// True mailed /// -----
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

    # ----- /// Active alarms /// -----
    @staticmethod
    def active_alarms(Discord_ID) : 
        alarms = Client["An_Timers"].find({
        "Discord_ID" :str(Discord_ID),
        "Mailed" : False 
        })

        return alarms


    @staticmethod
    def Return_GMT(Discord_ID) -> str : 

        try : 
            register = Client["User_Info"].find_one({
                "Discord_ID" : str(Discord_ID)
            })

            if register is not None :  
                return register["GMT"]

            else :
                print("This register does not have an GMT") 
                return "None" 

        except Exception as e : 
            print(e)
            return "None"
    
    @staticmethod
    def Now_GMT(GMT : str) : 

        gmtdict = {
            "GMT+0": pytz.timezone("Etc/GMT"),
            "GMT+1": pytz.timezone("Etc/GMT-1"),
            "GMT+2": pytz.timezone("Etc/GMT-2"),
            "GMT+3": pytz.timezone("Etc/GMT-3"),
            "GMT+4": pytz.timezone("Etc/GMT-4"),
            "GMT+5": pytz.timezone("Etc/GMT-5"),
            "GMT+6": pytz.timezone("Etc/GMT-6"),
            "GMT+7": pytz.timezone("Etc/GMT-7"),
            "GMT+8": pytz.timezone("Etc/GMT-8"),
            "GMT+9": pytz.timezone("Etc/GMT-9"),
            "GMT+10": pytz.timezone("Etc/GMT-10"),
            "GMT+11": pytz.timezone("Etc/GMT-11"),
            "GMT+12": pytz.timezone("Etc/GMT-12"),
            "GMT-1": pytz.timezone("Etc/GMT+1"),
            "GMT-2": pytz.timezone("Etc/GMT+2"),
            "GMT-3": pytz.timezone("Etc/GMT+3"),
            "GMT-4": pytz.timezone("Etc/GMT+4"),
            "GMT-5": pytz.timezone("Etc/GMT+5"),
            "GMT-6": pytz.timezone("Etc/GMT+6"),
            "GMT-7": pytz.timezone("Etc/GMT+7"),
            "GMT-8": pytz.timezone("Etc/GMT+8"),
            "GMT-9": pytz.timezone("Etc/GMT+9"),
            "GMT-10": pytz.timezone("Etc/GMT+10"),
            "GMT-11": pytz.timezone("Etc/GMT+11"),
            "GMT-12": pytz.timezone("Etc/GMT+12"),
        }

        return datetime.now(gmtdict[GMT])
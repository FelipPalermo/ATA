from pymongo.mongo_client import MongoClient
from datetime import datetime
import os
from typing import Union
from datetime import timedelta
from message_cryptography import  Cryptography
import certifi
import ssl
import pytz
import re 

# ----- /// MongoDB Connector /// -----
Uri = os.getenv("MONGODB_URI")
ssl_context = ssl.create_default_context(cafile=certifi.where())
Client = MongoClient(Uri, tlsCAFile=certifi.where())["Alan_the_Alarm"] 

now = datetime.now()

class mongo_ATA :  

    # ----- /// Create User /// -----
    @staticmethod
    def create_user(Discord_ID : str, GMT : str) -> Union[None, str]  : 
        padrao = r"^GMT([+-])([0-9]|1[0-2])$"
        GMT = GMT.upper() 

        if re.match(padrao, GMT):

            if Client["User_Info"].find_one({
                "Discord_ID" : Discord_ID
            }) is None : 

                Client["User_Info"].insert_one({
                    "Discord_ID" : Discord_ID,
                    "GMT" : GMT, 
                    "Alarm_Sound" : ""
                } )
            
            else : 
                # pattern dont match
                return "err1"
        else : 
            # user already exists
            return "err2"

    # ----- /// Delete User /// ----- 
    @staticmethod
    def delete_user(Discord_ID) -> str : 

        Discord_ID = str(Discord_ID)

        result = Client["User_Info"].find_one({
            "Discord_ID" : Discord_ID
        })

        if result is not None : 
            Client["User_Info"].delete_one({
                "Discord_ID" : Discord_ID
            })

            return "deleted" 

        else : 
            return "err3"

    # ----- /// Change GMT /// -----
    @staticmethod
    def Change_GMT(Discord_ID : Union[int, str], GMT : str) -> str : 
        padrao = r"^GMT([+-])([0-9]|1[0-2])$"
        GMT = GMT.upper() 

        Discord_ID = str(Discord_ID)
        result = Client["User_Info"].find_one({
                "Discord_ID" : Discord_ID
            })

        if result is not None : 
            if re.match(padrao, GMT) :
                
                Client["User_Info"].update_one({
                "Discord_ID" : Discord_ID}, 
                {"$set" : {"GMT" : GMT}})

                return "Updated"
            else : 
                # pattern dont match
                return "err1"
        else : 
            # err 3 = user do not exists
            return "err3"

    # ----- /// Insert timer /// -----  
    @staticmethod
    def insert_timer(Discord_ID, date_to_send, message, command) : 

        Discord_ID = str(Discord_ID)
        now = datetime.now()

        if command == "setus" : 
            document = {
                "Discord_ID": Discord_ID,
                "Date_to_Send": date_to_send,
                "Command" : command,
                "Created_At": now.strftime("%m/%d/%Y %I:%M %p"),
                "GMT" : mongo_ATA.Return_GMT(Discord_ID),
                "Message": Cryptography.encrypt(message),
                "Mailed": False,
                "Late" : "" 
        }

        else : 
            document = {
                "Discord_ID": Discord_ID,
                "Date_to_Send": date_to_send,
                "Command" : command,
                "Created_At": now.strftime("%d-%m-%Y %H:%M"),
                "GMT" : mongo_ATA.Return_GMT(Discord_ID),
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

        last_message = Client["Alarms"].find_one({
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

        if not isinstance(Discord_ID, str): 
            Discord_ID = str(Discord_ID)

        send_at = None  # Inicializando send_at para garantir que ela exista

        try:
            # Obtém o horário do alarme a ser enviado, em string
            send_at_str = mongo_ATA.Return_Time_to_Send(Discord_ID, Document_ID)  # type: ignore

            if send_at_str:
                # Converte a string para datetime
                try : 
                    send_at = datetime.strptime(send_at_str, "%d/%m/%Y %H:%M:%S")
                except :  # noqa: E722
                    send_at = datetime.strptime(send_at_str, "%m/%d/%Y %I:%M %p")
            else:
                raise ValueError("No valid send time found for this document.")

            # Busca a última mensagem não enviada (Mailed: False)
            last_message = Client["Alarms"].find_one({
                "_id": Document_ID,
                "Discord_ID": Discord_ID,
                "Mailed": False
            })

            if last_message :

                result_return_us = mongo_ATA.return_us(Document_ID)

                if result_return_us != "setus" : 
                    # Obtém o horário atual no GMT correto
                    current_time = mongo_ATA.now_GMT(Discord_ID)
                    treshold = timedelta(seconds=5)

                    # Verifica se `send_at` não tem timezone
                    if send_at.tzinfo is None: 
                        # Obtém o timezone do usuário e aplica a `send_at`
                        user_timezone = mongo_ATA.GMT(Discord_ID)
                        send_at = user_timezone.localize(send_at)

                    # Comparação entre datetimes timezone-aware
                    if send_at - treshold <= current_time <= send_at + treshold:
                        # Atualiza o status do alarme para "Mailed" se estiver dentro do range
                        Client["Alarms"].update_one(
                            {"_id": Document_ID},
                            {"$set": {"Mailed": True, "Late": False}}
                        )
                else : 
                    # Obtém o horário atual no GMT correto
                    current_time = mongo_ATA.nowus_GMT(Discord_ID)
                    treshold = timedelta(seconds=5)

                    # Verifica se `send_at` não tem timezone
                    if send_at.tzinfo is None: 
                        # Obtém o timezone do usuário e aplica a `send_at`
                        user_timezone = mongo_ATA.GMT(Discord_ID)
                        send_at = user_timezone.localize(send_at)

                    # Comparação entre datetimes timezone-aware
                    if send_at - treshold <= current_time <= send_at + treshold:
                        # Atualiza o status do alarme para "Mailed" se estiver dentro do range
                        Client["Alarms"].update_one(
                            {"_id": Document_ID},
                            {"$set": {"Mailed": True, "Late": False}}
                        )

            else:
                # Insere um erro e marca como "Late" se estiver fora do range
                Client["Errors"].insert_one({
                    "Error_Code": 3,
                    "Error": "Too late",
                    "Discord_ID": Discord_ID,
                    "Late": datetime.strftime(send_at, "%d/%m/%Y %H:%M:%S")}  # type: ignore
                )

                Client["Alarms"].update_one(
                    {"_id": Document_ID, "Discord_ID": Discord_ID},
                    {"$set": {"Mailed": True, "Late": datetime.strftime(send_at, "%d/%m/%Y %H:%M:%S")}}  # type: ignore
                )

        except ValueError as ve:
            print("Erro na exception")
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
        alarms = Client["Alarms"].find({
        "Discord_ID" :str(Discord_ID),
        "Mailed" : False 
        })

        return alarms

    # ----- /// Return GMT /// -----
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
    def return_us(Document_ID) : 
        document = Client["Alarms"].find_one({
            "_id" : Document_ID
        })

        if document : 
            return document["Command"]

        else : 
            return None

    # ----- /// Now GMT /// ----- 
    @staticmethod
    def GMT(Discord_ID) : 

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

        GMT = mongo_ATA.Return_GMT(str(Discord_ID))
        return gmtdict[GMT]

    @staticmethod
    def now_GMT(Discord_ID) :
        return datetime.now(mongo_ATA.GMT(str(Discord_ID)))

    @staticmethod 
    def nowus_GMT(Discord_ID) :
        return datetime.now(mongo_ATA.GMT(str(Discord_ID)))
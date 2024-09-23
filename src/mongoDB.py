from pymongo.mongo_client import MongoClient
from datetime import datetime, timedelta
import os
from typing import Union
import certifi
import ssl
import pytz
import re
from message_cryptography import Cryptography

# ----- /// MongoDB Connector /// -----
Uri = os.getenv("MONGODB_URI")
ssl_context = ssl.create_default_context(cafile=certifi.where())
Client = MongoClient(Uri, tlsCAFile=certifi.where())["Alan_the_Alarm"]

now = datetime.now()

class mongo_ATA:

    # ----- /// Create User /// -----
    @staticmethod
    def create_user(Discord_ID: str, GMT: str) -> Union[None, str]:
        pattern = r"^GMT([+-])([0-9]|1[0-2])$"
        GMT = GMT.upper()

        if not re.match(pattern, GMT):
            return "err1"  # Invalid GMT pattern

        if Client["User_Info"].find_one({"Discord_ID": Discord_ID}) is None:
            Client["User_Info"].insert_one({
                "Discord_ID": Discord_ID,
                "GMT": GMT,
                "Alarm_Sound": ""
            })
        else:
            return "err2"  # User already exists

    # ----- /// Delete User /// -----
    @staticmethod
    def delete_user(Discord_ID: str) -> str:
        result = Client["User_Info"].find_one({"Discord_ID": str(Discord_ID)})
        if result:
            Client["User_Info"].delete_one({"Discord_ID": str(Discord_ID)})
            return "deleted"
        return "err3"  # User does not exist

    # ----- /// Change GMT /// -----
    @staticmethod
    def Change_GMT(Discord_ID: Union[int, str], GMT: str) -> str:
        pattern = r"^GMT([+-])([0-9]|1[0-2])$"
        GMT = GMT.upper()

        result = Client["User_Info"].find_one({"Discord_ID": str(Discord_ID)})
        if not result:
            return "err3"  # User does not exist

        if re.match(pattern, GMT):
            Client["User_Info"].update_one(
                {"Discord_ID": str(Discord_ID)},
                {"$set": {"GMT": GMT}}
            )
            return "Updated"
        return "err1"  # Invalid GMT pattern

    # ----- /// Insert timer /// -----
    @staticmethod
    def insert_timer(Discord_ID: str, date_to_send: str, message: str, command: str) -> str:
        Discord_ID = str(Discord_ID)
        now = datetime.now()
        GMT = mongo_ATA.Return_GMT(Discord_ID)
        encrypted_message = Cryptography.encrypt(message)

        document = {
            "Discord_ID": Discord_ID,
            "Date_to_Send": date_to_send,
            "Command": command,
            "Created_At": now.strftime("%m/%d/%Y %I:%M %p") if command == "setus" else now.strftime("%d-%m-%Y %H:%M"),
            "GMT": GMT,
            "Message": encrypted_message,
            "Mailed": False,
            "Late": ""
        }

        result = Client["Alarms"].insert_one(document)
        return result.inserted_id

    # ----- /// Anonymous send not mailed /// -----
    @staticmethod
    def Anonymous_send_not_mailed() -> None:
        Anonymous_documents = Client["An_Timers"].find()

        for document in Anonymous_documents:
            if not document.get("Mailed", True):
                Client["An_Timers"].delete_one({"_id": document["_id"]})

    # ----- /// Return time to send /// -----
    @staticmethod
    def Return_Time_to_Send(Discord_ID: str, Document_ID: str) -> Union[str, None]:
        last_message = Client["Alarms"].find_one({
            "_id": Document_ID,
            "Mailed": False
        })
        if last_message:
            return str(last_message.get("Date_to_Send"))
        return None

    # ----- /// True mailed /// -----
    @staticmethod
    def true_mailed(Discord_ID: str, time: str, Document_ID: str) -> None:
        send_at_str = mongo_ATA.Return_Time_to_Send(Discord_ID, Document_ID)
        if not send_at_str:
            return  # No valid send time found

        try:
            try:
                send_at = datetime.strptime(send_at_str, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                send_at = datetime.strptime(send_at_str, "%m/%d/%Y %I:%M %p")

            current_time = mongo_ATA.now_GMT(Discord_ID)
            if mongo_ATA.return_us(Document_ID) == "setus":
                current_time = mongo_ATA.nowus_GMT(Discord_ID)

            treshold = timedelta(seconds=5)
            if send_at.tzinfo is None:
                send_at = mongo_ATA.GMT(Discord_ID).localize(send_at) # type: ignore

            if send_at - treshold <= current_time <= send_at + treshold:
                Client["Alarms"].update_one(
                    {"_id": Document_ID},
                    {"$set": {"Mailed": True, "Late": False}}
                )
            else:
                raise ValueError("Too late")

        except Exception as e:
            Client["Errors"].insert_one({
                "Error_Code": "Unknown",
                "Error": str(e),
                "Error_on": Document_ID,
                "Discord_ID": Discord_ID,
                "Late": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })

    # ----- /// Active alarms /// -----
    @staticmethod
    def active_alarms(Discord_ID: str):
        alarms = Client["Alarms"].find({
            "Discord_ID": str(Discord_ID),
            "Mailed": False
        })
        return alarms

    # ----- /// Return GMT /// -----
    @staticmethod
    def Return_GMT(Discord_ID: str) -> str:
        register = Client["User_Info"].find_one({"Discord_ID": str(Discord_ID)})
        if register:
            return register["GMT"]
        return "None"

    # ----- /// Return us /// -----
    @staticmethod
    def return_us(Document_ID: str) -> Union[str, None]:
        document = Client["Alarms"].find_one({"_id": Document_ID})
        return document.get("Command") if document else None

    # ----- /// Now GMT /// -----
    @staticmethod
    def GMT(Discord_ID: str):
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
            "GMT-12": pytz.timezone("Etc/GMT+12")
        }

        GMT = mongo_ATA.Return_GMT(str(Discord_ID))
        return gmtdict.get(GMT)

    @staticmethod
    def now_GMT(Discord_ID: str):
        return datetime.now(mongo_ATA.GMT(str(Discord_ID)))

    @staticmethod
    def nowus_GMT(Discord_ID: str):
        return datetime.now(mongo_ATA.GMT(str(Discord_ID)))
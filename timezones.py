import pytz
from datetime import datetime

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

class Gmt : 
    def __init__(self, timezone) : 
        now_in_gmt_plus_1 = datetime.now(gmtdict["timezone"])
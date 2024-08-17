from pymongo.mongo_client import MongoClient
from message_cryptography import Cryptography
import certifi 
import ssl
from os import getenv



Uri = getenv("MongoDB_URI")
Clinet = MongoClient(Uri, tlsCAFile=certifi.where())["Alan_the_Timer"]

# Criar contexto SSL personalizado
ssl_context = ssl.create_default_context(cafile=certifi.where())

class CustomConnector(aiohttp.TCPConnector):
    def __init__(self, *args, **kwargs):
        kwargs['ssl'] = ssl_context
        super().__init__(*args, **kwargs)
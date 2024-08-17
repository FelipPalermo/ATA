from cryptography.fernet import Fernet  # Corrigir a importação
from typing import Union

class Cryptography : 

    key = Fernet.generate_key() 
    cipher_suite = Fernet(key)

    @staticmethod
    def encrypt(message : str) -> bytes : 

        return Cryptography.cipher_suite.encrypt(message.encode())

    @staticmethod
    def decrypt(message : bytes) -> Union[str, Exception] : 

        try : 
            message = str(message) 
            message = message[2:-1]
            message = Cryptography.cipher_suite.decrypt(message.encode()).decode()

            return message 

        except Exception as e : 
            print("Error!")
            print(e)
            print("Must insert bytes type")
            
            return e

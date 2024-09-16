from cryptography.fernet import Fernet  # Corrigir a importação
from typing import Union


class Cryptography:
    key = b''
    with open('secret.key', 'rb') as key_file:
        key = key_file.read()

    # Criando a cipher suite com a chave carregada
    cipher_suite = Fernet(key)

    @staticmethod
    def encrypt(message: str) -> bytes:
        return Cryptography.cipher_suite.encrypt(message.encode())

    @staticmethod
    def decrypt(message) -> Union[str, Exception]:
        try:
            message = str(message)  # type: ignore
            message = Cryptography.cipher_suite.decrypt(message.encode()).decode()  # type: ignore

            return message  # type: ignore

        except Exception as e:
            print(e)
            return e
        

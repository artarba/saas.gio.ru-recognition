import nacl.secret
import nacl.encoding
import base64
import os
import dotenv

token_path = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_path=token_path)
SECRET_BOX = os.getenv('SECRET_BOX')
secret_box = base64.b64decode(SECRET_BOX)


def decryption(encrypted):
    box = nacl.secret.SecretBox(
    secret_box
    )
    enc64 = encrypted.encode()
    byt = base64.b64decode(enc64)
    plaintext = box.decrypt(byt)
    return plaintext.decode()


def save_image(string):
    imgdata = base64.b64decode(string)
    filename = 'someone.jpg'
    with open(filename, 'wb') as f:
        f.write(imgdata)




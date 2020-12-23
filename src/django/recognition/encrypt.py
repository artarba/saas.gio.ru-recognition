import nacl.secret
import nacl.encoding
import base64
import os
import dotenv

token_path = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_path=token_path)
SECRET_BOX = os.getenv('SECRET_BOX')
secret_box = base64.b64decode(SECRET_BOX)


def encryption(message):
    box = nacl.secret.SecretBox(
        secret_box
    )
    encrypted = box.encrypt(message.encode())
    dfdfd = base64.b64encode(encrypted)
    # encrypted.decode("utf-8")

    return dfdfd.decode()


# with open("b64-fb.png", "rb") as img_file:
#     my_string = base64.b64encode(img_file.read())
#     my_string = my_string.decode()
#     byt = my_string.encode()
# print(my_string)

def save_image(string):
    """
Функция сохраняет изображение, которое дается в бинарном коде
    :param string:
    """
    imgdata = base64.b64decode(string)
    filename = 'some_image.jpg'
    with open(filename, 'wb') as f:
        f.write(imgdata)


print(encryption('admin, 898989qW!'))

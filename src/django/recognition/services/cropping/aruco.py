import cv2
import cv2.aruco as aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import re
import os
import mysql.connector
from recognition.services.cropping.defs import four_point_transform, filtration, rows_test
import pytesseract
import dotenv


env_path = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_path=env_path)
mysql_pass = os.getenv('db_pass')
mysql_user = os.getenv('db_user')
database = os.getenv('database')
main_path = os.getcwd()
print(mysql_pass,mysql_user)

#main_path_env = os.getenv('main_path')
#main_path = main_path_env

mydb = mysql.connector.connect(
    host="rc1a-l7mf9thjhi1qacrh.mdb.yandexcloud.net",
    user=mysql_user,
    password=mysql_pass,
    database=database,
)

mycursor = mydb.cursor()

try:
    bonus_box = os.path.join(main_path, "for_bonus")
    os.mkdir(bonus_box)
except Exception as e:
    print(e)

a = 0
b = 0
c = 0
d = None
top_left = None
top_right = None
bottom_left = None
bottom_right = None
frame_markers = None

# создание словаря для идентификации маркеров
dict = aruco.Dictionary_get(aruco.DICT_6X6_50)
fig = plt.figure()
nx = 4
ny = 3
for i in range(1, nx * ny + 1):
    ax = fig.add_subplot(ny, nx, i)
    img = aruco.drawMarker(dict, i, 700)
    plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
    ax.axis("off")


def kbs(image, image_name):
    try:
        frame = cv2.resize(
            image, (905, 1280)
        )  # приведение к единому размеру
        original = np.copy(frame)  # сохранение оригинала
        gray = cv2.cvtColor(
            frame, cv2.COLOR_BGR2GRAY
        )  # переведение изобр. в оттенки серого
        blur = cv2.GaussianBlur(
            gray, (1, 1), 0
        )  # размытие изобр, изобр. с парметрами больше (1,1) не распознаются
        # распознавание маркеров
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        parameters = aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(
            blur, dict, parameters=parameters
        )
        frame_markers = aruco.drawDetectedMarkers(
            original, corners, ids
        )

        # работа с переменной ids, которая хранит массив с уникальными id маркеров
        # присваивание каждому углу правильный id
        reg = re.compile("[] []")
        id_marker = reg.sub("", str(ids)).split()
        corner_id1 = int(id_marker.index("1"))
        corner_id2 = int(id_marker.index("2"))
        cornet_id3 = int(id_marker.index("3"))
        corner_id4 = int(id_marker.index("4"))

        # coord top left
        id1 = corners[corner_id1]
        reg = re.compile("[].[]")
        count = reg.sub("", str(id1[0, 3]))
        top_left1 = int(count.split()[0])
        top_left2 = int(count.split()[1])
        top_left = (int(top_left1), int(top_left2))

        # coord top right
        id2 = corners[corner_id2]
        reg = re.compile("[].[]")
        count = reg.sub("", str(id2[0, 2]))
        top_right1 = int(count.split()[0])
        top_right2 = int(count.split()[1])
        top_right = (int(top_right1), int(top_right2))

        # coord bottom left
        id3 = corners[cornet_id3]
        reg = re.compile("[].[]")
        count = reg.sub("", str(id3[0, 0]))
        bottom_left1 = int(count.split()[0])
        bottom_left2 = int(count.split()[1])
        bottom_left = (int(bottom_left1), int(bottom_left2))

        # coord bottom right
        id4 = corners[corner_id4]
        reg = re.compile("[].[]")
        count = reg.sub("", str(id4[0, 1]))
        bottom_right1 = int(count.split()[0])
        bottom_right2 = int(count.split()[1])
        bottom_right = (int(bottom_right1), int(bottom_right2))

        pts = [top_left, top_right, bottom_left, bottom_right]

        table = four_point_transform(frame_markers, pts)
        bonus_normal = cv2.resize(table, (830, int(table.shape[0])))
        # cv2.imwrite(
        #     os.path.join(
        #         f"{main_path}/for_tables", f"{image_name}_table_.jpg"
        #     ),
        #     bonus_normal,
        # )
        table = bonus_normal[56:, 45:]
        cv2.imwrite(
            os.path.join(
                f"{main_path}/for_bonus", f"table_{image_name}_.jpg"
            ),
            table,
        )
        rows_test(f"{main_path}/for_bonus", str(image_name))
        filtration(f"{main_path}/for_bonus")
    except Exception as e:
        error = str(e).replace("'", "")
        mycursor.execute(
            "INSERT INTO logs (errors_kpi) VALUES  ('{}')".format(
                str(error)
            )
        )
        mydb.commit()
    str_fds = os.listdir(f"{main_path}/for_bonus")

    for box in str_fds:
        if re.search("box", box):
            image = cv2.imread(f"{main_path}/for_bonus/{box}")
            first_box = image[:, :84]
            second_box = image[:, 553:638]
            ### 3 БЛОК
            im = pytesseract.image_to_string(first_box, config="outputbase digits")
            cv2.imwrite(
                os.path.join(f"{main_path}/for_bonus", f"{im[0:5]}_{image_name}.jpg"), second_box
            )

    for im in str_fds:
        delete = re.search("box", im)
        if delete:
            os.remove(f"{main_path}/for_bonus/{im}")


def work_list(image, image_name):
    frame = cv2.resize(
        image, (905, 1280)
    )  # приведение к единому размеру
    original = np.copy(frame)  # сохранение оригинала
    gray = cv2.cvtColor(
        frame, cv2.COLOR_BGR2GRAY
    )  # переведение изобр. в оттенки серого
    blur = cv2.GaussianBlur(
        gray, (1, 1), 0
    )  # размытие изобр, изобр. с парметрами больше (1,1) не распознаются
    # распознавание маркеров
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        blur, dict, parameters=parameters
    )
    frame_markers = aruco.drawDetectedMarkers(original, corners, ids)
    # работа с переменной ids, которая хранит массив с уникальными id маркеров
    # присваивание каждому углу правильный id
    reg = re.compile("[] []")
    id_marker = reg.sub("", str(ids)).split()
    corner_id1 = int(id_marker.index("1"))
    corner_id2 = int(id_marker.index("2"))
    cornet_id3 = int(id_marker.index("3"))
    corner_id4 = int(id_marker.index("4"))

    # coord top left
    id1 = corners[corner_id1]
    reg = re.compile("[].[]")
    count = reg.sub(
        "", str(id1[0, 3])
    )  # берется нужная координата маркера (у каждого маркера 4 коорд.)
    top_left1 = int(count.split()[0])
    top_left2 = int(count.split()[1])
    top_left = (int(top_left1), int(top_left2))

    # coord top right
    id2 = corners[corner_id2]
    reg = re.compile("[].[]")
    count = reg.sub("", str(id2[0, 2]))
    top_right1 = int(count.split()[0])
    top_right2 = int(count.split()[1])
    top_right = (int(top_right1), int(top_right2))

    # coord bottom left
    id3 = corners[cornet_id3]
    reg = re.compile("[].[]")
    count = reg.sub("", str(id3[0, 0]))
    bottom_left1 = int(count.split()[0])
    bottom_left2 = int(count.split()[1])
    bottom_left = (int(bottom_left1), int(bottom_left2))

    # coord bottom right
    id4 = corners[corner_id4]
    reg = re.compile("[].[]")
    count = reg.sub("", str(id4[0, 1]))
    bottom_right1 = int(count.split()[0])
    bottom_right2 = int(count.split()[1])
    bottom_right = (int(bottom_right1), int(bottom_right2))

    pts = [top_left, top_right, bottom_left, bottom_right]

    table = four_point_transform(frame_markers, pts)
    # нормирование размеров изображения
    table_normal = cv2.resize(table, (829, 842))
    # сохранение вырезанного куска
    first_bon = table_normal[
        247:297, :90
    ]  # вырезка крайнего левого блока со знач. бонуса
    second_bon = table_normal[
        247:297, 423:507
    ]  # вырезка крайнего правого блока со знач. бонуса
    # сохранение блока с бонусом
    cv2.imwrite(
        os.path.join(f"{main_path}/for_bonus", f"{image_name}_bonus1.jpg"),
        first_bon,
    )
    cv2.imwrite(
        os.path.join(f"{main_path}/for_bonus", f"{image_name}_bonus2.jpg"),
        second_bon,
    )




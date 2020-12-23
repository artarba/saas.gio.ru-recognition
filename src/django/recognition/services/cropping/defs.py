import cv2
import numpy as np
import os
import re
import uuid
import dotenv


env_path = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_path=env_path)
main_path_env = os.getenv('main_path')
main_path = main_path_env


def four_point_transform(image, pts):
    """
    Функция вырезает необходимую область независимо от ориентации избражения
    :param image: изображение в виде numpy массива
    :param pts: контуры изображения, которое надо трансформировать
    :return: вырезанная область в правильной ориентации
    """
    rect = order_points(pts)  # координаты контуров
    (tl, tr, br, bl) = rect

    # вычисление максимального расстояния(по ширине)
    # между нижней правой и нижней левой координатой, верхними координатоми
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # вычисление по высоте аналогично
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # координаты итогового изображения
    dst = np.array(
        [[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]],
        dtype="float32",
    )

    M = cv2.getPerspectiveTransform(rect, dst)  # создание матрицы для преобразованного изобр.
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))  # преобразованное изображение
    return warped


def order_points(pts):
    """
    Функция нужна для упорядочения координат:
    координаты должны идти в след. порядке [левая верхняя, правая верхняя, правая нижняя, левая нижняя]
    :param pts: numpy массив с четырьмя точками в виде (x, y)
    :return: numpy массив с четырьмя точками в правильном порядке
    """
    src_pts = np.zeros((4, 2), dtype="float32")
    # print(pts)
    s = np.sum(pts, axis=1)
    src_pts[0] = pts[np.argmin(s)]
    src_pts[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    src_pts[1] = pts[np.argmin(diff)]
    src_pts[3] = pts[np.argmax(diff)]
    return src_pts


def remove(tables, errors, bonus_box):
    """
    Функция удаляет все изображения .jpg из директорий:
    :param tables: путь к директории, в которой хранятся вырезанные таблицы
    :param errors: путь к директории, в которой хранятся нераспознанные документы
    :param bonus_box: путь к директории, в которой хранятся вырезанные боксы с бонусами
    """
    fds = os.listdir(tables)
    fds1 = os.listdir(errors)
    fds2 = os.listdir(bonus_box)

    for img in fds:
        if re.search(".jpg", img):
            try:
                os.remove(os.path.join(main_path + '/for_tables', img))
            except Exception as e:
                print(e)

    for image in fds1:
        if re.search(".jpg", image):
            try:
                os.remove(os.path.join(main_path + '/for_errors', image))
            except Exception as e:
                print(e)

    for im in fds2:
        if re.search(".jpg", im):
            try:
                os.remove(os.path.join(main_path + '/for_bonus', im))
            except Exception as e:
                print(e)


def filtration(path):
    """
    Функция отфильтровывает изображения в директории по параметрам высоты и ширины: не валидные переименовываются
    :param path: путь к директории, в которой необходимо фильтровать изображения
    """
    i = 0
    fds2 = os.listdir(path)

    for img in fds2:
        if re.search("box", img):
            try:
                image = cv2.imread(os.path.join(path, img))
                if image.shape[0] > 50 or image.shape[0] < 40:  # параметры высоты изображения, image.shape =  тип tuple
                    os.remove(os.path.join(path, img))
                    i += 1


            except Exception as e:
                print(e)

        if re.search('work_', img):
            try:
                image = cv2.imread(os.path.join(path, img))
                if image.shape[0] > 50 or image.shape[0] < 40:  # параметры высоты изображения, image.shape =  тип tuple
                    os.remove(os.path.join(path, img))
            except Exception as e:
                print(e)


def rows(path1, list_name):
    """
    Функция ищет горизонтальные линии - строки, обрезает по строкам изображение
    :param path1: путь к директрии, в которой хранятся изображения для обрезки
    """
    fds = os.listdir(path1)

    a = 0

    for img in fds:
        if re.search(".jpg", img):
            # IMREAD_GRAYSCALE обязательный параметр при считывании, без него нельзя работать с шумами изобр.
            image = cv2.imread(os.path.join(path1, img), cv2.IMREAD_GRAYSCALE)
            original = np.copy(image)  # сохранение оригинала

            i = None

            (thresh, img_bin) = cv2.threshold(
                image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
            )  # создание шума
            img_bin = 255 - img_bin

            # длина ядра изобр, последнее число примерная ширина изобр. в пикселях
            kernel_length = np.array(image).shape[1] // 785
            # обнаружение гориз. линий
            horizontal_kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT, (kernel_length, 1)
            )
            img_temp2 = cv2.erode(img_bin, horizontal_kernel, iterations=3)
            horizontal_lines_img = cv2.dilate(
                img_temp2, horizontal_kernel, iterations=3
            )
            edges = cv2.Laplacian(horizontal_lines_img, cv2.CV_8U)
            # ядро используется для удалени я вертик. линий и коротких горизю линий
            kernel1 = np.zeros((7, 31), np.uint8)
            kernel1[2, :] = 1
            eroded = cv2.morphologyEx(edges, cv2.MORPH_ERODE, kernel1)

            indices = np.nonzero(eroded)  # координаты гориз. линий
            rows = np.unique(indices[0])  # координата y

            filtered_rows = []
            for ii in range(len(rows)):
                if ii == 0:
                    filtered_rows.append(rows[ii])
                else:
                    if np.abs(rows[ii] - rows[ii - 1]) >= 6:
                        filtered_rows.append(rows[ii])
            print(filtered_rows)
            # вырезание строк

            try:
                for i in np.arange(len(filtered_rows) - 1):
                    random_name = uuid.uuid1()
                    # cv2.imwrite(
                    #     (os.path.join(path1, str("box__") + str(list_name) + str(random_name)) + ".jpg"),
                    #     original[filtered_rows[i] : filtered_rows[i + 1]],
                    # )
                    cv2.imwrite(
                        (os.path.join('/home/maksim/PycharmProjects/recognition/for_tables', str("box__") + str(list_name) + str(random_name)) + ".jpg"),
                        original[filtered_rows[i]: filtered_rows[i + 1]],
                    )

            except IndexError:
                print("Thats all")


            # if image.shape[0] > 50 or image.shape[0] < 40:
            #     os.remove(os.path.join(path1, img))  # удаление строк,  у которых высота больше 50 пикселей


def dir_size(path):
    fds = os.listdir(path)
    a = 0
    for file in fds:
        size = os.path.getsize(path + '/' + str(file))
        a += int(size)

    return a/1000000000



def rows_test(path1, list_name):
    """
    Функция ищет горизонтальные линии - строки, обрезает по строкам изображение
    :param path1: путь к директрии, в которой хранятся изображения для обрезки
    """
    fds = os.listdir(path1)

    a = 0
    print('start rows_test')
    for img in fds:
        if re.search("table", img):
            # IMREAD_GRAYSCALE обязательный параметр при считывании, без него нельзя работать с шумами изобр.
            image = cv2.imread(os.path.join(path1, img), cv2.IMREAD_GRAYSCALE)
            print(type(image))
            original = np.copy(image)  # сохранение оригинала

            i = None

            (thresh, img_bin) = cv2.threshold(
                image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
            )  # создание шума
            img_bin = 255 - img_bin

            # длина ядра изобр, последнее число примерная ширина изобр. в пикселях
            kernel_length = np.array(image).shape[1] // 785
            # обнаружение гориз. линий
            horizontal_kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT, (kernel_length, 1)
            )
            img_temp2 = cv2.erode(img_bin, horizontal_kernel, iterations=3)
            horizontal_lines_img = cv2.dilate(
                img_temp2, horizontal_kernel, iterations=3
            )
            edges = cv2.Laplacian(horizontal_lines_img, cv2.CV_8U)
            # ядро используется для удалени я вертик. линий и коротких горизю линий
            kernel1 = np.zeros((7, 31), np.uint8)
            kernel1[2, :] = 1
            eroded = cv2.morphologyEx(edges, cv2.MORPH_ERODE, kernel1)

            indices = np.nonzero(eroded)  # координаты гориз. линий
            rows = np.unique(indices[0])  # координата y

            filtered_rows = []
            for ii in range(len(rows)):
                if ii == 0:
                    filtered_rows.append(rows[ii])
                else:
                    if np.abs(rows[ii] - rows[ii - 1]) >= 6:
                        filtered_rows.append(rows[ii])
            print(filtered_rows)
            # вырезание строк
            try:
                for i in np.arange(len(filtered_rows) - 1):
                    random_name = uuid.uuid1()
                    # cv2.imwrite(
                    #     (os.path.join(path1, str("box__") + str(list_name) + str(random_name)) + ".jpg"),
                    #     original[filtered_rows[i] : filtered_rows[i + 1]],
                    # )

                    print('start saving')
                    cv2.imwrite(
                        (os.path.join(main_path + '/for_bonus', str("box_") + str(list_name) + str(random_name)) + ".jpg"),
                        original[filtered_rows[i]: filtered_rows[i + 1]],
                    )
            except IndexError:
                print("Thats all")
        if re.search('table', img):
            os.remove(main_path + '/for_bonus/' + img)
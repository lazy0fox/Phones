import sys
import sqlite3
import os
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [600, 450]

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.getImage()
        self.initUI()

    def getImage(self):
        global adress
        map_request = "http://static-maps.yandex.ru/1.x/?ll=" + adress + "&spn=20,20&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        os.remove(self.map_file)


try:
    f = 0
    n = ''.join(sys.argv[1:])
    a = []
    i = 0
    if n[i] == "+":
        a.append("+")
        i = 2
    elif n[i] == "8":
        a.append("+")
        a.append("7")
        i += 1
    for j in range(len(n[i:])):
        if n[j] == '-' and n[j + 1] == "-":
            f = 1
            break
        elif n[j] in '0123456789()':
            a.append(n[j])
    if "(" in a or ")" in a:
        a.remove('(')
        a.remove(')')
    if a.count('(') != 0 or a.count(')') != 0:
        f = 1
    if f == 0 and len(a) < 19 and len(a) > 9:
        number = "".join(a)
        print('Введённый номер телефона корректен: ' + number)
    else:
        print(1 / 0)
    if number[0] == '+':
        a = str(number[1])
        b = str(number[1:3])
        c = str(number[1:4])
        d = str(number[1]) + '-' + number[2:5]
    else:
        a = str(number[0])
        b = str(number[:2])
        c = str(number[:3])
        d = str(number[0]) + '-' + number[1:4]
    con = sqlite3.connect('phones_codes.db')
    cur = con.cursor()
    what = "SELECT TitleRU FROM Code WHERE PhoneCode like " + a + " or PhoneCode like " + b + \
           " or PhoneCode like " + c + " or PhoneCode like " + d
    phones = cur.execute(what).fetchall()
    con.close()
    for i in phones:
        country = i
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + \
                           country + "&format=json"
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()

            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            print("имеет координаты:", toponym_coodrinates)
            adress = ','.join(toponym_coodrinates.split())
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
        if __name__ == '__main__':
            app = QApplication(sys.argv)
            ex = Example()
            ex.show()
            sys.exit(app.exec())
except ValueError:
    print('неверный формат')
except ZeroDivisionError:
    print('неверное количество цифр')
except Exception:
    print('ошибка подключения к базе данных, необходимо проверить корректность соединения')
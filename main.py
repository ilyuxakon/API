import sys
import requests
import keyboard
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPixmap
from ui_file import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    Z = '0.05'
    X = '0'
    Y = '0'
    THEME = 'light'


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()


    def initUI(self):
        self.search_button.clicked.connect(self.get_map)
        self.switch_check_box.clicked.connect(self.set_theme)
        self.search_button_2.clicked.connect(self.search_obj)


    def set_theme(self):
        if self.switch_check_box.isChecked():
            self.THEME = 'dark'
            self.switch_check_box.setText('Тёмная')

        else:
            self.THEME = 'light'
            self.switch_check_box.setText('Светлая')

        self.get_map()


    def set_position(self):
        if ',' in self.longitude.text():
            self.X = '.'.join(self.longitude.text().split(','))
        
        else:
            self.X = self.longitude.text()

        if ',' in self.latitude.text():
            self.Y = '.'.join(self.latitude.text().split(','))
        
        else:
            self.Y = self.latitude.text()
        
        self.get_map()


    def search_obj(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocode = self.search.text()

        geocoder_params = {
            "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
            "geocode": geocode,
            "sco": "longlat",
            "format": "json",
        }

        response = requests.get(geocoder_api_server, params=geocoder_params)
        json = response.json()
        toponym = json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        self.X, self.Y = toponym_coodrinates.split(" ")
        self.longitude.setText(self.X)
        self.latitude.setText(self.Y)

        self.get_map()


    def get_map(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocode = self.X + ', ' + self.Y

        geocoder_params = {
            "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
            "geocode": geocode,
            "sco": "longlat",
            "format": "json",
        }

        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            return
        
        json = response.json()
        toponym = json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        name = toponym['name']
        self.search.setText(name)
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([self.Z, self.Z]),
            "theme": self.THEME,
            "apikey": "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
        }

        map_api_server = "https://static-maps.yandex.ru/v1"

        response = requests.get(map_api_server, params=map_params)
        
        if not response:
            return
        
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.label.setPixmap(self.pixmap)


def main():
    def pg_up():
        a.Z = str(float(a.Z) * 1.5)
        a.get_map()

    def pg_down():
        a.Z = str(float(a.Z) / 1.5)
        a.get_map()

    def up():
        a.Y = str(float(a.Y) + float(a.Z) * 0.5)
        a.get_map()

    def down():
        a.Y = str(float(a.Y) - float(a.Z) * 0.5)
        a.get_map()

    def left():
        a.X = str(float(a.X) - float(a.Z) * 0.5)
        a.get_map()

    def right():
        a.X = str(float(a.X) + float(a.Z) * 0.5)
        a.get_map()

    keyboard.add_hotkey('page up', pg_up)
    keyboard.add_hotkey('page down', pg_down)
    keyboard.add_hotkey('up', up)
    keyboard.add_hotkey('down', down)
    keyboard.add_hotkey('left', left)
    keyboard.add_hotkey('right', right)

    app = QApplication(sys.argv)
    a = MainWindow()
    a.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
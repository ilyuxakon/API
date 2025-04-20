import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPixmap
from ui_file import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    Z = '0.05'

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.search_button.clicked.connect(self.get_map)

    def get_map(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocode = self.longitude.text() + ', ' + self.latitude.text()
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
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

        map_api_server = "https://static-maps.yandex.ru/v1"
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([self.Z, self.Z]),
            "apikey": "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
        }

        response = requests.get(map_api_server, params=map_params)
        
        if not response:
            return
        
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.label.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = MainWindow()
    a.show()
    sys.exit(app.exec())
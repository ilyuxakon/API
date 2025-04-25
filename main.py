import sys
import requests
import keyboard
import math
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt
from ui_file import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    Z = '0.05'
    X = '0'
    Y = '0'
    FLAG_X = None
    FLAG_Y = None
    THEME = 'light'
    ADDRESS = ''
    ADDRESS_FLAG = True
    POST_CODE = ''
    POST_CODE_FLAG = False


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.get_map({'ll': self.X + ',' + self.Y})


    def initUI(self):
        self.search_button.clicked.connect(self.main)
        self.switch_check_box.clicked.connect(self.set_theme)
        self.search_button_2.clicked.connect(self.main)
        self.reset.clicked.connect(self.reset_pt)
        self.post_cod_check_box.clicked.connect(self.set_post_code)

    
    def right_click(self):
        pos = self.get_coord_click()
        
        if not pos:
            return
        
        x, y = pos
        
        server = 'https://search-maps.yandex.ru/v1/'
        apikey = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'
        
        params = {
            'apikey': apikey,
            'lang': 'ru_RU',
            'text': 'организация',
            'll': x + ',' + y,
            'spn': '0.1,0.1',
            'type': 'biz'
        }
        
        response = requests.get(server, params=params)

        if not response:
            return
        
        response = response.json()
        
        if len(response['features']) == 0:
            return
        
        org_pos = response['features'][0]['geometry']['coordinates']
        
        float_pos = (float(pos[0]), float(pos[1]))
        float_org_pos = (float(org_pos[0]), float(org_pos[1]))
        
        if self.lonlat_distance(float_pos, float_org_pos) > 1000:
            return
        
        params = {
            'geocode': str(org_pos[0]) + ', ' + str(org_pos[1]),
            'sco': 'longlat'
        }
        
        pos, name, address, post_code = self.search_obj(params)
        
        self.ADDRESS = address
        self.ADDRESS_FLAG = True
        self.POST_CODE = post_code
        self.FLAG_X = self.X = str(pos[0])
        self.FLAG_Y = self.Y = str(pos[1])
        self.search.setText(name)
        
        params = {
            'll': ','.join([str(i) for i in pos]),
            'pt': ','.join([str(i) for i in pos]) + ',flag'
        }
        self.get_map(params)
        
    
    def lonlat_distance(self, a, b):
        degree_to_meters_factor = 111 * 1000 # 111 километров в метрах
        a_lon, a_lat = a
        b_lon, b_lat = b

        # Берем среднюю по широте точку и считаем коэффициент для нее.
        radians_lattitude = math.radians((a_lat + b_lat) / 2.)
        lat_lon_factor = math.cos(radians_lattitude)

        # Вычисляем смещения в метрах по вертикали и горизонтали.
        dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
        dy = abs(a_lat - b_lat) * degree_to_meters_factor

        # Вычисляем расстояние между точками.
        distance = math.sqrt(dx * dx + dy * dy)

        return distance


    def click(self):
        pos = self.get_coord_click()
        
        if not pos:
            return
        
        x, y = pos
        params = {
            'geocode': x + ', ' + y,
            'sco': 'longlat'
        }
        
        pos, name, address, post_code = self.search_obj(params)
        
        self.ADDRESS = address
        self.ADDRESS_FLAG = True
        self.POST_CODE = post_code
        self.FLAG_X = str(pos[0])
        self.FLAG_Y = str(pos[1])
        self.search.setText(name)
        
        params = {
            'll': self.X + ',' + self.Y,
            'pt': ','.join([str(i) for i in pos]) + ',flag'
        }
        self.get_map(params)

        if self.ADDRESS != '':
            self.address.setText(self.ADDRESS)
        
        if self.POST_CODE_FLAG and self.POST_CODE != '':
            self.address.setText(f'{self.address.text()}\n{self.POST_CODE}')
    
    
    def get_coord_click(self):
        pos = self.label.mapFromGlobal(QCursor().pos())
        if 0 <= pos.x() <= 600 and\
           0 <= pos.y() <= 450:
            x = pos.x() - 300
            y = pos.y() - 225
            x = str(float(self.X) + x * (float(self.Z) / 150))
            y = str(float(self.Y) - y * (float(self.Z) / 225))
            return x, y
        
        return False
    
    
    def set_theme(self):
        if self.THEME == 'light':
            self.THEME = 'dark'
            self.switch_check_box.setText('Тёмная')
        else:
            self.THEME = 'light'
            self.switch_check_box.setText('Светлая')
            
        self.main()
    
    
    def reset_pt(self):
        self.ADDRESS_FLAG = False
        self.ADDRESS = ''
        self.POST_CODE = ''
        self.POST_CODE_FLAG = False
        self.FLAG_Y = self.FLAG_X = None
        self.address.setText('')
        self.search.setText('')
        self.longitude.setText('')
        self.latitude.setText('')
        self.main()
    
    
    def set_post_code(self):
        self.POST_CODE_FLAG = not self.POST_CODE_FLAG
        if self.ADDRESS != '':
            self.address.setText(self.ADDRESS)
            
        if self.POST_CODE_FLAG and self.POST_CODE != '':
            self.address.setText(f'{self.address.text()}\n{self.POST_CODE}')
            
    
    def main(self):
        if self.sender() == self.search_button:
            if ',' in self.longitude.text():
                self.X = '.'.join(self.longitude.text().split(','))
            
            else:
                self.X = self.longitude.text()

            if ',' in self.latitude.text():
                self.Y = '.'.join(self.latitude.text().split(','))
            
            else:
                self.Y = self.latitude.text()
                
            params = {
                'geocode': self.X + ', ' + self.Y,
                'sco': 'longlat'
            }
            
            pos, name, address, post_code = self.search_obj(params)
            
            self.ADDRESS = address
            self.ADDRESS_FLAG = True
            self.POST_CODE = post_code
            self.FLAG_X = None
            self.FLAG_Y = None
            self.search.setText(name)
            
            params = {
                'll': ','.join([str(i) for i in pos])
            }
            self.get_map(params)
            
        elif self.sender() == self.search_button_2:
            params = {
                'geocode': self.search.text()
            }
            
            pos, name, address, post_code = self.search_obj(params)
            
            self.ADDRESS = address
            self.ADDRESS_FLAG = True
            self.POST_CODE = post_code
            
            self.latitude.setText(pos[1])
            self.longitude.setText(pos[0])
            
            self.X = self.FLAG_X = pos[0]
            self.Y = self.FLAG_Y = pos[1]
            
            params = {
                'll': ','.join([str(i) for i in pos]),
                'pt': ','.join([str(i) for i in pos]) + ',flag'
            }
            self.get_map(params)
            
        else:
            params = {'ll': self.X + ',' + self.Y}
            if self.FLAG_X is not None:
                params['pt'] = self.FLAG_X + ',' + self.FLAG_Y + ',flag'
            self.get_map(params)
            
        if self.ADDRESS != '':
            self.address.setText(self.ADDRESS)
            
        if self.POST_CODE_FLAG and self.POST_CODE != '':
            self.address.setText(f'{self.address.text()}\n{self.POST_CODE}')
        
        
    def search_obj(self, params):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        params["apikey"] = "8013b162-6b42-4997-9691-77b7074026e0"
        params["format"] = "json"

        response = requests.get(geocoder_api_server, params=params)

        if not response:
            return
        
        json = response.json()
        toponym = json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        name = toponym['name']
        address = toponym['metaDataProperty']['GeocoderMetaData']['text']
        post_code = ''
        if 'Address' in toponym['metaDataProperty']['GeocoderMetaData'] and\
           'postal_code' in toponym['metaDataProperty']['GeocoderMetaData']['Address']:
               post_code = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']

        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        
        return (toponym_longitude, toponym_lattitude), name, address, post_code


    def get_map(self, map_params):
        map_params['apikey'] = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        map_params['theme'] = self.THEME
        map_params["spn"] = ",".join([self.Z, self.Z])
        map_api_server = "https://static-maps.yandex.ru/v1"

        response = requests.get(map_api_server, params=map_params)
        
        if not response:
            return
        
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.label.setPixmap(self.pixmap)
    
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click()
            
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_click()


def main():
    def pg_up():
        a.Z = str(float(a.Z) * 1.5)
        a.main()

    def pg_down():
        a.Z = str(float(a.Z) / 1.5)
        a.main()

    def up():
        a.Y = str(float(a.Y) + float(a.Z) * 0.5)
        a.main()

    def down():
        a.Y = str(float(a.Y) - float(a.Z) * 0.5)
        a.main()

    def left():
        a.X = str(float(a.X) - float(a.Z) * 0.5)
        a.main()

    def right():
        a.X = str(float(a.X) + float(a.Z) * 0.5)
        a.main()

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
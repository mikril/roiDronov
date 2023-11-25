from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Ellipse
import random
from kivy.uix.widget import Widget

Config.set("graphics", "resizable", 0)
Config.set("graphics", "width", 1600)
Config.set("graphics", "height", 900)

class SettingsWidget(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_building = 0
        self.is_packaging = 0
        self.wall_pos = [(0, 0),(0, 0)]
    def remove_drone(self):
        if app.drone_amount >= 1:
            app.field.remove_drone()
        self.ids.drone_amount.text = str(app.drone_amount)

    def add_drone(self):
        app.field.add_drone()
        self.ids.drone_amount.text = str(app.drone_amount)

    def on_touch_up(self, touch):
        #TODO: отображать как будет выглядеть стена
        if self.is_building == 1:
            self.is_building = 2

        elif self.is_building == 2:
            self.wall_pos[0] = (touch.x, touch.y)
            self.is_building = 3 

        elif self.is_building == 3:
            self.wall_pos[1] = (touch.x, touch.y)
            self.is_building = 3
            app.field.add_wall(self.wall_pos[0], self.wall_pos[1])
            self.is_building = 0
            self.wall_pos = [(0, 0),(0, 0)]
        
        if self.is_packaging == 1:
            self.is_packaging = 2 

        elif self.is_packaging == 2:
            app.field.add_package((touch.x, touch.y))
            self.is_packaging = 0

    def add_wall(self):
        self.is_building = 1

    def add_package(self):
        self.is_packaging = 1

    def remove_wall(self):
        app.field.remove_wall()

class Wall(Widget):
    def __init__(self, first_point, second_point):
        super(Wall, self).__init__()
        self.first_point = first_point
        self.second_point = second_point
        self.color = Color(1, 0, 0, 1)
        self.canvas.add(self.color)
        with self.canvas:
            self.ellipse = Rectangle(pos=first_point, size=(second_point[0] - first_point[0], second_point[1] - first_point[1]))

class Station(Widget):
    def __init__(self):
        super(Station, self).__init__()
        self.color = Color(0.1, 0.5, 0.2, 1)
        self.pos = (600, 450)
        self.size = (200, 100)
        self.canvas.add(self.color)
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size, Color=self.color)
       

class Package(Widget):
    def __init__(self, start):
        super(Package, self).__init__()
        self.start = start
        self.storage = 0 #Номер склада
        self.life_time = 0 #Время жизни посылки

        self.color = Color(0, 1, 0, 1)
        self.canvas.add(self.color)
        with self.canvas:
            self.ellipse = Rectangle(pos=map(lambda x: x-10, start), size=(20,20))

        
class Drone(Widget):
    def __init__(self, sizeDron=None, field_size=None):
        super(Drone, self).__init__()
        self.sizeDron = sizeDron
        self.field_size = field_size

        self.pos = (700, 500)

        self.color = Color(0, 0, 0, 1)
        self.canvas.add(self.color)

        # Изменил создание Ellipse через инструкции рисования
        with self.canvas:
            self.ellipse = Ellipse(pos=self.pos, size=self.sizeDron)

        Clock.schedule_interval(self.update, 1.0 / 100)

    def update(self, dt):
        self.move()
        self.ellipse.pos = self.pos
        self.canvas.ask_update()

    def move(self):
        direction_x = int(random.choice([-1, 0, 1]))
        direction_y = int(random.choice([-1, 0, 1]))

        new_pos = (self.pos[0] + direction_x * 5, self.pos[1] + direction_y * 5)
        x_condition = 0 <= new_pos[0] <= self.field_size[0]-self.sizeDron[0]
        y_condition = 0 <= new_pos[1] <= self.field_size[1]-self.sizeDron[1]

        if x_condition and y_condition:
            self.pos = new_pos
        else:
            raise ValueError("Коллизия! Новая позиция за пределами допустимой области.")

class Field(FloatLayout):
    def __init__(self, sizeField):
        super(Field, self).__init__(size_hint = (None, 1))
        self.sizeField = sizeField
        self.rect = Rectangle(pos=self.pos, size=self.sizeField)
        self.canvas.add(self.rect)
        self.size = sizeField
        self.drones = []
        self.packages = []
        self.walls = []
        self.station = Station()
        self.add_widget(self.station)
        
    def add_drone(self):
        drone_to_add = Drone(sizeDron=(20, 20), field_size=self.size)
        self.drones.append(drone_to_add)
        self.add_widget(drone_to_add)
        app.drone_amount += 1
    
    def remove_drone(self):
        if app.drone_amount >= 1:   
            app.drone_amount -= 1     
            self.remove_widget(self.drones.pop())       

    def add_package(self, pos):
        package_to_add = Package(pos)
        self.packages.append(package_to_add)
        self.add_widget(package_to_add)

    def add_wall(self, first_pos, second_pos):
        wall_to_add = Wall(first_pos, second_pos)
        self.walls.append(wall_to_add)
        self.add_widget(wall_to_add)
    
    def remove_wall(self):
        #TODO: Удалять по клику на стену
        if len(self.walls) >= 1:      
            self.remove_widget(self.walls.pop()) 

class myApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drone_amount = 0
        self.field = Field((1400, 900))
        
    
    def build(self):
        
        boxLayout = BoxLayout(orientation='horizontal')
        boxLayout.add_widget(self.field)
        boxLayout.add_widget(SettingsWidget())
        return boxLayout
    
    

if __name__ == "__main__":
    app = myApp()
    app.run()
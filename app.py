from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.config import Config
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Ellipse
import random
from kivy.uix.widget import Widget

Config.set("graphics", "resizable", 0)
Config.set("graphics", "width", 1600)
Config.set("graphics", "height", 900)


def check_collision(obj1_x, obj1_y, obj1_width, obj1_height, obj2_x, obj2_y, obj2_width, obj2_height):
    # Проверка по оси X
    if obj1_x < obj2_x + obj2_width and obj1_x + obj1_width > obj2_x:
        # Проверка по оси Y
        if obj1_y < obj2_y + obj2_height and obj1_y + obj1_height > obj2_y:
            # Объекты пересекаются
            return True
    # Объекты не пересекаются
    return False



class Storage(Widget):
    def __init__(self, id, drop_point_1, drop_point_2, color):
        super(Storage, self).__init__()
        self.id = id
        self.drop_point_1 = drop_point_1
        self.drop_point_2 = drop_point_2
        self.color = Color(*map(lambda x: x*0.7, color))
        self.canvas.add(self.color)
        with self.canvas:
            self.ellipse = Rectangle(pos=drop_point_1, size=(drop_point_2[0] - drop_point_1[0], drop_point_2[1] - drop_point_1[1]))
            self.label = Label(text = str(self.id), pos=drop_point_1, color=(0, 0, 0, 1))
   
        

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
            pos=(touch.x, touch.y)
            app.field.add_package(pos)
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
    def __init__(self, pos):
        super(Package, self).__init__()
        self.pos = pos
        self.storage = 0 #Номер склада
        self.life_time = 0
        self.weight = str(random.randint(1,10))

        self.color = Color(0, 1, 0, 1)
        self.canvas.add(self.color)

        self.event=Clock.schedule_interval(self.update_life_time, 1)

        with self.canvas:
            self.ellipse = Rectangle(pos=map(lambda x: x-10, pos), size=(20,20))
            self.label_weight = Label(text=self.weight, pos=(self.pos[0]-50, self.pos[1]-50), color=(1, 0, 0, 1))
            self.label_life_time = Label(text='0:00', pos=(self.pos[0]-50, self.pos[1]-30), color=(0, 0, 0, 1))

    def update_life_time(self, dt):
        minutes = self.life_time // 60
        seconds = self.life_time % 60
        self.label_life_time.text = f'{minutes}:{seconds:02d}'
        self.life_time += 1

    def update_position(self, new_pos):
        self.pos = new_pos
        self.ellipse.pos = self.pos
        self.label_weight.pos = (self.pos[0]-40, self.pos[1]-40)
    def start_move(self):
        self.remove_widget(self.label_life_time)
        self.label_life_time.text = ''
        Clock.unschedule(self.event)
    
        
class Drone(Widget):
    def __init__(self, sizeDron=None, field_size=None,packages=None):
        super(Drone, self).__init__()
        self.sizeDron = sizeDron
        self.field_size = field_size
        self.packages=packages
        self.pos = (700, 500)
        self.indicator_power = 100
        self.gruz=None
        self.color = Color(0, 0, 0, 1)
        self.canvas.add(self.color)

        # Изменил создание Ellipse через инструкции рисования
        with self.canvas:
            self.ellipse = Ellipse(pos=self.pos, size=self.sizeDron)
            self.charge_percent = ProgressBar(max=100, size=(30, 50), pos=(self.pos[0], self.pos[1] + 10), value=self.indicator_power)
            self.percent_charge = Label(text=str(self.indicator_power), pos=(self.pos[0] - 65, self.pos[1] - 13), color=(0,0,0))
        self.event = Clock.schedule_interval(self.update, 1.0 / 100)

    def update(self, dt):
        if self.indicator_power>0:
            self.move()
        self.ellipse.pos = self.pos

        self.charge_percent.pos = (self.pos[0], self.pos[1] + 10)
        self.charge_percent.value = self.indicator_power
        self.percent_charge.pos = (self.pos[0] - 65, self.pos[1] - 13)
        self.percent_charge.text = str(int(self.indicator_power))

        if(self.gruz!=None):
            self.gruz.update_position(self.pos)
        


    def __del__(self):
        Clock.unschedule(self.event)
        del self

    def move(self):
        direction_x = int(random.choice([-1, 0, 1]))
        direction_y = int(random.choice([-1, 0, 1]))

        new_pos = (self.pos[0] + direction_x * 5, self.pos[1] + direction_y * 5)
        x_condition = 0 <= new_pos[0]+self.sizeDron[0] <= self.field_size[0]
        y_condition = 0 <= new_pos[1]+self.sizeDron[1] <= self.field_size[1]
        if(self.gruz==None):
            for package in self.packages:
                if check_collision(new_pos[0], new_pos[1], 20, 20, package.pos[0], package.pos[1], 20, 20):
                    self.gruz=package
                    self.gruz.start_move()
                    

        if x_condition and y_condition:
            self.pos = new_pos
        else:
            pass
        
        if self.indicator_power > 0:
            self.indicator_power -= 0.05

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

        self.storages = [Storage(0, (0, 0), (100, 100), (0, 0, 0, 1)),
                        Storage(1, (1300, 0), (1400, 100), (1, 0, 0, 1)),
                        Storage(2, (1300, 800), (1400, 900), (0, 1, 0, 1)),
                        Storage(3, (0, 800), (100, 900), (0, 0, 1, 1))]
        for storage in self.storages:
            self.add_widget(storage)
        
    def add_drone(self):
        drone_to_add = Drone(sizeDron=(20, 20), field_size=self.size, packages=self.packages)
        self.drones.append(drone_to_add)
        self.add_widget(drone_to_add)
        app.drone_amount += 1
    
    def remove_drone(self):
        if app.drone_amount >= 1:   
            app.drone_amount -= 1     
            drone_to_kill = self.drones.pop()
            self.remove_widget(drone_to_kill)  
            drone_to_kill.__del__()    
            print(self.drones)

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
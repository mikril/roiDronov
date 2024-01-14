from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.config import Config
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Ellipse, Line
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.image import Image
import heapq
import random
from queue import PriorityQueue

Config.set("graphics", "resizable", 0)
Config.set("graphics", "width", 1600)
Config.set("graphics", "height", 900)
Window.size = (1600, 900)
Window.clearcolor = (224/255, 184/255, 112/255, 1)
LabelBase.register(DEFAULT_FONT, fn_regular='./font.otf')

def check_collision(obj1_x, obj1_y, obj1_width, obj1_height, obj2_x, obj2_y, obj2_width, obj2_height):
    obj1_left = min( obj1_x, obj1_x + obj1_width) # 10
    obj1_right = max( obj1_x, obj1_x + obj1_width) #20
    obj1_top = min( obj1_y, obj1_y + obj1_height) #10
    obj1_bottom = max( obj1_y, obj1_y + obj1_height)  #20 квадрат 10 на 10 
    
    obj2_left = min( obj2_x, obj2_x + obj2_width) 
    obj2_right = max( obj2_x, obj2_x + obj2_width) 
    obj2_top = min( obj2_y, obj2_y + obj2_height) 
    obj2_bottom = max( obj2_y, obj2_y + obj2_height)    
    if obj1_left < obj2_right and obj1_right > obj2_left and obj1_top < obj2_bottom and obj1_bottom > obj2_top:
        return True
    return False
    
def heuristic(a, b):
    x1, y1 = a
    x2, y2 = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star(start, end, obstacles):
    count = 0
    open_set = PriorityQueue()
    start = tuple(start)
    end = tuple(end)
    open_set.put((0, count, start))
    came_from = {}
    g_score = {(x, y): float("inf") for x in range(0, 1381, 20) for y in range(0, 881, 20)}
    g_score[start] = 0
    f_score = {(x, y): float("inf") for x in range(0, 1381, 20) for y in range(0, 881, 20)}
    f_score[start] = heuristic(start, end)
    
    open_set_hash = {start}
    
    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path = reconstruct_path(came_from, end)
            return path

        for neighbor in get_neighbors(current, obstacles):
            temp_g_score = g_score[current] + 20
            if neighbor in g_score:
                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + heuristic(neighbor, end)
                    
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)

    return []

def get_neighbors(pos, obstacles):
    x, y = pos
    possible_neighbors = [(x + dx, y + dy) for dx, dy in [(0, 20), (20, 0), (0, -20), (-20, 0)]]
    possible_neighbors_diagonals = [(x + dx, y + dy) for dx, dy in [(20, 20), (-20, -20), (20, -20), (-20, 20)]]
    indexes_neighbors=[(0,1),(2,3),(1,2),(0,3)]
    return [neighbor for neighbor in possible_neighbors if not has_collision(neighbor, obstacles)] + [possible_neighbors_diagonals[neighborIND] for neighborIND in range(len(possible_neighbors_diagonals)) if not has_collision(possible_neighbors_diagonals[neighborIND], obstacles) and not has_collision(possible_neighbors[indexes_neighbors[neighborIND][0]], obstacles) and not has_collision(possible_neighbors[indexes_neighbors[neighborIND][1]], obstacles)]

def has_collision(pos, obstacles):
    x, y = pos
    
    for obstacle in obstacles:
        if check_collision(x, y, 20, 20, obstacle.first_point[0], obstacle.first_point[1], obstacle.wallSize[0], obstacle.wallSize[1]):
            
            return True
    return False


def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.insert(0, current)
        current = came_from[current]
    return path


class Storage(Widget):
    def __init__(self, id):
        super(Storage, self).__init__()
        self.id = id
        self.positions = [(0, 0), (1300, 0), (1300, 800), (0,800)]
        self.enteres = [(80, 80), (1300, 80), (1300, 800), (80,800)]
        self.enter=self.enteres[id]
        self.drop_point_1 = self.positions[id]
        self.drop_point_2 = list(map(lambda x: x + 100, self.drop_point_1))
        self.left_x = min(self.drop_point_1[0], self.drop_point_2[0])
        self.right_x = max(self.drop_point_1[0], self.drop_point_2[0])
        self.top_y = max(self.drop_point_1[1], self.drop_point_2[1])
        self.bot_y = min(self.drop_point_1[1], self.drop_point_2[1])
        with self.canvas:
            texture = Image(rf"./images/storage{self.id}.png").texture
            self.rectangle = Rectangle(texture=texture, pos=self.drop_point_1, size=(self.drop_point_2[0] - self.drop_point_1[0], self.drop_point_2[1] - self.drop_point_1[1]))
            #self.label = Label(text = str(self.id), pos=self.drop_point_1, color=(0, 0, 0, 1))
   
class SettingsWidget(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_building = 0
        self.is_packaging = 0
        self.is_generating = 0
        self.is_maintaining = 0
        self.is_deleteing = 0
        self.wall_pos = [(0, 0),(0, 0)]
        self.generatePackages = Clock.schedule_interval(self.generate_packages, 1)
       
        with self.canvas:
            Color(30/255, 30/255, 46/255, 0.8)
            self.pre_wall = Rectangle(pos=(-100, -100), size=(100, 100))
            
        Window.bind(mouse_pos=self.mouse_pos)
        self.event = Clock.schedule_interval(self.settings_change, 1.0/10)
        
    def settings_change(self, dt):
        if app.field.packages == [] and self.is_maintaining==1 and self.ids.deleting_walls.disabled == True:
            self.reset_except_id("")

    def mouse_pos(self, window, pos):
        if self.is_building == 3:
            left_x = (min(self.wall_pos[0][0], pos[0]) // 20) * 20
            right_x = (max(self.wall_pos[0][0], pos[0]) // 20 + 1) * 20
            top_y = (max(self.wall_pos[0][1], pos[1]) // 20 + 1) * 20
            bot_y = (min(self.wall_pos[0][1], pos[1]) // 20) * 20
            self.pre_wall.pos = (left_x, bot_y)
            self.pre_wall.size = (abs(right_x - left_x), abs(top_y - bot_y))
            
    def reset_except_id(self, except_id):
        if self.is_maintaining == 1:
            if except_id != "deleting_walls":
                self.is_deleteing = 0
                self.ids.deleting_walls.text = "Удаление"
                self.ids.deleting_walls.background_color = "cyan"
                self.ids.deleting_walls.disabled = False
                
            if except_id != "add_wall":
                self.is_building = 0
                self.ids.add_wall.disabled = False
                self.ids.add_wall.background_color = "cyan"
        else:
            if except_id != "is_packaging":
                self.is_packaging = 0
                self.ids.add_packages.disabled = False  
                self.ids.generate_package.disabled = False
                self.ids.add_wall.text = "Добавить"
                self.ids.add_wall.background_color = "cyan"
                self.ids.add_packages.text = "Создать"
                self.ids.add_packages.background_color = "cyan"


    def remove_drone(self):
        if app.drone_amount >= 1:
            app.field.remove_drone()
        self.ids.drone_amount.text = str(app.drone_amount)

    def remove_wall(self):
        if self.is_maintaining == 1:
            self.reset_except_id("deleting_walls")
            if self.is_deleteing == 0:
                self.is_deleteing = 1
                self.ids.deleting_walls.text = "Перестать"
                self.ids.deleting_walls.background_color = (0, 0, 0, 0.8)
            elif self.is_deleteing == 1:
                self.is_deleteing = 0
                self.ids.deleting_walls.text = "Удаление"
                self.ids.deleting_walls.background_color = "cyan"

    def add_drone(self):
        self.reset_except_id("drone_amount")
        self.disable_deleting_block()
        app.field.add_drone()
        self.ids.drone_amount.text = str(app.drone_amount)
        
    def on_touch_up(self, touch):
        if self.is_deleteing == 1: 
            for wall in app.field.obstacles:   
                if wall.left_x <= touch.x <= wall.right_x and wall.bot_y <= touch.y <= wall.top_y:
                    wall_to_remove = app.field.obstacles[app.field.obstacles.index(wall)]
                    app.field.remove_widget(wall_to_remove)
                    app.field.obstacles.remove(wall_to_remove)
                    wall_to_remove.__del__()   

        if self.is_building == 1:
            self.is_building = 2
            self.ids.add_wall.background_color = (0, 0, 0, 0.8)

        elif self.is_building == 2:
            self.wall_pos[0] = (touch.x, touch.y)
            self.is_building = 3 

        elif self.is_building == 3:
            self.wall_pos[1] = (touch.x, touch.y)
            self.is_building = 3
            wall_width = abs(self.wall_pos[0][0]-self.wall_pos[1][0])
            wall_height = abs(self.wall_pos[0][1]-self.wall_pos[1][1])
            flag = False
            for storage in app.field.storages:
                if check_collision(min(self.wall_pos[0][0], self.wall_pos[1][0]), min(self.wall_pos[0][1], self.wall_pos[1][1]), wall_width, wall_height, storage.left_x, storage.bot_y, storage.right_x-storage.left_x, storage.top_y-storage.bot_y):
                    flag = True
                    break
            if not flag and not check_collision(min(self.wall_pos[0][0], self.wall_pos[1][0]), min(self.wall_pos[0][1], self.wall_pos[1][1]), wall_width, wall_height, 600, 400, 200, 100):
                app.field.add_wall(self.wall_pos[0], self.wall_pos[1])
            self.is_building = 0
            self.wall_pos = [(0, 0),(0, 0)]
            self.ids.add_wall.background_color = "cyan"
            self.pre_wall.pos = (-100, -100)
            self.pre_wall.size = (1, 1)
        if self.is_packaging == 1:
            self.is_packaging = 2 

        elif self.is_packaging == 2:
            pos=(int(touch.x // 20 * 20) , int(touch.y // 20 * 20 ))
            flag = False

            if app.field.station.pos[0]  <= pos[0] <= app.field.station.pos[0] + 200 and app.field.station.pos[1]  <= pos[1] <= app.field.station.pos[1]  + 100 + 10:
                flag = True
            for wall in app.field.obstacles:
                if wall.left_x  <= pos[0] <= wall.right_x  and wall.bot_y  <= pos[1] <= wall.top_y :
                    flag = True
                    break
            for storage in app.field.storages:
                if storage.left_x  <= pos[0] <= storage.right_x  and storage.bot_y  <= pos[1] <= storage.top_y :
                    flag = True
                    break
            if not flag:
                app.field.add_package(pos)
            
            
            self.is_packaging = 2
            
    def disable_deleting_block(self):
        self.is_deleteing = 0
        self.ids.deleting_walls.text = "Удаление"
        self.ids.deleting_walls.background_color = "cyan"
        self.ids.deleting_walls.disabled = True
        
        self.is_building = 0
        self.ids.add_packages.text = "Создать"
        self.ids.add_packages.background_color = "cyan"
        self.ids.add_wall.disabled = True
    
    def disable_package_block(self):
        self.is_generating = 0
        self.ids.generate_package.disabled = True
        self.ids.generate_package.text = "Генерировать"
        self.ids.generate_package.background_color = "cyan"

        self.is_packaging = 0
        self.ids.add_packages.disabled = True
        self.ids.add_packages.text = "Создать"
        self.ids.add_packages.background_color = "cyan"
        
    def maintain(self):
        if self.is_maintaining == 0:
            self.is_maintaining = 1
            self.reset_except_id("")
            self.ids.maintaining.text = "Прекратить"
            self.ids.maintaining.background_color = (0, 0, 0, 0.8)

            self.disable_package_block()
            self.disable_deleting_block()
            
            

        elif self.is_maintaining == 1:
            self.is_maintaining = 0
            self.reset_except_id("")
            self.ids.maintaining.text = "Обслуживание"
            self.ids.maintaining.background_color = "cyan"
            
            self.disable_deleting_block()
           

    def add_wall(self):
        if self.is_maintaining == 1 :
            self.reset_except_id("add_wall")
            self.is_building = 1

    def generate_packages(self, dt):
        if self.is_generating == 1 and self.is_maintaining == 0:
            if len(app.field.drones) * 1.5 > len(app.field.packages):
                x = self.find_available_pos()
                app.field.add_package(x)

    def find_available_pos(self):
        flag = True
        while flag:
            flag = False
            pos_to_spawn = (random.randint(100 // 20, 1300 // 20) * 20 - 10, random.randint(100 // 20, 800 // 20) * 20 - 10) 

            if app.field.station.pos[0]  <= pos_to_spawn[0] <= app.field.station.pos[0] + 200 and app.field.station.pos[1]  <= pos_to_spawn[1] <= app.field.station.pos[1]  + 100 + 10:
                flag = True
            for wall in app.field.obstacles:
                if wall.left_x  <= pos_to_spawn[0] <= wall.right_x  and wall.bot_y  <= pos_to_spawn[1] <= wall.top_y :
                    flag = True
                    break
            for storage in app.field.storages:
                if storage.left_x  <= pos_to_spawn[0] <= storage.right_x  and storage.bot_y  <= pos_to_spawn[1] <= storage.top_y :
                    flag = True
                    break
            if not flag:
                return (int(pos_to_spawn[0]-10), int(pos_to_spawn[1]-10))

    def add_package(self):
        if self.is_maintaining == 0:
            self.reset_except_id("is_packaging")
            if self.is_packaging == 1 or self.is_packaging == 2:
                self.is_packaging = 0
                self.ids.add_packages.text = "Создать"
                self.ids.add_packages.background_color = "cyan"
            else:
                self.is_packaging = 1
                self.ids.add_packages.text = "Перестать"
                self.ids.add_packages.background_color = (0, 0, 0, 0.8)


    def switch_generate(self):
        if self.is_maintaining == 0:
            if self.is_generating == 0:
                self.is_generating = 1
                self.ids.generate_package.text = "Перестать"
                self.ids.generate_package.background_color = (0, 0, 0, 0.8)
            elif self.is_generating == 1:
                self.is_generating = 0
                self.ids.generate_package.text = "Генерировать"
                self.ids.generate_package.background_color = "cyan"

class Wall(Widget):
    def __init__(self, first_point, second_point):
        super(Wall, self).__init__()
        #self.color = Color(1, 0, 0, 1)
        #self.canvas.add(self.color)
        self.left_x = (min(first_point[0], second_point[0]) // 20) * 20
        self.right_x = (max(first_point[0], second_point[0]) // 20 + 1) * 20
        self.top_y = (max(first_point[1], second_point[1]) // 20 + 1) * 20
        self.bot_y = (min(first_point[1], second_point[1]) // 20) * 20
        self.first_point = (self.left_x, self.bot_y)
        
        self.wallSize=(abs(self.right_x - self.left_x), abs(self.top_y - self.bot_y))
        self.texture = Image(rf"./images/wall.png").texture
        self.texture.wrap = 'repeat'
        self.texture.uvsize = (self.wallSize[0]//20, self.wallSize[1]//20)
        with self.canvas:
            self.ellipse = Rectangle(texture=self.texture, pos=(self.left_x, self.bot_y), size=self.wallSize)
        
    def __del__(self):
        del self

class Station(Widget):
    def __init__(self):
        super(Station, self).__init__()
        self.pos = (600, 400)
        self.station_size = (200, 100)
        with self.canvas:
            texture = Image(rf"./images/station.png").texture
            self.rect = Rectangle(texture=texture,pos=self.pos, size=self.station_size)
       
class Package(Widget):
    def __init__(self, pos):
        super(Package, self).__init__()
        self.pos = pos
        self.is_employed = False 
        self.storage = random.randint(0,3)
        self.life_time = 0
        self.weight = random.randint(2,4)
        self.event=Clock.schedule_interval(self.update_life_time, 1)
    
        with self.canvas:
            texture = Image(f"./images/package{self.storage}{random.randint(0, 1)}.png").texture
            self.ellipse = Rectangle(texture=texture, pos=self.pos, size=(20,20))
            self.label_weight = Label(text=f"x{self.weight - 1}", pos=(self.pos[0]-40, self.pos[1]-60), color=(0, 0, 0, 1))
            self.label_life_time = Label(text='0:00', pos=(self.pos[0]-40, self.pos[1]-20), color=(0, 0, 0, 1))

    def update_life_time(self, dt):
        minutes = self.life_time // 60
        seconds = self.life_time % 60
        self.label_life_time.text = f'{minutes}:{seconds:02d}'
        self.life_time += 1

    def update_position(self, new_pos):
        self.pos = new_pos
        self.ellipse.pos = self.pos
        self.label_weight.pos = (self.pos[0]-40, self.pos[1]-60)
    def __del__(self):
        Clock.unschedule(self.event)
        self.parent.remove_widget(self)
    def start_move(self):
        self.remove_widget(self.label_life_time)
        self.label_life_time.text = ''
        Clock.unschedule(self.event)
    
        
class Drone(Widget):
    def __init__(self, sizeDron=None, field_size=None,packages=None,obstacles=None,station=None):
        super(Drone, self).__init__()
        self.sizeDron = sizeDron
        self.field_size = field_size
        self.packages=packages
        self.station=station
        self.pos = (700, 440)
        self.indicator_power = 100
        self.waste_power = 0.2
        self.choose_package=None
        self.catch_package=False
        self.obstacles = obstacles
        self.current_step = 0
        self.charged=True
        self.packages_count=len(self.packages)
        self.wasty=1
        self.step=1
        self.drone_path=[]
        self.get_path_pakage()
        with self.canvas:
            texture = Image(r"./images/drone.png").texture
            self.ellipse = Rectangle(texture=texture, pos=self.pos, size=self.sizeDron)
            self.charge_percent = ProgressBar(max=100, size=(30, 50), pos=(self.pos[0], self.pos[1] + 10), value=self.indicator_power)
            self.percent_charge = Label(text=str(self.indicator_power), pos=(self.pos[0] - 65, self.pos[1] - 13), color=(0,0,0))
        self.event = Clock.schedule_interval(self.update, 1.0/10)

    def get_path_pakage(self):
        near_package=(None, None)
        for package in self.packages:
            if not(package.is_employed):
                storage=Storage(package.storage)
                path = a_star(self.pos, list(package.pos), self.obstacles) + a_star(list(package.pos),storage.enter, self.obstacles)
                if self.indicator_power - len(a_star(self.pos, list(package.pos), self.obstacles) + a_star(list(package.pos),storage.enter, self.obstacles)*package.weight + a_star(storage.enter, ((self.station.pos[0] + self.station.station_size[0]/2), (self.station.pos[1] + self.station.station_size[1]/2)-10), self.obstacles)) * self.waste_power  > 0:  
                    if near_package == (None, None) or len(path)<len(near_package[1]):
                        near_package=(package,path)
                    
        if near_package != (None, None):
            self.choose_package=near_package[0]
            self.wasty=near_package[0].weight
            self.choose_package.is_employed=True
            self.drone_path = near_package[1]

    def update(self, dt):
        
        if (self.packages_count != len(self.packages) and self.choose_package==None):
            self.get_path_pakage()
            self.packages_count=len(self.packages)
        if  self.current_step<len(self.drone_path) and  self.charged:
            self.move(self.current_step,self.drone_path)
            self.current_step += self.step
            
        
        self.ellipse.pos = self.pos
        
        

        if self.catch_package:
            self.choose_package.update_position(self.pos)
        if int(self.current_step)==len(self.drone_path):
            self.wasty=1
            self.step=1
            if  self.choose_package!=None:
                self.packages.remove(self.choose_package)
                self.choose_package.__del__()   
                self.choose_package=None
            self.drone_path = []
            self.current_step=0
            self.catch_package=False
            

            power_path=len(a_star(self.pos, ((self.station.pos[0] + self.station.station_size[0]/2), (self.station.pos[1] + self.station.station_size[1]/2)-10), self.obstacles)) * self.waste_power
            if self.indicator_power - (power_path + power_path*5.75)<0:
                self.drone_path= a_star(self.pos, ((self.station.pos[0] + self.station.station_size[0]/2), (self.station.pos[1] + self.station.station_size[1]/2)-10), self.obstacles)
            else:
                self.get_path_pakage()
        self.power()
        self.charge_percent.pos = (self.pos[0], self.pos[1] + 10)
        self.charge_percent.value = self.indicator_power
        self.percent_charge.pos = (self.pos[0] - 65, self.pos[1] - 13)
        self.percent_charge.text = str(int(self.indicator_power))
            
           
    def power(self):
        if self.catch_package==False and self.current_step==0 and check_collision(self.station.pos[0], self.station.pos[1], 200, 100, self.pos[0], self.pos[1], self.sizeDron[0], self.sizeDron[1]):
            if self.indicator_power < 100:
                self.charged=False
                self.indicator_power += self.waste_power*5    
            else:
                self.charged=True

    def __del__(self):
        Clock.unschedule(self.event)
        del self

    def move(self,current_step,nearest_path):
        direction_x = nearest_path[int(current_step)][0]
        direction_y = nearest_path[int(current_step)][1]

        new_pos = (direction_x, direction_y)
        
        if self.choose_package!= None and check_collision(new_pos[0], new_pos[1], self.sizeDron[0], self.sizeDron[1], self.choose_package.pos[0], self.choose_package.pos[1], 20, 20):
            self.catch_package = True
            self.step = 1/self.wasty
            
            self.choose_package.start_move()
                
      
        
        if self.indicator_power > 0:
            self.indicator_power -= self.waste_power
        self.pos = new_pos 
        
            
        

class Field(FloatLayout):
    def __init__(self, sizeField):
        super(Field, self).__init__(size_hint = (None, 1))
        self.sizeField = sizeField
        self.rect = Rectangle(pos=self.pos, size=self.sizeField)
        self.canvas.add(self.rect)
        self.create_field()
        self.size = sizeField
        self.drones = []
        self.packages = []
        self.walls = []
        self.station = Station()
        self.add_widget(self.station)
        self.obstacles=[]
        self.storages = [Storage(0), Storage(1), Storage(2), Storage(3)]
        
        for storage in self.storages:
            self.add_widget(storage)

    def mouse_pos(self, window, pos):
        self.label.text = str(pos)
        
    def add_drone(self):
        drone_to_add = Drone(sizeDron=(20, 20), field_size=self.size, packages=self.packages, obstacles=self.obstacles, station=self.station)
        self.drones.append(drone_to_add)
        self.add_widget(drone_to_add)
        app.drone_amount += 1

    def create_field(self):
        for i in range(0, 1400, 20):
            for j in range(0, 900, 20):
                with self.canvas:
                    texture = Image(r"./images/floorTile.png").texture
                    self.rectangle = Rectangle(texture=texture, pos=(i, j), size=(20, 20))

    def remove_drone(self):
        if app.drone_amount >= 1:   
            app.drone_amount -= 1     
            print(self.drones)
            drone_to_kill = self.drones.pop()
            if  drone_to_kill.choose_package!=None:
                drone_to_kill.choose_package.is_employed=False
            self.remove_widget(drone_to_kill)  
            drone_to_kill.__del__()    

    def add_package(self, pos):
        package_to_add = Package(pos)
        self.packages.append(package_to_add)
        self.add_widget(package_to_add)

    def add_wall(self, first_pos, second_pos):
        wall_to_add = Wall(first_pos, second_pos)
        self.add_widget(wall_to_add)
        self.obstacles.append(wall_to_add)

class myApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drone_amount = 0
        self.field = Field((1400, 900))
        self.boxLayout = BoxLayout()
       
    
    def build(self):
        self.boxLayout.add_widget(self.field)
        self.boxLayout.add_widget( SettingsWidget())
        return self.boxLayout

if __name__ == "__main__":
    app = myApp()
    app.run()
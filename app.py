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
import heapq

Config.set("graphics", "resizable", 0)
Config.set("graphics", "width", 1600)
Config.set("graphics", "height", 900)


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
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, goal, obstacles):
    start = tuple(start)
    goal = tuple(goal)
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while open_set:
        current_cost, current = heapq.heappop(open_set)

        if current == goal:
            break

        for next in neighbors(current, obstacles):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                heapq.heappush(open_set, (priority, next))
                came_from[next] = current

    path = reconstruct_path(came_from, start, goal)
    return path

def neighbors(pos, obstacles):
    x, y = pos
    possible_neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    
    valid_neighbors = [neighbor for neighbor in possible_neighbors if not has_collision(neighbor, obstacles)]
    return valid_neighbors

def has_collision(pos, obstacles):
    x, y = pos
    
    for obstacle in obstacles:
        if check_collision(x, y, 20, 20, obstacle.first_point[0], obstacle.first_point[1], obstacle.wallSize[0], obstacle.wallSize[1]):
            
            return True
    return False

def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


class Storage(Widget):
    def __init__(self, id, drop_point_1, drop_point_2, color):
        super(Storage, self).__init__()
        self.id = id
        self.drop_point_1 = drop_point_1
        self.drop_point_2 = drop_point_2
        self.left_x = min(self.drop_point_1[0], self.drop_point_2[0])
        self.right_x = max(self.drop_point_1[0], self.drop_point_2[0])
        self.top_y = max(self.drop_point_1[1], self.drop_point_2[1])
        self.bot_y = min(self.drop_point_1[1], self.drop_point_2[1])
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
        self.is_generating = 0
        self.is_deleteing = 0
        self.wall_pos = [(0, 0),(0, 0)]
        self.generatePackages = Clock.schedule_interval(self.generate_packages, 1)

    def remove_drone(self):
        if app.drone_amount >= 1:
            app.field.remove_drone()
        self.ids.drone_amount.text = str(app.drone_amount)

    def remove_wall(self):
        if self.is_deleteing == 0:
            self.is_deleteing = 1
            self.ids.deleting_walls.text = "Перестать"
        elif self.is_deleteing == 1:
            self.is_deleteing = 0
            self.ids.deleting_walls.text = "Удаление"

    def add_drone(self):
        app.field.add_drone()
        self.ids.drone_amount.text = str(app.drone_amount)

    def on_touch_up(self, touch):
        #TODO: отображать как будет выглядеть стена
        if self.is_deleteing == 1: 
            for wall in app.field.obstacles:   
                if wall.left_x <= touch.x <= wall.right_x and wall.bot_y <= touch.y <= wall.top_y:
                    wall_to_remove = app.field.obstacles[app.field.obstacles.index(wall)]
                    app.field.remove_widget(wall_to_remove)
                    app.field.obstacles.remove(wall_to_remove)
                    wall_to_remove.__del__()   


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

    def generate_packages(self, dt):
        if self.is_generating == 1:
            if len(app.field.drones) * 1.5 > len(app.field.packages):
                x = self.find_available_pos()
                print(x)
                app.field.add_package(x)

    def find_available_pos(self):
        flag = True
        while flag:
            flag = False
            pos_to_spawn = (random.randint(100, 1300), random.randint(100, 800))

            if app.field.station.pos[0] - 10 <= pos_to_spawn[0] <= app.field.station.pos[0] + 200 + 10 and app.field.station.pos[1] - 10 <= pos_to_spawn[1] <= app.field.station.pos[1]  + 100 + 10:
                flag = True
            for wall in app.field.obstacles:
                if wall.left_x - 10 <= pos_to_spawn[0] <= wall.right_x + 10 and wall.bot_y - 10 <= pos_to_spawn[1] <= wall.top_y + 10:
                    flag = True
                    break
            for storage in app.field.storages:
                if storage.left_x - 10 <= pos_to_spawn[0] <= storage.right_x + 10 and storage.bot_y - 10 <= pos_to_spawn[1] <= storage.top_y + 10:
                    flag = True
                    break
            if not flag:
                return pos_to_spawn

    def add_package(self):
        self.is_packaging = 1

    def switch_generate(self):
        if self.is_generating == 0:
            self.is_generating = 1
            self.ids.generate_package.text = "Перестать"
        elif self.is_generating == 1:
            self.is_generating = 0
            self.ids.generate_package.text = "Генерировать"

class Wall(Widget):
    def __init__(self, first_point, second_point):
        super(Wall, self).__init__()
        self.first_point = first_point
        self.second_point = second_point
        self.color = Color(1, 0, 0, 1)
        self.canvas.add(self.color)
        self.left_x = min(self.first_point[0], self.second_point[0])
        self.right_x = max(self.first_point[0], self.second_point[0])
        self.top_y = max(self.first_point[1], self.second_point[1])
        self.bot_y = min(self.first_point[1], self.second_point[1])
        self.wallSize=(second_point[0] - first_point[0], second_point[1] - first_point[1])
        with self.canvas:
            self.ellipse = Rectangle(pos=first_point, size=self.wallSize)
        
    def __del__(self):
        del self

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
        self.storage = random.randint(0,3)
        self.life_time = 0
        self.weight = str(random.randint(1,10))

        self.colors = [(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)]
        self.color = Color(self.colors[self.storage])

        self.event=Clock.schedule_interval(self.update_life_time, 1)

        with self.canvas:
            Color(*map(lambda x: x*0.7, self.colors[self.storage]))
            self.ellipse = Rectangle(pos=map(lambda x: x-10, pos), size=(20,20))
            self.label_weight = Label(text=self.weight, pos=(self.pos[0]-50, self.pos[1]-50), color=(0, 0, 0, 1))
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
    def __init__(self, sizeDron=None, field_size=None,packages=None,obstacles=None,station=None):
        super(Drone, self).__init__()
        self.sizeDron = sizeDron
        self.field_size = field_size
        self.packages=packages
        self.station=station
        self.pos = (700, 500)
        self.indicator_power = 100
        self.gruz=None
        self.color = Color(0, 0, 0, 1)
        self.canvas.add(self.color)
        self.obstacles = obstacles
        self.current_step=0
        self.package_weight = 1
        start = (self.pos)
        goal = (50,50)
        self.path = a_star(start, goal, self.obstacles)
        # Изменил создание Ellipse через инструкции рисования
        with self.canvas:
            self.ellipse = Ellipse(pos=self.pos, size=self.sizeDron)
            self.charge_percent = ProgressBar(max=100, size=(30, 50), pos=(self.pos[0], self.pos[1] + 10), value=self.indicator_power)
            self.percent_charge = Label(text=str(self.indicator_power), pos=(self.pos[0] - 65, self.pos[1] - 13), color=(0,0,0))
        self.event = Clock.schedule_interval(self.update, 1.0/100)

    def update(self, dt):
        if self.indicator_power>0 and self.current_step<len(self.path):
            self.move(self.current_step)
        
        self.ellipse.pos = self.pos
        self.charge_percent.pos = (self.pos[0], self.pos[1] + 10)
        self.charge_percent.value = self.indicator_power
        self.percent_charge.pos = (self.pos[0] - 65, self.pos[1] - 13)
        self.percent_charge.text = str(int(self.indicator_power))
        self.power()

        if (self.gruz != None):
            self.gruz.update_position(self.pos)
        self.current_step += int(2/(self.package_weight/5))
        print( int(2/(self.package_weight/5)))
        
    def power(self):
        if check_collision(self.station.pos[0], self.station.pos[1], 200, 100, self.pos[0], self.pos[1], 20, 20):
            if self.indicator_power < 111:
                self.indicator_power += 0.05     

    def __del__(self):
        Clock.unschedule(self.event)
        del self

    def move(self,current_step):
        direction_x = self.path[current_step][0]
        direction_y = self.path[current_step][1]

        new_pos = (direction_x, direction_y)
        x_condition = 0 <= new_pos[0]+self.sizeDron[0] <= self.field_size[0]
        y_condition = 0 <= new_pos[1]+self.sizeDron[1] <= self.field_size[1]
        if(self.gruz==None):
            for package in self.packages:
                if check_collision(new_pos[0], new_pos[1], 20, 20, package.pos[0], package.pos[1], 20, 20):
                    self.gruz=package
                    self.package_weight = int(self.gruz.weight) 
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
        self.obstacles=[]

        self.storages = [Storage(0, (0, 0), (100, 100), (0, 0, 0, 1)),
                        Storage(1, (1300, 0), (1400, 100), (1, 0, 0, 1)),
                        Storage(2, (1300, 800), (1400, 900), (0, 1, 0, 1)),
                        Storage(3, (0, 800), (100, 900), (0, 0, 1, 1))]
        for storage in self.storages:
            self.add_widget(storage)
        
    def add_drone(self):
        drone_to_add = Drone(sizeDron=(20, 20), field_size=self.size, packages=self.packages, obstacles=self.obstacles, station=self.station)
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
        self.add_widget(wall_to_add)
        self.obstacles.append(wall_to_add)


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
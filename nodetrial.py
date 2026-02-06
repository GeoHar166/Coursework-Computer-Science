import pygame
import math
import pygame_gui
import threading
import time
import random
import py_singl_slider
pygame.init()

carindex = 0





# CD
#AEFG
#BHIJ
# KL





lanelinks = {
    "A" : [["E"],[0,333]], #  +25 to coordinate to have lane locked into grid 
    "B" : [["H"],[0,666]],
    "C" : [["E"],[600,0]],
    "D" : [["F"],[1200,0]],
    "E" : [["A","C","F","H"],[600,333]],    # 600,333 (800,100 for special)
    "F" : [["D","E","G","I"],[1200,333]],
    "G" : [["F"],[1800,333]],
    "H" : [["E","B","I","K"],[600,666]],
    "I" : [["F","H","J","L"],[1200,666] ],
    "J" : [["I"],[1800,666]],
    "K" : [["H"],[600,1000]],
    "L" : [["I"],[1200,1000]]
}

# lanelinks = {
#     "A" : [["J","B","D"],[25,575]], #  +25 to coordinate to have lane locked into grid 
#     "B" : [["A","C"],[25,25]],
#     "C" : [["B","D"],[275,25]],
#     "D" : [["C","E","A"],[275,575]],    
#     "E" : [["D","F"],[675,575]],        #675
#     "F" : [["E","G"],[575,25]],
#     "G" : [["F","H"],[1475,25]],
#     "H" : [["G","I"],[1075,375]],
#     "I" : [["H","J"],[1075,875]],
#     "J" : [["I","A"],[275,875]]
# }


lanelinksexits = []
for key in lanelinks:
    if len(lanelinks[key][0]) == 1:
        lanelinksexits.append(key)


    #GLOBAL VARS

# colours for later use
green = (30,100,30)
grey = (100,100,100)
"""
#white = (255, 255, 255)
#red = (180, 0, 0)
#blue = (0, 0, 180)
#black = (0,0,0)
"""

width = 1800        
height = 1000       #pixel size of window

screen = pygame.display.set_mode((width,height))    #make screen for display

cars = []
lights = []
traffic_lights = {}

carpngs = ["car.png","newcar.png","orangecar.png"]

vehicles_per_second = [2.0,1.0,0.5,0.5,0]    #   master,cars,lorrys,motorbikes



#pygame.Rect.collidepoint() !!!!!!!!
class vehicle:
    def __init__(self,speed,start,finish):
        self.angle = 0

        self.numplate = None

        self.basespeed = speed
        self.speed = self.basespeed

        self.paused = False
        self.behindcar = False

        self.start,self.finish = start,finish
        self.startx,self.starty = lanelinks[start][1]
        self.finishx,self.finishy = lanelinks[finish][1]

        self.x,self.y = self.startx,self.starty

        self.target = 1

        table = dykstras(self.start,nodes)
        self.getpath(table)     

    def draw(self): 
        font = pygame.font.Font(None,36)
        rotated_img = pygame.transform.rotate(self.car_img, self.angle) #self.angle
        numplate = font.render(str(self.numplate),True,(255,255,255))
        t_rect = numplate.get_rect(center=(self.x, self.y))
        rect = rotated_img.get_rect(center=(self.x, self.y)) 
        screen.blit(rotated_img, rect)
        screen.blit(numplate,t_rect)

    def previous_node(self):
        """return the last node traversed by the car"""
        return self.path[self.target - 1]

    def target_node(self):
        """return the next node to be traversed by the car"""
        return self.path[self.target]

    def getpath(self,table):
        self.path = dykstrapath(self.start,self.finish,table)
        self.next = self.path[self.target]
        self.nextx,self.nexty = lanelinks[self.next][1]
    
    def move(self, dt):
        distance = self.speed * dt

        while distance > 0:
            try:
                dx = self.nextx - self.x
                dy = self.nexty - self.y
            except IndexError:
                dx,dy = 0,0

            distance_to_next = math.hypot(dx,dy) # straight line distance between car and next point # pythagorus

            if distance_to_next <= distance:
                # Move to the next node and go around the loop again
            
                if self.target == len(self.path) - 1:
                    # there are no more nodes, so return indicating termination  
                    return False
                else:
                    self.x, self.y = lanelinks[self.path[self.target]][1]
                    self.target += 1 # increment target node pointer
                    self.nextx, self.nexty = lanelinks[self.path[self.target]][1]
                    distance -= distance_to_next
            else:
                # Move partial distance towards next node

                # dx,dy -> x,y distance from [target-1] to [target]
                # distance -> straight line distance from target-1 to target
                xchangeperunitlength = dx / distance_to_next
                ychangeperunitlength = dy / distance_to_next

                self.x += xchangeperunitlength * distance
                self.y += ychangeperunitlength * distance

                angle_rad = math.atan2(xchangeperunitlength,ychangeperunitlength)       # 0 is right, 180/-180 left, 90 up, -90 down
                self.angle = math.degrees(angle_rad) - 90       #updated angle algorithm  
                distance = 0
                                
        return True

    def dist_to_targetnode(self):
       dx,dy = self.nextx - self.x, self.nexty - self.y
       return(math.hypot(dx,dy))

    def dist_from_prevnode(self):
        dx,dy = lanelinks[self.previous_node()][1][0] - self.x, lanelinks[self.previous_node()][1][1] - self.y
        return(math.hypot(dx,dy))

    def nearcar(self,cars):
        closecars = 0
        if self.paused == False:
            for car in cars:
                if car is self: #dont compare to itself
                    continue

                if car.vehicle == "lorry":
                    min_distance = self.min_distance + 10
                elif car.vehicle == "car":
                    min_distance = self.min_distance
                elif car.vehicle == "motorbike":
                    min_distance = self.min_distance

                if car.previous_node() == self.previous_node() and car.target_node() == self.target_node():
                    # same source and destination
                    # determine distance along edge for both cars
                    # if too close, decide if we are the car behind (less far down the edge) then slow down

                    carremainingdist = car.dist_to_targetnode()
                    selfremainingdist = self.dist_to_targetnode()

                    if abs(selfremainingdist-carremainingdist) < (min_distance-(min_distance/4)) and selfremainingdist > carremainingdist:
                        closecars += 1
                        if self.speed > car.speed:
                            self.speed -= self.speed/2
                            """
                        self.speed = round(self.speed,1)"""

                    elif abs(selfremainingdist-carremainingdist) < min_distance and selfremainingdist > carremainingdist:
                        closecars += 1
                        if self.speed > car.speed:
                            self.speed -= self.speed/6
                            """
                        self.speed = round(self.speed,1)"""

                    """ # elif car.previous_node() == self.previous_node(): 
                #     # same source, different destination
                #     # determine distance along edge for both cars
                #     # if too close, decide if we are the car behind (less far down the edge) then slow down
                #     # this is not a realistic interaction and only occurs due to the graphical display of the simulation
                """

                elif car.target_node() == self.target_node():

                    # different source, same destination
                    # determine distance away from node (for self and car) if too close, furthest slows down

                    if self.speed != 0 and car.speed != 0 and car.nearlight(lights) == False:
                        
                        carremainingtime = car.dist_to_targetnode()/car.speed
                        selfremainingtime = self.dist_to_targetnode()/self.speed

                        if abs(selfremainingtime) > abs(carremainingtime):
                            closecars += 1
                            if self.speed > car.speed:
                                self.speed -= self.speed/6
                            self.speed = round(self.speed,1)
                    
                    else:
                        if self.dist_to_targetnode() + car.dist_to_targetnode() < min_distance:
                            if self.dist_to_targetnode() < car.dist_to_targetnode() and car.nearlight(self.lights) == False:
                                closecars += 1
               
                elif car.previous_node() == self.target_node() and car.target_node() != self.previous_node():
                    # self desination is car's source
                    # determine self distance to destination and determine distance car has travelled from source
                    # add these and if too close, self slow down
                    cartravelleddist = car.dist_from_prevnode()
                    selfremainingdist = self.dist_to_targetnode()

                    if abs(cartravelleddist) < min_distance and abs(selfremainingdist) < min_distance:
                        closecars += 1
                        if self.speed > car.speed:
                            self.speed -= self.speed/6
                        self.speed = round(self.speed,1)
            
                """# elif car.target_node() == self.previous_node():
                #     # does not matter as it is car's responsibility to slow down"""
                    
            if closecars == 0:
                if self.speed < self.basespeed:
                    self.speed += (self.basespeed-self.speed)/10

                self.speed = round(self.speed,1)
                    
        if self.speed < 1:
            self.speed = 0

    def nearlight(self,lights):
        self.lights = lights
        for light in lights:
            if light.state != 2:
                if (self.angle == 0 and self.x > light.x) or (self.angle == -180 and self.x < light.x) or (self.angle == 90 and self.y < light.y) or (self.angle == -90 and self.y > light.y):
                    pass
                else:
                    if math.hypot((light.x-self.x),(light.y-self.y)) < self.min_distance and self.angle == light.angle:
                        if math.hypot((light.x-self.x),(light.y-self.y)) < self.min_distance/4:
                            self.speed -= self.basespeed/2
                        else:
                            self.speed -= self.basespeed/10
                        if self.speed < 1:
                            self.speed = 0
                        return True


class car(vehicle):
    def __init__(self,speed,start,finish):
        self.vehicle = "car"
        self.car_img = pygame.image.load(random.choice(carpngs))
        self.car_img = pygame.transform.scale(self.car_img,(70,40))  
        self.min_distance = 80
        super().__init__(speed,start,finish)

class lorry(vehicle):
    def __init__(self,speed,start,finish):
        self.vehicle = "lorry"
        self.car_img = pygame.image.load("lorry.png")
        self.car_img = pygame.transform.scale(self.car_img,(140,50))
        self.min_distance = 110
        super().__init__(speed,start,finish)

class motorbike(vehicle):
    def __init__(self,speed,start,finish):
        self.vehicle = "motorbike"
        self.car_img = pygame.image.load("motorbike.png")
        self.car_img = pygame.transform.scale(self.car_img,(60,40))
        self.min_distance = 80
        super().__init__(speed,start,finish)
    

class trafficlight:
    def __init__(self,x,y,angle):
        self.x = x
        self.y = y
        self.state = 0
        self.light_img = pygame.image.load("trafficlightG.png")
        self.light_img = pygame.transform.scale(self.light_img,(15,35)) 
        self.rectlight = self.light_img.get_rect(center=(x,y))
        self.timer = 0.0
        self.lightlengths = [3.0,0.5,3.0,0.8]
        self.angle = angle

        # print("x:",self.x,"     y:",self.y,"    degangle:",self.angle,"     radangle",math.radians(self.angle))

    def changecolour(self,numlights):
        self.state = (self.state+1)%4 # %4 because 4 states

        self.draw()

    """
    def changebyclick(self):
        self.state = (self.state+2)%4
        if self.state == 0:
            self.light_img = pygame.image.load("trafficlightG.png")
        elif self.state == 1:
            self.light_img = pygame.image.load("trafficlightY.png")    
        elif self.state == 2:
            self.light_img = pygame.image.load("trafficlightR.png")  
        elif self.state == 3:
            self.light_img = pygame.image.load("trafficlightRY.png")  
        self.light_img = pygame.transform.scale(self.light_img,(13,35)) 
        self.rectlight = self.light_img.get_rect(center=(self.x,self.y))
    """

    def draw(self):
        if self.state == 0:
            self.light_img = pygame.image.load("trafficlightR.png")
        elif self.state == 1:
            self.light_img = pygame.image.load("trafficlightRY.png")
        elif self.state == 2:
            self.light_img = pygame.image.load("trafficlightG.png")  
        elif self.state == 3:
            self.light_img = pygame.image.load("trafficlightY.png")  
            
        self.light_img = pygame.transform.scale(self.light_img,(13,35)) 
        rotated_img = pygame.transform.rotate(self.light_img, self.angle-90) 
        rect = rotated_img.get_rect(center=(self.x, self.y)) 
        screen.blit(rotated_img, rect)
    
        # self.light_img = pygame.transform.scale(self.light_img,(13,35)) 
        # self.rectlight = self.light_img.get_rect(center=(self.x,self.y))
        # screen.blit(self.light_img,self.rectlight)      
            

def lanedraw(screen,start,end):
        #pygame.draw.line(screen,colour,(x,y),(x,y),width)
        pygame.draw.line(screen,(150,150,150),start,end,50)     #change so width is 100 when 2 way road

def lightatnode_init(node):
    traffic_lights[node] = []

    traffic_lights[node].append(trafficlight((lanelinks[node][1][0]-67.5),(lanelinks[node][1][1]-31.5), 0))        #nw
    traffic_lights[node].append(trafficlight((lanelinks[node][1][0]+31.5),(lanelinks[node][1][1])-67.5, -90))         #ne
    traffic_lights[node].append(trafficlight((lanelinks[node][1][0]+67.5),(lanelinks[node][1][1])+31.5, -180))       #se
    traffic_lights[node].append(trafficlight((lanelinks[node][1][0]-31.5),(lanelinks[node][1][1]+67.5), 90))      #sw

    traffic_lights[node][0].state = 2

    for light in traffic_lights[node]:
        lights.append(light)

def lightatnode_change(node,rotationnum):
    traffic_lights[node][rotationnum].changecolour(len(traffic_lights[node]))



#GLOBAL DYKSTRA FUNCTIONS:
def dykstras_nodes_create():
    nodes = {}
    for link in lanelinks.keys():
        nodes[link] = {}            
        for linklink in lanelinks[link][0]:
            dist = find_node_distance(link,linklink)
            nodes[link][linklink] = dist #+ self.traffic_weight
    return nodes

def find_node_distance(node1,node2):
    distanceAx = lanelinks[node1][1][0]-lanelinks[node2][1][0]  # x-x
    distanceBy = lanelinks[node1][1][1]-lanelinks[node2][1][1]  # y-y
    distanceCtotal = math.sqrt((distanceAx**2)+(distanceBy**2)) # a^2 + b^2 = c^2
    return distanceCtotal

def dykstras_table(visited,unvisited,table,nodes): 
    smallestnode = unvisited[0]

    for node in table:  #choose the smallest (distance) unvisited node
        if node in unvisited:
            if table[node][1] < table[smallestnode][1]:
                smallestnode = node

    currentnode = smallestnode

    for node in nodes[currentnode]:
        shortestpathposibility = table[currentnode][1] + int(nodes[currentnode][node])

        if table[node][1] > shortestpathposibility:
            table[node][1] = shortestpathposibility #   shortestdist = dist
            table[node][0] = currentnode            #   previousnode = currentnode

        elif table[node][1] == shortestpathposibility and random.randint(1,2) == 2:
            table[node][1] = shortestpathposibility #   shortestdist = dist
            table[node][0] = currentnode 

    visited.append(currentnode)
    unvisited.remove(currentnode)
    return visited,unvisited,table

def dykstrapath(firstnode,endnode,table): 
    #SELECT PATH
    # distance = table[endnode][1]

    path = [endnode]
    nodefind = endnode
    while path[0] != firstnode:
        path.insert(0,table[nodefind][0])
        nodefind = table[nodefind][0]
    return path

def dykstras(firstnode,nodes):
    """
    initialise the table for DSP
    """

    visited = []
    unvisited = list(lanelinks.keys())
    table = {}

    for node in lanelinks:
        #node   prevnode    shortestdist
        table[node] = [None,9999]
    table[firstnode] = [None,0]



    while len(unvisited) != 0:
        visited,unvisited,table = dykstras_table(visited,unvisited,table,nodes)
    
    return table
#END OF DYKSTRA

nodes = dykstras_nodes_create()

def empty_enterances():
    empty = True
    emptynum = len(lanelinksexits)
    for c in cars:
        for enterance in lanelinksexits:
            if math.hypot(c.x-lanelinks[enterance][1][0],c.y-lanelinks[enterance][1][1]) < 100:
                emptynum -= 1

    if emptynum == 0:
        empty = False
    return empty

def spawn_car():
    global carindex

    last_spawn_time = 0
    

    while True:



        vehicles_spawn = 60/round(vehicles_per_second[0])   #   time needed to wait between each spawn
        cars_spawn = round(vehicles_per_second[1])
        lorrys_spawn = round(vehicles_per_second[2])
        motorbikes_spawn = round(vehicles_per_second[3])
        total = round(vehicles_per_second[4])

        now = time.monotonic()

        if empty_enterances() == True and now - last_spawn_time >= vehicles_spawn:
            last_spawn_time = now
            randpathloop = True
            while randpathloop == True:

                rand1 = random.choice(lanelinksexits)
                rand2 = random.choice(lanelinksexits)

                occupied = False
                for c in cars:
                    if math.hypot(c.x-lanelinks[rand1][1][0],c.y-lanelinks[rand1][1][1]) < 50:
                        occupied = True
                        break       

                if not occupied and rand1 != rand2:
                    randpathloop = False

            choose_vehicle = random.randint(0,total)
                # choose random vehicle (most likely a car)
            if choose_vehicle <= cars_spawn:
                carobj = car(random.randint(125,175),rand1,rand2)
            elif choose_vehicle <= cars_spawn + lorrys_spawn:
                carobj = lorry(random.randint(100,150),rand1,rand2)
            elif choose_vehicle <= cars_spawn + lorrys_spawn + motorbikes_spawn:
                carobj = motorbike(random.randint(150,200),rand1,rand2)

            carobj.numplate = carindex
            cars.append(carobj)         # number on car for debugging
            carindex += 1

        time.sleep(0.01)

def run_threaded(function):
    thread = threading.Thread(target=function)
    thread.start()



def main():    

    running = True
    

#DRAW THIS BEFORE LOOP STARTS AS IT DOESNT CHANGE

    clock = pygame.time.Clock()
    fps = 30
    

    #cars.append(car3)
    
    run_threaded(spawn_car)

    nodes_with_lights = {}
    lightatnode_init("E")
    lightatnode_init("F")
    lightatnode_init("H")
    lightatnode_init("I")

#   nodes_with_lights[node] = [lightindex,phase,nextlight,greentime,yellowtime,light_change_timer]
    nodes_with_lights["E"] = [0,0,0,5.0,1.0,0]
    nodes_with_lights["F"] = [0,0,0,5.0,1.0,0]
    nodes_with_lights["H"] = [0,0,0,5.0,1.0,0]
    nodes_with_lights["I"] = [0,0,0,5.0,1.0,0]
    

    last = time.time()

# stats window
    vehicle_slidernum = 3   # how many sliders are there (- top slider)
    sliders = []
    y_coord = 175   # starting y coordinate for sliders (increases by 75 each iteration)

    sliders.append([py_singl_slider.PySinglSlider(x=1485,y=y_coord,min_value=2.0,max_value=100.0,initial_value=60.0),y_coord])
    
    for i in range(vehicle_slidernum):
        y_coord += 75
        sliders.append([py_singl_slider.PySinglSlider(x=1485,y=y_coord,min_value=2.0,max_value=100.0,initial_value=20.0),y_coord])
        

        """
    slider1 = py_singl_slider.PySinglSlider(x=1475,y=100,min_value=0,max_value=100,initial_value=20)
    slider2 = py_singl_slider.PySinglSlider(x=1475,y=150,min_value=0,max_value=100,initial_value=20)
    slider3 = py_singl_slider.PySinglSlider(x=1475,y=200,min_value=0,max_value=100,initial_value=20)
    slider4 = py_singl_slider.PySinglSlider(x=1475,y=250,min_value=0,max_value=100,initial_value=20)
    slider5 = py_singl_slider.PySinglSlider(x=1475,y=300,min_value=0,max_value=100,initial_value=20)
    """

    while running:
        
#HERE FOR INPUTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("Please kill the Terminal")
            # if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:    # if user clicks the screen
            for slider in sliders:
                slider[0].listen_event(event)

        dt = clock.tick(fps)/1000   # milliseconds
        now = time.time()
        if now - last > 1:
            print(dt, now - last)
        last = now

        



#DRAW HERE FOR CHANGING THINGS


        screen.fill(green) #clear screen so no repeated "draws"
        for node in lanelinks:
            for i in lanelinks[node][0]:
                lanedraw(screen,lanelinks[node][1],lanelinks[i][1])
            

#TRAFFIC LIGHT STUFF

# A B C D
# A turns RY, B turns Y
# A turns R, B turns G
# B turns RY, C turns Y
# B turns R, C turns G
# C turns RY etc

        for node in nodes_with_lights:

            nodes_with_lights[node][5] += dt

            currentlight = nodes_with_lights[node][0]
            nodes_with_lights[node][2] = (nodes_with_lights[node][0]+1)%len(traffic_lights[node])
        #   nextlight =                 #(lightindex)+1 %...
            
            if nodes_with_lights[node][1] == 0:
                if nodes_with_lights[node][5] >= nodes_with_lights[node][3]:
                                    #>= greentime
                    traffic_lights[node][currentlight].state = 1
                    traffic_lights[node][nodes_with_lights[node][2]].state = 3
                    nodes_with_lights[node][1] = 1
                    nodes_with_lights[node][5] = 0

            elif nodes_with_lights[node][1] == 1:
                if nodes_with_lights[node][5] >= nodes_with_lights[node][4]:
                    traffic_lights[node][currentlight].state = 0
                    traffic_lights[node][nodes_with_lights[node][2]].state = 2
                    nodes_with_lights[node][0] = nodes_with_lights[node][2]
                    nodes_with_lights[node][1] = 0
                    nodes_with_lights[node][5] = 0


        for lightkey in traffic_lights.keys():
            for light in traffic_lights[lightkey]:
                light.draw()

#OTHER STUFF  
        for c in cars:
            c.nearcar(cars)
            c.nearlight(lights)

        for c in cars.copy():
            moving = c.move(dt)
            c.draw()
            #c.nearnode()
            if not moving:
                cars.remove(c)
            

        #time_delta = clock.tick(fps)/1000.0 #ui clock

# STATS "WINDOW"

        pygame.draw.rect(screen,grey,(1450,50,300,900))

        for slider in sliders:
            slider[0].render(screen)

        font = pygame.font.Font(None,25)
        slidertexts = []
        slidertexts.append(font.render(f"Vehicles per minute: {sliders[0][0].value:.2f}",True,(0,0,0)))
        slidertexts.append(font.render(f"Chance for car: {sliders[1][0].value:.2f}",True,(0,0,0)))
        slidertexts.append(font.render(f"Chance for lorry: {sliders[2][0].value:.2f}",True,(0,0,0)))
        slidertexts.append(font.render(f"Chance for motorbike: {sliders[3][0].value:.2f}",True,(0,0,0)))

        for slidertext in enumerate(slidertexts):
            screen.blit(slidertext[1],(1470,sliders[slidertext[0]][1]-20))

        vehicles_per_second[0] = sliders[0][0].value    # master   
        vehicles_per_second[1] = sliders[1][0].value    # cars
        vehicles_per_second[2] = sliders[2][0].value    # lorrys
        vehicles_per_second[3] = sliders[3][0].value    # motorbikes
        vehicles_per_second[4] = vehicles_per_second[3] + vehicles_per_second[2] + vehicles_per_second[1] + vehicles_per_second[0]


        pygame.display.update()


main()
pygame.quit()

# traffic lights go right way                                                       # done
# multiple traffic lights                                                           # done
# random path                                                                       # done
# maybe overlapping objects in order to "stresst" stress test                       # done

# error at entry nodes stopping                                                     # done
# error at crossing nodes traffic                                                   # done

# cars shouldnt stop at traffic lights if they are already past the traffic light   # done

# new vehicles (lorry,motorbike,bus):                                               
#       if nearcar car is a lorry, mindist is larger (because larger img)           # done

# new roads (curved, T-junction)

# add UI
# add statistics in UI

# change speed limits:
#       select a road, option menu pops up

# add tools to change traffic light timings:
#       select a node, option menu pops up

# more vehicles (bus?)

# traffic lights can be on diagonal roads ~~> Tx = 74.5sin(25-arctan((x1-x2)/y1-y2))),  Ty = 74.5cos(25-arctan((x1-x2)/y1-y2)))

# spawn car at selected enterance
# block roads

# slider for main "spawning"
# slider for individual vehicle %
# slider for traffic light rotation speed
# toggle for traffic lights on or off
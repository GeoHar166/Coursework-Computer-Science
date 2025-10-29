import pygame
import math
import pygame_gui
import threading
import time
import sys

lanelinks = {
    "A" : [["J","B","D"],[25,575]], #  +25 to coordinate to have lane locked into grid 
    "B" : [["A","C"],[25,25]],
    "C" : [["B","D"],[275,25]],
    "D" : [["C","E","A"],[275,575]],
    "E" : [["D","F"],[675,575]],
    "F" : [["E","G"],[575,25]],
    "G" : [["F","H"],[1475,25]],
    "H" : [["G","I"],[1075,375]],
    "I" : [["H","J"],[1075,875]],
    "J" : [["I","A"],[275,875]]

}

    #GLOBAL VARS
# colours for later use
#white = (255, 255, 255)
#red = (180, 0, 0)
green = (30,100,30)
#blue = (0, 0, 180)
#black = (0,0,0)
grey = (100,100,100)

width = 1800        
height = 1000       #pixel size of window

screen = pygame.display.set_mode((width,height))    #make screen for display

cars = []



#pygame.Rect.collidepoint() !!!!!!!!
class car:
    def __init__(self,speed,start,finish):
        self.angle = 0

        self.basespeed = speed
        self.speed = self.basespeed

        self.paused = False
        self.behindcar = False

        self.start,self.finish = start,finish
        self.startx,self.starty = lanelinks[start][1]
        self.finishx,self.finishy = lanelinks[finish][1]

        self.x,self.y = self.startx,self.starty

        self.target = 1

        self.car_img = pygame.image.load("car.webp")
        self.car_img = pygame.transform.scale(self.car_img,(70,40))  

        table = dykstras(self.start,nodes)
        self.getpath(table)     

    def draw(self): 
        rotated_img = pygame.transform.rotate(self.car_img, self.angle) 
        rect = rotated_img.get_rect(center=(self.x, self.y)) 
        screen.blit(rotated_img, rect)

#    def createpath(self,endx,endy):

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

                angle_rad = math.atan2(-xchangeperunitlength,ychangeperunitlength)       # 0 is right, 180 left, 90 up, -90 down
                self.angle = math.degrees(angle_rad)        #updated angle algorithm  
                distance = 0
                                
        return True

        # # direction
        # if distance != 0:
        #     dir_x = dx / distance
        #     dir_y = dy / distance
        # else:
        #     dir_x,dir_y = 0,0

        # # actually move
        # if self.speed * dt > 0:
        #     self.x += dir_x * self.speed * dt
        #     self.y += dir_y * self.speed * dt

        #     angle_rad = math.atan2(-dir_y, dir_x)       # 0 is right, 180 left, 90 up, -90 down
        #     self.angle = math.degrees(angle_rad)        #updated angle algorithm   
        # return True 

    def nearcar(self,cars):
        closecars = 0
        if self.paused == False:
            for car in cars:
                if car is self: #dont compare to itself
                    continue
                    
                distance = math.hypot(self.x - car.x, self.y - car.y )  # distance between car and other cars on the road

                if distance <= 110:
                    self.behindcar = True
                    if self.speed >= car.speed:
                        self.speed = car.speed
                        print("close", self.x, self.y, car.x, car.y, distance, self.speed, car.speed)
                        sys.exit()
                    if distance <= 100:
                        self.speed -= self.speed/10
                        print("too close")
                        sys.exit()
                    closecars += 1
                    
                    
            if closecars == 0:
                if self.speed < self.basespeed:
                    self.speed += (self.basespeed-self.speed)/10
                    

    # def nearnode(self):
    #     for node in lanelinks.keys():
    #         distance = math.hypot(self.x - lanelinks[node][1][0], self.y - lanelinks[node][1][1])
    #         if distance < 50:
    #             if self.speed > self.basespeed*0.75:
    #                 self.speed -= (self.basespeed -self.speed)/10
    #             else:
    #                 self.speed = 0.5
            
    #         else:
    #             if self.speed < self.basespeed:
    #                 self.speed += (self.basespeed-self.speed)/10
    #             else:

#pseudo code:
# if slowed down, check around to see if there are any nearby cars
# 


class lane:
    def __init__(self):
        pass

def lanedraw(screen,start,end):
        #pygame.draw.line(screen,colour,(x,y),(x,y),width)
        pygame.draw.line(screen,(150,150,150),start,end,50)     #change so width is 100 when 2 way road


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

        if table[node][1] >= shortestpathposibility:
            table[node][1] = shortestpathposibility #   shortestdist = dist
            table[node][0] = currentnode            #   previousnode = currentnode

    visited.append(currentnode)
    unvisited.remove(currentnode)
    return visited,unvisited,table

def dykstrapath(firstnode,endnode,table): 
    #SELECT PATH
    distance = table[endnode][1]

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

def spawn_car():
    while True:
        carobj = car(150,"B","I")
        cars.append(carobj)
        time.sleep(60/60)

def run_threaded(function):
    thread = threading.Thread(target=function)
    thread.start()


#
def main():    

    running = True
    

#DRAW THIS BEFORE LOOP STARTS AS IT DOESNT CHANGE

        # rect = pygame.Rect(0,0,100,100)
        # rect.center = (lanelinks[node][1])
        # pygame.draw.rect(screen,(180,180,180),rect)

    clock = pygame.time.Clock()
    fps = 30
        

    #cars.append(car3)

    
    run_threaded(spawn_car) 
        

    last = time.time()

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        dt = clock.tick(fps)/1000   # milliseconds
        now = time.time()
        if now - last > 1:
            print(dt, now - last)
        last = now

#DRAW HERE FOR CHANGING THINGS

        # for car in cars:
        #     # if coords == coords_of_node:
        #     #     redo dykstras


        screen.fill(green) #clear screen so no repeated "draws"
        for node in lanelinks:
            for i in lanelinks[node][0]:
                lanedraw(screen,lanelinks[node][1],lanelinks[i][1]) 

#OTHER STUFF  

        for c in cars.copy():
            moving = c.move(dt)
            c.draw()
            #c.nearnode()
            if not moving:
                cars.remove(c)
            
        for c in cars:
            c.nearcar(cars)
            

        #time_delta = clock.tick(fps)/1000.0 #ui clock

        pygame.display.update()






main()
pygame.quit()
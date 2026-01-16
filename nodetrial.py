import pygame
import math
import pygame_gui
import threading
import time
import random


lanelinks = {
    "A" : [["E"],[0,333]], #  +25 to coordinate to have lane locked into grid 
    "B" : [["H"],[0,666]],
    "C" : [["E"],[600,0]],
    "D" : [["F"],[1200,0]],
    "E" : [["A","C","F","H"],[600,333]],
    "F" : [["D","E","G","I"],[1200,333]],
    "G" : [["F"],[1800,333]],
    "H" : [["E","B","I","K"],[600,666]],
    "I" : [["F","H","J","L"],[1200,666] ],
    "J" : [["I"],[1800,666]],
    "K" : [["H"],[600,1000]],
    "L" : [["I"],[1200,1000]]

}

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

        self.car_img = pygame.image.load("car.png")
        self.car_img = pygame.transform.scale(self.car_img,(70,40))  

        table = dykstras(self.start,nodes)
        self.getpath(table)     

    def draw(self): 
        rotated_img = pygame.transform.rotate(self.car_img, self.angle) 
        rect = rotated_img.get_rect(center=(self.x, self.y)) 
        screen.blit(rotated_img, rect)

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

                angle_rad = math.atan2(xchangeperunitlength,ychangeperunitlength)       # 0 is right, 180 left, 90 up, -90 down
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
        min_distance = 100
        max_check_distance = 250
        if self.paused == False:
            for car in cars:
                if car is self: #dont compare to itself
                    continue

                if math.hypot(car.x - self.x, car.y - self.y) > max_check_distance:
                    continue

                if car.previous_node() == self.previous_node() and car.target_node() == self.target_node():
                    # same source and destination
                    # determine distance along edge for both cars
                    # if too close, decide if we are the car behind (less far down the edge) then slow down

                    carremainingdist = car.dist_to_targetnode()
                    selfremainingdist = self.dist_to_targetnode()

                    if abs(selfremainingdist-carremainingdist) < min_distance and selfremainingdist > carremainingdist:
                        closecars += 1
                        if self.speed > car.speed:
                            self.speed -= self.speed/10

                        #print("nearcar1")

                    """ # elif car.previous_node() == self.previous_node(): 
                #     # same source, different destination
                #     # determine distance along edge for both cars
                #     # if too close, decide if we are the car behind (less far down the edge) then slow down
                #     # this is not a realistic interaction and only occurs due to the graphical display of the simulation
                """

                elif car.target_node() == self.target_node():

                    # different source, same destination
                    # determine distance away from node (for self and car) if too close, furthest slows down

                    if self.speed != 0 and car.speed != 0:
                        
                        carremainingtime = car.dist_to_targetnode()/car.speed
                        selfremainingtime = self.dist_to_targetnode()/self.speed

                        if abs(selfremainingtime) > abs(carremainingtime):
                            closecars += 1
                            if self.speed > car.speed:
                                self.speed -= self.speed/10

                            if self.speed == 0:
                                print("nearcar2")
                    
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

                    if abs(cartravelleddist) < 75 and abs(selfremainingdist) < 75:
                        closecars += 1
                        if self.speed > car.speed:
                            self.speed -= self.speed/5

                        if self.speed == 0:
                            print("nearcar3")
            
                """# elif car.target_node() == self.previous_node():
                #     # does not matter as it is car's responsibility to slow down"""
                    
            if closecars == 0:
                if self.speed < self.basespeed:
                    self.speed += (self.basespeed-self.speed)/10
                    
    def nearlight(self,lights):
        self.lights = lights
        mindist = 50
        for light in lights:
            if light.state in (2,3):
                if math.hypot((light.x-self.x),(light.y-self.y)) < mindist and self.angle == light.angle:
                    #print("im a light at",self.x,self.y,", someone is near me", )
                    self.speed = 0
                    return True


class lane:
    def __init__(self):
        pass

class trafficlights:
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

    def changecolour(self,dt):       

        self.timer += dt
        if self.timer >= self.lightlengths[self.state]:
            self.timer = 0.0
            self.state = (self.state+1)%4

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

    def draw(self):
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
        screen.blit(self.light_img,self.rectlight)
        

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



def spawn_car():
    while True:
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

        carobj = car(random.randint(100,200),rand1,rand2)
        cars.append(carobj)
        time.sleep(60/60)


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

    # node @ 600, 333

    trafficlighttest = trafficlights(600-60,333-42.5,0)   #NW
    trafficlight2 = trafficlights(600+32.5,333-67.5,-90)    #NE
    trafficlight3 = trafficlights(600+60,333+42.5,-180)      #SE
    trafficlight4 = trafficlights(600-32.5,333+67.5,90)    #SW


    lights.append(trafficlighttest)
    lights.append(trafficlight2)
    lights.append(trafficlight3)
    lights.append(trafficlight4)
    
    lights[1].state += 2
    lights[2].state += 2    #clicklightquad() only
    lights[3].state += 2

    lights[0].draw()
    lights[1].draw()
    lights[2].draw()  #clicklightquad() only
    lights[3].draw()


    last = time.time()

    clicklightquadrepeats = 0

    while running:
        
#HERE FOR INPUTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("Please kill the Terminal")
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                lights[clicklightquadrepeats].changebyclick()
                lights[(clicklightquadrepeats+1)%4].changebyclick()
                clicklightquadrepeats = (clicklightquadrepeats+1)%4


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
            
        #trafficlighttest.changecolour(dt)
        for trafficlight in lights:
            trafficlight.draw()


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

        pygame.display.update()


main()
pygame.quit()

# traffic lights go right way                                   # done
# multiple traffic lights                                       # done
# random path                                                   # done
# maybe overlapping objects in order to "stresst" stress test   # done

# error at entry nodes stopping     # FIX: only do the (first (maybe all)) nearcar check if it is not an enterance (adj nodes > 1) please.. work... !!!
# error at crossing nodes traffic   #

import pygame
import math
import pygame_gui



#pygame.Rect.collidepoint() !!!!!!!!
class car:
    def __init__(self,speed,start,finish):
        self.angle = 0
        self.basespeed = speed
        self.speed = self.basespeed
        self.paused = False
        self.behindcar = False

        self.start = start
        self.finish = finish
        self.x,self.y = lanelinks[start][1]
        self.finishx,self.finishy = lanelinks[finish][1]
        
        self.target = 0
        self.car_img = pygame.image.load("car.webp")
        self.car_img = pygame.transform.scale(self.car_img,(70,40))       

    def draw(self): 
        rotated_img = pygame.transform.rotate(self.car_img, self.angle) 
        rect = rotated_img.get_rect(center=(self.x, self.y)) 
        screen.blit(rotated_img, rect)

#    def createpath(self,endx,endy):
    
    def move(self):  #alternate move() function
        try:
            dx = self.finishx - self.x
            dy = self.finishy - self.y
        except IndexError:
            dx,dy = 0,0

        self.dx = dx
        self.dy = dy

        distance = math.hypot(dx, dy) # straight line distance between car and next point

        # if distance < self.speed:
        #     try:
        #         self.x, self.y = self.path[self.target]   
        #         self.target += 1    # so that the car does not drive past the checkpoint    
        #     except IndexError:  #if car reaches end before others, do nothing
        #         pass
        #     return


        # direction
        if distance != 0:
            dir_x = dx / distance
            dir_y = dy / distance
        else:
            dir_x,dir_y = 0,0
        if self.speed > 0:
            self.x += dir_x * self.speed
            self.y += dir_y * self.speed

            angle_rad = math.atan2(-dir_y, dir_x)       # 0 is right, 180 left, 90 up, -90 down
            self.angle = math.degrees(angle_rad)        #updated angle algorithm    

    def find_node_distance(self,node1,node2):
        distanceAx = lanelinks[node1][1][0]-lanelinks[node2][1][0]  # x-x
        distanceBy = lanelinks[node1][1][1]-lanelinks[node2][1][1]  # y-y
        distanceCtotal = math.sqrt((distanceAx**2)+(distanceBy**2)) # a^2 + b^2 = c^2
        return distanceCtotal

    def recursion_for_pathfinder(self,node,queue,visited):
        for link in lanelinks[node]:

            if link not in queue and link not in visited:
                queue.append(link)
                
        if queue: # is not empty
            nextnode = queue.pop(0)
            visited.append(nextnode)

            if nextnode in lanelinks:
                self.recursion_for_pathfinder(queue,lanelinks[link],visited)    #use link because it is the last link looked at so fulfills the breadthfirstsearch


    def findpath(self):     #find shortest path (dykstra's?)
        queue = []  #   current vertex, prev vertex, path cost
        visted = []
        prev_node = [] 
        path_found = []

        queue.append(self.finish)
        self.recursion_for_pathfinder(self.start,queue,visted)
        print(visted)


      

    def nearcar(self,cars):
        closecars = 0

        if self.paused == False:
            for car in cars:
                #prevposself = self.path[self.target-1]
                try:
                    nextposself = self.path[self.target]
                    prevposcar = car.path[car.target-2]

                    if car is self: #dont compare with itself
                        continue

                    distance = math.hypot(self.x - car.x, self.y - car.y )  # distance between car and other cars on the road

                    if distance <= 110:      #if car is close and going the same direction, stop!
                        if int(-1*self.angle) + 180 == int(-1*car.angle) or int(-1*self.angle) - 180 == int(-1*car.angle):  
                            pass    #if travelling direct opposite directions, do nothing
                                    #if not, stay behind car ahead
                        else:       
                            if nextposself == prevposcar:
                                self.behindcar = True
                                if self.speed >= car.speed:
                                    self.speed = car.speed
                                if abs(self.x - car.x) < 100 or abs(self.y - car.y) < 100:
                                    self.speed -= self.speed/10
                                closecars += 1
                            
                        if self.behindcar == True:
                            if nextposself in (car.path[car.target+1],car.path[car.target],car.path[car.target-1],car.path[car.target-2],car.path[car.target-3]):
                                self.behindcar = True
                                self.speed = car.speed

                            if abs(self.x - car.x) < 100 or abs(self.y - car.y) < 100:
                                self.speed -= self.speed/10

                            else:
                                self.behindcar = False

                    else:
                        if closecars < 1:
                            while self.speed < self.basespeed:
                                self.speed += self.basespeed/10
                                

                            
                except IndexError:
                    pass        
                        
        else:
            self.speed = 0

class lane:
    def __init__(self):
        pass

def lanedraw(screen,start,end):
        #pygame.draw.line(screen,colour,(x,y),(x,y),width)
        pygame.draw.line(screen,(180,180,180),start,end,50)     #change so width is 100 when 2 way road

#lanelinks[A][0] = links
#lanelinks[A][1] = properties (x,y)

lanelinks = {
    "A" : [["J","B","D"],[25,575]], #  +25 to coordinate to have lane locked into 
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

def main():    

    # GLOBAL VARs
    global screen,white,black,grey

    width = 1800        
    height = 1000       #pixel size of window
    screen = pygame.display.set_mode((width,height))    #make screen for display


    running = True

    # colours for later use
    white = (255, 255, 255)
    red = (180, 0, 0)
    green = (30,180,30)
    blue = (0, 0, 180)
    black = (0,0,0)
    grey = (180,180,180)

    car1 = car(1,"B","I")
    


#DRAW THIS BEFORE LOOP STARTS AS IT DOESNT CHANGE



        # rect = pygame.Rect(0,0,100,100)
        # rect.center = (lanelinks[node][1])
        # pygame.draw.rect(screen,(180,180,180),rect)


    

    clock = pygame.time.Clock()
    fps = 300

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        

        
        clock.tick(fps)

#DRAW HERE FOR CHANGING THINGS
        


        screen.fill(green) #clear screen so no repeated "draws"
        for node in lanelinks:
            for i in lanelinks[node][0]:
                lanedraw(screen,lanelinks[node][1],lanelinks[i][1]) 
        car1.draw()
        
#OTHER STUFF  

        car1.move()

        #time_delta = clock.tick(fps)/1000.0 #ui clock

        pygame.display.update()

main()
pygame.quit()
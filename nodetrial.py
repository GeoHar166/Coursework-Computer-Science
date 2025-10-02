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

def draw(screen,start,end):
        #pygame.draw.line(screen,colour,(x,y),(x,y),width)
        pygame.draw.line(screen,(180,180,180),start,end,100)

#lanelinks[A][0] = links
#lanelinks[A][1] = properties (x,y)

lanelinks = {
    "A" : [["J","B"],[50,600]],
    "B" : [["A","C"],[50,50]],
    "C" : [["B","D"],[300,50]],
    "D" : [["C","E"],[300,600]],
    "E" : [["D","F"],[700,600]],
    "F" : [["E","G"],[600,50]],
    "G" : [["F","H"],[1500,50]],
    "H" : [["G","I"],[1100,400]],
    "I" : [["H","J"],[1100,900]],
    "J" : [["I","A"],[300,900]]

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

    car1 = car(1,"B","G")
    


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
                draw(screen,lanelinks[node][1],lanelinks[i][1]) 
        car1.draw()
        
#OTHER STUFF  

        car1.move()

        #time_delta = clock.tick(fps)/1000.0 #ui clock

        pygame.display.update()

main()
pygame.quit()
import pygame
import math
import pygame_gui

pygame.init()
screen=white=black=grey=columns=grid = None

#define vars


#MAIN ROAD CLASS, THEN INHERITED CLASSES FOR DIFFERENT ROAD TYPES


class lane:
    def __init__(self, x, y, length):
        self.length = length
        self.x = x
        self.y = y


class lanehori(lane):
    def __init__(self,x,y,length,right):
        super().__init__(x,y,length)
        self.width = 50
        self.height = 50
        self.right = right #True or false - is it moving right?

    def draw(self):
        pygame.draw.rect(screen,grey,(self.x,self.y,(self.width)*self.length,self.height))  # display road

    def findspace(self):
        xplacehold = self.x/50
        self.tiles = []       
        for i in range(int(self.length)):     # which tiles in the grid does this road take up
            self.tiles.append([int(xplacehold),int(self.y/50)])   
            xplacehold += 1
            grid[int(self.tiles[i][0])][int(self.tiles[i][1])] = self  # fill big grid
        return self.tiles                                               # output looks like [[x,y],[x,y],[x,y]]
    
    def movingdefault(self):
        return self.right

    
        
class lanevert(lane):
    def __init__(self,x,y,length,down):
        super().__init__(x,y,length)
        self.width = 50
        self.height = 50
        self.down = down #True or false - is it moving down?

    def draw(self):
        pygame.draw.rect(screen,grey,(self.x,self.y,self.width,(self.height)*self.length))  # display road

    def findspace(self):
        yplacehold = self.y/50
        self.tiles = []       
        for i in range(int(self.length)):     # which tiles in the grid does this road take up
            self.tiles.append([int(self.x/50),int(yplacehold)])
            yplacehold += 1
            grid[int(self.tiles[i][0])][int(self.tiles[i][1])] = self
        return self.tiles
    
    def movingdefault(self):
        return self.down
    
# end of lane class
        

# CAR CLASS - need to attatch to roads so that they know where they are on the road and can position themselves without my input            

class car:
    def __init__(self,path,speed):
        self.x = path[0][0]
        self.y = path[0][1]
        self.angle = 0
        self.basespeed = speed
        self.speed = self.basespeed
        self.path = path
        self.paused = False
        
        self.target = 0
        self.car_img = pygame.image.load("assets/car.webp")
        self.car_img = pygame.transform.scale(self.car_img,(70,40))       

    def draw(self): 
        rotated_img = pygame.transform.rotate(self.car_img, self.angle) 
        rect = rotated_img.get_rect(center=(self.x, self.y)) 
        screen.blit(rotated_img, rect)

#    def createpath(self,endx,endy):
    
    def move(self):  #alternate move() function
        try:
            dx = self.path[self.target][0] - self.x
            dy = self.path[self.target][1] - self.y
        except IndexError:
            dx,dy = 0,0

        distance = math.hypot(dx, dy) # straight line distance between car and next point

        if distance < self.speed:
            try:
                self.x, self.y = self.path[self.target]   
                self.target += 1    # so that the car does not drive past the checkpoint    
            except IndexError:  #if car reaches end before others, do nothing
                pass
            return


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

    def nearcar(self,cars):  # is this car near enough another car to stop
        closecars = 0
        if self.paused == False:
            for car in cars:
                if car is self: #dont compare with itself
                    continue
                distance = math.hypot(self.x - car.x, self.y - car.y )  # distance between car and other cars on the road
                if distance <= 100:      #if car is close and going the same direction, stop!
                    if int(-1*self.angle) + 180 == int(-1*car.angle) or int(-1*self.angle) - 180 == int(-1*car.angle):  
                        pass    #if travelling direct opposite directions, do nothing
                    else:       #if not, stay behind car ahead

                        if (self.angle >= -45 and self.angle <= 45) and (car.angle >= -45 and car.angle <= 45):  # going right +- 45
                            if self.x < car.x or self.y > car.y:
                                self.speed = min(self.basespeed,car.speed)
                                if distance < 95:
                                    self.speed -= self.speed/10
                        # elif (self.angle >= 45 and self.angle <= 135) and (car.angle >= 45 and car.angle <= 135):    #going up +- 45
                        #     if self.y > car.y:
                        #         self.speed = min(self.basespeed,car.speed)  
                        #         if distance < 95:
                        #             self.speed -= self.speed/10
                        elif ((self.angle >= 135 and self.angle <= 180) or (self.angle >= -180 and self.angle <= -135)) and ((car.angle >= 135 and car.angle <= 180) or (car.angle >= -180 and car.angle <= -135)):
                            if self.x > car.x:                          #going left +- 45
                                self.speed = min(self.basespeed,car.speed)
                                if distance < 95:
                                    self.speed -= self.speed/10
                        # elif (self.angle >= -135 and self.angle <= -45) and (car.angle >= -135 and car.angle <= -45):  #going down +- 45
                        #     if self.y < car.y:
                        #         self.speed = min(self.basespeed,car.speed)
                        #         if distance < 95:
                        #             self.speed -= self.speed/10
                        else:
                            self.speed = self.speed

                        closecars += 1
                        
                else:
                    if closecars < 1:
                        self.speed = self.basespeed
        else:
            self.speed = 0

    def pause(self):
        self.paused= True
    
    def play(self):
        self.paused = False



    
    
#end of car class
 

def lanepath(path,traveldefault):
    lanepath = []
    for tile in path:
        pixel_x = tile[0]*50+25
        pixel_y = tile[1]*50+25
        lanepath.append([pixel_x, pixel_y])
    if traveldefault == False:
        lanepath.reverse()
    return lanepath


def main():

    # GLOBAL VARs
    global screen,white,black,grey,columns,grid

    width = 1800        #pixel size of window
    height = 1000
    screen = pygame.display.set_mode((width,height))    #make screen for display

    running = True

    # colours for later use
    white = (255, 255, 255)
    red = (180, 0, 0)
    green = (30,180,30)
    blue = (0, 0, 180)
    black = (0,0,0)
    grey = (180,180,180)

    #table to store road locations, [x][y], 36x20
    cols = int(width/50)
    rows = int(height/50)
    columns = []
    grid = [["" for i in range(rows)] for i in range(cols)]

    cars = []

            
    #lanes GO LEFT TO RIGHT/UP TO DOWN
    #lanenum = hori/vert (x,y,length,default direction?)
    lane1 = lanehori(200,200,23,True)       #HORIZONTAL MAX = 27
    lane2 = lanehori(250,250,22,False)      #VERTICAL MAX = 20
    lane3 = lanevert(200,200,16,False)
    lane4 = lanevert(250,250,15,True)
    lane5 = lanehori(0,0,27,True)
    lane6 = lanehori(50,50,26,False)
    lane7 = lanevert(0,0,20,False)
    lane8 = lanevert(50,50,19,True)

    # car  

    clock = pygame.time.Clock()
    fps = 300

    car_path = []
    car_path1 = []
    car_path2 = []

        #where car go
    car_path.extend(lanepath(lane7.findspace(),lane7.movingdefault()))
    car_path.extend(lanepath(lane5.findspace(),lane5.movingdefault()))
    car_path.extend(lanepath(lane6.findspace(),lane6.movingdefault()))
    car_path.extend(lanepath(lane8.findspace(),lane8.movingdefault()))
    car_path.extend(lanepath(lane3.findspace(),lane3.movingdefault()))
    car_path.extend(lanepath(lane1.findspace(),lane1.movingdefault()))
    car_path.extend(lanepath(lane2.findspace(),lane2.movingdefault()))
    car_path.extend(lanepath(lane4.findspace(),lane4.movingdefault()))

    car_path1.extend(lanepath(lane3.findspace(),lane3.movingdefault()))
    car_path1.extend(lanepath(lane1.findspace(),lane1.movingdefault()))
    car_path1.extend(lanepath(lane2.findspace(),lane2.movingdefault()))
    car_path1.extend(lanepath(lane4.findspace(),lane4.movingdefault()))
    car_path1.extend(lanepath(lane7.findspace(),lane7.movingdefault())) 
    car_path1.extend(lanepath(lane5.findspace(),lane5.movingdefault())) 
    car_path1.extend(lanepath(lane6.findspace(),lane6.movingdefault())) 
    car_path1.extend(lanepath(lane8.findspace(),lane8.movingdefault()))

    car_path2.extend(lanepath(lane6.findspace(),lane6.movingdefault()))
    car_path2.extend(lanepath(lane8.findspace(),lane8.movingdefault()))
    car_path2.extend(lanepath(lane3.findspace(),lane3.movingdefault()))
    car_path2.extend(lanepath(lane1.findspace(),lane1.movingdefault()))
    car_path2.extend(lanepath(lane2.findspace(),lane2.movingdefault()))
    car_path2.extend(lanepath(lane4.findspace(),lane4.movingdefault()))

 



    car1 = car(car_path,2)
    car2 = car(car_path1,4)   #create carss
    car3 = car(car_path2,1)
    cars.append(car1)
    cars.append(car2)
    cars.append(car3)




    #ui
    manager = pygame_gui.UIManager((1800,1000))
    #clock = pygame.time.Clock()

    test = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1700,950), (100,50)),
                                        text="car",
                                        manager=manager)
    pause = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1700,900),(100,50)),
                                         text="pause",
                                         manager=manager)
    play = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1700,850),(100,50)),
                                        text="play",
                                        manager=manager)


    while running:
                
        time_delta = clock.tick(fps)/1000.0 #ui clock

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == test:
                    print("hi there")
                if event.ui_element == pause:
                    for c in cars:
                        c.paused = True
                    print("cars paused")
                if event.ui_element == play:
                    for c in cars:
                        c.paused = False
                    print("cars unpaused")
                    

            manager.process_events(event)

        manager.update(time_delta)
        
        clock.tick(fps)
        screen.fill(green)
        
        

           

        lane1.draw()
        lane2.draw()
        lane3.draw()
        lane4.draw()
        lane5.draw()
        lane6.draw()
        lane7.draw()
        lane8.draw()
        
        for c in cars:
            c.move()
            c.draw()
            c.nearcar(cars)

        pygame.draw.circle(screen, red, (car_path[0][0], car_path[0][1]), 5)    #where does car spawn
        for point in car_path:
            pygame.draw.circle(screen, blue, (int(point[0]), int(point[1])), 3) # where does the car pass through

        #ui

        pygame.draw.rect(screen,(175,175,175),(1350,0,550,1000))    #ui section
        pygame.draw.rect(screen,(0,0,0),(1347,0,3,1000))            #seperating ui and visuals
        manager.draw_ui(screen)

        pygame.display.update()

main()
pygame.quit()


#########commented_out###########python -m pygbag main.py           +/#debug
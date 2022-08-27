#pylint:disable=W0621
import pygame
from sys import exit as sysexit
from random import randint
pygame.init()

#----------All game configuration
class Config():
    def __init__(self):
        #screen_size
        self.s_width = 720
        self.s_height = 1440
        
        self.pillar_w = 100 #pillar width
        self.pillar_h = self.s_height
        self.p_col_b = (0,100,20) #pillar color gradient begin
        self.p_col_e = (230,230,200)
        
        self.p_border_col = (30,50,20) #pillar border col
        self.p_col_step = 10 #gradient steps
        self.pillar_cap = 50 #pillar cap height
        
        self.n_pillar = 2 #nunber of pillar to be spawned
        
        self.bird_size = 50
        self.bird_sizey=0 #calculated y value
        self.b_body_col = (0,160,220)
        self.b_border = (40,30,50)
        
        self.b_w = (self.bird_size*4)//100 #border width percent
        self.beak_col = (200,30,80)
        self.wing_col = (200,200,200)
        #fly up as long as there is energy
        #each click bird will get this amount of energy
        self.bird_energy = 100
        self.bird_speed = 400 #fly up and down base speed
        self.energy_rate = 5
        self.speed_rate  = 10
        
        self.bg_sky = (30,120,180)
        self.bg_pos = 600 #screen_height - bg_pos = cloud begin
        self.bg_h_sub = 50 #space between layers of cloud and tree
        self.bg_cloud = (200,220,220)
        self.cloud_r = (50,200) #circle radius
        self.cloud_sp=40 #loop space between two cloud x
        
        self.bg_tree = (80,180,50)
        self.tree_r=(50,100)
        self.tree_sp = 10
        
        self.hr_space = 500 #space between pillar x axis
        self.vr_space = 200/2 #y axis space/two pillar = each pillar gap
        self.vr_variance = 50 #y space variance
        self.speed = 300 #pillar speed
        #gap between two pillar y rand range
        self.pillar_y_pos = (self.s_height*30)//100,self.s_height-(self.s_height*30)//100
        
        self.button_size = (150,100)
        #each time generate all artworks
        self.regenerate = True
        self.cheat = False
        
    def change_res(self, width, height):
        self.s_width = width
        self.s_height = height
        self.pillar_h = self.s_height
        self.pillar_y_pos = (self.s_height*30)//100,self.s_height-(self.s_height*30)//100
conf = Config()
#---------------------

#-------Artworks
def __gradient(color1,color2,step):
    #large number of step = fine gradient
    step -=1
    colors = []
    rm,gm,bm = [(c2-color1[i])/step for i,c2 in enumerate(color2)]
    for i in range(step):
        r = int(round(color1[0] + (rm*i),0))
        g = int(round(color1[1] + (gm*i),0))
        b = int(round(color1[2] + (bm*i),0))
        colors.append((r,g,b))
    colors.append(color2)
    return colors

def __dim(color=(120,80,90),f=30):
    return [max((0,c-f)) for c in color]
    
def __light(color=(120,80,90),f=30):
    return [min((255,c+f)) for c in color]
    
def rand_col(b=0,e=255):
    return [randint(b,e) for _ in range(3)]

def create_bg():
    h = conf.s_height
    w = conf.s_width
    r = conf.bg_pos
    surface = pygame.Surface((conf.s_width,conf.s_height))
    pygame.draw.rect(surface,conf.bg_sky,(0,0,conf.s_width,conf.s_height))
    #place cloud
    for i in range(0,w,conf.cloud_sp):
        pygame.draw.circle(surface,__dim(conf.bg_cloud,10),(i,h-r+randint(0,100)),randint(*conf.cloud_r)/2)
    #next layer of cloud
    r-=conf.bg_h_sub #spacing from top layer
    for i in range(0,w,conf.cloud_sp):
        pygame.draw.circle(surface,conf.bg_cloud,(i,h-r+randint(0,100)),randint(*conf.cloud_r)/2)
    #three layers of tree
    r-=(conf.bg_h_sub*2)
    for i in range(0,w,conf.tree_sp):
        pygame.draw.circle(surface,__dim(conf.bg_tree,50),(i,h-r+randint(0,100)),randint(*conf.tree_r)/2)
        
    r-=conf.bg_h_sub
    for i in range(0,w,conf.tree_sp):
        pygame.draw.circle(surface,__dim(conf.bg_tree,25),(i,h-r+randint(0,100)),randint(*conf.tree_r)/2)
        
    r-=conf.bg_h_sub 
    for i in range(0,w,conf.tree_sp):
        pygame.draw.circle(surface,conf.bg_tree,(i,h-r+randint(0,100)),randint(*conf.tree_r)/2)
    r-=conf.bg_h_sub 
    #make ground green
    pygame.draw.rect(surface,conf.bg_tree,(0,h-r,w,h))
    return surface

def create_pillar(flip=False):
    surface = pygame.Surface((conf.pillar_w,conf.pillar_h))
    surface.set_colorkey((0))
    pygame.draw.rect(surface,conf.p_border_col,(0,0,conf.pillar_w,conf.pillar_cap),width=3)
    colors = __gradient(conf.p_col_b,conf.p_col_e,conf.p_col_step)
    width = conf.pillar_w/conf.p_col_step
    for x,col in enumerate(colors):
        if x!=0 and x!=conf.p_col_step-1:
            pygame.draw.rect(surface,col,(width*x,0,width,conf.pillar_h))
        else:
            pygame.draw.rect(surface,col,(width*x,0,width,conf.pillar_cap))
            
    pygame.draw.rect(surface,conf.p_border_col,(0,0,conf.pillar_w,conf.pillar_cap),width=4)
    pygame.draw.rect(surface,conf.p_border_col,(width,conf.pillar_cap,conf.pillar_w-(width*2),conf.pillar_h),width=4)
    if flip:
        surface=pygame.transform.flip(surface,False,True)
    return surface

def create_bird(flap=3,rotate=0):
    def scale(points,bsize):
        result = []
        bx,by = bsize
        for x,y in points:
            x= (x/34)*bx
            y= (y/24)*by
            result.append((x,y))
        return result
    bsize = conf.bird_size,conf.bird_size*(24/34)
    conf.bird_sizey=bsize[1]
    surface = pygame.Surface(bsize)
    surface.set_colorkey((0))
    
    body = (23,0),(12,0),(8,2),(2,8),(2,13),(4,18),(10,23),(19,23),(25,18),(29,11),(29,6)
    eye = (23,0),(18,0),(16,4),(16,9),(18,11),(20,13),(29,13),(29,6),(26,3)
    eye_ball = (24,6),(24,9),(26,9),(26,6)
    beak = (16,16),(20,21),(29,21),(31,19),(31,17),(20,17),(20,16),(32,16),(33,15),(31,12),(20,12)
    flap1 = (13,15),(10,12),(2,12),(0,14),(0,19),(2,21),(8,21)
    flap2 = (11,10),(1,10),(0,12),(0,15),(2,17),(11,17),(13,15),(13,12)
    flap3 = (13,10),(9,6),(2,6),(0,7),(0,13),(4,17),(9,16),(13,13)
    
    flap1_s = (4,5),(4,10),(8,3),(8,14) #speed line
    flap3_s = (6,20),(6,12),(10,18),(10,9)
    
    scaled_body = scale(body,bsize)
    scaled_eye = scale(eye,bsize)
    scaled_ball = scale(eye_ball,bsize)
    scaled_beak = scale(beak,bsize)
    scaled_flap1 = scale(flap1,bsize)
    scaled_flap1_s = scale(flap1_s,bsize)
    scaled_flap2 = scale(flap2,bsize)
    scaled_flap3 = scale(flap3,bsize)
    scaled_flap3_s = scale(flap3_s,bsize)
    
    pygame.draw.polygon(surface,conf.b_body_col,scaled_body)
    pygame.draw.polygon(surface,conf.b_border,scaled_body,width=conf.b_w)
    pygame.draw.polygon(surface,(220,220,220),scaled_eye)
    pygame.draw.polygon(surface,conf.b_border,scaled_eye,width=conf.b_w)
    pygame.draw.polygon(surface,(10,10,10),scaled_ball)
    pygame.draw.polygon(surface,conf.beak_col,scaled_beak)
    pygame.draw.polygon(surface,conf.b_border,scaled_beak,width=conf.b_w)
    
    if flap==1:
        pygame.draw.polygon(surface,conf.wing_col,scaled_flap1)
        pygame.draw.polygon(surface,conf.b_border,scaled_flap1,width=conf.b_w)
        pygame.draw.line(surface,(8,10,20),scaled_flap1_s[0],scaled_flap1_s[1])
        pygame.draw.line(surface,(8,10,20),scaled_flap1_s[2],scaled_flap1_s[3])
    elif flap == 2:
        pygame.draw.polygon(surface,conf.wing_col,scaled_flap2)
        pygame.draw.polygon(surface,conf.b_border,scaled_flap2,width=conf.b_w)
    elif flap== 3:
        pygame.draw.polygon(surface,__light(conf.wing_col,20),scaled_flap3)
        pygame.draw.polygon(surface,conf.b_border,scaled_flap3,width=conf.b_w)
        pygame.draw.line(surface,(8,10,20),scaled_flap3_s[0],scaled_flap3_s[1])
        pygame.draw.line(surface,(8,10,20),scaled_flap3_s[2],scaled_flap3_s[3])
    if rotate:
        return pygame.transform.rotate(surface,rotate)
    return surface
#------------------------

#--------bird sprite

class Bird():
    def __init__(self):
        self.screen = None
        self.sprite = None
        self.active_sprite = None #this will be blited
        self.c_frame = 0 #current frame
        self.frame_n = 0 #number of frame
        self.rect=None
        self.position = (50,conf.s_height/2)
        self.alive = False #in gameplay
        self.home_bird = True #bird is in homescreen
        self.flipped = False #died and flipped
        self.clock=pygame.time.Clock()
        
        self.energy=conf.bird_energy
        self.speed = conf.bird_speed
        self.time_passed = 0
    @classmethod
    def create(cls,screen):
        bird = cls()
        flap1 = create_bird(flap=1) #down
        flap2 = create_bird(flap=2,rotate=0) #mid
        flap3 = create_bird(flap=3) #up
        bird.rect = flap1.get_rect()
        bird.sprite = [flap1,flap2,flap3]
        bird.active_sprite = flap2
        bird.screen = screen
        bird.frame_n = 3
        return bird
        
    def flip(self):
        #flip and rotate
        self.flipped= True
        self.active_sprite = pygame.transform.flip(self.sprite[1],False,True)
        self.active_sprite = pygame.transform.rotate(self.active_sprite,-30)
        
    def fly(self):
        if self.alive: #game is running
            tick = self.clock.tick()/1000
            self.time_passed+=tick #animation speed control
            px,py = self.position
            if self.energy>10: #do flapping
                py -= self.speed*tick
                self.energy -= conf.energy_rate
                if self.speed>100: #reduce speed gradually untill 100
                    self.speed-=conf.speed_rate
                    
                if self.time_passed > .04 and not self.flipped:
                    #if flipped no flapping animation
                    self.active_sprite = pygame.transform.rotate(self.sprite[self.c_frame],20)
                    self.c_frame +=1
                    if self.c_frame>2: #looping back to first frame
                        self.c_frame=0
                    self.time_passed=0
            
            elif self.energy<=0: #no energy
                self.speed+=conf.speed_rate
                py += self.speed*tick #so go down
                if not self.flipped:
                    self.active_sprite = self.sprite[1]
                self.c_frame=1
            else:
                #if 0<energy<20 no upward or downward movement, bird is stable
                self.energy -=5 #reducing energy to no energy state
            self.position=px,py
            
        if self.home_bird: #if in homescreen do only flapping
            tick = self.clock.tick()/1000
            self.time_passed+=tick
            if self.time_passed > .1:
                self.active_sprite = self.sprite[self.c_frame]
                self.c_frame +=1
                if self.c_frame>2:
                    self.c_frame=0
                self.time_passed=0
        self.screen.blit(self.active_sprite,self.position)

class Pillar():
    def __init__(self):
        self.screen = None
        self.sprite = None
        self.respawn_pos = None
        self.position = (0,0)
        self.rect = None
        self.clock = pygame.time.Clock()
        self.respawn = False
        
    @classmethod
    def create(cls,screen,flip = False):
        pillar = cls()
        pillar.screen = screen
        pillar.position=(-300,0)
        pillar.sprite = create_pillar(flip)
        return pillar
    
    def move(self):
        if not self.respawn:
            tick = self.clock.tick()/1000
            px,py = self.position
            px -=(conf.speed*tick)#move right to left
            self.position =px,py
            if px<-100:
                self.respawn=True
            
    def render(self):
        self.screen.blit(self.sprite,self.position)
    
class Game():
    def __init__(self,screen):
        self.screen = screen
        
        self.score = 0
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace",40)
        
        #sprites
        self.bg = create_bg()
        self.bird = Bird.create(screen)
        self.pillars = [] #all pillar sprites
        #-------
        #distance between all pillar is same so
        #this value will be used to calculate position of new respwaned pillar
        self.last_respawn = 0 #latest respawned pillar index
        
        self.running = False
        self.bird_collide_with_pillar=False
        
        #homescreen config
        self.home_bird_pos = None
        self.button = None #button surface
        self.button_pos= None
        self.home_score = None #score surface
        self.score_pos = None
        
        self.home_screen_asset()
        self.bird.position=self.home_bird_pos
        #-----------
        
        #self.die=pygame.mixer.Sound("./res/die.wav")
        
    def regenerate(self):
        #make all artwork again
        conf.b_body_col = rand_col(0,255)#bird color
        conf.p_col_b=rand_col(0,150)
        conf.beak_col=rand_col(0,255)
        
        self.bg = create_bg() 
        self.bird = Bird.create(self.screen)
        self.pillars=[] #clearing
        self.create_pillars()#before appending new pillar
     
    def create_pillars(self):
        for i in range(conf.n_pillar):
            pos = randint(*conf.pillar_y_pos) #mid position between two pillar
            hr_space = conf.s_width+(conf.hr_space*i)
            bottom_p = Pillar.create(self.screen)
            top_p = Pillar.create(self.screen,flip=True)
            
            bottom_p.position = hr_space,pos+conf.vr_space
            top_p.position=hr_space,-conf.s_height+pos-conf.vr_space
            
            self.pillars.append((bottom_p,top_p)) #pillar pair
        self.last_respawn=i
        
    #this function contains a bug
    def pillars_update(self):
        bx,by= self.bird.position
        respawn = self.last_respawn
        for num,pillars in enumerate(self.pillars):#loop pillar pair
            pos = randint(*conf.pillar_y_pos)
            for i,pillar in enumerate(pillars):
                if pillar.respawn:
                    respawn=num
                    if i==0:#bottom_pillar
                        y_pos = pos+conf.vr_space
                    else:
                        y_pos = -conf.s_height+pos-conf.vr_space
                    #last_respawned pillar pair, using bottom pillar to
                    #calculate distance to respawn. so space between
                    #last pillar and respawned pillar is same = conf.hr_space
                    #but it does not work as expected xpos contains bug
                    x_pos = self.pillars[self.last_respawn][0].position[0]+conf.hr_space
                    pillar.position = x_pos,y_pos
                    pillar.respawn = False #no need respawning
                px,py = pillar.position
                
                #check if this pillar in collision with bird
                if self.collision_detect(bx,by,px,py):
                    if not conf.cheat:
                        self.bird_collide_with_pillar = True
                    
                pillar.move()
                pillar.render()
            self.last_respawn=respawn
            
    def collision_detect(self,bx,by,px,py):
        if px+conf.pillar_w+10<bx+conf.bird_size<px+conf.pillar_w+20 and 0<by<conf.s_height:
            #if self.bird_collide_with_pillar:
            self.score+=1
        if px<bx<px+conf.pillar_w and py<by<py+conf.pillar_h:
            return True
        elif px<bx+conf.bird_size<px+conf.pillar_w and py<by+conf.bird_sizey<py+conf.pillar_h:
            return True
        
    def collision(self):
        _,py=self.bird.position
        if not 0<py<conf.s_height:
            self.go_home()
            
        if (self.bird_collide_with_pillar and not self.bird.flipped):
            self.bird.flip()
            #pygame.mixer.Sound.play(self.die)
            
   
    def energy_gain(self):
        #bird will gain energy after each mouse click
        if self.running and not self.bird_collide_with_pillar:
            self.bird.energy=conf.bird_energy
            self.bird.speed = conf.bird_speed 
    
    def listen(self,mpos):
        #listen mouseclick
        if self.running:
            self.energy_gain()
        else:
            #if in homescreen check if the click on play button
            px,py = mpos
            bx,by = self.button_pos
            w,h = conf.button_size
            if bx<px<bx+w and by<py<by+h:
                if conf.regenerate:
                    self.regenerate()
                self.score=0
                self.bird.alive=True
                self.bird.home_bird=False
                self.bird.speed = conf.bird_speed
                self.bird.position = 50,self.bird.position[1]
                self.running=True
                
    def go_home(self):
        self.bird.alive=False
        self.bird.home_bird=True
        self.running=False
        self.bird_collide_with_pillar=False   
        self.bird.position = self.home_bird_pos
        self.home_score = self.score_render(text="last score",ret=True)
        score_x,_ = self.home_score.get_size()
        self.score_pos = conf.s_width/2-score_x/2,conf.s_height/2+200
        
    def home_screen_asset(self):
        _,_,w,h = self.bird.rect
        sw = conf.s_width/2
        sh = conf.s_height/2
        bx,by = conf.button_size
        

        button = pygame.Surface((bx,by))
        pygame.draw.rect(button,(25,75,120),(0,0,bx,by),width=3)
        play_text = self.font.render("play",3,(10,10,10))
        text_x,text_y = play_text.get_size()
        button.blit(play_text,(bx/2-text_x/2,by/2-text_y/2))
        button.set_colorkey((0))
        self.home_score=self.score_render(ret=True)
        score_x,_ = self.home_score.get_size()
        self.score_pos = sw-score_x/2,sh+200
        
        self.button = button
        self.button_pos=sw-bx/2,sh+100
        self.home_bird_pos=(sw-w/2,sh-h/2)
        
    def score_render(self,pos=(10,100),text="score",ret=False):
        score_text = self.font.render(f"{text} {self.score}",0,(255,255,255))
        if ret:
            return score_text
        self.screen.blit(score_text,pos)
        
    def render_bg(self):
        self.screen.blit(self.bg,(0,0))
        
    def render(self):
        if self.running:
            self.pillars_update()
            self.bird.fly()
            self.collision()
            self.score_render(text="")
        else:
            self.bird.fly()
            self.screen.blit(self.button,self.button_pos)
            self.screen.blit(self.home_score,self.score_pos)
            
            
        
    
    
def run():
    screen = pygame.display.set_mode((conf.s_width,conf.s_height))
    game = Game(screen)
    game.create_pillars()
    clock = pygame.time.Clock()
    while True:
        clock.tick(100)
        game.render_bg()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sysexit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.listen(event.pos)
        game.render()
        game.collision()
        pygame.display.update()
            

if __name__=="__main__":
    width = 355
    height = 520
    conf.change_res(width,height)
    conf.p_col_step=5
    conf.n_pillar=2
    conf.hr_space=400
    conf.pillar_w = 50
    conf.pillar_cap = 25
    conf.vr_space = 100//2
    conf.bird_size = 25
    conf.speed=200
    conf.bird_speed=300
    conf.bg_pos = 300
    conf.cloud_r = (50,100)
    conf.cloud_sp=20

    conf.tree_r=(25,50)
    conf.tree_sp = 3
    run()

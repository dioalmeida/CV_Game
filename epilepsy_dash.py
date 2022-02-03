#  Dev Team: Diogo Almeida, Rodrigo Ferreira & Luís Laranjeira
import math
import random
import sys
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from panda3d.core import *
from panda3d.ode import *
from panda3d.physics import *
import mediapipe_hands
import cv2

SEED=11
random.seed(11)
PLAYER_TAG = "player-instance"
MAP_TAG = "map-instance"
TRAPS_TAG = "traps-instance"
SPEED = 20
JUMP_SPEED = 10
FLOOR_Z=1
ENDING_Y=610
scores=[0]

colours=[(255,255,0),(0,255,255),(255,0,255)]

zones = [0,1,2]
CAMERA_DIST_X = 40
CAMERA_DIST_Y = 50
CAMERA_DIST_Z= 10
INITIAL_ALIGHT=(0.15,0.15,0.15,1)
INITIAL_SLIGHT=(2,2,2,1)
INITIAL_PLAYRATE=1



class Game(ShowBase):
          

    def __init__(self, hand_mode=0):
        super().__init__()
        self.variable_initialization()       
        self.load_back()
        self.add_UI()
        self.add_player()
        self.setup_level()
        self.add_lighting()
        self.camera_initialization()
        self.input_initialization()
        self.add_soundtrack()
        self.menu()
        self.taskMgr.add(self.followCubeBehindTask, "followCubeBehindTask")
        self.taskMgr.add(self.followCubeSideTask, "followCubeSideTask")
        self.taskMgr.add(self.closestWallTask,"closestWallTask", priority=1)
        self.taskMgr.add(self.checkImpactTask2,"checkImpactTask2", priority=2)
        self.taskMgr.add(self.updateColoursTask,"updateColoursTask")
        self.taskMgr.add(self.updateScoreTask,"updateScoreTask")
        self.taskMgr.add(self.zonePropertiesTask,"zonePropertiesTask")
        self.taskMgr.add(self.update_ode, "UpdateODE")
    
        if hand_mode==1:
            self.hand_detection = mediapipe_hands.detection()
            self.taskMgr.add(self.detectHandTask,"detectHandTask")
            

    def input_initialization(self):
        """
        Defining the keymap and keymap inputs allowed.
        """
        self.keymap = {"left":False,"right":False,"jump":False}
        self.accept("a", self.update_keymap,["left",True]) 
        self.accept("a-up", self.update_keymap,["left",False])
        self.accept("d", self.update_keymap,["right",True])
        self.accept("d-up", self.update_keymap,["right",False])
        self.accept("space", self.update_keymap,["jump",True])
        self.accept("r", self.restart_game)
        self.accept("q", self.quit)


    def camera_initialization(self):
        """
        Initializing the the rear and side cameras.
        """
        self.camState = True # true = behind, false = side
        self.dr = base.camNode.getDisplayRegion(0)
        self.dr.setActive(1) 
        self.camBehind= Camera("camBehind")
        self.camSide = Camera("camSide")
        self.cameraBehind = self.render.attachNewNode(self.camBehind)
        self.cameraSide = self.render.attachNewNode(self.camSide)
        self.dr.setCamera(self.cameraBehind)


    def variable_initialization(self):
        """
        Initializing various variables required.
        """
        self.speed = SPEED
        self.jump = 0
        self.jump_speed = JUMP_SPEED
        self.sm = None
        self.score=0
        self.ground = None
        self.contacts = None
        self.space = None
        self.dt=0
        self.reverse=0
        self.colourTimer=0
        self.closestWall=None
        self.currentZone=-1
        self.zoneChanges=["CAMERA CHANGE", "SPEEDING UP", "LIGHTS OUT", "REVERSE CONTROLS", "REVERSE CONTROLS"]
        self.zones=[(50,90),(110,250), (270, 350),(400,500)]
        self.cubeColourIndex=0
        self.wallTexDict={}


    def add_UI(self):
        """
        Adding score and notification UI to the scene.
        """
        self.scoreUI = OnscreenText(text = "0",
                        pos = (-1.3, 0.825),
                        fg=(199,21,133,1),
                        bg=(0,0,255,1),
                        mayChange = True,
                        scale=(0.2),
                        align = TextNode.ALeft)
        
        self.notificationUI = OnscreenText(text = "",    
            fg=(255,255,255,1),
            bg=(0,0,0,0.5),
            pos=(0,0.8),
            scale=(0.2),
            mayChange = True,
            align = TextNode.ACenter)


    def add_soundtrack(self):
        """
        Adding sound to the scene.
        """
        self.mySound = base.loader.loadSfx("assets/sound/initialduck.mp3")
        self.mySound.setPlayRate(1)
        self.mySound.setLoop(True)
        self.mySound.play()


    def load_back(self):
        """
        Loading the background.
        """
        self.nyancat = self.loader.loadModel("assets/nyancat/textest")
        self.nyancat.setPos(0,50,0)
        self.nyancat.setScale(100)
        self.nyancat.reparentTo(self.render)
        self.nyancatSide = self.loader.loadModel("assets/nyancat/textest")
        self.nyancatSide.setPos(-50,-20,0)
        self.nyancatSide.setScale(100)
        self.nyancatSide.setHpr(self.nyancatSide, (90,0,0))
        self.nyancatSide.reparentTo(self.render)
        

    def restart_game(self): 
        """
        Restarts several parameters to allow the player to replay the map.
        """
        self.taskMgr.add(self.update_ode, "UpdateODE")
        self.taskMgr.add(self.updateScoreTask,"updateScoreTask")
        self.taskMgr.add(self.zonePropertiesTask,"zonePropertiesTask")
        self.keymap = {"left":False,"right":False,"jump":False}
        self.sm.setPos(0,-50,FLOOR_Z)
        self.plane.setPos(5,20,-1)
        self.nyancat.setPos(0,50,0)
        self.nyancatSide.setPos(-50,-20,0)
        self.slnp.setPos(0, 0, 300)
        self.currentZone=-1
        self.reverse=0
        scores.append(int(self.score/25))
      
        self.score=0
        self.wallsActive = []
        self.notificationUI.setText("")
        for wall in self.walls:
            wall.reparentTo(self.render)
            self.wallsActive.append(wall)
        self.gameOverScreen.hide()
        self.mySound.play()


    def updateScoreTask(self, task):
        """
        Task responsible for updating the score.
        """
        self.score +=1
        if self.score%25==0:
            self.scoreUI.setText(str(int(self.score/25)))
        return Task.cont


    def zonePropertiesTask(self, task):
        """
        Task responsible for changing gameplay properties given the zone.
        """
        zone_1 = self.zones[0]
        zone_2 = self.zones[1]
        zone_3 = self.zones[2]
        zone_4 = self.zones[3]
        if zone_1[0]<=self.sm.getY()<=zone_1[1]:
            
            if self.currentZone!=1:
                
                self.notificationUI.setText(self.zoneChanges[0])
                self.toggleCamera(self.camState)
                self.currentZone=1
        
        elif zone_2[0]<=self.sm.getY()<=zone_2[1]:
            
            if self.currentZone!=2:
                self.notificationUI.setText(self.zoneChanges[1])
                self.speed=self.speed*3
                self.currentZone=2
                self.mySound.setPlayRate(1.5)
        elif zone_3[0]<=self.sm.getY()<=zone_3[1]:
           
            if self.currentZone!=3:
                self.notificationUI.setText(self.zoneChanges[2])
                self.slight.setColor((0.05,0.05,0.05,0.05))
                self.alight.setColor((.05,.05,.05,0.05))
                #self.render.clearLight(self.alnp)
                self.currentZone=3
        
        elif zone_4[0]<=self.sm.getY()<=zone_4[1]:
           
            if self.currentZone!=4:
                self.notificationUI.setText(self.zoneChanges[3])
                self.reverse=1
                self.mySound.setPlayRate(-1)
                self.currentZone=4
        else:
            self.notificationUI.setText("")
            if not self.camState:
                
                self.toggleCamera(self.camState)

                self.currentZone=-1
            if not self.speed==SPEED:
                self.speed=SPEED
                self.mySound.setPlayRate(INITIAL_PLAYRATE)
            
            if self.slight.color!=INITIAL_SLIGHT:
                self.alight.setColor(INITIAL_ALIGHT)
                self.slight.setColor(INITIAL_SLIGHT)

            if self.reverse:
                self.reverse=0
                self.mySound.setPlayRate(INITIAL_PLAYRATE)
            
        if self.sm.getY()>ENDING_Y:
            self.notificationUI.setText("YOU WON")
            self.stop(won=True) ###
        return Task.cont

    
    def detectHandTask(self, task):
        """
        Task responsible for extracting input from hand detection.
        """
        handDecision = self.hand_detection.get_frame()
        self.update_keymap("left", bool(handDecision["Left"]))
        self.update_keymap("right", bool(handDecision["Right"]))
        self.update_keymap("jump", bool(handDecision["Jump"]))
        return Task.cont
       
    
    def updateColoursTask(self, task):
        """
        Task responsible for updating the obstacle and player colours.
        """
        self.colourTimer+=self.dt
        if self.colourTimer>2:
           
            new_cube_tex = self.all_tex[random.randint(0,2)]
            for wall in self.wallsActive:
                new_wall_tex = self.all_tex[random.randint(0,2)]
                wall.setTexture(new_wall_tex)
                self.wallTexDict[wall.getY()]=new_wall_tex
                
                    
            self.colourTimer=0
            self.sm.setTexture(new_cube_tex)
            self.cubeColourIndex=new_cube_tex
        return Task.cont

       
    def add_player(self):
        """
        Generate the player entity.
        """
        
        self.player = self.loader.loadModel("assets/textest.egg")
        self.sm = self.render.attachNewNode(PLAYER_TAG)
        self.sm.setColor(*colours[0])
        self.sm.setPos(0,-50, FLOOR_Z)
        cube_tex = self.loader.loadTexture('assets/tex/brick.png')
        self.sm.setTexture(cube_tex, 1)
        self.colliderNode = CollisionNode("cPlayer")

        self.colliderNode.addSolid(CollisionBox(LPoint3(0,0,0),LPoint3(2,2,2)))
        self.collider = self.sm.attachNewNode(self.colliderNode)
        
        #self.collider.show()
        self.player.instanceTo(self.sm)
        self.jumping=False
        self.jumpSpeed=0
       
        
    def setup_level(self):
        """
        Generate the level (floor and obstacles)
        """
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
       
        floor = self.render.attachNewNode(CollisionNode("floor"))
        floorColliderNode = CollisionNode("cFloor")
        floorColliderNode.addSolid(CollisionPlane(Plane(Vec3(0, 0, 0), Point3(0, 0, 0))))
        floor.setColor(0,0,0,0.5)
        
        
        self.floorCollider = floor.attachNewNode(floorColliderNode)
       
        self.plane = self.loader.loadModel("assets/new_floor.egg")
        #self.plane = self.loader.loadModel("assets/floor_new_new.egg")
        self.plane.setPos(5,20,-1)
        self.plane.setColor(0,0,255,1)
        self.plane.reparentTo(self.render)
        
        tex_candy = self.loader.loadTexture('assets/tex/candy.png')
        tex_candy.setWrapU(Texture.WM_mirror)
        tex_candy.setWrapV(Texture.WM_mirror)
        self.plane.setTexture(tex_candy)
        #self.plane.setColor()
        tex0 = self.loader.loadTexture('assets/tex/brick0.png')
        tex1 = self.loader.loadTexture('assets/tex/brick1.png')
        tex2 = self.loader.loadTexture('assets/tex/brick2.png')
        self.all_tex = [tex0,tex1,tex2]
        #self.plane.setTexture(tex_moon, 1)

        wall_heights= [FLOOR_Z,FLOOR_Z+4]
        self.walls = []
        self.wallsActive = []
        for i in range(50):
            
            wall = self.loader.loadModel("assets/WALL_NEW.egg")
            
            wall.setPos(random.randint(-4,2),12*(i+1),wall_heights[random.randint(0,(len(wall_heights))-1)])
            wall.reparentTo(self.render)
            #wall.setColor(Vec4(*colours[random.randint(0,2)],1))
            
            
            
            myMaterial = Material()
            myMaterial.setShininess(5) # Make this material shiny
            myMaterial.setAmbient((222, 222, 222, 1)) # Make this material blue
            myMaterial.setBaseColor((255,0,0,1))
            myMaterial.setEmission((255,0,0,1))
            
            colour=Vec4(*colours[random.randint(0,2)],.1)
            
            myMaterial.setDiffuse(colour)
            wall.setMaterial(myMaterial) # Apply the material to this nodePath
            self.walls.append(wall)
            self.wallsActive.append(wall)
            texture_index = random.randint(0,2)
            wall.setTexture(self.all_tex[texture_index], 1)
            
            self.wallTexDict[12*(i+1)]=texture_index
        
        self.pusher.addCollider(self.collider, self.sm)
        
        
        self.cTrav.addCollider(self.collider, self.pusher)
        
    
    def closestWallTask(self, task):
        """
        Find the wall currently closest to the player and remove walls already passed by.

        """
        dist=1000
        closest=None
        
        for wall in self.wallsActive:
            
            curr_dist = wall.getY() - self.sm.getY()
            if curr_dist>=0 and curr_dist< dist:
                dist=curr_dist
                closest=wall
            
            elif curr_dist<-7:
                wall.detachNode()
                self.wallsActive.remove(wall)
        self.closestWall = closest
       
        return Task.cont  

    
    def add_lighting(self):
        """
        Add the lighting to the scene.
        """
        self.alight = AmbientLight("alight")
        self.alight.setColor(INITIAL_ALIGHT)
  
        self.slight = PointLight('plight')
        self.slight.setColor(INITIAL_SLIGHT)
        self.slnp = self.render.attachNewNode(self.slight)
        self.slnp.setPos(0, 0, 300)
        self.slnp.lookAt(self.sm)
        self.render.setLight(self.slnp)
      
        self.render.setLight(self.render.attachNewNode(self.alight))
       
        self.render.setShaderAuto()
    

    def toggleCamera(self,state):
        if self.camState:
            self.dr.setCamera(self.cameraSide)
            self.keymap["left"]=False
            self.keymap["right"]=False
        else:
            self.dr.setCamera(self.cameraBehind)
        self.camState = not self.camState
    

    def followCubeBehindTask(self, task):
        """
        Task responsible for making the rear camera follow the cube.
        """
        self.cameraBehind.setPos(self.sm.getX(), self.sm.getY()-CAMERA_DIST_Y, CAMERA_DIST_Z)
        self.cameraBehind.lookAt(self.sm)
       
        

    

        return Task.cont
    

    def checkImpactTask2(self, task):
        """
        Task responsible for checking for impacts with the closest wall.
        """
        if self.closestWall:
            if (self.sm.getY() >= self.closestWall.getY()-3 and self.sm.getY() <= self.closestWall.getY()+1):
                
                if  (self.sm.getZ() >= self.closestWall.getZ()-1 and self.sm.getZ() <= self.closestWall.getZ()+1) and (self.sm.getX() >= self.closestWall.getX()-3 and self.sm.getX() <= self.closestWall.getX()+3.5):
                  
                    if self.sm.getTexture()!=self.closestWall.getTexture():
                        self.stop()
                        
                
        return Task.cont
    

    def followCubeSideTask(self, task):
        """
        Task responsible for having the side camera following the cube.
        """
        

        self.cameraSide.setPos(self.sm.getX()+ CAMERA_DIST_X, self.sm.getY()-5, CAMERA_DIST_Z)
       
        self.cameraSide.lookAt(self.sm)
        

    

        return Task.cont
    

    def update_ode(self, task):
        """
        Apply movement to the various entities.
        """
        current_vec=self.sm.getPos()

        
        change_vec=Vec3(0,0,0)
       
        self.dt = globalClock.getDt()
        
        updated_z=FLOOR_Z
        if self.keymap["left"]:
            change_vec+= Vec3(-self.speed*self.dt,0,0)
            
        if self.keymap["right"]:
            change_vec+= Vec3(self.speed*self.dt,0,0)
            
       
        if self.jumping:
       
           
            updated_z=self.sm.getZ()+self.jumpSpeed*self.dt
            self.jumpSpeed = self.jumpSpeed - 9.8*self.dt
            if updated_z<=FLOOR_Z:
                self.jumping=False
               
        
        change_vec+=Vec3(0,self.speed*self.dt,0)
        self.plane.setPos(self.plane.getPos() + Vec3(0,self.speed*self.dt,0))
        self.sm.setPos(current_vec+change_vec)
        self.sm.setZ(updated_z)
        
        curr_X = self.sm.getX()
        if curr_X<=-5.98 or curr_X>=4.98:
            self.stop()

        self.nyancat.setPos(self.nyancat.getPos() + Vec3(0,self.speed*self.dt,0))
        self.nyancatSide.setPos(self.nyancatSide.getPos() + Vec3(0,self.speed*self.dt,0))
       
        if self.sm.getY()<350: #lights out zone ending
            self.slnp.setPos(self.slnp.getPos() + Vec3(0,self.speed*self.dt,0))
       
        
        return task.cont
    

    def update_keymap(self,key,state):
        """
        Update the keymap given the current input.
        """

        if key in ["left", "right"] and self.camState:
           
            if self.reverse:
                
                        
                if key == "left":
                    self.keymap["right"] =  state
                    
                    
                else:
                    self.keymap["left"] = state
                    
                          
            else:
                self.keymap[key] = state
            
            
        if self.jumping==False and key=="jump" and state==True:
            self.keymap[key] = state
            self.jumping=True
            self.jumpSpeed=JUMP_SPEED


    def quit(self):
        """
        Quit the application.
        """
        sys.exit()


    def stop(self, won=False):
        """
        Stop the game.
        """
        self.gameOverScreen.show()
        if won:
            self.resultLabel.setText("You Beat The Game!")
        else:
            self.resultLabel.setText("Game Over!")

        current_score=int(self.score/25)
        self.finalScoreLabel["text"] = "Final score: " + str(current_score) + "\nBest Score: " +\
            str(max(current_score,max(scores)))
        self.finalScoreLabel.setText()
        self.mySound.stop()
        self.taskMgr.remove('zonePropertiesTask')
        self.taskMgr.remove('updateScoreTask')
        self.taskMgr.remove("UpdateODE")
        

    def menu(self):
        """
        Create post game menu.
        """
        self.gameOverScreen = DirectDialog(frameSize = (-0.7, 0.7, -0.7, 0.7),
                                   fadeScreen = 0.4,
                                   relief = DGG.FLAT)

        self.gameOverScreen.hide()

        self.resultLabel = DirectLabel(text = "Game Over!",
                    parent = self.gameOverScreen,
                    scale = 0.1,
                    pos = (0, 0, 0.2))

        self.finalScoreLabel = DirectLabel(text = "",
                                        parent = self.gameOverScreen,
                                        scale = 0.07,
                                        pos = (0, 0, 0))

        btn = DirectButton(text = "Restart (r)",
                   command = self.restart_game,
                   pos = (-0.3, 0, -0.2),
                   parent = self.gameOverScreen,
                   scale = 0.07)

        btn.setTransparency(True)

        btn = DirectButton(text = "Quit (q)",
                        command = self.quit,
                        pos = (0.3, 0, -0.2),
                        parent = self.gameOverScreen,
                        scale = 0.07)

        btn.setTransparency(True)
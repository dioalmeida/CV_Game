#  Dev Team: Diogo Almeida, Rodrigo Ferreira & Luís Laranjeira
import math
import random

from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from panda3d.core import *
from panda3d.ode import *
from panda3d.physics import *
#import gltf

PLAYER_TAG = "player-instance"
MAP_TAG = "map-instance"
TRAPS_TAG = "traps-instance"
SPEED = 20
JUMP_SPEED = 10
FLOOR_Z=1
scores=[]
#colours=[(84,206,145),(120,84,206),(206,84,116)]
colours=[(255,255,0),(0,255,255),(255,0,255)]
zones = [0,1,2]
CAMERA_DIST_X = 40
CAMERA_DIST_Y = 50
CAMERA_DIST_Z= 10
class Game(ShowBase):
          

    def __init__(self):
        super().__init__()
       
        # Variable declaration
        self.speed = SPEED
        self.jump = 0
        self.jump_speed = JUMP_SPEED

        self.sm = None
        self.score=0
        self.scoreUI = OnscreenText(text = "0",
                            pos = (-1.3, 0.825),
                            mayChange = True,
                            align = TextNode.ALeft)
        self.ground = None
        self.contacts = None
        self.space = None
        self.dt=0
        self.colourTimer=0
        # Setup collision detection & physics
        self.add_player()
        self.setup_level()
        self.add_lighting()
        # Setup game world and instances
        self.camState = True # true = behind, false = side
        self.dr = base.camNode.getDisplayRegion(0)
        self.dr.setActive(1) 
        self.camBehind= Camera("camBehind")
        self.camSide = Camera("camSide")
        self.cameraBehind = self.render.attachNewNode(self.camBehind)
        self.cameraSide = self.render.attachNewNode(self.camSide)
        self.dr.setCamera(self.cameraBehind)
        self.taskMgr.add(self.followCubeBehindTask, "followCubeBehindTask")
        self.taskMgr.add(self.followCubeSideTask, "followCubeSideTask")
        self.taskMgr.add(self.checkImpactTask,"checkImpactTask")
        self.taskMgr.add(self.updateColoursTask,"updateColoursTask")
        self.taskMgr.add(self.updateScoreTask,"updateScoreTask")

       

        # Start tasks
        self.taskMgr.add(self.update_ode, "UpdateODE")

        # register event handlers
        self.keymap = {"left":False,"right":False,"jump":False}
        self.accept("a", self.__update_keymap,["left",True])  # , ["w"])
        self.accept("a-up", self.__update_keymap,["left",False])
        self.accept("d", self.__update_keymap,["right",True])
        self.accept("d-up", self.__update_keymap,["right",False])
        self.accept("e", self.toggleCamera,[self.camState])
        self.accept("space", self.__update_keymap,["jump",True])
        self.accept("r", self.restart_game)

    def restart_game(self): 
        self.sm.setPos(0,-40,FLOOR_Z)
        scores.append(int(self.score/25))
        print(scores)
        self.score=0
       

    def updateScoreTask(self, task):
        self.score +=1
        if self.score%25==0:
            self.scoreUI.setText(str(int(self.score/25)))
        return Task.cont

    
    def updateColoursTask(self, task):
        
        self.colourTimer+=self.dt
        if self.colourTimer>2:
            new_cube_colour = Vec4(*colours[random.randint(0,2)],1)
            for wall in self.walls:
                new_wall_colour = Vec4(*colours[random.randint(0,2)],1)
                wall.setColor(new_wall_colour)
                #if new_cube_colour== new_wall_colour:
                    #print("same colour")
            self.colourTimer=0
            self.sm.setColor(new_cube_colour)
        return Task.cont

    
    def add_player(self):

        #self.player = self.loader.loadModel("assets/cube2.egg")
        #self.player = self.loader.loadModel("assets/cube_tex.egg")
        self.player = self.loader.loadModel("assets/textest.egg")
        self.sm = self.render.attachNewNode(PLAYER_TAG)
        self.sm.setColor(*colours[0])
        self.sm.setPos(0,-40, FLOOR_Z)
        cube_tex = self.loader.loadTexture('assets/brick.png')
        self.sm.setTexture(cube_tex, 1)
        self.colliderNode = CollisionNode("cPlayer")

        self.colliderNode.addSolid(CollisionBox(LPoint3(0,0,0),LPoint3(2,2,2))) # change later
        self.collider = self.sm.attachNewNode(self.colliderNode)
        #self.collider.show() #remove later
        
        self.player.instanceTo(self.sm)
        self.jumping=False
        self.jumpSpeed=0
        self.lastX=-1
        self.lastY=-1
        self.lastZ=-1
        
        
        
    def setup_level(self):
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        #self.queue = CollisionHandlerQueue()
        floor = self.render.attachNewNode(CollisionNode("floor"))
        floorColliderNode = CollisionNode("cFloor")
        floorColliderNode.addSolid(CollisionPlane(Plane(Vec3(0, 0, 0), Point3(0, 0, 0))))
        floor.setColor(0,0,0,0.5)
        
        
        self.floorCollider = floor.attachNewNode(floorColliderNode)
        #self.floorCollider.show()
        self.plane = self.loader.loadModel("assets/floorplane.egg")
        self.plane.setPos(5,20,-1)
        self.plane.reparentTo(self.render)
        self.plane.setColor(100,100,100,0.5)
        tex = self.loader.loadTexture('assets/brick.png')
        self.plane.setTexture(tex, 1)

        wall_heights= [FLOOR_Z,FLOOR_Z+4]
        self.walls = []
        for i in range(20):
            #if random.randint(0,1):#ghost or regular wall
            wall = self.loader.loadModel("assets/basewall.egg")
            #else:
            #    wall = self.loader.loadModel("assets/ghostbasewall.egg")
            wall.setPos(random.randint(-4,2),12*(i+1),wall_heights[random.randint(0,(len(wall_heights))-1)])
            wall.reparentTo(self.render)
            wall.setColor(Vec4(*colours[random.randint(0,2)],1))
            #tex = self.loader.loadTexture('assets/brick.png')
            wall.setTexture(tex, 1)
            #myMaterial = Material()
            #myMaterial.setShininess(5.0) # Make this material shiny
            #myMaterial.setAmbient((0, 0, 1, 1)) # Make this material blue
            #wall.setMaterial(myMaterial) # Apply the material to this nodePath
            self.walls.append(wall)
        
        self.pusher.addCollider(self.collider, self.sm)
        
        
        self.cTrav.addCollider(self.collider, self.pusher)
        
      
    def add_lighting(self):
        self.alight = AmbientLight("alight")
        self.alight.setColor((0.2, 0.2, 0.2, .2))
        
        self.dlight = DirectionalLight("dlight")
        self.dlight.setDirection(LVector3(0, 45, 45))
        self.dlight.setColor((0.2, 0.2, 0.2, .2))
        
        self.render.setLight(self.render.attachNewNode(self.alight))
        self.render.setLight(self.render.attachNewNode(self.dlight))
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

        self.cameraBehind.setPos(self.sm.getX(), self.sm.getY()-CAMERA_DIST_Y, CAMERA_DIST_Z)
        self.cameraBehind.lookAt(self.sm)
        

    

        return Task.cont
    
    def checkImpactTask(self, task):
        if self.sm.getY() == self.lastY:
            self.restart_game()
        if self.sm.getZ() == self.lastZ and self.lastZ>1:
            self.jumping=False
            self.restart_game()
        #if self.camState and (self.keymap["left"] or self.keymap["right"]) and self.sm.getX()==self.lastX:
        #    self.restart_game()
        else:    
            self.lastX= self.sm.getX()
            self.lastY = self.sm.getY()
            self.lastZ = self.sm.getZ()
        return Task.cont
    
    def followCubeSideTask(self, task):

        

        self.cameraSide.setPos(self.sm.getX()+ CAMERA_DIST_X, self.sm.getY()-5, CAMERA_DIST_Z)
        self.cameraSide.lookAt(self.sm)
        

    

        return Task.cont
    
    def update_ode(self, task):
       
        current_vec=self.sm.getPos()

        
        change_vec=Vec3(0,0,0)
       
        self.dt = globalClock.getDt()
        
        updated_z=FLOOR_Z
        if self.keymap["left"]:
            change_vec+= Vec3(-self.speed*self.dt,0,0)
            
        if self.keymap["right"]:
            change_vec+= Vec3(self.speed*self.dt,0,0)
            
        #if self.keymap["jump"]:
        if self.jumping:
       
            """
            updated_z=self.sm.getZ()+self.jumpSpeed*dt
            if updated_z > FLOOR_Z:
                self.jumpSpeed = self.jumpSpeed - 9.8*dt #faster 
            if updated_z < FLOOR_Z:
                updated_z=FLOOR_Z
                self.jumpSpeed = 0
                self.jumping = False
            """
            updated_z=self.sm.getZ()+self.jumpSpeed*self.dt
            self.jumpSpeed = self.jumpSpeed - 9.8*self.dt
            if updated_z<=FLOOR_Z:
                self.jumping=False
               
        
        change_vec+=Vec3(0,self.speed*self.dt,0)
        self.plane.setPos(self.plane.getPos() + Vec3(0,self.speed*self.dt,0))
        self.sm.setPos(current_vec+change_vec)
        self.sm.setZ(updated_z)
        
        curr_X = self.sm.getX()
        if curr_X<=-7 or curr_X>=6:
            self.restart_game()

        return task.cont
    
    def __update_keymap(self,key,state):
        if key in ["left", "right"] and self.camState:
            self.keymap[key] = state
        if self.jumping==False and key=="jump" and not self.camState:
            self.keymap[key] = state
            self.jumping=True
            self.jumpSpeed=JUMP_SPEED
            
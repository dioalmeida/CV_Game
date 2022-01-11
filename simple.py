#  Dev Team: Diogo Almeida, Rodrigo Ferreira & Luís Laranjeira
import math
import random

from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
from panda3d.ode import *
from panda3d.physics import *
import gltf

PLAYER_TAG = "player-instance"
MAP_TAG = "map-instance"
TRAPS_TAG = "traps-instance"
SPEED = 15
JUMP_SPEED = 10
FLOOR_Z=1

CAMERA_DIST_X = 40
CAMERA_DIST_Y = 50
class Game(ShowBase):

    def __init__(self):
        super().__init__()
        gltf.patch_loader(self.loader) #enable gltf reading

        # Variable declaration
        self.speed = SPEED
        self.jump = 0
        self.jump_speed = JUMP_SPEED

        self.sm = None
        self.ground = None
        self.contacts = None
        self.space = None
        # Setup collision detection & physics
        self.add_player()
        self.setup_level()
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
    def restart_game(self): #simple just for debugging
        self.sm.setPos(0,-40,FLOOR_Z)
    
    def add_player(self):

        self.player = self.loader.loadModel("assets/cube2.egg")
        self.sm = self.render.attachNewNode(PLAYER_TAG)
        self.sm.setColor(0,255,0,0.5)
        self.sm.setPos(0,-40, FLOOR_Z)
        self.colliderNode = CollisionNode("cPlayer")

        self.colliderNode.addSolid(CollisionBox(LPoint3(0,0,0),LPoint3(2,2,2))) # change later
        self.collider = self.sm.attachNewNode(self.colliderNode)
        self.collider.show() #remove later
        
        self.player.instanceTo(self.sm)
        self.jumping=False
        self.jumpSpeed=0
        
        
        
    def setup_level(self):
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        floor = self.render.attachNewNode(CollisionNode("floor"))
        floorColliderNode = CollisionNode("cFloor")
        floorColliderNode.addSolid(CollisionPlane(Plane(Vec3(0, 0, FLOOR_Z), Point3(0, 0, 0))))
        floor.setColor(0,0,255,0.5)
        
        
        self.floorCollider = floor.attachNewNode(floorColliderNode)
        self.floorCollider.show()
        self.plane = self.loader.loadModel("assets/floor.egg")
        self.plane.setPos(0,0,FLOOR_Z)
        self.plane.reparentTo(self.render)
        self.plane.setColor(255,0,0,0.5)

        self.map = self.loader.loadModel("assets/testmap3.egg")
        
        self.map.setPos(1,0,2)
        self.map.reparentTo(self.render)
        self.map.setColor(0,0,255,0.5)
        self.traps = self.loader.loadModel("assets/traps.glb")
        
        self.traps.setPos(1,0,2)
        self.traps.reparentTo(self.render)
        self.traps.setColor(0,0,255,0.5)
        """
        
        self.map2 = self.loader.loadModel("assets/untitled.egg")
        self.map2.setPos(1,10,2)
        self.map2.reparentTo(self.render)
        self.map2.setColor(0,0,255,0.5)
        """

        base.pusher.addCollider(self.collider, self.sm)
        base.cTrav.addCollider(self.collider, self.pusher)
        #base.pusher.addCollider(self.floorCollider, floor)
        #base.cTrav.addCollider(self.floorCollider, self.pusher)

    def add_lighting(self):
        self.alight = AmbientLight("alight")
        self.alight.setColor((0.2, 0.2, 0.2, 1))
        
        self.dlight = DirectionalLight("dlight")
        self.dlight.setDirection(LVector3(0, 45, -45))
        self.dlight.setColor((0.2, 0.2, 0.2, 1))
        
        self.render.setLight(self.render.attachNewNode(self.alight))
        self.render.setLight(self.render.attachNewNode(self.dlight))
    
    def toggleCamera(self,state):
        if self.camState:
            self.dr.setCamera(self.cameraSide)
        else:
            self.dr.setCamera(self.cameraBehind)
        self.camState = not self.camState
    

    def followCubeBehindTask(self, task):

        self.cameraBehind.setPos(self.sm.getX(), self.sm.getY()-CAMERA_DIST_Y, 3)
        self.cameraBehind.lookAt(self.sm)
        

    

        return Task.cont

    def followCubeSideTask(self, task):

        

        self.cameraSide.setPos(self.sm.getX()+ CAMERA_DIST_X, self.sm.getY()-5, 10)
        self.cameraSide.lookAt(self.sm)
        

    

        return Task.cont
    
    def update_ode(self, task):
       
        current_vec=self.sm.getPos()
        change_vec=Vec3(0,0,0)
       
        dt = globalClock.getDt()
        
        updated_z=FLOOR_Z
        if self.keymap["left"]:
            change_vec+= Vec3(-self.speed*dt,0,0)
            
        if self.keymap["right"]:
            change_vec+= Vec3(self.speed*dt,0,0)
            
        if self.keymap["jump"]:
       
       
            """
            updated_z=self.sm.getZ()+self.jumpSpeed*dt
            if updated_z > FLOOR_Z:
                self.jumpSpeed = self.jumpSpeed - 9.8*dt #faster 
            if updated_z < FLOOR_Z:
                updated_z=FLOOR_Z
                self.jumpSpeed = 0
                self.jumping = False
            """
            updated_z=self.sm.getZ()+self.jumpSpeed*dt
            self.jumpSpeed = self.jumpSpeed - 9.8*dt
            if updated_z<=FLOOR_Z:
                self.jumping=False
       
        change_vec+=Vec3(0,self.speed*dt,0)

        self.sm.setPos(current_vec+change_vec)
        self.sm.setZ(updated_z)


        return task.cont
    
    def __update_keymap(self,key,state):
        if key in ["left", "right"] and self.camState:
            self.keymap[key] = state
        if self.jumping==False and key=="jump" and not self.camState:
            self.keymap[key] = state
            self.jumping=True
            self.jumpSpeed=JUMP_SPEED
            
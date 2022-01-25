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
random.seed(11)
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
        self.load_back()
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
        self.closestWall=None
        self.cubeColourIndex=0
        self.wallTexDict={}
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
        self.taskMgr.add(self.closestWallTask,"closestWallTask", priority=1)
        self.taskMgr.add(self.checkImpactTask2,"checkImpactTask2", priority=2)
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


    def load_back(self):
        """
        myImage=PNMImage()
        myImage.read(Filename("assets/nyancat.gif"))
        back_tex = Texture()
        back_tex.load(myImage)
        self.skybox = self.loader.loadModel("assets/cube2")
        self.skybox.setPos(-100,1000,10)
        self.skybox.reparentTo(self.render)
        #self.skybox.setColor(100,100,100,0.5)
        self.skybox.setScale(100)
        self.skybox.setTwoSided(True)
        self.skybox.setTexture(back_tex)
        """
        self.nyancat = self.loader.loadModel("assets/nyancat/textest")
        self.nyancat.setPos(-10,50,0)
        self.nyancat.setScale(100)
        self.nyancat.reparentTo(self.render)
        self.nyancatSide = self.loader.loadModel("assets/nyancat/textest")
        self.nyancatSide.setPos(-50,-20,0)
        self.nyancatSide.setScale(100)
        self.nyancatSide.setHpr(self.nyancatSide, (90,0,0))
        self.nyancatSide.reparentTo(self.render)
        """
        skybox = loader.loadModel("assets/test.egg")
        skybox.setScale(512)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(render)
        """

    def restart_game(self): 
        self.sm.setPos(0,-50,FLOOR_Z)
        self.plane.setPos(5,20,-1)
        self.nyancat.setPos(-10,50,0)
        self.nyancatSide.setPos(-50,-20,0)
        scores.append(int(self.score/25))
        print(scores)
        self.score=0
        self.wallsActive = []
        for wall in self.walls:
            wall.reparentTo(self.render)
            self.wallsActive.append(wall)
    def updateScoreTask(self, task):
        self.score +=1
        if self.score%25==0:
            self.scoreUI.setText(str(int(self.score/25)))
        return Task.cont

    
    def updateColoursTask(self, task):
        
        self.colourTimer+=self.dt
        if self.colourTimer>2:
            #new_cube_colour = Vec4(*colours[random.randint(0,2)],1)
            new_cube_tex = self.all_tex[random.randint(0,2)]
            for wall in self.wallsActive:
                new_wall_tex = self.all_tex[random.randint(0,2)]
                wall.setTexture(new_wall_tex)
                self.wallTexDict[wall.getY()]=new_wall_tex
                #if new_cube_tex== new_wall_tex:
                    
            self.colourTimer=0
            self.sm.setTexture(new_cube_tex)
            self.cubeColourIndex=new_cube_tex
        return Task.cont

    
    def add_player(self):

        #self.player = self.loader.loadModel("assets/cube2.egg")
        #self.player = self.loader.loadModel("assets/cube_tex.egg")
        self.player = self.loader.loadModel("assets/textest.egg")
        self.sm = self.render.attachNewNode(PLAYER_TAG)
        self.sm.setColor(*colours[0])
        self.sm.setPos(0,-50, FLOOR_Z)
        cube_tex = self.loader.loadTexture('assets/tex/brick.png')
        self.sm.setTexture(cube_tex, 1)
        self.colliderNode = CollisionNode("cPlayer")

        self.colliderNode.addSolid(CollisionBox(LPoint3(0,0,0),LPoint3(2,2,2))) # change later
        self.collider = self.sm.attachNewNode(self.colliderNode)
        #self.collider.show() #remove later
        
        self.player.instanceTo(self.sm)
        self.jumping=False
        self.jumpSpeed=0
        self.lastX=-1
        self.lastY=12
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
        self.plane.setColor(0,0,255,0.5)
        tex_moon = self.loader.loadTexture('assets/tex/moon.png')
        self.plane.setTexture(tex_moon)
        tex0 = self.loader.loadTexture('assets/tex/brick0.png')
        tex1 = self.loader.loadTexture('assets/tex/brick1.png')
        tex2 = self.loader.loadTexture('assets/tex/brick2.png')
        self.all_tex = [tex0,tex1,tex2]
        self.plane.setTexture(tex_moon, 1)

        wall_heights= [FLOOR_Z,FLOOR_Z+4]
        self.walls = []
        self.wallsActive = []
        for i in range(15):
            #if random.randint(0,1):#ghost or regular wall
            #wall = self.loader.loadModel("assets/basewall.egg")
            wall = self.loader.loadModel("assets/ghostwall_tex.egg")
            #else:
            #    wall = self.loader.loadModel("assets/ghostbasewall.egg")
            wall.setPos(random.randint(-4,2),12*(i+1),wall_heights[random.randint(0,(len(wall_heights))-1)])
            wall.reparentTo(self.render)
            #wall.setColor(Vec4(*colours[random.randint(0,2)],1))
            #tex = self.loader.loadTexture('assets/brick.png')
            
            
            
            myMaterial = Material()
            myMaterial.setShininess(5.0) # Make this material shiny
            myMaterial.setAmbient((0, 0, 1, 1)) # Make this material blue
            colour=Vec4(*colours[random.randint(0,2)],1)
            myMaterial.setDiffuse(colour)
            wall.setMaterial(myMaterial) # Apply the material to this nodePath
            texture_index = random.randint(0,2)
            wall.setTexture(self.all_tex[texture_index], 1)
            self.walls.append(wall)
            self.wallsActive.append(wall)
            self.wallTexDict[12*(i+1)]=texture_index
        
        self.pusher.addCollider(self.collider, self.sm)
        
        
        self.cTrav.addCollider(self.collider, self.pusher)
        
    def closestWallTask(self, task):
        dist=1000
        closest=None
        
        for wall in self.wallsActive:
            #self.walls.remove()
            curr_dist = wall.getY() - self.sm.getY()
            if curr_dist>=0 and curr_dist< dist:
                dist=curr_dist
                closest=wall
            #if curr_dist>=0:
                #self.walls.append((wall,tex))
            #    pass
            elif curr_dist<-7:
                wall.detachNode()
                self.wallsActive.remove(wall)
        self.closestWall = closest
        #moon =  self.loader.loadTexture('assets/tex/moon.png')
        #if self.closestWall:
        #    self.closestWall.setTexture(moon)
        #moontex=self.loader.loadTexture('assets/tex/moon.png')
        #closest.setTexture(moontex,1)
        return Task.cont  
    def add_lighting(self):
        
        self.alight = AmbientLight("alight")
        self.alight.setColor((255, 255, 255, .2))
        """
        
        self.dlight = DirectionalLight("dlight")
        self.dlight.setDirection(LVector3(0, 45, 45))
        self.dlight.setColor((0.2, 0.2, 0.2, .2))

        plight = PointLight('plight')
        plight.setColor((0.2, 0.2, 0.2, 1))
        plnp = self.render.attachNewNode(plight)
        plnp.setPos(0, 0, 0)
        self.render.setLight(plnp)
        """
        
        self.render.setLight(self.render.attachNewNode(self.alight))
        #self.render.setLight(self.render.attachNewNode(self.dlight))
        slight = Spotlight('slight')
        slight.setColor((255, 255, 255, 0.5))
        lens = PerspectiveLens()
        slight.setLens(lens)
        self.slnp = self.render.attachNewNode(slight)
        self.slnp.setPos(0, self.sm.getY()-CAMERA_DIST_Y, 100)
        self.slnp.lookAt(self.sm)
        self.render.setLight(self.slnp)
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
        #self.slnp.lookAt(self.sm)
        

    

        return Task.cont
    
    def checkImpactTask(self, task):
        ####check closest wall
        if self.sm.getY() == self.lastY:
            #if self.cubeColourIndex!=self.wallTexDict[self.lastY]:
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
    
    
    def checkImpactTask2(self, task):
        
        if self.closestWall:
            if (self.sm.getY() >= self.closestWall.getY()-3 and self.sm.getY() <= self.closestWall.getY()+1):
                
                if  (self.sm.getZ() >= self.closestWall.getZ()-1 and self.sm.getZ() <= self.closestWall.getZ()+1) and (self.sm.getX() >= self.closestWall.getX()-3 and self.sm.getX() <= self.closestWall.getX()+3):
                    #if self.cubeColourIndex!=self.wallTexDict[self.closestWall.getY()]:#[self.lastY]:
                    if self.sm.getTexture()!=self.closestWall.getTexture():#[self.lastY]:
                        self.restart_game()
                
                
            
        return Task.cont
    
    def followCubeSideTask(self, task):

        

        self.cameraSide.setPos(self.sm.getX()+ CAMERA_DIST_X, self.sm.getY()-5, CAMERA_DIST_Z)
        #self.slnp.setPos(self.sm.getX()+ CAMERA_DIST_X, self.sm.getY()-5,100)
        #self.slnp.lookAt(self.sm)
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
       
           
            updated_z=self.sm.getZ()+self.jumpSpeed*self.dt
            self.jumpSpeed = self.jumpSpeed - 9.8*self.dt
            if updated_z<=FLOOR_Z:
                self.jumping=False
               
        
        change_vec+=Vec3(0,self.speed*self.dt,0)
        self.plane.setPos(self.plane.getPos() + Vec3(0,self.speed*self.dt,0))
        self.sm.setPos(current_vec+change_vec)
        self.sm.setZ(updated_z)
        
        curr_X = self.sm.getX()
        if curr_X<=-7 or curr_X>=5.90:
            self.restart_game()
        self.slnp.setPos(self.slnp.getPos() + Vec3(0,self.speed*self.dt,0))
        self.slnp.lookAt(self.sm)
        self.nyancat.setPos(self.nyancat.getPos() + Vec3(0,self.speed*self.dt,0))
        self.nyancatSide.setPos(self.nyancatSide.getPos() + Vec3(0,self.speed*self.dt,0))

        return task.cont
    
    def __update_keymap(self,key,state):
        if key in ["left", "right"] and self.camState:
            self.keymap[key] = state
        if self.jumping==False and key=="jump":# and not self.camState:
            self.keymap[key] = state
            self.jumping=True
            self.jumpSpeed=JUMP_SPEED
            
from math import cos, pi, sin

from direct.actor.Actor import Actor
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
"""

from panda3d.core import (CardMaker, Geom, GeomNode, GeomTriangles,
                          GeomVertexData, GeomVertexFormat, GeomVertexWriter,
                          Light, LVector3, PerspectiveLens, Point3, Spotlight,
                          TextNode, Texture, Vec3, Vec4, lookAt,ClockObject, Camera)

"""
from panda3d.core import *
class GameObject():
    pass    
class Player(GameObject):
    pass
class Obstacle(GameObject):
    pass

# aux function
def normalized(*args):
    myVec = LVector3(*args)
    myVec.normalize()
    return myVec


# creating a square for the cube
def makeSquare(x1, y1, z1, x2, y2, z2):
    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData('square', format, Geom.UHDynamic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    # make sure we draw the sqaure in the right plane
    if x1 != x2:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y1, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y2, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y2 - 1, 2 * z2 - 1))

    else:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y2, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y1, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z2 - 1))

    # adding different colors to the vertex for visibility
    color.addData4f(1.0, 0.0, 0.0, 1.0)
    #color.addData4f(1.0, 0.0, 0.0, 1.0)
    #color.addData4f(1.0, 0.0, 0.0, 1.0)
    #color.addData4f(1.0, 0.0, 0.0, 1.0)
    color.addData4f(0.0, 1.0, 0.0, 1.0)
    color.addData4f(0.0, 0.0, 1.0, 1.0)
    color.addData4f(1.0, 0.0, 1.0, 1.0)

    texcoord.addData2f(0.0, 1.0)
    texcoord.addData2f(0.0, 0.0)
    texcoord.addData2f(1.0, 0.0)
    texcoord.addData2f(1.0, 1.0)

    # Quads aren't directly supported by the Geom interface
    # you might be interested in the CardMaker class if you are
    # interested in rectangle though
    tris = GeomTriangles(Geom.UHDynamic)
    tris.addVertices(0, 1, 3)
    tris.addVertices(1, 2, 3)

    square = Geom(vdata)
    square.addPrimitive(tris)
    return square



class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        #setting up scene
        properties = WindowProperties()
        properties.setSize(900, 900)
        self.win.requestProperties(properties)
        self.scene = self.loader.loadModel("models/environment")
        
        self.scene.reparentTo(self.render)
        self.scene.setScale(.25,.25,.25)
        self.scene.setPos(-8,42,-3)
        
        #setting up cameras
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
        
        
        #setting up cube and its movement
        self.updateTask = self.taskMgr.add(self.update, "update")
        square0 = makeSquare(-1, -1, -1, 1, -1, 1)
        square1 = makeSquare(-1, 1, -1, 1, 1, 1)
        square2 = makeSquare(-1, 1, 1, 1, -1, 1)
        square3 = makeSquare(-1, 1, -1, 1, -1, -1)
        square4 = makeSquare(-1, -1, -1, -1, 1, 1)
        square5 = makeSquare(1, -1, -1, 1, 1, 1)
        snode = GeomNode('square')
        snode.addGeom(square0)
        snode.addGeom(square1)
        snode.addGeom(square2)
        snode.addGeom(square3)
        snode.addGeom(square4)
        snode.addGeom(square5)

        self.cube = self.render.attachNewNode(snode)
        self.cube.setTwoSided(True)
        self.taskMgr.add(self.advanceCube,"advanceCube")
        self.taskMgr.add(self.jumpCube,"jumpCube")
        #self.jumpSpeed=3 #testing
        self.jumping=False
        self.jumpSpeed=0
        """
        self.cTrav = CollisionTraverser()

        self.cubeCol = CollisionNode('cubeCol')
        self.cubeCol.addSolid(CollisionSphere(center=(0, 0, 2), radius=1.5)) # change to cube
        self.cubeCol.addSolid(CollisionSphere(center=(0, -0.25, 4), radius=1.5)) # # change to cube
        self.cubeCol.setFromCollideMask(CollideMask.bit(0))
        self.cubeCol.setIntoCollideMask(CollideMask.allOff())
        self.cubeColNp = self.cube.attachNewNode(self.cubeCol)
        self.cubePusher = CollisionHandlerPusher()
        self.cubePusher.horizontal = True
        self.cTrav.showCollisions(render)
        # Note that we need to add ralph both to the pusher and to the
        # traverser; the pusher needs to know which node to push back when a
        # collision occurs!
        self.cubePusher.addCollider(self.cubeColNp, self.cube)
        self.cTrav.addCollider(self.cubeColNp, self.cubePusher)

        """
        #setting up interactions
        self.keyMap = {
            "left" : False,
            "right" : False            
        }

        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("w", self.jumpPressed)
        self.accept("s", self.toggleCamera,[self.camState])

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
        print (controlName, "set to", controlState)
    """
    def addFloor(self):
        self.floor = CollisionHandlerFloor()
        floor = self.render.attachNewNode(CollisionNode("floor"))
        floor.node().addSolid(CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0))))

        self.cTrav.addCollider(self.col_player, self.floor)

        floor.show()

    """
    def toggleCamera(self,state):
        if self.camState:
            self.dr.setCamera(self.cameraSide)
        else:
            self.dr.setCamera(self.cameraBehind)
        print("switched cams")
        self.camState = not self.camState

    def followCubeBehindTask(self, task):

        

        self.cameraBehind.setPos(self.cube.getX(), self.cube.getY()-15, 3)
        self.cameraBehind.lookAt(self.cube)
        

    

        return Task.cont

    def followCubeSideTask(self, task):

        

        self.cameraSide.setPos(self.cube.getX()+ 20, self.cube.getY()-5, 3)
        self.cameraSide.lookAt(self.cube)
        

    

        return Task.cont

    def toggleCameraTask(self, task):
        pass

    def advanceCube(self, task):
        self.cube.setPos(self.cube.getPos() + Vec3(0,0.1, 0))
        return task.cont

    def jumpPressed(self):
        if self.jumping == False:
            self.jumping=True
            self.jumpSpeed=13
            

    def jumpCube(self, task):
        dt = ClockObject.getGlobalClock().dt
        self.cube.setZ(self.cube.getZ()+self.jumpSpeed*dt)
        if self.cube.getZ() > 0:
            self.jumpSpeed = self.jumpSpeed - 9.8*dt #faster 
        if self.cube.getZ() < 0:
            self.cube.setZ(0)
            self.jumpSpeed = 0
            self.jumping = False
        return task.cont


    def update(self,task):
        dt = ClockObject.getGlobalClock().dt

        if self.keyMap["left"]:
            self.cube.setPos(self.cube.getPos() + Vec3(-5.0*dt,0, 0))
        if self.keyMap["right"]:
            self.cube.setPos(self.cube.getPos() + Vec3(5*dt,0, 0))
        
        return task.cont

app = MyApp()
app.run()

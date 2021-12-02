from math import cos, pi, sin

from direct.actor.Actor import Actor
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (CardMaker, Geom, GeomNode, GeomTriangles,
                          GeomVertexData, GeomVertexFormat, GeomVertexWriter,
                          Light, LVector3, PerspectiveLens, Point3, Spotlight,
                          TextNode, Texture, Vec3, Vec4, lookAt,ClockObject)


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
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(.25,.25,.25)
        self.scene.setPos(-8,42,-3)
       
        self.taskMgr.add(self.followCubeTask, "followCubeTask")  
        self.updateTask = self.taskMgr.add(self.update, "update")  
        self.taskMgr.add(self.advanceCube,"advanceCube")
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
        
        self.camera.setPos(0,-10,0)
        
        self.keyMap = {
            "left" : False,
            "right" : False            
        }
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
        print (controlName, "set to", controlState)

    def followCubeTask(self, task):

        

        self.camera.setPos(self.cube.getX(), self.cube.getY()-15, 3)
        self.camera.lookAt(self.cube)
        

    

        return Task.cont

    def advanceCube(self, task):
        self.cube.setPos(self.cube.getPos() + Vec3(0,0.1, 0))
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

#  Dev Team: Diogo Almeida, Rodrigo Ferreira & Luís Laranjeira
import math
import random

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
from panda3d.ode import *
from panda3d.physics import *

PLAYER_TAG = "player-instance"
SPEED = 15
JUMP_SPEED = 10


class Game(ShowBase):

    def __init__(self):
        super().__init__()
        # Variable declaration
        self.speed = SPEED
        self.jump = 0
        self.jump_speed = JUMP_SPEED
        # Setup collision detection & physics
        self.setup_collision_detection()
        self.setup_physics()

        # Setup game world and instances
        self.cam.setPos(0, -100, 10)
        self.setup_ode()
        self.add_ground()
        self.add_player()

        # Start tasks
        self.taskMgr.add(self.update_ode, "UpdateODE")
        self.taskMgr.add(self.spin_cam_task, "spinCamTask")

        # register event handlers
        self.keymap = {"left":False,"right":False,"up":False,"down":False,"jump":False}
        self.accept("a", self.__update_keymap,["left",True])  # , ["w"])
        self.accept("a-up", self.__update_keymap,["left",False])
        self.accept("d", self.__update_keymap,["right",True])
        self.accept("d-up", self.__update_keymap,["right",False])
        self.accept("w", self.__update_keymap,["up",True])
        self.accept("w-up", self.__update_keymap,["up",False])
        self.accept("s", self.__update_keymap,["down",True])
        self.accept("s-up", self.__update_keymap,["down",False])
        self.accept("space", self.__update_keymap,["jump",True])
        self.accept("space-up", self.__update_keymap,["jump",False])

        # self.accept("%s-up" % (w_button), self.stop_moving_forward)

    def setup_collision_detection(self):
        self.cTrav = CollisionTraverser()
        self.cTrav.showCollisions(self.render)
        self.notifier = CollisionHandlerEvent()
        self.notifier.addInPattern("%fn-into-%in")
        self.notifier.addOutPattern("%fn-out-%in")
        self.accept(PLAYER_TAG + "-into-floor", self.onCollisionStart)
        self.accept(PLAYER_TAG + "-out-floor", self.onCollisionEnd)

    def setup_physics(self):
        self.enableParticles()

        gravNode = ForceNode("gravity")
        self.render.attachNewNode(gravNode)
        gravityForce = LinearVectorForce(0, 0, -9.81)
        # gravityForce = LinearVectorForce(0, 0, 20)
        gravNode.addForce(gravityForce)
        self.physicsMgr.addLinearForce(gravityForce)

    def setup_ode(self):
        self.odeWorld = OdeWorld()
        self.odeWorld.setGravity(0, 0, -9.81)
        self.odeWorld.initSurfaceTable(1)
        self.odeWorld.setSurfaceEntry(0, 0, 200, 0.7, 0.2, 0.9,
                                      0.00001, 0.0, 0.002)
        self.space = OdeSimpleSpace()
        self.space.setAutoCollideWorld(self.odeWorld)
        self.contacts = OdeJointGroup()
        self.space.setAutoCollideJointGroup(self.contacts)

    def add_ground(self):
        cm = CardMaker("ground")

        # cm.setFrame(-500, 500, -500, 500)
        cm.setFrame(-20, 20, -20, 20)
        ground = render.attachNewNode(cm.generate())
        ground.setColor(0.2, 0.4, 0.8)
        ground.lookAt(0, 0, -1)
        groundGeom = OdePlaneGeom(self.space, Vec4(0, 0, 1, 0))

    def add_player(self):
        self.player = self.loader.loadModel("assets/cube.egg")
        sm = self.render.attachNewNode(PLAYER_TAG)
        # sm.setPos(random.uniform(-20, 20), random.uniform(-30, 30), random.uniform(10, 30))
        sm.setPos(0,0, 1)
        self.player.instanceTo(sm)
        body = OdeBody(self.odeWorld)
        mass = OdeMass()
        # mass.setSphereTotal(10, 1)
        mass.setBoxTotal(2000, 1,1,1)
        body.setMass(mass)
        body.setPosition(sm.getPos())
        geom = OdeSphereGeom(self.space, 1)
        geom.setBody(body)
        sm.setPythonTag("body", body)

    def add_floor(self):
        floor = self.render.attachNewNode(CollisionNode("floor"))
        floor.node().addSolid(CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0))))
        floor.show()

    def onCollisionStart(self, entry):
        pass
        print("player touched the floor.")
        # self.physicsMgr.addLinearForce(self.thrustForce)

    def onCollisionEnd(self, entry):
        print("player left the floor.")
        # self.physicsMgr.removeLinearForce(self.thrustForce)

    def monitor_player(self, task):
        pass
        # print(self.player.getPos())
        # vel = self.player.getPythonTag("velocity")
        # z = self.player.getZ()
        # self.player.setZ(z + vel)
        # vel -= 0.001
        # self.player.setPythonTag("velocity", vel)

        return task.cont

    def spin_cam_task(self, task):
        self.cameraRadius = 30.0

        # angleDegrees = 1  # task.time * 20.0
        # angleDegrees = task.time * 20.0
        # angleRadians = angleDegrees * (math.pi / 180.0)
        # self.camera.setPos(self.cameraRadius * math.sin(angleRadians), -self.cameraRadius * math.cos(angleRadians), 10)
        self.camera.lookAt(0.0, 0.0, 0.0)
        return Task.cont

    def update_ode(self, task):
        player = self.render.find(PLAYER_TAG)
        body = player.getPythonTag("body")
        pos = body.getPosition()
        dt = globalClock.getDt()

        if self.keymap["left"]:
            pos.x -= self.speed * dt
        if self.keymap["right"]:
            pos.x += self.speed * dt
        if self.keymap["up"]:
            pos.y += self.speed * dt
        if self.keymap["down"]:
            pos.y -= self.speed * dt
        if self.keymap["jump"]:
            # self.taskMgr.add(self.__jump, "jumpTask")
            pos.z += self.jump_speed * dt
            print("dt:",dt)
        else:
            self.taskMgr.remove("jumpTask")

        # self.jump -= 1 * dt
        #
        # highestZ = -100
        # if highestZ > self.man.getZ() - .3:
        #     self.jump = 0
        #     self.man.setZ(highestZ + .3)
        #
        body.setPosition(pos)

        # self.player.setPos(pos)

        self.space.autoCollide()
        self.odeWorld.quickStep(dt)
        body = player.getPythonTag("body")
        player.setPosQuat(body.getPosition(), Quat(body.getQuaternion()))
        self.contacts.empty()


        return task.cont

    def __jump(self, task):
        body = self.render.find(PLAYER_TAG).getPythonTag("body")
        pos = body.getPosition()
        dt = globalClock.getDt()
        pos.z += self.jump_speed * dt
        if dt == 0:
            print("dt:",dt)
        print(pos.z)
        body.setPosition(pos)

        return task.cont

    def __update_keymap(self,key,state):
        self.keymap[key] = state
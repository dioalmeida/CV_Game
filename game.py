#  Dev Team: Diogo Almeida, Rodrigo Ferreira & Luís Laranjeira
import math
import os
from direct.showbase.ShowBase import ShowBase
from direct.task import Task


class Game(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.cameraRadius = 30.0
        self.disableMouse()
        self.camera.setPos(0, -30, 0)




    def spinCameraTask(self, task):
        # self.cameraRadius = 30.0

        # angleDegrees = 1#task.time * 20.0
        angleDegrees = task.time * 20.0
        angleRadians = angleDegrees * (math.pi / 180.0)
        self.camera.setPos(self.cameraRadius * math.sin(          angleRadians), -self.cameraRadius * math.cos(angleRadians),               0)
        self.camera.lookAt(0.0, 0.0, 0.0)
        return Task.cont
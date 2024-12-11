import random
import numpy as np
from vpython import vector,mag

class Price:
    def __init__(self):
        r = random.uniform(2,24)
        theta = random.uniform(-np.pi / 2, np.pi / 2)
        alpha = random.uniform(0, np.pi / 2)

        self.x = r * np.cos(theta) * np.sin(alpha)
        self.y = r * np.sin(theta) * np.sin(alpha)
        self.z = r * np.cos(alpha)
        self.pos = vector(self.x,self.y,self.z)

    def pickDet(self,ee_pos):
        """
        This function detects if the end-effector is touching or colliding with provided the price.
        :param ee_pos: vector describing position of end-effector.
        :return: boolean
        """
        d = mag(ee_pos-self.pos)
        if d<1.5:
            print("pick deteceted")
            return True
        else:
            return False

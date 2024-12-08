import random
from vpython import vector,mag

class Price:
    def __init__(self):
        self.x = random.uniform(0,20)
        self.y = random.uniform(0,20)
        self.z = random.uniform(0,20)
        self.pos = vector(self.x,self.y,self.z)

    def pickDet(self,ee_pos):
        """
        This function detects if the end-effector is touching or colliding with provided the price.
        :param ee_pos: vector describing position of end-effector.
        :return: boolean
        """
        d = mag(ee_pos-self.pos)
        print(d)
        if d<2:
            return True
        else:
            return False

from robotic_arm import RoboticArm
import numpy as np

def test_forward_kinematics():
    dh_params = [(0, np.pi/2, 10.5, 0)]
    arm = RoboticArm(dh_params)
    result = arm.forward_kinematics()
    assert isinstance(result, np.ndarray)

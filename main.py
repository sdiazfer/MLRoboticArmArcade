import numpy as np
from robotic_arm import RoboticArm
from gui import GUIManager
from time import sleep

if __name__ == "__main__":
    dh_params = [
        # (a,    alpha,      d,    theta)
        (0,      np.pi/2,    10,   0),  # Link 1
        (10,     0,          0,    0),  # Link 2
        (7,      0,          0,    0),  # Link 3
        (5,      0,          0,    0),  # Link 4
        (3,      0,          0,    0),  # Link 5
    ]

    joint_limits = [
        # (Lower limit,   Upper limit)
        (-90,             90),
        (-90,             90),
        (-170,            170),
        (-170,            170),
        (-170,            170),
    ]

    arm = RoboticArm(dh_params,joint_limits)
    gui = GUIManager(arm)

    while True:
        sleep(1)

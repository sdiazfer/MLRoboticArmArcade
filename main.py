import numpy as np
from robotic_arm import RoboticArm
from gui import GUIManager
from time import sleep

if __name__ == "__main__":
    dh_params = [
        # (a,      alpha,          d,      theta_offset)
        (0,        np.pi/2,        10.5,   0),  # Link 1
        (13.5,     0,              0,      0),   # Link 2
        (16,       0,              0,      0),   # Link 3
        (5.5,     -np.pi/2,        0,      0),   # Link 4
        (0,        0,              7,      0),   # Link 5
    ]
    arm = RoboticArm(dh_params)
    gui = GUIManager(arm)

    while True:
        sleep(1)

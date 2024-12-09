import numpy as np
from vpython import vector

class RoboticArm:
    def __init__(self, dh_params=None, joint_limit = None):
        """
        Initialize the RoboticArm with given DH parameters.
        If no DH parameters are provided, use default values.
        """
        if dh_params is not None:
            self.dh_params = dh_params
        else:
            # Default DH parameters: (a, alpha, d, theta_offset)
            self.dh_params = [
                # (a,     alpha,      d,      theta_offset)
                (0,       np.pi/2,    0.75,   0),    # Link 1
                (0.35,    0,          0,      0),    # Link 2
                (1.25,    0,          0,      0),    # Link 3
                (0.054,   np.pi/2,    1.5,    0),    # Link 4
                (0,      -np.pi/2,    0,      0),    # Link 5
            ]
        self.joint_angles = [0] * len(self.dh_params)  # Initialize joint angles in radians
        self.joint_limit = joint_limit
        print(joint_limit[1][1])

    def dh_matrix(self, a, alpha, d, theta):
        """
        Compute the DH transformation matrix.
        """
        return np.array([
            [np.cos(theta), -np.sin(theta) * np.cos(alpha),  np.sin(theta) * np.sin(alpha), a * np.cos(theta)],
            [np.sin(theta),  np.cos(theta) * np.cos(alpha), -np.cos(theta) * np.sin(alpha), a * np.sin(theta)],
            [0,              np.sin(alpha),                 np.cos(alpha),                d],
            [0,              0,                             0,                            1]
        ])

    def reset_arm(self):
        """
        Reset the joint angles to zero.
        """
        self.joint_angles = [0] * len(self.dh_params)

    def get_joint_pos(self):
        """
        Calculates the position of given joint num.
        :return: pos of join
        """
        joint_pos = [vector(0,0,0)]
        t = np.eye(4)
        for i in range(len(self.dh_params)):
            a, alpha, d, theta = self.dh_params[i]
            t = np.dot(t, self.dh_matrix(a, alpha, d, theta + self.joint_angles[i]))
            joint_pos.append(vector(t[0, 3], t[1, 3], t[2, 3]))
        return joint_pos

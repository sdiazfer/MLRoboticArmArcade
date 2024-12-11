
import numpy as np
from numpy import sin,cos
from vpython import vector,mag

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

    def get_joint_pos(self,joint_angles):
        """
        Calculates the position of given joint num.
        :return: pos of join
        """
        joint_pos = [vector(0,0,0)]
        t = np.eye(4)
        for i in range(len(self.dh_params)):
            a, alpha, d, theta = self.dh_params[i]
            t = np.dot(t, self.dh_matrix(a, alpha, d, theta + joint_angles[i]))
            joint_pos.append(vector(t[0, 3], t[1, 3], t[2, 3]))
        return joint_pos

    def dirKin(self,joint_angles):
        ee_pos = self.get_joint_pos(joint_angles)[-1]
        return ee_pos

    def jacobian(self,joint_angels):
        t1,t2,t3,t4,t5 = joint_angels
        A = 10*cos(t2) + 7*cos(t2+t3) + 5*cos(t2+t3+t4) + 3 * cos(t2+t3+t4+t5)
        j11 = -sin(t1) * A
        j12 = cos(t1) * (-10*sin(t2) - 7*sin(t2+t3) - 5*sin(t2+t3+t4) - 3*sin(t2+t3+t4+t5))
        j13 = cos(t1) * (- 7*sin(t2+t3) - 5*sin(t2+t3+t4) - 3*sin(t2+t3+t4+t5))
        j14 = cos(t1) * (- 5*sin(t2+t3+t4) - 3*sin(t2+t3+t4+t5))
        j15 = cos(t1) * (- 3*sin(t2+t3+t4+t5))
        j21 = cos(t1) * A
        j22 = sin(t1) * (-10*sin(t2) - 7*sin(t2+t3) - 5*sin(t2+t3+t4) - 3*sin(t2+t3+t4+t5))
        j23 = sin(t1) * (- 7*sin(t2+t3) - 5*sin(t2+t3+t4) - 3*sin(t2+t3+t4+t5))
        j24 = sin(t1) * (- 5*sin(t2+t3+t4) - 3*sin(t2+t3+t4+t5))
        j25 = sin(t1) * (- 3*sin(t2+t3+t4+t5))
        j31 = 0
        j32 = A
        j33 = 7*cos(t2+t3) + 5*cos(t2+t3+t4) + 3 * cos(t2+t3+t4+t5)
        j34 = 5*cos(t2+t3+t4) + 3 * cos(t2+t3+t4+t5)
        j35 = 3 * cos(t2+t3+t4+t5)

        j = np.array([
            [j11, j12, j13, j14, j15],
            [j21, j22, j23, j24, j25],
            [j31, j32, j33, j34, j35],
        ])
        return j

    def sequence_planner(self,prices):
        # find a sequence of prices to collect
        num_of_prices = len(prices)
        seq = [self.dirKin(self.joint_angles)]
        seq = seq + [0] * num_of_prices
        for j in range(num_of_prices):
            d = 1000
            for price in prices:
                if (mag(seq[j] - price.pos)) < d:
                    seq[j+1] = price.pos
                    d = (mag(seq[j] - price.pos))
                    m = price
            prices.remove(m)
        return seq

    def trajectory_planner(self,seq,ee_v):
        trajectory = [seq[0]]
        step_count = []
        qc = self.joint_angles
        pc = self.dirKin(qc)
        trajectory_file = open("Trajectory.txt", "w")

        for i in range(len(seq)-1):
            err = 10
            dir = seq[i+1] - trajectory[-1]
            dir = dir.norm()
            old_point = trajectory[-1]
            step = 0
            while err > ee_v * 0.01:
                new_point = old_point + dir * ee_v * 0.01 * step
                err = mag(seq[i+1] - new_point)
                step = step + 1
                pd = new_point
                pc,qc = self.resolved_rate(pd,pc,qc)
                trajectory_file.writelines(",".join(map(str,qc)) + "\n")
            trajectory.append(new_point)
            step_count.append(step)
        trajectory_file.close()


    def resolved_rate(self,pd,pc,qc):
        t = 0.01
        eP = 0.1
        lambdaP = 2
        Vmin = 5
        Vmax = 15
        delta_p = mag(pd-pc)
        qc_mat = np.reshape(qc,(5,1))
        while delta_p>eP:
            Vmod = self.V(delta_p,lambdaP,Vmin,Vmax,eP)
            n_cap = pd - pc
            n_cap.norm()
            pd_dot = Vmod * n_cap
            pd_dot = np.array([[pd_dot.x],[pd_dot.y],[pd_dot.z]])
            j = self.jacobian(qc)
            qd_dot =  np.dot(np.linalg.pinv(j), pd_dot)
            qc_mat = qc_mat + qd_dot * t
            qc = qc_mat.flatten().tolist()
            pc = self.dirKin(qc)
            delta_p = mag(pd-pc)
        return pc,qc

    def V(self,delta_p,lambdaP,Vmin,Vmax,eP):
        if delta_p/eP>lambdaP:
            Vmod = Vmax
        else:
            Vmod = Vmin + (Vmax - Vmin) * (delta_p - eP) / (eP * (lambdaP - 1))
        return Vmod





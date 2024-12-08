from copyreg import pickle

from vpython import *
import numpy as np
import price
from price import Price


class GUIManager:
    def __init__(self, arm):
        self.arm = arm
        # Adjust the center and range to fit the larger robot dimensions
        self.scene = canvas(title="Arcade Robotic Arm Simulator", width=800, height=600)
        self.scene.camera.pos = vector(45,-45,45)
        self.scene.camera.axis = vector(-45,45,-45)
        self.scene.up = vector(0,0,1)

        self.joints = []  # List to hold joint spheres
        self.links = []   # List to hold link cylinders
        self.sliders = []  # List to hold sliders
        self.setup_scene()
        self.update_scene()  # Update positions after setup

    def setup_scene(self):
        """
        Initialize the VPython 3D scene and robotic arm visualization.
        """
        # Base Joint (Joint 1)
        base = sphere(pos=vector(0, 0, 0), radius=1.0, color=color.red)
        self.joints.append(base)

        # Adjust radii based on the scale of the robot
        link_radius = max([param[0] for param in self.arm.dh_params]) * 0.02  # 2% of the largest 'a'
        joint_radius = link_radius * 2

        # Create links and joints
        for i in range(len(self.arm.dh_params)):
            # Links (Blue Cylinders)
            link = cylinder(pos=vector(0, 0, 0), axis=vector(1, 0, 0), radius=link_radius, color=color.blue)
            self.links.append(link)

            # Joints (Red Spheres)
            joint = sphere(pos=vector(0, 0, 0), radius=joint_radius, color=color.red)
            self.joints.append(joint)

        # Add Sliders for Manual Control
        for i in range(len(self.arm.dh_params)):
            wtext(text=f"Joint {i+1}: ")
            slider_ctrl = slider(min=-180, max=180, value=0, length=200, bind=self.update_angle, right=15)
            self.sliders.append(slider_ctrl)
            wtext(text="\n")

        # Create Price list
        self.priceSphere = []
        self.prices = []
        for i in range(5):
            temp = price.Price()
            self.prices.append(temp)
            self.priceSphere.append(sphere(pos = temp.pos,radius = 2.0,color = color.green))


        # Add Randomize and Reset Buttons
        self.randomize_button = button(text="Randomize", bind=self.randomize)
        self.reset_button = button(text="Reset", bind=self.reset_arm)
        self.status = wtext(text=" Status: Ready")  # Status text next to buttons

    def update_scene(self):
        """
        Update the 3D visualization based on the current joint angles.
        """
        t = np.eye(4)  # Start with the identity matrix
        pos = vector(0, 0, 0)  # Initial position

        for i, (link, joint) in enumerate(zip(self.links, self.joints[1:])):
            # Compute the transformation matrix for the current joint
            a, alpha, d, theta_offset = self.arm.dh_params[i]
            theta = self.arm.joint_angles[i] + theta_offset
            t = np.dot(t, self.arm.dh_matrix(a, alpha, d, theta))

            # Extract the new position from the transformation matrix
            new_pos = vector(t[0, 3], t[1, 3], t[2, 3])

            # Update the link's position and orientation
            link.pos = pos
            link.axis = new_pos - pos

            # Update the joint's position
            joint.pos = new_pos

            # Move to the next position
            pos = new_pos
            print(pos)
            for i in range(len(self.prices)):
                if self.prices[i].pickDet(pos):
                    del self.prices[i]
                    self.priceSphere[i].visible = False




    def update_angle(self, slider):
        """
        Update joint angles when sliders are moved.
        """
        idx = self.sliders.index(slider)
        self.arm.joint_angles[idx] = radians(slider.value)
        self.update_scene()

    def randomize(self, button=None):
        """
        Randomize the joint angles.
        """
        import random
        for i in range(len(self.arm.joint_angles)):
            self.arm.joint_angles[i] = random.uniform(-np.pi, np.pi)  # Random angle in radians
            self.sliders[i].value = degrees(self.arm.joint_angles[i])  # Update slider values
        self.update_scene()
        self.status.text = " Status: Randomized"

    def reset_arm(self, button=None):
        """
        Reset the robotic arm to the home position.
        """
        self.arm.reset_arm()
        for slider in self.sliders:
            slider.value = 0
        self.update_scene()
        self.status.text = " Status: Reset"



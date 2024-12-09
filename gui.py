from vpython import *
import numpy as np
import price



class GUIManager:
    def __init__(self, arm):
        self.arm = arm
        # Adjust the center and range to fit the larger robot dimensions
        self.scene = canvas(title="Arcade Robotic Arm Simulator", width=800, height=600)
        self.scene.camera.pos = vector(25,-25,25)
        self.scene.camera.axis = vector(-25,25,-25)
        self.scene.up = vector(0,0,1)

        self.joints = []  # List to hold joint spheres
        self.links = []   # List to hold link cylinders
        self.sliders = []  # List to hold sliders
        self.priceSphere = []  # List to hold price sphere objects
        self.prices = []  # List to hold the pos of the prices

        self.randomize_button = button(text="Randomize", bind=self.randomize)
        self.reset_button = button(text="Reset", bind=self.reset_arm)
        self.status = wtext(text=" Status: Ready\n")  # Status text next to buttons

        self.setup_scene()  # Setting up the scene
        self.update_scene()  # Update positions after setup

    def setup_scene(self):
        """
        Initialize the VPython 3D scene and robotic arm visualization.
        """

        # Adjust radii based on the scale of the robot
        link_radius = max([param[0] for param in self.arm.dh_params]) * 0.02  # 2% of the largest 'a'
        joint_radius = link_radius * 2

        # Base Joint (Joint 1)
        base = sphere(pos=vector(0, 0, 0), radius=joint_radius * 1.5, color=color.red)
        self.joints.append(base)

        # x = cylinder(pos=vector(0, 0, 0), axis=vector(5, 0, 0), radius=link_radius * 2, color=color.cyan)
        # y = cylinder(pos=vector(0, 0, 0), axis=vector(0, 5, 0), radius=link_radius * 2, color=color.blue)
        # z = cylinder(pos=vector(0, 0, 0), axis=vector(0, 0, 5), radius=link_radius * 2, color=color.green)
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
            slider_ctrl = slider(min = self.arm.joint_limit[i][0],
                                 max = self.arm.joint_limit[i][1],
                                 length = 200,
                                 bind = self.update_angle,
                                 value = 0,
                                 right = 15
                                 )
            self.sliders.append(slider_ctrl)
            wtext(text="\n")

        # Create Prices
        self.priceSphere = []
        self.prices = []
        for i in range(5):
            temp = price.Price()
            self.prices.append(temp)
            self.priceSphere.append(sphere(pos = temp.pos,radius = 1.5,color = color.green))

    def update_scene(self):
        """
        Update the 3D visualization based on the current joint angles.
        """
        pos = vector(0, 0, 0)  # Initial position
        joint_pos = self.arm.get_joint_pos()

        for i, (link, joint) in enumerate(zip(self.links, self.joints[1:])):
            joint.pos = joint_pos[i+1]
            link.pos = joint_pos[i]
            link.axis = joint_pos[i+1] - joint_pos[i]

        for i in range(len(self.prices)):
            if self.prices[i].pickDet(joint_pos[-1]):
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
        self.status.text = " Status: Reset\n"



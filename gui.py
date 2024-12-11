import time
from vpython import *
import numpy as np
from price import Price


class GUIManager:
    def __init__(self, arm):
        self.caught_count = 0
        self.arm = arm
        # create the canvas and adjust the camera
        self.scene = canvas(title="Arcade Robotic Arm Simulator", width=800, height=600)
        self.scene.camera.pos = vector(25, -25, 25)
        self.scene.camera.axis = vector(-25, 25, -25)
        self.scene.up = vector(0, 0, 1)

        #Initailizing variables needed
        self.joints = []  # List to hold joint spheres
        self.links = []  # List to hold link cylinders
        self.sliders = []  # List to hold sliders
        self.priceSphere = []  # List to hold price sphere objects
        self.prices = []  # List to hold the pos of the prices

        self.setup_scene()  # Setting up the scene
        self.update_scene()  # Update positions after setup
        # self.run_machine()

    def setup_scene(self):
        """
        Initialize the VPython 3D scene and robotic arm visualization.
        """
        self.randomize_button = button(text="Randomize", bind=self.randomize)
        self.reset_button = button(text="Reset", bind=self.reset_arm)
        self.generate_price_button = button(text="Generate Prices", bind=self.generate_price)
        self.status = wtext(text=" Status: Ready\n")  # Status text next to buttons
        self.run_machine_button = button(text="Run Machine", bind=self.run_machine)

        # Add a ground plane (a white flat plane)
        ground_plane = box(pos=vector(0, 0, -0.5), size=vector(100, 100, 0.1), color=color.white, opacity=0.6)

        # Adjust radii based on the scale of the robot
        link_radius = max([param[0] for param in self.arm.dh_params]) * 0.02  # 2% of the largest 'a'
        joint_radius = link_radius * 2

        # Base Joint (Joint 1)
        base = sphere(pos=vector(0, 0, 0), radius=joint_radius * 1.5, color=color.red)
        self.joints.append(base)

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
            wtext(text=f"Joint {i + 1}: ")
            slider_ctrl = slider(min=self.arm.joint_limit[i][0],
                                 max=self.arm.joint_limit[i][1],
                                 length=200,
                                 bind=self.update_angle,
                                 value=0,
                                 right=15
                                 )
            self.sliders.append(slider_ctrl)
            wtext(text="\n")

        # Create Prices
        self.priceGenerated = False
        self.generate_price()
        print("price created")

    def update_scene(self):
        """
        Update the 3D visualization based on the current joint angles.
        """
        pos = vector(0, 0, 0)  # Initial position
        joint_pos = self.arm.get_joint_pos(self.arm.joint_angles)

        for i, (link, joint) in enumerate(zip(self.links, self.joints[1:])):
            joint.pos = joint_pos[i + 1]
            link.pos = joint_pos[i]
            link.axis = joint_pos[i + 1] - joint_pos[i]

        ee_pos = self.arm.dirKin(self.arm.joint_angles)
        for i in range(len(self.prices)):
            if self.prices[i].pickDet(ee_pos):
                self.priceSphere[i].visible = False
                self.caught_count += 1
                self.status.text = f" Status: You caught a prize! Total caught: {self.caught_count}\n"

        if self.caught_count == len(self.prices):
            self.status.text = "Congratulations! You caught all the prizes!"

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
        for price in self.priceSphere:
            price.visible = True

    def run_machine(self):
        self.reset_arm()
        seq = self.arm.sequence_planner(self.prices)
        ee_v = 1
        self.arm.trajectory_planner(seq, ee_v)
        print("Trajectory Done")

        file = open("Trajectory.txt")
        for line in file:
            self.arm.joint_angles = list(map(float, line.strip().split(',')))
            self.update_scene()
            time.sleep(0.01)

    def generate_price(self):
        self.reset_arm()
        if self.priceGenerated:
            self.prices.clear()
            for price in self.priceSphere:
                price.visible = False
                del price
            self.priceSphere.clear()

        for i in range(5):
            temp = Price()
            self.prices.append(temp)
            self.priceSphere.append(sphere(pos=temp.pos, radius=1.5, color=color.green))
        self.priceGenerated = True

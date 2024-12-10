from vpython import *
import numpy as np
import price



class GUIManager:
    def __init__(self, arm):
        self.arm = arm
        self.scene = canvas(title="Arcade Robotic Arm Simulator", width=1000, height=600)  # 宽度增加到1000
        self.scene.camera.pos = vector(25, -25, 25)
        self.scene.camera.axis = vector(-25, 25, -25)
        self.scene.up = vector(0, 0, 1)

        self.joints = []
        self.links = []
        self.sliders = []
        self.priceSphere = []
        self.prices = []

        self.setup_scene()
        self.setup_controls()
        self.update_scene()

        self.price_picked_count = 0

    def setup_scene(self):
        """
        Initialize the VPython 3D scene and robotic arm visualization.
        """

        # Adjust radii based on the scale of the robot
        link_radius = max([param[0] for param in self.arm.dh_params]) * 0.02  # 2% of the largest 'a'
        joint_radius = link_radius * 2

        # Base Joint (Joint 1)
        base = sphere(pos=vector(0, 0, 0), radius=joint_radius * 1.5, color=color.red)


        # Add a ground plane (a white flat plane)
        ground_plane = box(
            pos=vector(0, 0, -0.5),  # Align with the base's Z position
            size=vector(100, 100, 0.1),
            color=color.white,
            opacity=0.6
        )

        # Create links and joints
        for i in range(len(self.arm.dh_params)):
            # Links (Blue Cylinders)
            link = cylinder(pos=vector(0, 0, 0), axis=vector(1, 0, 0), radius=link_radius, color=color.blue)
            self.links.append(link)

            # Joints (Red Spheres)
            joint = sphere(pos=vector(0, 0, 0), radius=joint_radius, color=color.red)
            self.joints.append(joint)

        # Create Prices
        for i in range(5):
            temp = price.Price()
            self.prices.append(temp)
            price_sphere = sphere(pos=temp.pos, radius=1.5, color=color.green)
            self.priceSphere.append(price_sphere)




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
                self.price_picked_count += 1  # Increment counter
                self.status.text = f" Status: {self.price_picked_count} Prices Picked\n"


    # def update_angle(self, slider):
    #     """
    #     Update joint angles when sliders are moved.
    #     """
    #     idx = self.sliders.index(slider)
    #     self.arm.joint_angles[idx] = radians(slider.value)
    #     self.update_scene()
    def update_angle(self, idx, value):
        """
        更新关节角度并重绘场景。
        """
        self.arm.joint_angles[idx] = radians(float(value))
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
        # Reset prices
        self.price_picked_count = 0
        for sphere in self.priceSphere:
            sphere.visible = True
        self.status.text = " Status: Reset\n"
        self.update_scene()

    def setup_controls(self):
        """
        使用 HTML 和 CSS 将滑块和按钮放置到右侧的 Controls 区域。
        """
        self.scene.append_to_title("""
            <style>
                .control-panel {
                    position: absolute;
                    top: 10%;
                    right: 20%;
                    width: 300px;
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 15px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    font-family: Arial, sans-serif;
                }
                .control-panel h3 {
                    margin-top: 0;
                    text-align: center;
                }
                .control-panel label {
                    display: block;
                    margin-bottom: 5px;
                }
                .control-panel input[type="range"] {
                    width: 80%;
                    margin-bottom: 10px;
                }
                .control-panel button {
                    width: 100px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                    margin: 5px auto;
                    cursor: pointer;
                    font-size: 14px;
                    display: block;
                }
                .control-panel button.reset {
                    background-color: #6c757d;
                }
            </style>
            <div class="control-panel">
                <h3>Controls</h3>
                <label for="slider1">Joint 1:</label>
                <input type="range" id="slider1" min="-90" max="90" value="0" 
                oninput="scene.get_canvas().control.update_angle(0, this.value)">

                <label for="slider2">Joint 2:</label>
                <input type="range" id="slider2" min="-90" max="90" value="0" 
                oninput="scene.get_canvas().control.update_angle(1, this.value)">

                <label for="slider3">Joint 3:</label>
                <input type="range" id="slider3" min="-170" max="170" value="0" 
                oninput="scene.get_canvas().control.update_angle(2, this.value)">

                <label for="slider4">Joint 4:</label>
                <input type="range" id="slider4" min="-170" max="170" value="0" 
                oninput="scene.get_canvas().control.update_angle(3, this.value)">

                <label for="slider5">Joint 5:</label>
                <input type="range" id="slider5" min="-170" max="170" value="0" 
                oninput="scene.get_canvas().control.update_angle(4, this.value)">

                <button onclick="scene.get_canvas().control.randomize()">Randomize</button>
                <button class="reset" onclick="scene.get_canvas().control.reset_arm()">Reset</button>
            </div>
        """)

        self.scene.control = self


'''
    def setup_controls(self):
        """
        设置控件和布局，使用HTML和CSS进行完整布局。
        """
        self.scene.append_to_title("""
        <style>

            .control-panel {
                position: absolute;
                top: 10%;
                right: 20%;
                width: 320px;
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                font-family: Arial, sans-serif;
            }
            .control-panel h3 {
                margin-top: 0;
                text-align: center;
            }
            .control-panel label {
                display: block;
                margin-bottom: 5px;
            }
            .control-panel input[type="range"] {
                width: 80%;
                margin-bottom: 10px;
            }
            .control-panel button {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                margin: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            .control-panel button.reset {
                background-color: #6c757d;
            }
            .control-panel div.buttons {
                text-align: center;
                margin-top: 15px;
            }
        </style>
        <div class="control-panel">
            <h3>Controls</h3>
            <label for="slider1">Joint 1:</label>
            <input type="range" id="slider1" min="-90" max="90" value="0" 
            oninput="scene.get_canvas().control.update_angle(1, this.value)">

            <label for="slider2">Joint 2:</label>
            <input type="range" id="slider2" min="-90" max="90" value="0" 
            oninput="scene.get_canvas().control.update_angle(2, this.value)">

            <label for="slider3">Joint 3:</label>
            <input type="range" id="slider3" min="-170" max="170" value="0" 
            oninput="scene.get_canvas().control.update_angle(3, this.value)">

            <label for="slider4">Joint 4:</label>
            <input type="range" id="slider4" min="-170" max="170" value="0" 
            oninput="scene.get_canvas().control.update_angle(4, this.value)">

            <label for="slider5">Joint 5:</label>
            <input type="range" id="slider5" min="-170" max="170" value="0" 
            oninput="scene.get_canvas().control.update_angle(5, this.value)">

            <div class="buttons">
                <button onclick="scene.get_canvas().control.randomize()">Randomize</button>
                <button class="reset" onclick="scene.get_canvas().control.reset_arm()">Reset</button>
            </div>
        </div>
        """)

        # 绑定Python控制器到scene.control，供HTML调用Python方法
        self.scene.control = self

'''



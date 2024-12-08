import tkinter as tk
from tkinter import messagebox
import pandas as pd
import random
import math

class RobotArm:
    def __init__(self, num_segments=3, segment_length=50):
        self.base_position = [20, 200]  # Base position at the left side of the canvas
        self.angles = [0] * num_segments  # Angles for each segment
        self.num_segments = num_segments
        self.segment_length = segment_length
        self.has_prize = False

    def move(self, delta_angles):
        # Update angles
        for i in range(len(self.angles)):
            self.angles[i] += delta_angles[i]
        print(f"Robot Arm angles updated to: {self.angles}")

    def get_joint_positions(self):
        # Calculate the positions of each joint
        positions = [tuple(self.base_position)]
        x, y = self.base_position
        total_angle = 0
        for angle in self.angles:
            total_angle += angle
            x += self.segment_length * math.cos(math.radians(total_angle))
            y += self.segment_length * math.sin(math.radians(total_angle))
            positions.append((x, y))
        return positions

    def check_for_prize(self, prize_area):
        end_effector = self.get_joint_positions()[-1]  # Get the position of the end effector
        x, y = end_effector

        # Center point of the prize area
        prize_center_x = (prize_area[0] + prize_area[2]) / 2
        prize_center_y = (prize_area[1] + prize_area[3]) / 2

        # Allowed margin of error (more strict)
        strict_threshold = 10  # Adjust this value; smaller values make the check stricter
        distance = math.sqrt((x - prize_center_x) ** 2 + (y - prize_center_y) ** 2)

        if distance <= strict_threshold:  # Check if the end effector is within the strict range
            self.has_prize = True
            print("Prize acquired!")
        else:
            self.has_prize = False

    def perform_random_movement(self, movements):
        # Choose a random movement
        movement = random.choice(movements)
        delta_angles = [movement.get(f'angle{i+1}', 0) for i in range(self.num_segments)]
        print(f"Performing random movement: {delta_angles}")
        self.move(delta_angles)

class ArcadeGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Robotic Arm Arcade Game")
        self.canvas_size = 400
        self.attempts_limit = 10  # Set the number of attempts per game
        self.attempts_left = self.attempts_limit
        self.robot_arm = RobotArm()
        self.prize_area = self.generate_prize_location()
        self.movements = self.load_movements()
        self.create_widgets()
        self.update_canvas()

    def load_movements(self):
        # Read movements from Excel file
        df = pd.read_excel('movements.xlsx')
        movements = df.to_dict('records')
        print("Movements loaded from Excel.")
        return movements

    def create_widgets(self):
        self.canvas = tk.Canvas(self.master, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        # Display attempts left
        self.attempts_label = tk.Label(self.master, text=f"Attempts Left: {self.attempts_left}")
        self.attempts_label.pack()

        # Buttons for manual control
        control_frame = tk.Frame(self.master)
        control_frame.pack()

        # Create buttons for each joint
        self.joint_controls = []
        for i in range(self.robot_arm.num_segments):
            frame = tk.Frame(control_frame)
            frame.pack(side=tk.LEFT, padx=5)

            label = tk.Label(frame, text=f"Joint {i+1}")
            label.pack()

            btn_increase = tk.Button(frame, text="+", command=lambda i=i: self.move_joint(i, 5))
            btn_increase.pack(side=tk.TOP)

            btn_decrease = tk.Button(frame, text="-", command=lambda i=i: self.move_joint(i, -5))
            btn_decrease.pack(side=tk.TOP)

        # Random movement button
        self.random_button = tk.Button(self.master, text="Random Move", command=self.random_movement)
        self.random_button.pack()

        # Reset game button
        self.reset_button = tk.Button(self.master, text="Reset Game", command=self.reset_game)
        self.reset_button.pack()

    def move_joint(self, joint_index, delta_angle):
        if self.attempts_left > 0:
            delta_angles = [0] * self.robot_arm.num_segments
            delta_angles[joint_index] = delta_angle
            self.robot_arm.move(delta_angles)
            self.attempts_left -= 1
            self.update_attempts_label()
            self.update_canvas()
            self.robot_arm.check_for_prize(self.prize_area)
            self.check_win_condition()
        else:
            messagebox.showinfo("No Attempts Left", "You have no attempts left. Resetting the game.")
            self.reset_game()

    def random_movement(self):
        if self.attempts_left > 0:
            self.robot_arm.perform_random_movement(self.movements)
            self.attempts_left -= 1
            self.update_attempts_label()
            self.update_canvas()
            self.robot_arm.check_for_prize(self.prize_area)
            self.check_win_condition()
        else:
            messagebox.showinfo("No Attempts Left", "You have no attempts left. Resetting the game.")
            self.reset_game()

    def update_canvas(self):
        self.canvas.delete("all")

        # Draw the robotic arm
        joint_positions = self.robot_arm.get_joint_positions()
        for i in range(len(joint_positions) - 1):
            x1, y1 = joint_positions[i]
            x2, y2 = joint_positions[i + 1]
            # Draw the segment
            self.canvas.create_line(x1, y1, x2, y2, width=5, fill="blue")
            # Draw the joint
            self.canvas.create_oval(x1 - 5, y1 - 5, x1 + 5, y1 + 5, fill="red")

        # Draw the end effector joint
        x_end, y_end = joint_positions[-1]
        self.canvas.create_oval(x_end - 5, y_end - 5, x_end + 5, y_end + 5, fill="green")

        # Draw the target area (prize area)
        x1, y1, x2, y2 = self.prize_area
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="gold", outline="black")

    def check_win_condition(self):
        if self.robot_arm.has_prize:
            messagebox.showinfo("Congratulations!", "You have won a prize!")
            self.reset_game()
        elif self.attempts_left == 0:
            messagebox.showinfo("Out of Attempts", "You have run out of attempts. The game will reset and the prize location will change.")
            self.reset_game()

    def update_attempts_label(self):
        self.attempts_label.config(text=f"Attempts Left: {self.attempts_left}")

    def reset_game(self):
        self.attempts_left = self.attempts_limit
        self.robot_arm = RobotArm()
        self.update_attempts_label()
        self.update_prize_location()
        self.update_canvas()

    def generate_prize_location(self):
        max_reach = self.robot_arm.num_segments * self.robot_arm.segment_length  # Maximum reachable distance
        base_x, base_y = self.robot_arm.base_position

        while True:
            x = random.randint(50, self.canvas_size - 70)
            y = random.randint(50, self.canvas_size - 70)
            distance = math.sqrt((x - base_x) ** 2 + (y - base_y) ** 2)  # Calculate distance from base to target
            if distance <= max_reach:  # Ensure the target is within the reachable range
                break

        size = 20  # Size of the square
        prize_area = (x, y, x + size, y + size)
        print(f"New reachable prize location: {prize_area}")
        return prize_area

    def update_prize_location(self):
        self.prize_area = self.generate_prize_location()
        self.update_canvas()

def main():
    root = tk.Tk()
    game = ArcadeGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()

# Robotic Arm Simulator

## Overview
This project is a **robotic arm simulator** developed using **VPython**. It allows users to control a robotic arm in a 3D environment and perform object manipulation tasks.

The main objectives are:
- Visualize the robotic arm in a 3D space.
- Interact with the arm using sliders and buttons.
- Simulate trajectory planning and execution.

---

## Features
- **3D Visualization**: Displays joints, links, and interactive objects in a 3D environment.
- **GUI Controls**:
  - Adjust joint angles using sliders.
  - Randomize configurations with a button.
  - Reset the arm to its initial position.
- **Trajectory Planning**: Calculates joint angles to follow a specific path.
- **Object Interaction**: Collects target objects in the environment.

---

## File Structure
- **main.py**: The entry point of the program. Initializes the robotic arm and GUI.
- **robotic_arm.py**: Contains the robotic arm's logic, including DH parameter calculations and joint position computation.
- **gui.py**: Handles the GUI and scene setup using VPython. Implements sliders, buttons, and their interactions.
- **price.py**: Defines the interactive objects (e.g., green spheres) and their behaviors.
- **random_movement.py**: A utility file for generating random movements or configurations (if applicable).
- **movements.xlsx**: A file storing trajectory data or logs.
- **tests.py**: Unit tests for ensuring functionality and robustness of the codebase.


---

## Setup and Installation

### Prerequisites
Make sure you have the following installed:
- Python 3.11 or higher
- Required libraries:
  ```bash
  pip install vpython numpy

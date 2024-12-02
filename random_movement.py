import random

def generate_random_angles(num_joints, limits):
    return [random.uniform(l[0], l[1]) for l in limits]

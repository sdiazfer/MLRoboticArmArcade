from robotic_arm import RoboticArm
import numpy as np
from price import Price
from vpython import vector
import pytest

# Defining robot arm to test, defining joint_angles to check values
joint_angles = [np.pi/4,-np.pi/3,np.pi/6,np.pi/2,0]
dh_params = [
    # (a,    alpha,      d,    theta)
    (0, np.pi / 2, 10, 0),  # Link 1
    (10, 0, 0, 0),  # Link 2
    (7, 0, 0, 0),  # Link 3
    (5, 0, 0, 0),  # Link 4
    (3, 0, 0, 0),  # Link 5
]
joint_limits = [
    # (Lower limit,   Upper limit)
    (-90, 90),
    (-90, 90),
    (-170, 170),
    (-170, 170),
    (-170, 170),
]
arm = RoboticArm(dh_params, joint_limits)

# Generating prices with predefined position to check sequence planner
prices = []
for i in range(5):
    price = Price()
    price.pos = vector(i+1,i+1,i+1)
    prices.append(price)

def test_dirKin():
    result = arm.dirKin(joint_angles)
    expected = vector(10.6506, 10.6506, 4.76795)
    assert np.isclose(result.x, expected.x, atol=1e-4)
    assert np.isclose(result.y, expected.y, atol=1e-4)
    assert np.isclose(result.z, expected.z, atol=1e-4)

def test_jacobian():
    result = arm.jacobian(joint_angles)
    expected = np.array([
        [-10.651, 3.700, -2.424, -4.899, -1.837],
        [10.651, 3.700, -2.424, -4.899, -1.837],
        [0.000, 15.062, 10.062, 4.000, 1.500]
    ])

    # Validate the result
    assert result.shape == expected.shape, "Jacobian matrix dimensions do not match expected."
    assert np.allclose(result, expected, atol=1e-3), "Jacobian matrix values do not match expected."

def test_sequence_planner():
    seq = arm.sequence_planner(prices)
    expected_positions = [vector(25,0,10),vector(5, 5, 5), vector(4, 4, 4),vector(3, 3, 3),vector(2, 2, 2), vector(1, 1, 1)]
    assert seq == expected_positions

def test_pickDet():
    price = Price()
    check_pos = price.pos + vector(1,0,0)
    result = price.pickDet(check_pos)
    assert result == True
    check_pos = price.pos + vector(3, 0, 0)
    result = price.pickDet(check_pos)
    assert result == False

eP = 0.1
lambdaP = 2
Vmin = 5
Vmax = 15
def test_V():
    result = arm.V(0.3,lambdaP,Vmin,Vmax,eP)
    assert result == Vmax


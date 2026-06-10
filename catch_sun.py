# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import sys
import math

# -------------------------- Core Parameter Configuration --------------------------
STEP_PER_DEGREE = 1.56
DELAY_MS = 3
ANGLE_TOLERANCE = 5.0  # 5 degrees tolerance for both axes

MAX_PITCH = 45.0
MIN_PITCH = -45.0

MAX_YAW = 360.0
MIN_YAW = 0.0

TARGET_YAW = 135.0    #yaw 0-360
TARGET_PITCH = 30.0   #pitch -45-45  

x_IN1, x_IN2, x_IN3, x_IN4 = 17, 18, 27, 22  # Yaw motor (X-axis)
y_IN1, y_IN2, y_IN3, y_IN4 = 5, 6, 13, 19    # Pitch motor (Y-axis)

# -------------------------- Stepper Motor Control --------------------------
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    for pin in [x_IN1, x_IN2, x_IN3, x_IN4, y_IN1, y_IN2, y_IN3, y_IN4]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def setStep(axis, w1, w2, w3, w4):
    pins = {'x': [x_IN1, x_IN2, x_IN3, x_IN4], 'y': [y_IN1, y_IN2, y_IN3, y_IN4]}
    for pin, val in zip(pins[axis], [w1, w2, w3, w4]):
        GPIO.output(pin, val)

def clockwise(axis, delay):
    seq = [(1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1)]
    for step in seq:
        setStep(axis, *step)
        time.sleep(delay)

def counterClockwise(axis, delay):
    seq = [(0,0,0,1), (0,0,1,0), (0,1,0,0), (1,0,0,0)]
    for step in seq:
        setStep(axis, *step)
        time.sleep(delay)

def motorMoveSteps(axis, steps, delay):
    """Move motor by exact number of steps"""
    if steps > 0:
        for _ in range(int(steps)):
            clockwise(axis, delay)
    elif steps < 0:
        for _ in range(int(abs(steps))):
            counterClockwise(axis, delay)

def moveAxisToTarget(axis, current_angle, target_angle, angle_range=360):
    """
    Move one axis to target angle (handles circular wrap for Yaw)
    Returns new current angle after movement
    """
    delay = DELAY_MS / 1000.0
    
    if axis == 'x':  # Yaw is circular (0-360)
        # Normalize angles
        target = target_angle % 360
        current = current_angle % 360
        
        # Calculate shortest direction
        diff = (target - current + 180) % 360 - 180  # [-180, 180)
    else:  # Pitch is linear
        diff = target_angle - current_angle

    if abs(diff) <= ANGLE_TOLERANCE:
        return current_angle  # Already within tolerance

    # Calculate steps to move
    steps = abs(diff) * STEP_PER_DEGREE
    direction = 1 if diff > 0 else -1
    
    print(f"Moving {axis.upper()} axis by {diff:.1f} degrees ({int(steps)} steps)...")
    motorMoveSteps(axis, direction * steps, delay)
    
    return current_angle + diff

# -------------------------- Main Program --------------------------
if __name__ == '__main__':
    setup_gpio()
    print("=== Open-Loop Solar Tracker (Manual Target Angles) ===")
    print(f"Target Yaw: {TARGET_YAW:.1f}, Target Pitch: {TARGET_PITCH:.1f}")
    print("-" * 55)

    try:
        # Start from assumed zero position
        current_yaw = 0.0
        current_pitch = 0.0

        # Step 1: Move Yaw first
        sys.stdout.write("Sun Tracking in Progress...\r")
        sys.stdout.flush()
        current_yaw = moveAxisToTarget('x', current_yaw, TARGET_YAW)

        # Step 2: Then move Pitch
        current_pitch = moveAxisToTarget('y', current_pitch, TARGET_PITCH)

        # Done!
        sys.stdout.write("Sun Tracking Successful!       \n")
        sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nStopped by User (Ctrl+C)")
    finally:
        # Clean up
        for pin in [x_IN1, x_IN2, x_IN3, x_IN4, y_IN1, y_IN2, y_IN3, y_IN4]:
            GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup()

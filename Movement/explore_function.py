'''
THE FOLLOWING FUNCTIONS ARE HELPER FUNCTIONS

CONCERNS: Numbering of the wheels, need to verify this
'''

fl = robot.getDevice("wheel1") # front left wheel
fr = robot.getDevice("wheel2") # front right wheel
bl = robot.getDevice("wheel3") # back left wheel
br = robot.getDevice("wheel4") # back right wheel

wheels = [fl, fr, bl, br]

SPEED = 6.28 #Max speed, we can change this as needed

def base_set_wheel_velocity(device, velocity):
    device.setPosition('inf')
    device.setVelocity(velocity)

def base_set_wheel_speeds_helper(speeds):
    for i in range(4):
        base_set_wheel_velocity(wheels[i], speeds[i])

def base_reset():
    speeds = [0.0, 0.0, 0.0, 0.0]
    base_set_wheel_speeds_helper(speeds)

def base_forwards():
    speeds = [SPEED, SPEED, SPEED, SPEED]
    base_set_wheel_speeds_helper(speeds)

def base_backwards():
    speeds = [-SPEED, -SPEED, -SPEED, -SPEED]
    base_set_wheel_speeds_helper(speeds)

def base_turn_left():
    speeds = [-SPEED, SPEED, -SPEED, SPEED]
    base_set_wheel_speeds_helper(speeds);

def base_turn_right():
    speeds = [SPEED, -SPEED, SPEED, -SPEED]
    base_set_wheel_speeds_helper(speeds);

'''
THE FOLLOWING FUNCTIONS WILL BE RUN EVERY TIMESTEP:

Rotate Function: input THETA tells us the degree from camera vision data. The robot takes 150 timesteps to
complete a 90 degree rotation. So, the function calculates the ratio of the angle to 90 degrees, then
multiplies this coefficient to 150. Thus, we are essentially only changing the number of time steps
turn left or turn right is running (instead of the angle itself since we don't have a gps/gyro).

Random walk function: moves forward for 100 timesteps, then rotates left or right (by randomized choice)
for between 50-150 timesteps (also a randomized choice). This serves as the explore function for the robot. 
'''

def rotate_degree(theta):
    i = 0
    if 0 <= theta < 180:
        ratio = theta/90
        if i < ratio*150:
            base_turn_right()
    if 180 <= theta < 370:
        ratio = (theta - 180)/90
        if i < ratio*150:
            base_turn_left()
            
def random_walk():
    i = 0
    rand_time = range(150,250)
    if i <= 100:
        return base_forwards()
    if 100 < i < rand_time:
        base_reset()
        direction = random.choice([base_turn_left, base_turn_right])
        return direction
    if i >= rand_time:
        i = 0
    i += 
    
    
    

"""youbot_turn controller."""
# stripped down version to do develop turn feature

from controller import Robot, Motor, Camera, Accelerometer, GPS, Gyro, LightSensor, Receiver, RangeFinder, Lidar
from controller import Supervisor

from youbot_zombie import *
   
#------------------CHANGE CODE BELOW HERE ONLY--------------------------
#define functions here for making decisions and using sensor inputs
print("Hi, I'm ready!")



""" -------- Robot motion helper functions --------
"""    

def base_set_wheel_speeds_helper(wheels, speeds):
    for i in range(4):
        wheels[i].setVelocity(speeds[i])
    return

def base_reset(wheels):
    speeds = [0.0, 0.0, 0.0, 0.0]
    base_set_wheel_speeds_helper(wheels, speeds)
    return

def base_forwards(wheels):
    speeds = [6.28, 6.28, 6.28, 6.28]
    base_set_wheel_speeds_helper(wheels, speeds)
    return

def base_backwards(wheels):
    speeds = [-6.28, -6.28, -6.28, -6.28]
    base_set_wheel_speeds_helper(wheels, speeds)
    return

def base_turn_left(wheels):
    speeds = [12, -12, 12, -12]
    base_set_wheel_speeds_helper(wheels, speeds)
    return

def base_turn_right(wheels):
    speeds = [-12, 12, -12, 12]
    base_set_wheel_speeds_helper(wheels, speeds)
    return


def rotate_degree(wheels, theta):
    """
    Rotate Function: input THETA tells us the degree from camera vision data. The robot takes 150 timesteps to
    complete a 90 degree rotation. So, the function calculates the ratio of the angle to 90 degrees, then
    multiplies this coefficient to 150. Thus, we are essentially only changing the number of time steps
    turn left or turn right is running (instead of the angle itself since we don't have a gps/gyro).
    """
    speeds = [-6.28, 6.28, -6.28, 6.28]
    base_set_wheel_speeds_helper(wheels, speeds)
    
    
 
    return

"""
def waggle():
    # make robot move forward in a zigzag, to cover all bases (blindspots)

    return
"""
 

"""
EXPLORE AND EAT BERRIES FUNCTION

random_walk - when no berries are around, create random trajectory
berry_lookout - vision-based berry function
berry_distance_calculation - calculate closest berry
berry_angle - calculate angle of closest berry
"""


def random_walk(wheels, choice):
    """
    Random walk function: moves forward for 100 timesteps, then rotates left or right
    for between 50-150 timesteps (a randomized choice). This serves as the explore function for the robot.
    
    INPUT: Choice - random choice between 0 and 1 to tell the robot to turn left or right
    for a certain number of timesteps
    """
    i = 0
    rand_time = [150,250]
    
    if i <= 100:
        base_forwards(wheels)
        
    if 100 < i < rand_time[0]:
        if choice == 0:
            base_turn_left(wheels)
        if choice == 1:
            base_turn_right(wheels)
    if i >= rand_time[1]:
        i = 0
    i += 1
    return




#------------------CHANGE CODE ABOVE HERE ONLY--------------------------

def main():
    robot = Supervisor()

    # get the time step of the current world.
    timestep = int(robot.getBasicTimeStep())
    
    #health, energy, armour in that order 
    robot_info = [100,100,0]
    passive_wait(0.1, robot, timestep)
    pc = 0
    timer = 0
    
    robot_node = robot.getFromDef("Youbot")
    trans_field = robot_node.getField("translation")
    
    get_all_berry_pos(robot)
    
    robot_not_dead = 1
    
    #------------------CHANGE CODE BELOW HERE ONLY--------------------------
    
    #COMMENT OUT ALL SENSORS THAT ARE NOT USED. READ SPEC SHEET FOR MORE DETAILS
    
    accelerometer = robot.getDevice("accelerometer") # 100 cost
    accelerometer.enable(timestep)
    
 
    
    # INITIALIZE WHEEL POSITIONS
    fr = robot.getDevice("wheel1")
    fl = robot.getDevice("wheel2")
    br = robot.getDevice("wheel3")
    bl = robot.getDevice("wheel4")
    wheels = [fr, fl, br, bl]

    fr.setPosition(float('inf'))   
    fl.setPosition(float('inf'))
    br.setPosition(float('inf'))
    bl.setPosition(float('inf'))    

    make_turn = 0   # semaphore

    #------------------CHANGE CODE ABOVE HERE ONLY--------------------------
    
    
    while(robot_not_dead == 1):
        
        if(robot_info[0] < 0):
           
            robot_not_dead = 0
            print("ROBOT IS OUT OF HEALTH")
            #if(zombieTest):
            #    print("TEST PASSED")
            #else:
            #    print("TEST FAILED")
            #robot.simulationQuit(20)
            #exit()
            
        if(timer%2==0):
            trans = trans_field.getSFVec3f()
            robot_info = check_berry_collision(robot_info, trans[0], trans[2], robot)
            robot_info = check_zombie_collision(robot_info, trans[0], trans[2], robot)
            
        if(timer%16==0):
            robot_info = update_robot(robot_info)
            timer = 0
        
        if(robot.step(timestep)==-1):
            exit()
            
            
        timer += 1
        
     #------------------CHANGE CODE BELOW HERE ONLY--------------------------   
        # The following code is called every timestep:
        
        if make_turn == 1:    
            base_turn_right(wheels)
        """
        # debugging for turn 
        desired_turn_angle = 60 # degrees
        i = 0
        for i in range(100):    
            #if actual_turn < desired_turn_angle:
            base_turn_right(wheels)
            i += 1
            
        j = 0
        for j in range(100):
            base_forwards(wheels)
            j += 1
        """   
        
        #possible pseudocode for moving forward, then doing a 90 degree left turn
        #if i <100
            #base_forwards() -> can implement in Python with Webots C code (/Zombie world/libraries/youbot_control) as an example or make your own
        
        #if == 100 
            # base_reset() 
            # base_turn_left()  
            #it takes about 150 timesteps for the robot to complete the turn
                 
        #if i==300
            # i = 0
        
        #i+=1
        
        #make decisions using inputs if you choose to do so
         
                
        #------------------CHANGE CODE ABOVE HERE ONLY--------------------------
        
        
    return 0   


main()

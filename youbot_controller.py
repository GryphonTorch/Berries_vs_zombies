"""youbot_controller controller."""

from controller import Robot, Motor, Camera, Accelerometer, GPS, Gyro, LightSensor, Receiver, RangeFinder, Lidar
from controller import Supervisor

from youbot_zombie import *
   
#------------------CHANGE CODE BELOW HERE ONLY--------------------------
#define functions here for making decisions and using sensor inputs
print("Hi, I'm ready!")

""" -------- Robot motion helper functions -------- """    

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
    speeds = [10, -1, 10, -1]
    base_set_wheel_speeds_helper(wheels, speeds)
    return

def base_turn_right(wheels):
    speeds = [-1, 10, -1, 10]
    base_set_wheel_speeds_helper(wheels, speeds)
    return

"""
def rotate_degree(wheels, theta):
    
    #Rotate Function: input THETA tells us the degree from camera vision data. The robot takes 150 timesteps to
    #complete a 90 degree rotation. So, the function calculates the ratio of the angle to 90 degrees, then
    #multiplies this coefficient to 150. Thus, we are essentially only changing the number of time steps
    #turn left or turn right is running (instead of the angle itself since we don't have a gps/gyro).
    
    speeds = [-6.28, 6.28, -6.28, 6.28]
    base_set_wheel_speeds_helper(wheels, speeds)
    return


def waggle():
    # make robot move forward in a zigzag, to cover all bases (blindspots)

    return
"""

""" -------- Camera Vision Helper functions --------
    Based on standalone testing of camera images, we obtained representative
    R, G, B pixel values for various zombies, berries, and terrain features. This allows
    the robot to filter away the background and focus on possible zombie threats
    and berries in the field of vision. 
"""

# Dictionary of items of interest in RGB order, obtained from testing
visual_dict = {"Aqua_bright":(37, 221, 194), 
               "Aqua_shadow":(10, 69, 67),
               "Blue_bright":(33, 143, 230),
               "Blue_shadow":(10, 40, 99),
               "Green_bright":(35, 192, 39),
               "Green_shadow":(9, 53, 12),
               "Purple_bright":(112, 48, 182),
               "Purple_shadow":(87, 37, 154),
               "Sky":(90, 109, 152),
               "Mountain":(77, 73, 78),
               "Earth":(217, 182, 169),
               "Red_bright": (211, 64, 48),
               "Red_shadow": (71, 19, 18),
               "Pink_bright": (214, 142, 187),
               "Pink_shadow": (88, 53, 87),
               "Orange_bright": (198, 127, 87),
               "Orange_shadow": (64, 39, 33),
               "Yellow_bright": (185, 173, 28),
               "Yellow_shadow": (71, 68, 16),
               "Stump_bright": (31, 31, 34),
               "Stump_shadow": (10, 11, 15),
               "Wall_bright": (211, 212, 216),
               "Wall_shadow": (71, 76, 97)
               }


def make_image_array(wb_cam_output):
    """
    Function to get [px11, px12, px13...] array from Webot camera output
    data structure
    Outputs array of RGB pixels (so each pxij is [R, G, B] array)
    Modified from standalone Spyder IDE version (not using PNG images)
    """
    output = []
    #print("Image dimensions:", len(wb_cam_output)," x ",len(wb_cam_output[0]))
    #print(wb_cam_output)
    
    for col_idx in range(len(wb_cam_output)):
        scanline = []    # re-initialize at every row
        for row_idx in range(len(wb_cam_output[0])):  
            red_pixel   = wb_cam_output[col_idx][row_idx][0]
            green_pixel = wb_cam_output[col_idx][row_idx][1]
            blue_pixel  = wb_cam_output[col_idx][row_idx][2]
            scanline.append([red_pixel, green_pixel, blue_pixel])                             
        output.append(scanline)
        
    #print("Debugging check:", output[127][63])
    return output



def is_pixel_match(pixel_RGB, target_RGB):
    """
    Helper function. Input: pixel RGB is tuple of three values
    Assume standard deviation (error bar) of +/-10 for all values
    Returns True if match, False if not
    10 is empirically tested; if too big we can't pin down zombie/berry type
    """
    flag = True       # True if pixel is target
    for idx in (0,1,2):
        if pixel_RGB[idx] not in range(target_RGB[idx]-10, target_RGB[idx]+10):
            flag = False
            break
    return flag 

"""
ESCAPE ZOMBIE FUNCTIONS

Zombie lookout - vision-based zombie alert function
Zombie escape - calculate best angle of escape based on four camera lookout inputs
"""

def zombie_lookout(image_array, x_size, y_size, threshold):
    """
    Main vision-based zombie alert function
    Need to test vigorously with different inputs! image_array consists of vertical strips now
    Inputs:
        - Array
        - Image dimensions
        - Pixel threshold for zombie warning
    Psuedocode:
        - Filter out pixels with sky, mountain or earth
        - Of remaining pixels cluster pixels to determine if a zombie is near
        - From average of cluster, determine relative horizontal position
    Return None if no zombie, else return (type, angle(degree) ) tuple 
    """
    filtered_array = []   # new list of RGB pixels for non-background objects
    filtered_pos = []     # positions to save x,y information
    for col_idx in range(x_size):
        for row_idx in range(y_size):
            pix_RGB = image_array[col_idx][row_idx]    # a tuple
            # Now compare againsst known Sky, Mountain and Earth data
            if(is_pixel_match(pix_RGB, visual_dict["Sky"]) == False):
                if(is_pixel_match(pix_RGB, visual_dict["Mountain"]) == False):    
                    if(is_pixel_match(pix_RGB, visual_dict["Earth"]) == False): 
                        filtered_array.append(pix_RGB)
                        filtered_pos.append((col_idx, row_idx))  # note order!


    # Find the color via counting scores
    #print("Debugging filtered length:",len(filtered_array))
    aqua_score = [0,0,0]  # pixel count, Sum of x (col_idx), Sum of y (row_idx)
    blue_score = [0,0,0]
    green_score = [0,0,0]
    purple_score = [0,0,0]
    #debug_array_x = []    # for debugging to see which pixels are picked up
    #debug_array_y = []
    
    for idx in range(len(filtered_array)):
        if (is_pixel_match(filtered_array[idx],visual_dict["Aqua_bright"]) or is_pixel_match(filtered_array[idx], visual_dict["Aqua_shadow"])):
            aqua_score[0] += 1.0  # increment count
            aqua_score[1] += filtered_pos[idx][0] # col_idx
            aqua_score[2] += filtered_pos[idx][1] # row_idx
        if (is_pixel_match(filtered_array[idx],visual_dict["Blue_bright"]) or is_pixel_match(filtered_array[idx], visual_dict["Blue_shadow"])):
            blue_score[0] += 1.0  # increment count
            blue_score[1] += filtered_pos[idx][0] # col_idx
            blue_score[2] += filtered_pos[idx][1] # row_idx
            
            
        if (is_pixel_match(filtered_array[idx],visual_dict["Green_bright"]) or is_pixel_match(filtered_array[idx], visual_dict["Green_shadow"])):
            green_score[0] += 1.0  # increment count
            green_score[1] += filtered_pos[idx][0] # col_idx
            green_score[2] += filtered_pos[idx][1] # row_idx
            
            
        if (is_pixel_match(filtered_array[idx],visual_dict["Purple_bright"]) or is_pixel_match(filtered_array[idx], visual_dict["Purple_shadow"])):
            purple_score[0] += 1.0  # increment count
            purple_score[1] += filtered_pos[idx][0] # col_idx
            purple_score[2] += filtered_pos[idx][1] # row_idx
            #debug_array_x.append(filtered_pos[idx][0])
            #debug_array_y.append(filtered_pos[idx][1])

    # Primary zombie ID complete, analyze results
    # We estimate scaling factors for range and angle to zombie
    #print("\nDebugging A/B/G/P zombie scores:", aqua_score, blue_score, green_score, purple_score, "\n")
    
    if aqua_score[0] < threshold and blue_score[0] < threshold and \
        green_score[0] < threshold and purple_score[0] < threshold:
        # No zombie nearby; use a threshold instead of 0
        return None
    
    
    elif aqua_score[0] >= blue_score[0] and aqua_score[0] >= green_score[0] and aqua_score[0] >= purple_score[0]:
        # aqua biggest
        zombie_type = "aqua"
        #zombie_distance = (1-aqua_score[0]/(x_size*y_size))*5.0 # in meters 
        zombie_x = aqua_score[1] / aqua_score[0]    # float, x-center of mass
        angle = (zombie_x - x_size/2)/x_size * 28.5   # angles - estimation from 1 rad FOV!
       
    elif blue_score[0] >= green_score[0] and blue_score[0] >= purple_score[0]:
        # check if blue biggest
        zombie_type = "blue"
        #zombie_distance = (1-blue_score[0]/(x_size*y_size))*5.0 # in meters 
        zombie_x = blue_score[1] / blue_score[0]    # float, x-center of mass
        angle = (zombie_x - x_size/2)/x_size * 28.5   # angles - estimation from 1 rad FOV!
        
    elif green_score[0] >= purple_score[0]:
        # check if green biggest
        zombie_type = "green"
        #zombie_distance = (1-green_score[0]/(x_size*y_size))*5.0 # in meters 
        zombie_x = green_score[1] / green_score[0]  # float, x-center of mass
        angle = (zombie_x - x_size/2)/x_size * 28.5   # angles - estimation from 1 rad FOV!
    
    else:
        # so purple is biggest
        zombie_type = "purple"
        #zombie_distance = (1-purple_score[0]/(x_size*y_size))*5.0 # in meters 
        zombie_x = purple_score[1] / purple_score[0] # float, x-center of mass
        angle = (zombie_x - x_size/2)/x_size * 28.5    # angles - estimation from 1 rad FOV!
       
    # debug 
    #plt.plot(debug_array_x,debug_array_y, ".")
    #plt.show()    
    
    #print("Zombie type", zombie_type, "at", angle, "deg boresight.")
    return zombie_type, angle


def make_escape(front_lookout, right_lookout, back_lookout, left_lookout, wheels):
    """
    Function to escape based on four camera lookouts
    Each input lookout is (zombie type, angle) tuple so we can tailor according
    to color if desired. 
    Does not return anything, just moves the wheels directly
    i.e. zero degrees front lookout: facing head-on, so go BACK
         zero degrees right lookout: coming from the right, go LEFT
    """
    
    # for now treat all zombies uniformly
    zombie_sum = 0    # vector sum of incident zombie directions
    if front_lookout != None or right_lookout != None or left_lookout != None:
        base_move_backwards(wheels)    # keeping it simple
    elif back_lookout != None:
        base_move_forwards(wheels)
    return
    

"""
EXPLORE AND EAT BERRIES FUNCTION

random_walk - when no berries are around, create random trajectory
berry_lookout - vision-based berry function, returns ("color", angle, distance) 
get_berry - moves robot towards berry
"""


def random_walk(wheels, choice):
    """
    Random walk function: moves forward for 100 timesteps, then rotates left or right
    for between 50-150 timesteps (a randomized choice). This serves as the explore function for the robot.
    
    INPUT: Choice - random choice between 0 and 1 to tell the robot to turn left or right
    for a certain number of timesteps
    """
    if choice == 0:
        base_turn_left(wheels)
    elif choice == 1:
        base_turn_right(wheels)
    else:
        base_forwards(wheels)
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
    """
    
    return

def berry_lookout(image_array, x_size, y_size, threshold):
    """
    Adapted from Yu Jun's Comp Vision for Zombie Lookout function
    Main vision-based berry function
    Inputs:
        - Array
        - Image dimensions
        - Pixel threshold for when berries are detected
    Do nothing if no berries above threshold, else return (type, angle(degree), distance) triple 
    """
    #print("Debugging: in berry_lookout mode")
    
    filtered_array = []   # new list of RGB pixels for non-background objects
    filtered_pos = []     # positions to save x,y information
    for col_idx in range(x_size):
        for row_idx in range(y_size):
            pix_RGB = image_array[col_idx][row_idx]    # a tuple
            # Now compare againsst known Sky, Mountain and Earth data
            if(is_pixel_match(pix_RGB, visual_dict["Sky"]) == False):
                if(is_pixel_match(pix_RGB, visual_dict["Mountain"]) == False):    
                    if(is_pixel_match(pix_RGB, visual_dict["Earth"]) == False): 
                        filtered_array.append(pix_RGB)
                        filtered_pos.append((col_idx, row_idx))  # note order!


    # Find the color via counting scores
    #print("Debugging filtered length:",len(filtered_array))
    red_score = [0,0,0]  # pixel count, Sum of x (col_idx), Sum of y (row_idx)
    pink_score = [0,0,0]
    orange_score = [0,0,0]
    yellow_score = [0,0,0]
    #debug_array_x = []    # for debugging to see which pixels are picked up
    #debug_array_y = []
    
    for idx in range(len(filtered_array)):
        if (is_pixel_match(filtered_array[idx],visual_dict["Red_bright"]) or is_pixel_match(filtered_array[idx], visual_dict["Red_shadow"])):
            red_score[0] += 1.0  # increment count
            red_score[1] += filtered_pos[idx][0] # col_idx
            red_score[2] += filtered_pos[idx][1] # row_idx
            
        if (is_pixel_match(filtered_array[idx],visual_dict["Pink_bright"]) or is_pixel_match(filtered_array[idx], visual_dict["Pink_shadow"])):
            pink_score[0] += 1.0  # increment count
            pink_score[1] += filtered_pos[idx][0] # col_idx
            pink_score[2] += filtered_pos[idx][1] # row_idx
            
            
        if (is_pixel_match(filtered_array[idx],visual_dict["Orange_bright"]) or is_pixel_match(filtered_array[idx], visual_dict["Orange_shadow"])):
            orange_score[0] += 1.0  # increment count
            orange_score[1] += filtered_pos[idx][0] # col_idx
            orange_score[2] += filtered_pos[idx][1] # row_idx
            
            
        if (is_pixel_match(filtered_array[idx],visual_dict["Yellow_bright"]) or is_pixel_match(filtered_array[idx], visual_dict["Yellow_shadow"])):
            yellow_score[0] += 1.0  # increment count
            yellow_score[1] += filtered_pos[idx][0] # col_idx
            yellow_score[2] += filtered_pos[idx][1] # row_idx
            #debug_array_x.append(filtered_pos[idx][0])
            #debug_array_y.append(filtered_pos[idx][1])

    # Primary berry color ID complete, analyze results
    # We estimate scaling factors for range and angle to zombie
    #print("\nDebugging R/P/O/Y berry scores:", red_score, pink_score, orange_score, yellow_score, "\n")
    
    if red_score[0] < threshold and pink_score[0] < threshold and \
        orange_score[0] < threshold and yellow_score[0] < threshold:
        berry_type = None     # default type
        berry_distance = 1000
        angle = 0
        #print("No berries detected")
    
    elif red_score[0] >= pink_score[0] and red_score[0] >= orange_score[0] and red_score[0] >= yellow_score[0]:
        # red berry closest
        berry_type = "red"
        #print("Debugging: red, red_score[0]", red_score[0], "red_score[1]", red_score[1]) 
        berry_x = red_score[1] / red_score[0]    # float, x-center of mass
        berry_distance = (1-red_score[0]/(x_size*y_size))*5.0 # in meters
        angle = (berry_x - x_size/2)/x_size * 28.5   # angles - estimation from 1 rad FOV!
       
    elif pink_score[0] >= orange_score[0] and pink_score[0] >= yellow_score[0]:
        # pink berry closest 
        berry_type = "pink"
        berry_x = pink_score[1] / pink_score[0]    # float, x-center of mass
        berry_distance = (1-pink_score[0]/(x_size*y_size))*5.0 # in meters
        angle = (berry_x - x_size/2)/x_size * 28.5   # angles - estimation from 1 rad FOV!
        
    elif orange_score[0] >= yellow_score[0]:
        # orange berry closest
        berry_type = "orange"
        berry_x = orange_score[1] / orange_score[0]    # float, x-center of mass
        berry_distance = (1-orange_score[0]/(x_size*y_size))*5.0 # in meters
        angle = (berry_x - x_size/2)/x_size * 28.5   # angles - estimation from 1 rad FOV!
    
    else:
        # yellow berry closest
        berry_type = "yellow"
        berry_x = yellow_score[1] / yellow_score[0]    # float, x-center of mass
        berry_distance = (1-yellow_score[0]/(x_size*y_size))*5.0 # in meters
        angle = (berry_x - x_size/2)/x_size * 28.5   # angles - estimation from 1 rad FOV!
       
    #print("Berry type", berry_type, "at", angle, "deg, at", berry_distance, "meters")
    return berry_type, angle, berry_distance


def get_berry(front_food, right_food, back_food, left_food, good_berry_list, wheels):
    """
    Simplified berry eat algorithm, with a bias for berry ahead
    Returns color of the berry it has picked, for energy check later 
    """
    print("In get_berry...")
    if front_food[0] != None and front_food[0] in good_berry_list:
        if front_food[1] > 1:
            # Rotate left; allow window 
            base_turn_left(wheels)
            print("Turn left")
        elif front_food[1] < -1:
            base_turn_right(wheels)
            print("Turn right")
        else:
            base_forwards(wheels)
            print("Debugging: go forward")
            
        return front_food[0]    # return color
    elif right_food[0] != None and (right_food[0] in good_berry_list):
        print("Debugging: see right")
        if left_food[0] != None:
            if right_food[1]<left_food[0]: 
                # go after the right berry 
                base_turn_right(wheels)
                return right_food[0]
            else:
                pass
        else:
            base_turn_right(wheels)
            return right_food[0]   
    elif left_food[0] != None and left_food[0] in good_berry_list:
        print("Debugging: see left")
        # before eating left berry, still check its desirability
        base_turn_left(wheels)
        return left_food[0]
    else:
        # Keep looking, move wheels later randomly    
        print("Debugging: no see")   
        return 0 # None
 

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
    
    #gps = robot.getDevice("gps")
    #gps.enable(timestep)
    
    #compass = robot.getDevice("compass")
    #compass.enable(timestep)
    
    camera1 = robot.getDevice("ForwardLowResBigFov") # 300 cost
    camera1.enable(timestep)
    
    #camera2 = robot.getDevice("ForwardHighResSmallFov")
    #camera2.enable(timestep)
    
    #camera3 = robot.getDevice("ForwardHighRes")   
    #camera3.enable(timestep)
    
    #camera4 = robot.getDevice("ForwardHighResSmall")
    #camera4.enable(timestep)
    
    camera5 = robot.getDevice("BackLowRes")      # 200 cost
    camera5.enable(timestep)
    
    camera6 = robot.getDevice("RightLowRes")     # 200 cost
    camera6.enable(timestep)
    
    camera7 = robot.getDevice("LeftLowRes")      # 200 cost
    camera7.enable(timestep)
    
    #camera8 = robot.getDevice("BackHighRes")
    #camera8.enable(timestep)
    
    #gyro = robot.getDevice("gyro")
    #gyro.enable(timestep)
    
    #lightSensor = robot.getDevice("light sensor")
    #lightSensor.enable(timestep)
    
    #receiver = robot.getDevice("receiver")
    #receiver.enable(timestep)
    
    #rangeFinder = robot.getDevice("range-finder")
    #rangeFinder.enable(timestep)
    
    #lidar = robot.getDevice("lidar")
    #lidar.enable(timestep)
    
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
    
    good_berry_list = ["red", "orange", "pink", "yellow"]
    
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
           
        # Observe from four cameras 
        camera1.saveImage('cam1front.png',100)  # for testing purposes, best quality PNG save
        camera6.saveImage('cam6right.png',100) 
        camera5.saveImage('cam5back.png',100) 
        camera7.saveImage('cam7left.png',100)
        front_RGB = make_image_array(camera1.getImageArray())   # to get RGB order
        right_RGB = make_image_array(camera6.getImageArray()) 
        back_RGB  = make_image_array(camera5.getImageArray()) 
        left_RGB  = make_image_array(camera7.getImageArray()) 
        
        # Compute zombie lookout data types; pick good thresholds
        front_lookout = zombie_lookout(front_RGB, 128, 64, 5) # x, y image size from specs
        right_lookout = zombie_lookout(right_RGB, 128, 64, 5)
        back_lookout  = zombie_lookout(back_RGB, 128, 64, 5)
        left_lookout  = zombie_lookout(left_RGB, 128, 64, 5)

        # Escape from zombie if needed, else find berries
        if front_lookout != None or right_lookout != None or back_lookout != None or left_lookout != None:  
            print("Zombie spotted! Run...")
            make_escape(front_lookout, right_lookout, back_lookout, left_lookout, wheels)
        else:
            print("No zombie spotted this turn")

            # Compute type and angle of food
            front_food = berry_lookout(front_RGB, 128, 64, 1) # x, y image size from specs
            right_food = berry_lookout(right_RGB, 128, 64, 1)
            back_food  = berry_lookout(back_RGB, 128, 64, 1)
            left_food  = berry_lookout(left_RGB, 128, 64, 1)
            
            # Get the berry; move, and take note of color string in want_to_eat
            init_energy = robot_info[1]
            want_to_eat = get_berry(front_food, right_food, back_food, left_food, good_berry_list, wheels)
            print("want_to_eat:", want_to_eat)
             
            # Learning: create list of good berries; any that gives -20 energy gets blacklisted
            final_energy = robot_info[1]
            if (final_energy - init_energy) < -19:
                good_berry_list.remove(want_to_eat)
                print("Ate bad berry :", want_to_eat) 
            else:
                if want_to_eat == 0:
                    random_walk(wheels, random.choice([0,1]))
                    print("No berry spotted, random wander")
        
        print(" ")   # for clarity in printout
        #------------------CHANGE CODE ABOVE HERE ONLY--------------------------
        
    
    return 0   


main()

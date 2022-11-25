"""youbot_controller controller."""

from controller import Robot, Motor, Camera, Accelerometer, GPS, Gyro, LightSensor, Receiver, RangeFinder, Lidar
from controller import Supervisor

from youbot_zombie import *
   
#------------------CHANGE CODE BELOW HERE ONLY--------------------------
#define functions here for making decisions and using sensor inputs
print("Hi, I'm ready!")

""" -------- Robot motion helper functions --------
    Turn wheels TODO
"""    

# initialize wheel positions ?    
#frontright_pos = float('inf')
#frontleft_pos = float('inf')
#backleft_pos = float('inf')
#backright_pos = float('inf')

def base_turn_left(angle):
    # basic turn left function, angle 
    # 1) Compare angle against gyro, keep turning until reach
    # 2) or scale angle out of 150/360 since ~150 steps to turn full circle 
    # need to figure out how many steps taken 

    return 

def base_turn_right(angle):
    # basic turn right function, angle argument?

    return 

def waggle():
    # make robot move forward in a zigzag, to cover all bases (blindspots)

    return


""" -------- Camera helper functions --------
    Based on standalone testing of camera images, we obtained representative
    R, G, B pixel values for various zombies and terrain features. This allows
    the robot to filter away the background and focus on possible zombie threats
    in the field of vision. 
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
               "Earth":(217, 182, 169) 
               }


def make_image_array(wb_cam_output):
    """
    Function to get [px11, px12, px13...] array from Webot camera output
    data structure, which returns BGRA instead
    Outputs array of RGB pixels (so each pxij is [R, G, B] array)
    Modified from standalone Spyder IDE version (not using PNG images)
    """
    output = []
    for row_idx in range(len(wb_cam_output)):
        scanline = []    # re-initialize at every row
        for col_idx in range(len(wb_cam_output[0])):
            red_pixel   = wb_cam_output[row_idx][col_idx][2]
            green_pixel = wb_cam_output[row_idx][col_idx][1]
            blue_pixel  = wb_cam_output[row_idx][col_idx][0]
            scanline.append([red_pixel, green_pixel, blue_pixel])                             
        output.append(scanline)
    return output



def is_pixel_match(pixel_RGB, target_RGB):
    """
    Helper function. Input: pixel RGB is tuple of three values
    Assume standard deviation (error bar) of +/-10 for all values
    Returns True if match, False if not
    10 is empirically tested; if too big we can't pin down zombie type
    """
    flag = True       # True if pixel is target
    for idx in (0,1,2):
        if pixel_RGB[idx] not in range(target_RGB[idx]-12, target_RGB[idx]+12):
            flag = False
            break
    return flag 


def zombie_lookout(image_array, x_size, y_size, threshold):
    """
    Main vision-based zombie alert function
    Need to test vigorously with different inputs! 
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
    for row_idx in range(y_size):
        for col_idx in range(x_size):
            pix_RGB = image_array[row_idx][col_idx]    # a tuple
            # Now compare againsst known Sky, Mountain and Earth data
            if(is_pixel_match(pix_RGB, visual_dict["Sky"]) == False):
                if(is_pixel_match(pix_RGB, visual_dict["Mountain"]) == False):    
                    if(is_pixel_match(pix_RGB, visual_dict["Earth"]) == False): 
                        filtered_array.append(pix_RGB)
                        filtered_pos.append((col_idx, row_idx))  # note order!


    # Find the color via counting scores
    print("Filtered length:",len(filtered_array))
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
    print("\nDebugging scores:", aqua_score, blue_score, green_score, purple_score, "\n")
    
    if aqua_score[0] < threshold and blue_score[0] < threshold and \
        green_score[0] < threshold and purple_score[0] < threshold:
        # No zombie nearby; use a threshold instead of 0
        return None
    
    
    if aqua_score[0] >= blue_score[0] and aqua_score[0] >= green_score[0] and aqua_score[0] >= purple_score[0]:
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
    
    return zombie_type, angle


"""-------- Robot escape logic helper functions --------"""


def compute_escape(front_lookout, right_lookout, back_lookout, left_lookout):
    """
    Function to calculate escape TURN angle based on four camera lookouts
    Each input lookout is (zombie type, angle) tuple so we can tailor according
    to color if desired. 
    Output escape angle (from -180 to 180 deg), for motor action
    i.e. zero degrees front lookout: facing head-on, so go BACK
         zero degrees right lookout: coming from the right, go LEFT
         
    """
    
    # for now treat all zombies uniformly
    escape_angle = 0
    if front_lookout != None:
        escape_angle += front_lookout[1] + 180
    if right_lookout != None:
        escape_angle += right_lookout[1] + 270
    if back_lookout != None:
        escape_angle += back_lookout[1]   # see math
    if left_lookout != None:
        escape_angle += left_lookout[1] + 90
    
    while escape_angle >= 360:
        escape_angle -= 360
    
    if escape_angle > 180:
        return 360-escape_angle    # turn left/anticlockwise
    else:
        return escape_angle        # turn clockwise



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
    #accelerometer = robot.getDevice("accelerometer")
    #accelerometer.enable(timestep)
    
    #gps = robot.getDevice("gps")
    #gps.enable(timestep)
    
    #compass = robot.getDevice("compass")
    #compass.enable(timestep)
    
    #camera1 = robot.getDevice("ForwardLowResBigFov")
    #camera1.enable(timestep)
    
    #camera2 = robot.getDevice("ForwardHighResSmallFov")
    #camera2.enable(timestep)
    
    camera3 = robot.getDevice("ForwardHighRes")   # 400 cost
    camera3.enable(timestep)
    
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
    
    fr = robot.getDevice("wheel1")
    fl = robot.getDevice("wheel2")
    br = robot.getDevice("wheel3")
    bl = robot.getDevice("wheel4")
    
    

    # float('inf')    differential wheel velocity to turn 10,1,10,1
    fr.setPosition(float('inf'))   # modified
    fr.setVelocity(0)
    fl.setPosition(float('inf'))
    fl.setVelocity(0)
    br.setPosition(float('inf'))
    br.setVelocity(0)
    bl.setPosition(float('inf'))
    bl.setVelocity(0)

    
           

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
           
        # Read from four cameras 
        # camera1.saveImage('cam1.png',100)  # for testing purposes, best quality PNG save
        front_RGB = make_image_array(camera3.getImage())   # to get RGB order
        right_RGB = make_image_array(camera6.getImage()) 
        back_RGB  = make_image_array(camera5.getImage()) 
        left_RGB  = make_image_array(camera7.getImage()) 
        
        # Compute lookout data types; take care of threshold
        front_lookout = zombie_lookout(front_RGB, 256, 128, 50) # x, y image size from specs
        right_lookout = zombie_lookout(right_RGB, 128, 64, 50)
        back_lookout  = zombie_lookout(back_RGB, 128, 64, 50)
        left_lookout  = zombie_lookout(left_RGB, 128, 64, 50)

        # Compute escape angle     
        escape_angle = compute_escape(front_lookout, right_lookout, back_lookout, left_lookout)

        # Feed escape_angle to motor
        
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
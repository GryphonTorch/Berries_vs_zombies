
# Dictionary of items of interest in RGB order
visual_dict = {"Red_bright": (211, 64, 48),
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


def berry_lookout(image_array, x_size, y_size, threshold):
    """
    Adapted from Yu Jun's Comp Vision for Zombie Lookout function
    Main vision-based berry function
    Inputs:
        - Array
        - Image dimensions
        - Pixel threshold for when berries are detected
    Do nothing if no berries above threshold, else return (type, angle(degree), distance) tuple 
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
    print("\nDebugging R/P/O/Y berry scores:", red_score, pink_score, orange_score, yellow_score, "\n")
    
    if red_score[0] < threshold and pink_score[0] < threshold and \
        orange_score[0] < threshold and yellow_score[0] < threshold:
        return None
    
    if red_score[0] >= pink_score[0] and red_score[0] >= orange_score[0] and red_score[0] >= yellow_score[0]:
        # red berry closest
        berry_type = "red"
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
       
    # debug 
    #plt.plot(debug_array_x,debug_array_y, ".")
    #plt.show()    
    
    print("Berry type", berry_type, "at", angle, "deg boresight, at", berry_distance, "meters")
    return berry_type, angle, berry_distance


def berry_distance_comparison(front_food, right_food, back_food, left_food):
'''
Returns closest berry in distance
'''
    if front_food[2] >= right_food[2]  and front_food[2]  >= back_food[2]  and front_food[2]  >= left_food[2] :
        closest_berry = front_food
        return closest_berry
    
    elif:
        right_food[2]  >= back_food[2]  and right_food[2]  >= left_food[2] 
        closest_berry = right_food
        return right_berry
    
    elif:
        back_food[2]  >= left_food[2] 
        closest_berry = back_food
        return closest_berry
    
    else:
        closest_berry = left_food
        return closest_berry
        
def berry_angle_calculation(closest_view):
    """
    Function to calculate berry angle based on four camera lookouts
    Output berry angle (from -180 to 180 deg), for motor action
    Modified based on camera input
    """
    
    berry_angle = 0
    if closest_view = front_food:
        berry_angle = front_food[1]
    if closest_view = right_food:
        berry_angle = right_food[1] + 90
    if closest_view = back_food:
        berry_angle = back_food[1] + 180  # see math
    if closest_view = left_food:
        berry_angle = left_food[1] + 270
    
    if berry_angle > 180:
        return 360 - berry_angle    # turn left/anticlockwise
    else:
        return berry_angle        # turn clockwise



'''
COMPUTING FOR EACH TIMESTEP:
- Getting closest berry at each field of view
- Getting closest berry among all four cameras
- Calculating angle of that single berry
'''
# Compute type and angle of food
front_food = berry_lookout(front_RGB, 256, 128, 1) # x, y image size from specs
right_food = berry_lookout(right_RGB, 128, 64, 1)
back_food  = berry_lookout(back_RGB, 128, 64, 1)
left_food  = berry_lookout(left_RGB, 128, 64, 1)

closest_view = berry_distance_comparison(front_food, right_food, back_food, left_food)
berry_angle = berry_calculation(closest_view)

'''
LEARNING ALGORITHM:
We create a list of good berries, once one berry gives us a -20 energy, we black list it.
'''


good_berry_list = ["red", "orange", "pink", "yellow"]

if closest_view[0] in good_berry_list:
    
    rotate_degree(berry_angle)
    init_energy = robot_info[1]
    
    while front_food != None: 
        base_forward()
        
    if front_food == None:
        final_energy = robot_info[1]
        
    if final_energy - init_energy < 0:
        good_berry_list.remove(index(closest_view[0]))

else:
    random_walk()


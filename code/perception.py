import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

# find the obstacle
def color_thresh_obstacle(img, rgb_thresh=(80, 80, 80)):
    # Create an array of zeros same xy size as img, but single channel
    obstacle_select = np.zeros_like(img[:,:,0])
 
    below_thresh = (img[:,:,0] < rgb_thresh[0]) \
                & (img[:,:,1] < rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    obstacle_select[below_thresh] = 1
    # Return the binary image
    return obstacle_select

def rock_thresh(img):
    low_yellow = np.array([20, 100, 100], dtype = "uint8")
    high_yellow = np.array([55, 255, 255], dtype = "uint8")        # convert to HSV space
    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV,3)    # mask yellow values
    mask_rock = cv2.inRange(img_hsv, low_yellow, high_yellow)
    return mask_rock

# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # TODO:Done
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    # Apply a rotation
    xpix_rotated = xpix * np.cos(yaw_rad) - ypix * np.sin(yaw_rad)
    ypix_rotated = xpix * np.sin(yaw_rad) + ypix * np.cos(yaw_rad)
    # Return the result  
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # TODO:Done
    # Apply a scaling and a translation
    xpix_translated = xpos + (xpix_rot / scale)
    ypix_translated = ypos + (ypix_rot / scale)
    # Return the result  
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    if (Rover.roll <358 and Rover.roll >2) or (Rover.pitch <358 and Rover.pitch>2):
        return Rover

    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform    img=Rover.img
    img=Rover.img
    dst_size = 5 
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[img.shape[1]/2 - dst_size, img.shape[0] - bottom_offset],
                  [img.shape[1]/2 + dst_size, img.shape[0] - bottom_offset],
                  [img.shape[1]/2 + dst_size, img.shape[0] - 2*dst_size - bottom_offset], 
                  [img.shape[1]/2 - dst_size, img.shape[0] - 2*dst_size - bottom_offset],
                  ])

    # 2) Apply perspective transform
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    warped = perspect_transform(img, source, destination)
    threshed = color_thresh(warped)
    rock_select=rock_thresh(warped)
    obstacle_select=color_thresh_obstacle(warped)
    Rover.vision_image[:,:,0]=obstacle_select*255
    Rover.vision_image[:,:,1]=rock_select*255
    Rover.vision_image[:,:,2]=threshed*255
    # 5) Convert map image pixel values to rover-centric coords

    xpix, ypix = rover_coords(threshed)
    xpix_obstacle, ypix_obstacle = rover_coords(obstacle_select)
    xpix_rock, ypix_rock = rover_coords(rock_select)
    # 6) Convert rover-centric pixel values to world coordinates
    scale=10
    rover_xpos=Rover.pos[0]
    rover_ypos=Rover.pos[1]

    x_world, y_world = pix_to_world(xpix, ypix, rover_xpos, 
                                    rover_ypos, Rover.yaw, 
                                    Rover.worldmap.shape[0], scale)


    obstacle_x_world, obstacle_y_world = pix_to_world(xpix_obstacle, ypix_obstacle, rover_xpos, 
                                    rover_ypos, Rover.yaw, 
                                    Rover.worldmap.shape[0], scale)


    rock_x_world, rock_y_world = pix_to_world(xpix_rock, ypix_rock, rover_xpos, 
                                    rover_ypos, Rover.yaw, 
                                    Rover.worldmap.shape[0], scale)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    Rover.worldmap[y_world, x_world,2] += 1
    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    dist, angles = to_polar_coords(xpix, ypix)
    Rover.nav_dists=dist
    Rover.nav_angles = angles
    
 
    if len(rock_x_world)>5:
        Rover.see_sample = 1
        dist_rock, angles_rock = to_polar_coords(xpix_rock, ypix_rock)
        if np.min(dist_rock)<5:
            Rover.throttle = 0
            Rover.brake = Rover.brake_set
#            Rover.mode == 'stop'
        else: 
            print("----------------I heading for", np.min(dist_rock))
            Rover.steer = np.clip(np.mean(angles_rock * 180/np.pi), -15, 15)
            #Rover.throttle=0.02
        print("----------------I see isee change to ",Rover.steer )
    else: Rover.see_sample=0

    
    
    return Rover

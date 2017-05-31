## Project: Search and Sample Return
 

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
 
##### following the course, there's no too mu difficulchty in this, I write a color_thresh_rock() to identify the rock, later I saw a way (from slack) using opencv and hsv , better than mine .

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

##### movie in the output1 directory, but how can i draw the arrow in the video?

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

##### in perception , my previous work can't show the vision_image, with the help from community, multiply it with 255.
##### I waste a lot of time in picking-up, an variable see_sample is added to rover_state, when rover see the rock , it will change the steer for heading to it. 
##### restriction of roll and pitch is also in consideration


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

##### in my autonomous simulation, the rover can collect some rocks. but sometimes it got stuck  or moved in circle loop (in the square, e.g). I have tried to give a fixed offset to Rover.steer, which seems not work
##### it can't get back to the starting point, no implementation making sue mapping 100%. I need to improve in this orientation




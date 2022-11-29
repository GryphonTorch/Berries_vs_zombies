CPSC 472 Final Project Berries_vs_zombies 

Robot needs to find and eat berries while avoiding dangerous zombies! 

Full documentation and workings at:
https://docs.google.com/document/d/1lpzJqTAA1lr0GP-oU-W4man2UXQBcRrqUkJqqb4J70Y/edit?usp=sharing

Preliminary performance on test world 1: https://drive.google.com/file/d/1W-MHpjuspnriWQ1fiHwI9vkQ8PiUIxeE/view?usp=sharing 

Debugging (and solutions)

1 - Tune up zombie threshold to 75 such that it does not overwhelm berry search

2 - If two berries in line of sight, could oscillate --> use timer%10 semaphore to control counter_timer variable. i.e. give it enough time to turn/move, before next camera sensor analysis

3 - Hitting a stump --> adjust turn to have slight backwards component instead of pivot on the spot. Looks a bit funny in action but seems to work when bumped up a stump (esp when vision is not blocked)

Open issues 

4 - Robot ends up in a corner of the world and beats on, borne back ceaselessly into the past :(

5 - Zombie teabags robot (hard to see zombie that is on top of robot)

6 - Ate a bad berry along the way when running from the zombie (by accident, was not aiming for it) -- then want_to_eat is 0 and cannot be deleted from the good_berry_list


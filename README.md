# Sine wave experiment (+Mooneys!)

Clone, install psychopy v3 and dependencies (https://www.psychopy.org/download.html), and run
`python sine_wave.py` (using Python 3). 

## Notes
* Press 'q' to proceed onward from the instructions (for both part 1 and part 2). This is to prevent subjects from starting on their own prior to receiving verbal instructions from the experimenter.
* Part 2 (mooney images) begins with general instructions which are followed by a couple examples of mooney images.
* If you want to test just sine_waves or just mooney images, set `num_blocks_sine_wave` or `num_blocks_mooney` to 0
* Uses psychtoolbox driver for sounds
* Uses some functions from a LupyanLab library file - useful_functions_python3.py
* If the text or images are not not centered, you'll want to downgrade pyglet (the library used by psychopy to display stims): `pip uninstall pyglet` then `pip install pyglet==1.3.2`

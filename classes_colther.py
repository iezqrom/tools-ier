#!/usr/bin/env python3

#Time
from datetime import datetime
import time
from time import sleep
import logging

#System
try:
    import sys
except:
    pass

try:
    import tty
except:
    pass

try:
    import termios
except:
    pass
try:
    import os
except:
    pass

import zaber.serial as zs

import keyboard
import serial
try:
    import winsound
except:
    pass

import matplotlib.pyplot as plt

# My stuff
try:
    import globals
except:
    pass

from classes_arduino import ArdUIno

from grabPorts import grabPorts
from pyd import PYD
from saving_data import *

# Maths
import numpy as np
import pandas as pd
import curses
import math

import struct

from scipy import stats
from scipy.interpolate import interp1d

from failing import *

################################################################################################################
################################################################################################################
############################ SYRINGE LOOK-UP TABLE (LUT) 
################################################################################################################
################################################################################################################

end_220000 = 25.98
end_210000 = 27.17
end_200000 = 28.09
end_190000 = 28.78
end_170000 = 29.18
end_140000 = 30.78

ends = [end_220000, end_210000, end_200000, end_190000, end_170000, end_140000]
zebers = [220000, 210000, 200000, 190000, 170000, 140000]

slope, intercept, r_value, p_value, std_err = stats.linregress(zebers, ends)

# %%
y_vals = intercept + slope * np.asarray(zebers) + (33 - ends[-1])
zebers_inter = np.arange(220000, 140000, -150)
y_vals_inter = intercept + slope * zebers_inter + (33 - ends[-1])


################################################################################################################
################################################################################################################
############################ CLASS 
################################################################################################################
################################################################################################################
logging.basicConfig(filename='./zaber_positions.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

class Zaber(grabPorts):
    """
        Zaber class developed by Ivan Ezquerra-Romano at the Action & Body lab (2018-2020)
    """

    def __init__(self, n_device, who, usb_port = None, n_modem = None, winPort = None, port = None):
        self.ports = grabPorts()
        self.ports.zaberPort(who, usb_port, n_modem, winPort)

        if n_device == 1: # number 1 device is chosen to lead the Daisy chain
            try:
                self.port = zs.AsciiSerial(self.ports.zaber_port)
            except:
                self.port = zs.AsciiSerial(self.ports.zaber_port[0])

            # print(self.port)
            self.device = zs.AsciiDevice(self.port, n_device)
        else:
            self.port = port
            self.device = zs.AsciiDevice(port.port, n_device)
        
        # print(self.device)

    def move(self, amount):
        reply = self.device.move_rel(amount)
        print(reply)

    def manual(self):
        amount = input("Distance per click: (300-5000)")
        amount = int(amount)
        while True:
            move = input("Direction: (r for right | l for left | e to end)")
            if move in ('r'):
                self.move(amount)
            elif move in ('l'):
                self.move(0 - amount)
            elif move in ('e'):
                break
            else:
                print('\n Only r, l and e are valid answers')
                continue

    def manualCon1(self, devices):
        """
            Method for Object Zaber to move 3 axes in ONE zaber with keyboard presses.
            Like a game!
        """
        try:

            device = devices[globals.current_device]

            while True:
                #### Y axis
                if keyboard.is_pressed('up'):
                    try:
                        device[2].move_rel(globals.amount)
                    except:
                        device[2].device.move_rel(globals.amount)

                elif keyboard.is_pressed('down'):
                    try:
                        device[2].move_rel(0 - globals.amount)
                    except:
                        device[2].device.move_rel(0 - globals.amount)

                #### X axis

                elif keyboard.is_pressed('left'):
                    try:
                        device[1].move_rel(0 - globals.amount)
                    except:
                        device[1].device.move_rel(0 - globals.amount)

                elif keyboard.is_pressed('right'):
                    try:
                        device[1].move_rel(globals.amount)
                    except:
                        device[1].device.move_rel(globals.amount)

                ### Z axis
                elif keyboard.is_pressed('d'):
                    try:
                        device[0].move_rel(globals.amount)
                    except:
                        device[0].device.move_rel(globals.amount)

                elif keyboard.is_pressed('u'):
                    try:
                        device[0].move_rel(0 - globals.amount)
                    except:
                        device[0].device.move_rel(0 - globals.amount)

                ### TERMINATE
                elif keyboard.is_pressed('e'):
                    homingZabers(devices)
                    break

                # Press letter h and Zaber will home, first z axis, then y and finally x
                # Control

                elif keyboard.is_pressed('h'):
                    homingZabers(devices)
            
                elif keyboard.is_pressed('z'):
                    try:
                        posX = device[2].send("/get pos")
                    except:
                        posX = device[2].device.send("/get pos")

                    try:
                        posY = device[1].send("/get pos")
                    except:
                        posY = device[1].device.send("/get pos")

                    try:
                        posZ = device[0].send("/get pos")
                    except:
                        posZ = device[0].device.send("/get pos")

                    globals.positions[globals.current_device][0] = int(posX.data)
                    globals.positions[globals.current_device][1] = int(posY.data)
                    globals.positions[globals.current_device][2] = int(posZ.data)

                    # logging.info(globals.positions)

                else:
                    continue

        except Exception as e: 
            print(e)

    def manualCon2(self, devices, arduino = None, home='y', rules = globals.rules):
        """
            Method for Object Zabers to move the three axes of TWO zabers with keyboard presses.
            Like a game!
        """

        if home not in ('y', 'n'):
            print("Invalid value for 'home', only 'y' and 'n' are valid values")
            print("'y' selected by default")
            home = 'y'

        print('Zaber game activated')

        if arduino != None:
            stimulus = 0
            arduino.arduino.write(struct.pack('>B', stimulus))

        try:
            device = devices[globals.current_device]

            while True:
                #### Y axis
                if keyboard.is_pressed('up'):
                    try:
                        device['y'].move_rel(0 - revDirection(globals.current_device, 'y', rules, globals.amount))
                    except:
                        device['y'].device.move_rel(0 - revDirection(globals.current_device, 'y', rules, globals.amount))

                elif keyboard.is_pressed('down'):
                    try:
                        device['y'].move_rel(0 + revDirection(globals.current_device, 'y', rules, globals.amount))
                    except:
                        device['y'].device.move_rel(0 + revDirection(globals.current_device, 'y', rules, globals.amount))

                #### X axis

                elif keyboard.is_pressed('left'):
                    try:
                        device['x'].move_rel(0 - revDirection(globals.current_device, 'x', rules, globals.amount))
                    except:
                        device['x'].device.move_rel(0 - revDirection(globals.current_device, 'x', rules, globals.amount))

                elif keyboard.is_pressed('right'):
                    try:
                        device['x'].move_rel(0 + revDirection(globals.current_device, 'x', rules, globals.amount))
                    except:
                        device['x'].device.move_rel(0 + revDirection(globals.current_device, 'x', rules, globals.amount))

                ### Z axis
                elif keyboard.is_pressed('d'):
                    try:
                        device['z'].move_rel(0 + revDirection(globals.current_device, 'z', rules, globals.amount))
                    except:
                        device['z'].device.move_rel(0 + revDirection(globals.current_device, 'z', rules, globals.amount))

                elif keyboard.is_pressed('u'):
                    try:
                        device['z'].move_rel(0 - revDirection(globals.current_device, 'z', rules, globals.amount))
                    except:
                        device['z'].device.move_rel(0 - revDirection(globals.current_device, 'z', rules, globals.amount))

                elif keyboard.is_pressed('p'):
                    globals.centreROI = [globals.indx0, globals.indy0]
                    print(f'Centre of ROI is: {globals.centreROI}')

                ### TERMINATE
                elif keyboard.is_pressed('e'):
                    vars = [globals.centreROI, globals.positions]
                    if all(v is not None for v in vars) and home =='n':
                        print('Terminating Zaber game \n')
                        break

                    elif all(v is not None for v in vars) and home =='y':
                        homingZabers(devices)
                        break
                    else:
                        print('You are missing something...')
                        print(globals.centreROI, globals.positions)


                #### GET POSITION 

                elif keyboard.is_pressed('z'):
                    try:
                        posX = device['x'].send("/get pos")

                    except:
                        posX = device['x'].device.send("/get pos")

                    try:
                        posY = device['y'].send("/get pos")
                    except:
                        posY = device['y'].device.send("/get pos")

                    try:
                        posZ = device['z'].send("/get pos")
                    except:
                        posZ = device['z'].device.send("/get pos")

                    globals.positions[globals.current_device]['x'] = int(posX.data)
                    globals.positions[globals.current_device]['y'] = int(posY.data)
                    globals.positions[globals.current_device]['z'] = int(posZ.data)

                    print(globals.positions)
                    logging.info(globals.positions)

                # Press letter h and Zaber will home, first z axis, then y and finally x
                # Control

                elif keyboard.is_pressed('h'):
                    homingZabers(devices)
                    
                elif keyboard.is_pressed('o'): # Open Arduino shutter
                    globals.stimulus = 1
                    arduino.arduino.write(struct.pack('>B', globals.stimulus))
                    # time.sleep(2)

                elif keyboard.is_pressed('c'): # Close Arduino shutter
                    globals.stimulus = 0
                    arduino.arduino.write(struct.pack('>B', globals.stimulus))
                    # time.sleep(2)

                #### Double

                elif keyboard.is_pressed('k'):
                    device = devices['camera']
                    globals.current_device = 'camera'

                elif keyboard.is_pressed('f'):
                    device = devices['colther']
                    globals.current_device = 'colther'

                else:
                    continue


        finally:
            if arduino != None:
                stimulus = 0
                arduino.arduino.write(struct.pack('>B', stimulus))

    def manualCon3(self, devices, amount, arduino = None):
        """
            Method for Object Zaber to move the 3 axes of THREE zabers with keyboard presses. Like a game!
            The coordinates of two positions can be saved with 'z' and 'x'
            This method was created and it is specific to the experiment in which we measure cold 
            thresholds with and without touch
        """

        try:
            device = devices[globals.current_device]

            while True:
                #### Y axis
                if keyboard.is_pressed('up'):
                    try:
                        device[2].move_rel(globals.amount)
                    except:
                        device[2].device.move_rel(globals.amount)

                elif keyboard.is_pressed('down'):
                    try:
                        device[2].move_rel(0 - globals.amount)
                    except:
                        device[2].device.move_rel(0 - globals.amount)

                #### X axis

                elif keyboard.is_pressed('left'):
                    try:
                        device[1].move_rel(0 - globals.amount)
                    except:
                        device[1].device.move_rel(0 - globals.amount)

                elif keyboard.is_pressed('right'):
                    try:
                        device[1].move_rel(globals.amount)
                    except:
                        device[1].device.move_rel(globals.amount)

                ### Z axis
                elif keyboard.is_pressed('d'):
                    try:
                        device[0].move_rel(globals.amount)
                    except:
                        device[0].device.move_rel(globals.amount)

                elif keyboard.is_pressed('u'):
                    try:
                        device[0].move_rel(0 - globals.amount)
                    except:
                        device[0].device.move_rel(0 - globals.amount)

                elif keyboard.is_pressed('p'):
                    globals.centreROI = [globals.indx0, globals.indy0]
                    

                ### TERMINATE
                elif keyboard.is_pressed('e'):
                    homingZabers(devices)
                    break


                #### GET POSITION 

                elif keyboard.is_pressed('z'):
                    try:
                        posX = device[2].send("/get pos")

                    except:
                        posX = device[2].device.send("/get pos")

                    try:
                        posY = device[1].send("/get pos")
                    except:
                        posY = device[1].device.send("/get pos")

                    try:
                        posZ = device[0].send("/get pos")
                    except:
                        posZ = device[0].device.send("/get pos")

                    globals.positions[globals.current_device]['control'][0] = int(posX.data)
                    globals.positions[globals.current_device]['control'][1] = int(posY.data)
                    globals.positions[globals.current_device]['control'][2] = int(posZ.data)

                elif keyboard.is_pressed('x'):
                    try:
                        posX = device[2].send("/get pos")

                    except:
                        posX = device[2].device.send("/get pos")

                    try:
                        posY = device[1].send("/get pos")
                    except:
                        posY = device[1].device.send("/get pos")

                    try:
                        posZ = device[0].send("/get pos")
                    except:
                        posZ = device[0].device.send("/get pos")

                    globals.positions[globals.current_device]['experimental'][0] = int(posX.data)
                    globals.positions[globals.current_device]['experimental'][1] = int(posY.data)
                    globals.positions[globals.current_device]['experimental'][2] = int(posZ.data)


                # Press letter h and Zaber will home, first z axis, then y and finally x
                # Control

                elif keyboard.is_pressed('h'):
                    homingZabers(devices)


                #### Double

                elif keyboard.is_pressed('k'):
                    device = devices['camera']
                    globals.current_device = 'camera'

                elif keyboard.is_pressed('f'):
                    device = devices['colther']
                    globals.current_device = 'colther'

                elif keyboard.is_pressed('t'):
                    device = devices['tactile']
                    globals.current_device = 'tactile'
                
                elif keyboard.is_pressed('n'):
                    device = devices['tactile']
                    globals.current_device = 'non_tactile'

                else:
                    continue


        finally:
            if arduino != None:
                stimulus = 0
                arduino.arduino.write(struct.pack('>B', stimulus))

    def manualCon3OneCon(self, devices, amount, arduino = None):

        try:
            device = devices[globals.current_device]

            while True:
                #### Y axis
                if keyboard.is_pressed('up'):
                    try:
                        device[2].move_rel(globals.amount)
                    except:
                        device[2].device.move_rel(globals.amount)

                elif keyboard.is_pressed('down'):
                    try:
                        device[2].move_rel(0 - globals.amount)
                    except:
                        device[2].device.move_rel(0 - globals.amount)

                #### X axis

                elif keyboard.is_pressed('left'):
                    try:
                        device[1].move_rel(0 - globals.amount)
                    except:
                        device[1].device.move_rel(0 - globals.amount)

                elif keyboard.is_pressed('right'):
                    try:
                        device[1].move_rel(globals.amount)
                    except:
                        device[1].device.move_rel(globals.amount)

                ### Z axis
                elif keyboard.is_pressed('d'):
                    try:
                        device[0].move_rel(globals.amount)
                    except:
                        device[0].device.move_rel(globals.amount)

                elif keyboard.is_pressed('o'): # Open Arduino shutter
                    globals.stimulus = 1
                    arduino.arduino.write(struct.pack('>B', globals.stimulus))


                elif keyboard.is_pressed('c'): # Close Arduino shutter
                    globals.stimulus = 0
                    arduino.arduino.write(struct.pack('>B', globals.stimulus))


                elif keyboard.is_pressed('u'):
                    try:
                        device[0].move_rel(0 - globals.amount)
                    except:
                        device[0].device.move_rel(0 - globals.amount)

                elif keyboard.is_pressed('p'):
                    globals.centreROI = [globals.indx0, globals.indy0]
                    

                ### TERMINATE
                elif keyboard.is_pressed('e'):
                    # homingZabers(devices)
                    break


                #### GET POSITION 

                elif keyboard.is_pressed('z'):
                    try:
                        posX = device[2].send("/get pos")

                    except:
                        posX = device[2].device.send("/get pos")

                    try:
                        posY = device[1].send("/get pos")
                    except:
                        posY = device[1].device.send("/get pos")

                    try:
                        posZ = device[0].send("/get pos")
                    except:
                        posZ = device[0].device.send("/get pos")

                    globals.positions1[globals.current_device][0] = int(posX.data)
                    globals.positions1[globals.current_device][1] = int(posY.data)
                    globals.positions1[globals.current_device][2] = int(posZ.data)

                # Press letter h and Zaber will home, first z axis, then y and finally x
                # Control

                elif keyboard.is_pressed('h'):
                    homingZabers(devices)

                #### Double

                elif keyboard.is_pressed('k'):
                    device = devices['camera']
                    globals.current_device = 'camera'

                elif keyboard.is_pressed('f'):
                    device = devices['colther']
                    globals.current_device = 'colther'

                elif keyboard.is_pressed('t'):
                    device = devices['tactile']
                    globals.current_device = 'tactile'
                
                elif keyboard.is_pressed('n'):
                    device = devices['tactile']
                    globals.current_device = 'non_tactile'

                else:
                    continue


        finally:
            if arduino != None:
                stimulus = 0
                arduino.arduino.write(struct.pack('>B', stimulus))

    def manualConGUIthree(self, devices, arduino = None):

        """
        Controls:               # letter 'f' for colther
                                # letter 'h' for camera
                                # letter 't' for tactile
                                # letter 'n' for non-tactile

                                # letter 'c' to close shutter
                                # letter 'o' to open shutter

                                # letter 'p' to get centre ROI tactile
                                # letter 'i' to get centre ROI non-tactile

                                # letter 'h' to home all zabers
                                # press 'enter' to terminate
                                # press arrow 'up' to move x axis forward
                                # press arrow 'down' to move x axis backwards
                                # press arrow 'left' to move y axis forward
                                # press arrow 'right' to move y axis backwards
                                # letter 'd' to move Z axis down
                                # letter 'u' to move Z axis up
                                # letter 'z' to save CONTROL spot position
                                # letter 'x' to save EXPERIMENTAL spot position
        """

        if arduino != None:
            globals.stimulus = 0
            arduino.arduino.write(struct.pack('>B', globals.stimulus))
            # print('make sure shutter is closed')

        try:
            # Default zaber is camera
            device = devices[globals.current_device]

            while True:

                #### Y axis
                if keyboard.is_pressed('up'):
                    try:
                        device[1].move_rel(globals.amount)
                    except:
                        device[1].device.move_rel(globals.amount)
                    # print(curses.KEY_UP)

                elif keyboard.is_pressed('down'):
                    try:
                        device[1].move_rel(0 - globals.amount)
                    except:
                        device[1].device.move_rel(0 - globals.amount)

                #### X axis

                elif keyboard.is_pressed('left'):
                    try:
                        device[2].move_rel(0 - globals.amount)
                    except:
                        device[2].device.move_rel(0 - globals.amount)

                elif keyboard.is_pressed('right'):
                    try:
                        device[2].move_rel(globals.amount)
                    except:
                        device[2].device.move_rel(globals.amount)

                ### Z axis
                elif keyboard.is_pressed('d'):
                    try:
                        device[0].move_rel(globals.amount)
                    except:
                        device[0].device.move_rel(globals.amount)

                elif keyboard.is_pressed('u'):
                    try:
                        device[0].move_rel(0 - globals.amount)
                    except:
                        device[0].device.move_rel(0 - globals.amount)

                ### TERMINATE
                elif keyboard.is_pressed('e'):
                    homingZabers(devices)

                    break


                #### GET POSITION ZABER
                # Experimental
                elif keyboard.is_pressed('x'):
                    try:
                        posX = device[0].send("/get pos")

                    except:
                        posX = device[0].device.send("/get pos")


                    try:
                        posY = device[1].send("/get pos")
                    except:
                        posY = device[1].device.send("/get pos")


                    try:
                        posZ = device[2].send("/get pos")
                    except:
                        posZ = device[2].device.send("/get pos")

                    globals.positions[globals.current_device]['experimental'][2] = int(posX.data)
                    globals.positions[globals.current_device]['experimental'][1] = int(posY.data)
                    globals.positions[globals.current_device]['experimental'][0] = int(posZ.data)

                    # print(globals.positions)

                elif keyboard.is_pressed('z'):
                    try:
                        posX = device[0].send("/get pos")

                    except:
                        posX = device[0].device.send("/get pos")


                    try:
                        posY = device[1].send("/get pos")
                    except:
                        posY = device[1].device.send("/get pos")


                    try:
                        posZ = device[2].send("/get pos")
                    except:
                        posZ = device[2].device.send("/get pos")

                    globals.positions[globals.current_device]['control'][2] = int(posX.data)
                    globals.positions[globals.current_device]['control'][1] = int(posY.data)
                    globals.positions[globals.current_device]['control'][0] = int(posZ.data)

                    print(posX.data)

                # Press letter h and Zaber will home, first z axis, then y and finally x
                # Control

                elif keyboard.is_pressed('h'):
                    homingZabers(devices)

                elif keyboard.is_pressed('o'): # Open Arduino shutter
                    globals.stimulus = 1
                    arduino.arduino.write(struct.pack('>B', globals.stimulus))
                    # time.sleep(2)

                elif keyboard.is_pressed('c'): # Close Arduino shutter
                    globals.stimulus = 0
                    arduino.arduino.write(struct.pack('>B', globals.stimulus))
                    # time.sleep(2)

                elif keyboard.is_pressed('p'):
                    # print([globals.indx0, globals.indy0])
                    globals.centreROI['control'] = [globals.indx0, globals.indy0]

                elif keyboard.is_pressed('i'):
                        globals.centreROI['experimental'] = [globals.indx0, globals.indy0]

                elif keyboard.is_pressed('t'):
                    device = devices['tactile']
                    globals.current_device = 'tactile'

                elif keyboard.is_pressed('n'):
                    device = devices['tactile']
                    globals.current_device = 'non_tactile'

                elif keyboard.is_pressed('k'):
                    device = devices['camera']
                    globals.current_device = 'camera'

                elif keyboard.is_pressed('f'):
                    device = devices['colther']
                    globals.current_device = 'colther'


                else:
                    continue


        finally:
            if arduino != None:
                globals.shutter_state = 'close'
                arduino.arduino.write(globals.shutter_state.encode())

    def ROIPID(self, device, set_point, event1, arduino = None, radio = 20.):

        """
            Method function to perform PID on a pre-selected ROI. 
            It synchronises with the camera, so it needs an event.
            Globals: pid_out, stimulus, temp, pos_zaber
        """

        ## PID parameters
        Kp = -1500
        Ki = -100
        Kd = -800
        output_limits = (-3000, 3000)

        # we initialise PID object
        PID = PYD(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=set_point, output_limits=output_limits)
        print('PID initialised')

        pos = device[0].device.send("/get pos")
        globals.pos_zaber = int(pos.data)

        if arduino != None:
            globals.stimulus = 1
            arduino.arduino.write(struct.pack('>B', globals.stimulus))
            # print('Shutter '+ str(globals.stimulus))

        try:
            while True:
                if globals.stimulus == 1:
                    event1.wait()
                    # print(globals.stimulus)
                    # print('In while loop, stimulus')
                    print(globals.temp)

                    while globals.temp > (set_point + 0.4):
                        # print('waiting to start close-loop')
                        # print(type(set_point))
                        time.sleep(0.0001)

                    PID.run(globals.temp)
                    globals.pid_out = PID.output

                    device[0].device.move_rel(int(globals.pid_out))
                    pos = device[0].device.send("/get pos")
                    globals.pos_zaber = int(pos.data)
                    previous_temp = globals.temp

                elif globals.stimulus == 0:
                    print('Close shutter')
                    arduino.arduino.write(struct.pack('>B', globals.stimulus))
                    break

                event1.clear()
                # print('event cleared')

        except Exception as e: 
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        except KeyboardInterrupt:
            sys.exit(0)

        finally:
            print('Stop PID')
            pass


    def ROIPIDSyringe(self, device, set_point, event1, radio, arduino = None):

        ## PID parameters

        thermal_range = np.round(np.arange(24.00, 33.01, 0.01), 2)

        Kp_down = -800
        Kp_up = -1500
        Kp_range = np.round(np.arange(Kp_down, Kp_up, -abs(Kp_down - Kp_up)/len(thermal_range)), 2)

        Ki_down = -100
        Ki_up = -500
        Ki_range = np.round(np.arange(Ki_down, Ki_up, -abs(Ki_down - Ki_up)/len(thermal_range)), 2)

        Kd_down = -100
        Kd_up = -500
        Kd_range = np.round(np.arange(Kd_down, Kd_up, -abs(Kp_down - Ki_up)/len(thermal_range)), 2)

        output_limits = (-3000, 3000)

        # we initialise PID object
        PID = PYD(Kp_range, Ki_range, Kd_range, set_point, gain_scheduling_range=thermal_range, output_limits = output_limits)
        counter = 0
        try:
            while True:
                if globals.stimulus == 1:
                    counter += 1

                    event1.wait()

                    if counter == 1:

                        while globals.temp > (set_point + 0.4):
                            # print('waiting to start close-loop')
                            # print(type(set_point))
                            time.sleep(0.0001)

                    # Calculate controller variable
                    PID.runGainSchedule(globals.temp)

                    print(globals.temp)
                    print(PID.output)

                    # Move zaber
                    device[0].device.move_rel(int(PID.output))
                    pos = device[0].device.send("/get pos")
                    pos = int(pos.data)
                    previous_temp = globals.temp

                    # Send global variables to save
                    globals.pos_zaber = pos
                    globals.Kp = PID.current_Kp
                    globals.Ki = PID.current_Ki
                    globals.Kd = PID.current_Kd

                    globals.proportional = PID.proportional
                    globals.integral = PID.integral
                    globals.derivative = PID.derivative

                elif globals.stimulus == 0:

                    continue

                previous_temp = globals.temp
                event1.clear()


        except KeyboardInterrupt:
            sys.exit(0)

    def DistROI(self, device, set_point, event, file, folder, name_dev = 'colther'):

        dataTS = {'Koutput': [], 'data': [], 'Kp': [], 'Ki': [], 'error': [], 'positionX': [], 'positionY': [], 'positionZ': [], 'set_point': [], 'time': []}
        ## PID parameters
        Kp = -400
        Ki = -100
        output_limits = (-500, 500)

        # we initialise PID object
        PID = PYD(Kp, set_point, Ki= Ki, output_limits= output_limits)

        while True:

            event.wait()

            PID.run(globals.data)
            # print(globals.data)
            # print(PID.error)
            # print('PID data: ' + str(int(PID.output)))

            now = time.time()
            loop_data = [PID.output, globals.data, PID.proportional, PID.integral, PID.error, globals.positions['colther'][0], globals.positions['colther'][1], globals.positions['colther'][2], globals.dist, now]
            # print(globals.positions['colther'])

            device[name_dev][0].device.move_rel(int(PID.output))
            pos = device[name_dev][0].device.send("/get pos")
            pos = int(pos.data)

            globals.pos_zaber = pos

            event.clear()

            for k, l in zip(dataTS, loop_data):
                dataTS[k].append(l)

            if keyboard.is_pressed('e'):
                saveIndv(file, folder, dataTS)
                break

    def manualCon(self, devices, amount, arduino = None):
        """
            Very early method to control three axes of one zaber while displying instructions and
            other info on screen. It uses the curses library
        """

        if arduino != None:
            stimulus = 0
            arduino.arduino.write(struct.pack('>B', stimulus))

        # self.spotsPosX = {'C1': [], 'C2': [], 'NonC': []}
        # self.spotsPosY = {'C1': [], 'C2': [], 'NonC': []}

        def my_raw_input(stdscr, r, c, prompt_string):
            curses.echo()
            stdscr.addstr(r, c, prompt_string)
            stdscr.refresh()
            input = stdscr.getstr(r + 1, c, 20)
            return input

        try:

            stdscr = curses.initscr()
            stdscr.keypad(1)

            stdscr.addstr(0,0,'\n Move COLTHER. \n Device 1 (x): left and right arrows \n Device 2 (y): up and down arrows \n Device 3 (z): "u" (up) and "d" (down) \n Press "o" to open the shutter \n Press "c" to close the shutter \n Press "a" to choose how many steps to move \n Press "e" to terminate \n Press "s" to get Zaber coordiantes \n Press "p" tp get ROI centre"s coordinates')
            stdscr.refresh()

            key = ''
            while True:

                try:
                    stdscr.move(23, 0)
                    stdscr.clrtoeol()

                except Exception as e:
                    stdscr.refresh()
                    curses.endwin()
                    # print(e)


                stdscr.addstr(19,0, 'Minimum temperature: {}'.format(globals.temp))

                stdscr.move(19, 59)
                stdscr.clrtoeol()

                key = stdscr.getch()
                stdscr.refresh()

                if key == curses.KEY_UP:
                    devices[1].device.move_rel(amount)
                    # print(curses.KEY_UP)
                elif key == curses.KEY_DOWN:
                    devices[1].device.move_rel(0 - amount)

                elif key == ord('e'): ### TERMINATE
                    for i in reversed(devices):
                        i.device.home()
                    break

                elif key == ord('a'): ### ZABER STEPS
                    while True:
                        amount = my_raw_input(stdscr, 10, 50, "\n How much would you like to move?").decode("utf-8")
                        try:
                            amount = int(amount)
                            stdscr.move(10 + 1, 0)
                            # stdscr.refresh()
                            stdscr.clrtoeol()
                            break
                        except:
                            stdscr.addstr(14, 0, 'Only integers are valid numbers')


                elif key == curses.KEY_LEFT:
                    devices[0].device.move_rel(0 - amount)
                elif key == curses.KEY_RIGHT:
                    devices[0].device.move_rel(amount)

                elif key == curses.KEY_LEFT:
                    devices[0].device.move_rel(0 - amount)
                elif key == curses.KEY_RIGHT:
                    devices[0].device.move_rel(amount)

                elif key == ord('d'):
                    devices[2].device.move_rel(amount)
                    # print('d')
                elif key == ord('u'):
                    devices[2].device.move_rel(0 - amount)

                elif key == ord('s'): #### GET POSITION ZABER

                    posX = devices[0].device.send("/get pos")
                    globals.posX = int(posX.data)

                    posY = devices[1].device.send("/get pos")
                    globals.posY = int(posY.data)

                    posZ = devices[2].device.send("/get pos")
                    globals.posZ = int(posZ.data)

                    stdscr.addstr(15,0, 'X: {} // Y: {} // Z: {}'.format(globals.posX, globals.posY, globals.posZ))

                elif key == ord('h'): # Press letter h and Zaber will home, first z axis, then y and finally x
                    for i in reversed(devices):
                        i.device.home()

                elif key == ord('o'): # Open Arduino shutter
                    globals.stimulus = 1
                    arduino.arduino.write(struct.pack('>B', globals.stimulus))

                elif key == ord('c'): # Close Arduino shutter
                    globals.stimulus = 0
                    arduino.arduino.write(struct.pack('>B', globals.stimulus))

                elif key == ord('p'):
                    globals.indx_saved = globals.indx0
                    globals.indy_saved = globals.indy0

                else:
                    continue


        finally:

            if arduino != None:
                globals.stimulus = 0
                arduino.arduino.write(struct.pack('>B', globals.stimulus))

            stdscr.refresh()
            curses.endwin()



######################## Developing phase
    def maintainColdMinPeak(self, amount, devices, set_point, range, event1, arduino = None):

        devices[0].device.move_abs(globals.posX)
        devices[1].device.move_abs(globals.posY)
        devices[2].device.move_abs(globals.posZ)

        previous_temp = globals.temp

        # We define the low and upper bounds
        lowR = set_point - range/2
        highR = set_point + range/2

        # time.sleep(2)

        if arduino != None:
            shutter = 'open'
            arduino.arduino.write(shutter.encode())
            time.sleep(1.2)
            globals.shutter_state = 'open'
            print(globals.shutter_state)

        counter = 0

        try:

            while True:

                if globals.shutter_state == 'open':
                    counter += 1

                    # print('we are here')
                    event1.wait()
                    # print('Minimum temperature: ' + str(globals.temp))

                    if counter == 1:
                        while globals.temp > (set_point + 0.4):
                            # print('waiting to start close-loop')
                            # print(type(set_point))
                            time.sleep(0.0001)


                    if keyboard.is_pressed('c'):
                        shutter = 'close'
                        arduino.arduino.write(shutter.encode())

                        globals.shutter_state = 'close'
                        devices[2].device.move_abs(0)
                        devices[1].device.move_abs(0)
                        devices[0].device.move_abs(0)

                    if globals.temp < lowR: # BELOW lower bound
                        diff = abs(set_point - globals.temp)
                        a = amount * 10 * diff
                        b = amount * 4 * diff

                    if globals.temp > highR: # ABOVE upper bound
                        diff = abs(set_point - globals.temp)
                        a = amount * 10 * diff
                        b = amount * 4 * diff

                    if globals.temp > (set_point - 1.5) and globals.temp < (set_point + 1.5):
                        # print('here')
                        diff = abs(set_point - globals.temp)
                        a = amount * 4 * diff
                        b = amount * 10 * diff

                    print(diff)
                    zaber_pos = a * (set_point - globals.temp) + b * (previous_temp - globals.temp)

                    # print(zaber_pos)

                    devices[2].device.move_rel(-int(zaber_pos))
                    pos = devices[2].device.send("/get pos")
                    pos = int(pos.data)
                    previous_temp = globals.temp
                    globals.posZ = pos

                elif globals.shutter_state == 'close':
                    # print('we are here actually')
                    # time.sleep(0.01)
                    continue

                previous_temp = globals.temp
                event1.clear()


        except KeyboardInterrupt:
            sys.exit(0)

    def maintainColdMeanROIPID(self, devices, set_point, event1, radio, arduino = None):

        devices[0].device.move_abs(globals.posX)
        devices[1].device.move_abs(globals.posY)
        devices[2].device.move_abs(globals.posZ)

        previous_temp = globals.temp

        # We define the low and upper bounds
        # lowR = set_point - range/2
        # highR = set_point + range/2
        # print(lowR, highR)

        if arduino != None:
            shutter = 'open'
            arduino.arduino.write(shutter.encode())
            time.sleep(1.2)
            globals.shutter_state = 'open'
            print(globals.shutter_state)

        counter = 0

        try:

            while True:

                if globals.shutter_state == 'open':
                    counter += 1

                    # print('we are here')
                    event1.wait()
                    # print('Minimum temperature: ' + str(globals.temp))

                    if counter == 1:

                        while globals.temp > (set_point + 0.4):
                            # print('waiting to start close-loop')
                            # print(type(set_point))
                            time.sleep(0.0001)

                            ## PID parameters
                        Kp = -1500
                        Ki = -100
                        Kd = -800
                        output_limits = (-3000, 3000)
                        range = 0.3

                        # we initialise PID object
                        PID = PYD(Kp, Ki, Kd, set_point)


                    if keyboard.is_pressed('c'):
                        shutter = 'close'
                        arduino.arduino.write(shutter.encode())

                        globals.shutter_state = 'close'
                        devices[2].device.move_abs(0)
                        devices[1].device.move_abs(0)
                        devices[0].device.move_abs(0)

                    zaber_pos = PID(globals.temp)

                    # print(zaber_pos)

                    devices[2].device.move_rel(int(zaber_pos))
                    pos = devices[2].device.send("/get pos")
                    pos = int(pos.data)
                    previous_temp = globals.temp
                    globals.posZ = pos

                elif globals.shutter_state == 'close':
                    # print('we are here actually')
                    # time.sleep(0.01)
                    continue

                previous_temp = globals.temp
                event1.clear()


        except KeyboardInterrupt:
            sys.exit(0)

    def OscColdMeanROIPID(self, devices, set_point, event1, radio, amplitude, frequency, arduino = None):

        devices[0].device.move_abs(globals.posX)
        devices[1].device.move_abs(globals.posY)
        devices[2].device.move_abs(globals.posZ)

        previous_temp = globals.temp

        if arduino != None:
            shutter = 'open'
            arduino.arduino.write(shutter.encode())
            time.sleep(1.2)
            globals.shutter_state = 'open'
            print(globals.shutter_state)

        counter = 0

        wave = sineWave(set_point, amplitude, frequency)

        try:
            while True:
                if globals.shutter_state == 'open':

                    # print('we are here')
                    event1.wait()
                    # print('Minimum temperature: ' + str(globals.temp))

                    if counter == 0:

                        while globals.temp > (set_point + 0.4):
                            # print('waiting to start close-loop')
                            # print(type(set_point))
                            time.sleep(0.0001)

                            ## PID parameters
                        Kp = -1500
                        Ki = -100
                        Kd = -800
                        output_limits = (-3000, 3000)
                        range = 0.3

                        # we initialise PID object
                        PID = PYD(Kp, Ki, Kd, set_point)


                    if keyboard.is_pressed('c'):
                        shutter = 'close'
                        arduino.arduino.write(shutter.encode())

                        globals.shutter_state = 'close'
                        devices[2].device.move_abs(0)
                        devices[1].device.move_abs(0)
                        devices[0].device.move_abs(0)

                    zaber_pos = PID(globals.temp, osc = wave[counter])
                    print(wave[counter])
                    counter += 1

                    # print(zaber_pos)

                    devices[2].device.move_rel(int(zaber_pos))
                    pos = devices[2].device.send("/get pos")
                    pos = int(pos.data)
                    previous_temp = globals.temp
                    globals.posZ = pos

                elif globals.shutter_state == 'close':

                    continue

                previous_temp = globals.temp
                event1.clear()


        except KeyboardInterrupt:
            sys.exit(0)

    def testHeight(self, devices, steps):
        globals.pos = 0

        while globals.pos < 230000:

            time.sleep(0.01)
            devices[0].move(steps)
            pos = devices[0].device.send("/get pos")
            pos = int(pos.data)
            # print(pos)
            globals.pos = pos
            # print(globals.pos)
    def goStartingPosition(self, x_Spos, y_Spos, devices):
        devices[0].device.move_abs(x_Spos)
        devices[1].device.move_abs(y_Spos)


    def __repr__(self):

        return 'Device {} at port {}'.format(self.device, self.port)

################################################################################################################
################################################################################################################
############################ FUNCTIONS 
################################################################################################################
################################################################################################################

def grid_calculation(zaber, grid_separation, step_size = globals.step_sizes, pos = globals.positions, rule = globals.rules, dim = [3, 3]):
    """
        Function to estimate a grid from a point. The initial point becomes the centre cell.
        grid_separation in millimetres
    """
    if len(dim) < 2:
        raise Exception('dim should be of the form [x, y]')

    # print(pos)

    # step_size = step_size[zaber]

    one_cm_zaber_steps = grid_separation/(step_size[zaber]/1000)

    grid = {}

    #Calculate origin
    # print(revDirection(zaber, 'x', rule, one_cm_zaber_steps))
    x_origin = pos[zaber]['x'] - revDirection(zaber, 'x', rule, one_cm_zaber_steps)
    y_origin = pos[zaber]['y'] - revDirection(zaber, 'y', rule, one_cm_zaber_steps)

    if x_origin < 0 or y_origin < 0:
        x_origin = int(max(0, x_origin))
        y_origin = int(max(0, y_origin))
        print(f"Either X or Y were found to be negative values.\n They were set to 0, but the grid won't apply properly")

    # print(x_origin)
    # print(y_origin)
    cell = 0
    for i in np.arange(dim[1]):
        for j in np.arange(dim[0]):
            grid[cell] = { 'x': math.ceil(x_origin + revDirection(zaber, 'x', rule, one_cm_zaber_steps*j)), 'y': math.ceil(y_origin + revDirection(zaber, 'y', rule, one_cm_zaber_steps*i)), 'z': pos[zaber]['z']}
            # print(j, i)
            cell += 1

    print("Grid calculated")

    return grid


def manualorder(haxes):
    """
        Function to manually choose the order for homing and moving multiple Zabers
    """
    print(f'There are {len(haxes.keys())} set of zabers, their names are: ')
    list_keys = list(haxes.keys())

    for i, k in enumerate(list_keys):
        print(k + ' ({})'.format(i))

    pos_zabs = tuple(str(i) for i in range(0, len(list_keys)))
    # print(pos_zabs)

    nhaxes = {}
    temp_zabers = []

    for i in np.arange((len(list_keys))):
        temp_axes = []
        # Select the zaber
        if i == 0:
            while True:
                chosen = input("Which Zaber set should we move first?\n")
                if chosen in temp_zabers:
                    print(f'\n{chosen.upper()} has been selected already\n')
                
                elif chosen in pos_zabs:
                    break
                else:
                    print(f'Only {pos_zabs} are valid answers \n')
                    continue
        else:
            if len(list_keys) > 2:
                while True:
                    chosen = input("Which Zaber set should we move next?   ")
                    if chosen in temp_zabers:
                        print(f'{chosen} has been selected already \n')
                    
                    elif chosen in pos_zabs:
                        break
                    else:
                        print(f'Only {pos_zabs} are valid answers\n')
                        continue
            else:
                set_diff_za = set(list_keys) - set(temp_zabers)
                diff_za = list(set_diff_za)
                chosen = list_keys.index(diff_za[0])
                print(f"\n{list_keys[int(chosen)].upper()} was selected\n")
                # temp_zabers.append(chosen)

        temp_zabers.append(list_keys[int(chosen)])

        # Select 1st the axes
        while True:
            firstaxis = input("Which axis should move first? \n You probably want to choose then one that is above the rest, so they don't crash each other\n")
            if firstaxis in ('x', 'y', 'z'):
                if firstaxis == 'x' and list_keys[int(chosen)] == 'colther':
                    print("It is probably not a good idea to move the x axis of colther first\n ")
                    continue
                else:
                    break
            else:
                print(f"Only 'x', 'y' & 'z' are valid answers\n ")
                continue

        temp_axes.append(firstaxis)
        # Select 2nd the axes
        while True:
            secondaxis = input("Which axis should move next?    ")
            
            if firstaxis == secondaxis:
                print(f'{secondaxis} has already been selected \n')
                continue
            
            elif secondaxis in ('x', 'y', 'z'):
                break

            else:
                print(f"Only 'x', 'y' & 'z' are valid answers \n")
                continue
        
        temp_axes.append(secondaxis)

        set_diff = set(haxes[list_keys[int(chosen)]]) - set(temp_axes)
        diff = list(set_diff)
        temp_axes.append(diff[0])
        
        # put into haxes dictionary
        nhaxes[list_keys[int(chosen)]] = temp_axes
    
    return nhaxes

def revDirection(zaber, axis, rule, number):
    """
        Function to get the negative value of a number depending on zaber rules
    """
    if not rule[zaber][axis]:
        number = -number

    return number

def homingZabers(zabers, axes = None, speed = 153600):
    """
        This function is to home all zabers in a Zaber object
    """
    if axes == None:
        axes = {}
        for kzabers, vzabers in zabers.items():
            axes[kzabers] = ['x', 'y', 'z']
        print('\n Homing to default axes order [x, y, z] \n')

    speed = str(speed)
    # print(axes)
    for kaxes, vaxes in axes.items():
        for d in vaxes:
            print(f'\n Homing {d} axis of {kaxes}\n')
            try:
                zabers[kaxes][d].device.send('/set maxspeed {}'.format(speed))
                zabers[kaxes][d].device.home()  
            except:
                zabers[kaxes][d].send('/set maxspeed {}'.format(speed))
                zabers[kaxes][d].home()


def movetostartZabers(zabers, zaber, axes, pos = globals.positions, cond = None):
    # print(pos)

    for d in axes:
        print(f'\n Moving axis {d} of {zaber} to {pos[d]}')
        try:
            zabers[zaber][d].device.move_abs(pos[d])
        except:
            zabers[zaber][d].move_abs(pos[d])
        time.sleep(0.1)

def sineWave(set_point, amplitude, freq, phase = 0, repeats = 1):

    t = np.arange(0, repeats * 10, 0.01)
    w = 2 * math.pi * freq
    phi = phase # phase to change the phase of sine function

    A = ((set_point + amplitude/2) - (set_point - amplitude/2))/2
    wave = A * np.sin(w * t + phi) + ((set_point + amplitude/2) + (set_point - amplitude/2))/2

    # self.volt = np.tile(self.volt, repeats)
    # duration = int(1000 * repeats/globals.rate_NI) # duration of sound
    return wave


def zrabber(n_trail, port, low_temp):

    while True:
        device = zaberClass(n_trail, port)

        if globals.temp < low_temp:

            device.move(5000)  #negative is up

        # elif globals.temp > high_temp:
        #
        #     device.move(-5000) #positive is down
        else:
            device.move(-5000)
            continue

def read_reply(command):
        return ['Message type:  ' + command.message_type, 'Device address:  ' + str(command.device_address), 'Axis number:  ' + str(command.axis_number), 'Message ID:  ' + str(command.message_id), 'Reply flag:  ' + str(command.reply_flag), 'Device status:  ' + str(command.device_status), 'Warning flag:  ' + str(command.warning_flag), 'Data: ' + str(command.data), 'Checksum:  ' + str(command.checksum)]

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def lutsyringe(temp):
    near_zaber = find_nearest(y_vals_inter, temp)
    where_near_zaber = np.where(y_vals_inter == near_zaber)
    return zebers_inter[where_near_zaber[0][0]]

def set_up_big_three():

    ### Zabers
    colther1 = Zaber(1, who = 'serial')
    colther2 = Zaber(2, port = colther1, who = 'serial')
    colther3 = Zaber(3, port = colther1, who = 'serial')

    camera12 = Zaber(1, who = 'modem', usb_port = 2, n_modem = 1)
    camera1 = camera12.device.axis(1)
    camera2 = camera12.device.axis(2)
    camera3 = Zaber(2, port = camera12, who = 'modem', usb_port = 2, n_modem = 1)

    tactile12 = Zaber(1, who = 'modem', usb_port = 2, n_modem = 2)
    tactile1 = tactile12.device.axis(1)
    tactile2 = tactile12.device.axis(2)
    tactile3 = Zaber(2, port = tactile12, who = 'modem', usb_port = 2, n_modem = 2)

    colther = [colther3, colther2, colther1]
    camera = [camera3, camera2, camera1]
    tactile = [tactile3, tactile2, tactile1]

    zabers = {'colther': [colther3, colther2, colther1], 'camera': [camera3, camera1, camera2],
                'tactile': [tactile3, tactile1, tactile2]}

    return zabers


def set_up_one_zaber(name_dev, axes, who = 'serial', usb_port = None, n_modem = None, winPort = None):
    """
        name_dev: string name for your zaber, without spaces
        axes: name and order of axes
        This function is for setting up ONE zaber set-up with 3 linear stage actuators
    """
    ### Zabers
    try:
        if who == 'serial':
            zaber1 = Zaber(1, who, usb_port, n_modem, winPort = winPort)
            zaber2 = Zaber(2, port = zaber1, who = who, winPort = winPort)
            zaber3 = Zaber(3, port = zaber1, who = who, winPort = winPort)
            
        elif who == 'modem':
            zaber12 = Zaber(1, who, usb_port, n_modem)
            
            zaber1 = zaber12.device.axis(1)
            zaber2 = zaber12.device.axis(2)
            zaber3 = Zaber(2, port = zaber12, who = who, usb_port = usb_port, n_modem = n_modem)

        zabers = {'{}'.format(name_dev): {f'{axes[0]}': zaber1, f'{axes[1]}': zaber2, f'{axes[2]}': zaber3} }
    except Exception as e:
        errorloc(e)
    return zabers

################################################################################################################
################################################################################################################
############################ TRASH 
################################################################################################################
################################################################################################################

# def rampCold(self, amount, duration, devices, amplitude):
#
#     globals.trial = 'on'
#     globals.time_limit = duration
#     globals.shutter = 'open'
#
#     start = time.time()
#
#     while globals.distance > globals.distance_limit and globals.elapsed < globals.time_limit and globals.status == 'active' and globals.temp > 25:
#         startRamp = time.time()
#
#         while startRamp <= 1:
#
#             if globals.temp < globals.temp - amplitude:   #negative is up
#
#                 devices[2].device.move_rel(-amount)
#
#                 end = time.time()
#                 globals.elapsed = end - start
#
#             elif globals.temp > globals.temp + amplitude:
#
#                 devices[2].device.move_rel(amount)  #positive is down
#
#                 end = time.time()
#                 globals.elapsed = end - start
#
#         low_bound -= 0.3
#         high_bound -= 0.3
#
#
#
#     globals.status = 'inactive'
#     globals.shutter = 'close'
#
# def rampColdOpen(self, amount, devices):
#
#         globals.trial = 'on'
#         globals.shutter = 'open'
#
#         start = time.time()
#
#         sleep(2)
#
#         while globals.distance > globals.distance_limit and globals.status == 'active' and globals.temp > 0:
#
#             devices[2].device.move_rel(amount)  #positive is down
#             # print(globals.status)
#
#
#         globals.status = 'inactive'
#         globals.shutter = 'close'
#         # print('ramp dead')

# def plotLive(self, vminT, vmaxT):
#     import matplotlib as mpl
#     mpl.rc('image', cmap='hot')
#
#     global dev
#     global devh
#     global tiff_frame
#
#     # plt.ion()
#
#     fig = plt.figure()
#     ax = plt.axes()
#
#     fig.tight_layout()
#
#     dummy = np.zeros([120, 160])
#
#     img = ax.imshow(dummy, interpolation='nearest', vmin = vminT, vmax = vmaxT, animated = True)
#     fig.colorbar(img)
#
#     current_cmap = plt.cm.get_cmap()
#     current_cmap.set_bad(color='black')
#
#     try:
#         while True:
#             # time.sleep(0.01)
#             data = q.get(True, 500)
#             if data is None:
#                 print('Data is none')
#                 exit(1)
#
#             # We save the data
#             minimoK = np.min(data)
#             minimo = (minimoK - 27315) / 100
#             # print('Minimo: ' + str(minimo))
#             globals.temp = minimo
#
#             data = (data - 27315) / 100
#
#             # under_threshold_indices = data < 5
#             # data[under_threshold_indices] = np.nan
#             # super_threshold_indices = data > 60
#             # data[super_threshold_indices] = np.nan
#             # fig.clear()
#
#             # img.set_data(data)
#             ax.clear()
#             ax.set_xticks([])
#             ax.set_yticks([])
#
#             ax.spines['top'].set_visible(False)
#             ax.spines['right'].set_visible(False)
#             ax.spines['left'].set_visible(False)
#             ax.spines['bottom'].set_visible(False)
#             ax.imshow(data, vmin = vminT, vmax = vmaxT)
#             # print(data)
#             plt.pause(0.0005)
#
#             #
#             # if cv2.waitKey(1) & 0xFF == ord('e'):
#             #     cv2.destroyAllWindows()
#             #     frame = 1
#             #     print('We are done')
#             #     exit(1)
#
#             if cv2.waitKey(1) & keyboard.is_pressed('e'):
#                 cv2.destroyAllWindows()
#                 frame = 1
#                 # print('We are done')
#                 break
#
#     except:
#         pass
#     #     # print('Stop streaming')
#     #     libuvc.uvc_stop_streaming(devh)

# def rampColdStopFam(self, amount, duration, devices, amplitude):
#
#     globals.trial = 'on'
#     globals.time_limit = duration
#     globals.shutter = 'open'
#     globals.status = 'active'
#     globals.fam = 'solo'
#
#     start = time.time()
#     # First we ramp the temperature
#
#     while globals.distance > globals.distance_limit and globals.elapsed < globals.time_limit and globals.status == 'active' and globals.temp > 27:
#         startRamp = time.time()
#
#         while startRamp <= 1:
#
#             if globals.temp < globals.temp - amplitude:   #negative is up
#
#                 devices[2].device.move_rel(-amount)
#
#                 end = time.time()
#                 globals.elapsed = end - start
#
#             elif globals.temp > globals.temp + amplitude:
#
#                 devices[2].device.move_rel(amount)  #positive is down
#
#                 end = time.time()
#                 globals.elapsed = end - start
#
#         low_bound -= 0.3
#         high_bound -= 0.3
#
#     # Second we maintain the temperature
#     while globals.distance > globals.distance_limit and globals.elapsed < globals.time_limit:
#
#         if globals.status == 'active':
#
#                 if globals.temp < 27 - amplitude:   #negative is up
#
#                     devices[2].device.move_rel(-amount)
#
#                     end = time.time()
#                     globals.elapsed = end - start
#
#                 elif globals.temp > 27 + amplitude:
#
#                     devices[2].device.move_rel(amount)  #positive is down
#
#                     end = time.time()
#                     globals.elapsed = end - start
#
#                 elif keyboard.is_pressed('c'):
#                     globals.fam = 'tgi'
#
#         elif globals.status == 'inactive':
#             globals.shutter = 'close'
#             break

# %%

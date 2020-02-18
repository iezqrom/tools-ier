#!/usr/bin/env python3

#Time
from datetime import datetime
import time
from time import sleep
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

# Maths
import numpy as np
import pandas as pd
import curses
import math

from pyd import PYD
import struct

def homingZabers(zabers):
    for kzabers, vzabers in zabers.items():
        for d in vzabers:
            try:
                d.device.home()

            except:
                d.home()

def movetostartZabers(zabers, zaber, cond):
    poses = globals.positions[zaber][cond]


    if zaber == 'non_tactile':
        zaber = 'tactile'

    for d, p in zip(reversed(zabers[zaber]), poses):
        # print(d)
        # print(p)
        try:
            d.device.move_abs(p)
        except:
            d.move_abs(p)

def sineWave(set_point, amplitude, freq, phase = 0, repeats = 1):

    t = np.arange(0, repeats * 10, 0.01)
    w = 2 * math.pi * freq
    phi = phase # phase to change the phase of sine function

    A = ((set_point + amplitude/2) - (set_point - amplitude/2))/2
    wave = A * np.sin(w * t + phi) + ((set_point + amplitude/2) + (set_point - amplitude/2))/2

    # self.volt = np.tile(self.volt, repeats)
    # duration = int(1000 * repeats/globals.rate_NI) # duration of sound
    return wave

# wave = sineWave(27, 2, 0.15)
#
# # plt.plot(wave)

class Zaber(grabPorts):

    def __init__(self, n_device, who, usb_port = None, n_modem = None, winPort = None, port = None):
        self.ports = grabPorts()
        self.ports.zaberPort(who, usb_port, n_modem, winPort)

        if n_device == 1: # number 1 device is chosen to lead the Daisy chain
            self.port = zs.AsciiSerial(self.ports.zaber_port[0])
            self.device = zs.AsciiDevice(self.port, n_device)
        else:
            self.port = port
            self.device = zs.AsciiDevice(port.port, n_device)

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

    def manualCon(self, devices, amount, arduino = None):

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


    def manualConGUIsingle(self, devices, arduino = None):

        if arduino != None:
            stimulus = 0
            arduino.arduino.write(struct.pack('>B', stimulus))

        # self.spotsPosX = {'C1': [], 'C2': [], 'NonC': []}
        # self.spotsPosY = {'C1': [], 'C2': [], 'NonC': []}

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
                elif keyboard.is_pressed('enter'):
                    homingZabers(devices)
                    break

                # Press letter h and Zaber will home, first z axis, then y and finally x
                # Control

                elif keyboard.is_pressed('h'):
                    homingZabers(devices)

                else:
                    continue


        finally:
            if arduino != None:
                globals.shutter_state = 'close'
                arduino.arduino.write(globals.shutter_state.encode())


    def manualCon2(self, devices, amount, arduino = None):

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
            device = devices[globals.current_device]

            while True:
                event[0].wait()
                # print('MOVE ZABER')
                event[1].clear()

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
                elif keyboard.is_pressed('enter'):
                    homingZabers(devices)
                    break


                #### GET POSITION ZABER
                # Experimental
                elif keyboard.is_pressed('w'):
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

                elif keyboard.is_pressed('q'):
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

                    # print(globals.positions)

                # Press letter h and Zaber will home, first z axis, then y and finally x
                # Control

                elif keyboard.is_pressed('h'):
                    homingZabers(devices)


                #### Double

                elif keyboard.is_pressed('t'):
                    device = devices['tactile']
                    globals.current_device = 'tactile'
                    movetostartZabers(devices, 'tactile', 'experimental')

                elif keyboard.is_pressed('n'):
                    device = devices['tactile']
                    globals.current_device = 'tactile'
                    movetostartZabers(devices, 'tactile', 'control')

                else:
                    continue

                event[1].set()
                event[0].clear()

        finally:
            if arduino != None:
                globals.shutter_state = 'close'
                arduino.arduino.write(globals.shutter_state.encode())

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
            globals.shutter = 'close'
            arduino.arduino.write(globals.shutter.encode())
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
                elif keyboard.is_pressed('enter'):
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

                    # print(globals.positions)

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

                elif keyboard.is_pressed('t'):
                    device = devices['tactile']
                    globals.current_device = 'tactile'

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

    def ROIPID(self, device, set_point, event1, radio, arduino = None):

        previous_temp = globals.temp

        if arduino != None:
            globals.stimulus = 1
            arduino.arduino.write(struct.pack('>B', globals.stimulus))
            print('Shutter '+ globals.stimulus)

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

                        ## PID parameters
                        Kp = -1500
                        Ki = -100
                        Kd = -800
                        output_limits = (-3000, 3000)


                        # we initialise PID object
                        PID = PYD(Kp, Ki, Kd, set_point, output_limits)


                    zaber_pos = PID(globals.temp)

                    device[0].device.move_rel(int(zaber_pos))
                    pos = device[0].device.send("/get pos")
                    pos = int(pos.data)
                    previous_temp = globals.temp
                    globals.pos_zaber = pos

                elif globals.stimulus == 0:

                    continue

                previous_temp = globals.temp
                event1.clear()


        except KeyboardInterrupt:
            sys.exit(0)


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

############################################################################
################### FUNCTIONS ##############################################
############################################################################

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

############################################################################
################### TRASH ##################################################
############################################################################

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

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
import glob
import keyboard
import serial
try:
    import winsound
except:
    pass

# My stuff
try:
    import globals
except:
    pass
from grabPorts import grabPorts


# Maths
import numpy as np
import pandas as pd
import curses
import re
import struct


class ArdUIno(grabPorts):

    def __init__(self, winPort = None, num_ards = 1, usb_port = None, n_modem = None):

        self.ports = grabPorts()
        self.ports.arduinoPort(winPort, num_ards, usb_port, n_modem)
        print(self.ports)
        print('Arduino port: ')
        print(str(self.ports.arduino_ports))

        if num_ards == 1:
            try:
                self.arduino = serial.Serial(self.ports.arduino_ports[0], 9600, timeout = 5)
            except IndexError:
                print('I cannot find any arduino boards!')
        elif num_ards > 1:
            self.arduino1 = serial.Serial(self.ports.arduino_ports[0], 9600, timeout = 5)
            self.arduino2 = serial.Serial(self.ports.arduino_ports[1], 9600, timeout = 5)

    def readFloat(self, start, finish, globali, event):
        while True:
            read = self.arduino.readline()
            cropp = read[start:finish]
            # print(read)
            try:
                float_cropp = float(cropp)
                rounded_float_cropp = round(float_cropp, 3)

                globali.set(rounded_float_cropp)
            except Exception as e:
                print(e)

            if keyboard.is_pressed('enter'):
                event[0].set()
                break
            elif keyboard.is_pressed('l'):
                event[0].set()
                # print('Waiting for Zaber to move')
                event[1].wait()

    def OpenClose(self, wait_close, wait_open, devices = None):

        if devices != None:
            devices[0].device.move_abs(globals.posX)
            devices[1].device.move_abs(globals.posY)
            devices[2].device.move_abs(globals.posZ)

        while True:

            try:

                time.sleep(wait_close*1/10)

                globals.stimulus = 1
                self.arduino.write(struct.pack('>B', globals.stimulus))


                time.sleep(wait_open)

                globals.stimulus = 0
                self.arduino.write(struct.pack('>B', globals.stimulus))


                time.sleep(wait_close*9/10)

                globals.counter +=1

                if globals.counter == 3:
                    globals.stimulus = 0
                    self.arduino.write(struct.pack('>B', globals.stimulus))
                    break
                # if keyboard.is_pressed('e'):
                #
                #     globals.stimulus = 0
                #     self.arduino.write(struct.pack('>B', globals.stimulus))
                #     break

            except KeyboardInterrupt:
                sys.exit(1)

    def controlShu(self):

        while True:

            try:

                if keyboard.is_pressed('c'):
                    globals.stimulus = 0
                    self.arduino.write(struct.pack('>B', globals.stimulus))

                if keyboard.is_pressed('o'):
                    globals.stimulus = 1
                    self.arduino.write(struct.pack('>B', globals.stimulus))

                if keyboard.is_pressed('e'):

                    globals.stimulus = 0
                    self.arduino.write(struct.pack('>B', globals.stimulus))
                    break

            except KeyboardInterrupt:
                sys.exit(1)

    def OpenCloseMoF(self):

        time.sleep(1)

        globals.stimulus = 1
        self.arduino.write(struct.pack('>B', globals.stimulus))
        start = time.time()

        while True:
            time.sleep(0.001)
            if globals.stimulus == 0:
                globals.rt = time.time() - start
                self.arduino.write(struct.pack('>B', globals.stimulus))
                break

################################################################################
############################# FUNCTION #########################################
################################################################################

def shakeShutter(ard, times):
    for i in np.arange(times):
        globals.stimulus = 1
        ard.arduino.write(struct.pack('>B', globals.stimulus))
        # read = ard.arduino.readline()
        # print(read)
        print('Open shutter')

        time.sleep(0.3)

        globals.stimulus = 0
        ard.arduino.write(struct.pack('>B', globals.stimulus))
        # read = ard.arduino.readline()
        # print(read)
        print('Close shutter')
        time.sleep(0.3)


################ Developing Trash
# def ardRun(self, save = 'N', subjN = None, trial_counter = None):
#     # import time
#     self.arduino.flushInput()
#     counter = 0
#
#     temp_array = []
#     threshold = []
#     time_array = []
#
#     while globals.distance > globals.distance_limit and globals.trial == 'on':
#         if globals.status == 'active':
#
#             if counter == 0:
#
#                 # print('we are here')
#
#                 self.arduino.flushInput()
#
#                 shutter = 'open'
#
#                 sleep(2)
#
#                 self.arduino.write(shutter.encode())
#                 winsound.PlaySound('beep.wav', winsound.SND_ASYNC)
#                 counter += 1
#
#
#             else:
#
#                 sleep(0.0001)
#                 data = self.arduino.readline()
#                 # print('still readin arduino')
#                 sleep(0.0001)
#
#
#                 try:
#                     data = str(data)
#                     data = data[2:9]
#                     # print(data)
#                     var, value = data.split("_")
#                     # print("var: " + var)
#                     # print("value: " + value)
#
#                     if var == 't':
#                         # print('This is MAI temp: ' + value)
#                         value_t = float(value)
#                         globals.temp = value_t
#                         time = time.time()
#
#                         temp_array.append(globals.temp)
#                         threshold.append(globals.thres)
#                         time_array.append(time)
#
#
#                     elif var == 'd':
#                         # print('This is MAI distance: ' + value)
#                         value_d = float(value)
#                         globals.distance = value_d
#
#                 except:
#                     continue
#
#             if globals.status == 'inactive':
#                 # sleep(2)
#                 # print('killing')
#                 shutter = globals.shutter
#                 print(shutter)
#                 self.arduino.write(shutter.encode())
#
#                 if save == 'Y':
#                     dataFile = open('./data/subj_{}/trial_{}.csv'.format(subjN, trial_counter), 'a')
#                     data_writer = csv.writer(dataFile)
#
#                     for i in np.arange(len(temp_array)):
#                         data_writer.writerow(temp_array[i], threshold[i], time_array[i])
#                     dataFile.close()
#
#                 break
#
#
#         elif globals.status == 'inactive':
#             shutter = globals.shutter
#             self.arduino.write(shutter.encode())
#             # print('ard')
#             continue
#
#     globals.shutter = 'close'
#     shutter = globals.shutter
#     self.arduino.write(shutter.encode())
#     # print(globals.temp)
#     # print(globals.distance)
#     print('Arduino dead')
#
# def AllIn(self):
#
#     ports = grabPorts()
#     ports.arduinoPort()
#     arduino = serial.Serial(ports.arduino_port, 9600, timeout = 5)
#
#     time.sleep(0.01)
#     arduino.flush()
#
#     state = 'open'
#     arduino.write(state)
#     time.sleep(0.001)
#
#     while globals.status == None and globals.distance > globals.distance_limit and globals.elapsed < globals.time_limit:
#         data = arduino.readline()
#         time.sleep(0.0001)
#         # print(globals.status)
#         # print(globals.distance)
#         # print(globals.elapsed)
#
#         try:
#             data = str(data)
#             data = data[2:9]
#             # print(data)
#             var, value = data.split("_")
#             # print("var: " + var)
#             # print("value: " + value)
#
#             if var == 't':
#                 # print('This is MAI temp: ' + value)
#                 value_t = float(value)
#                 globals.temp = value_t
#
#
#             elif var == 'd':
#                 # print('This is MAI distance: ' + value)
#                 value_d = float(value)
#                 globals.distance = value_d
#
#         except:
#             continue
#
#     state = 'close'
#     arduino.write(state)
#     time.sleep(0.001)
#
# def writeString(self):
#
#     while True:
#
#         written = self.arduino.write(globals.meanStr.encode())
#         # print(written)
#
#         read = self.arduino.readline()
#         print(read)
#
#         if keyboard.is_pressed('e'):
#
#             break

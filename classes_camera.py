#!/usr/bin/env python3

### Data structure
from __future__ import print_function
from classes_arduino import ardUIno
import numpy as np
import ctypes
import struct
import h5py
import keyboard

## Maths
from scipy import optimize

## Media
import time
import cv2
from imutils.video import VideoStream
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import animation

## Comms
from uvctypes import *

from queue import Queue

import platform
# from pynput import keyboard
import os
import argparse
import imutils
import matplotlib as mpl

try:
    import globals
    # print(globals.shutter_state)
except:
    pass

def py_frame_callback(frame, userptr):

  array_pointer = cast(frame.contents.data, POINTER(c_uint16 * (frame.contents.width * frame.contents.height)))
  data = np.frombuffer(
    array_pointer.contents, dtype=np.dtype(np.uint16)
  ).reshape(
    frame.contents.height, frame.contents.width
  ) # no copy

  # data = np.fromiter(
  #   frame.contents.data, dtype=np.dtype(np.uint8), count=frame.contents.data_bytes
  # ).reshape(
  #   frame.contents.height, frame.contents.width, 2
  # ) # copy

  if frame.contents.data_bytes != (2 * frame.contents.width * frame.contents.height):
    return

  if not q.full():
    q.put(data)

def generate_colour_map():
    """
    Conversion of the colour map from GetThermal to a numpy LUT:
        https://github.com/groupgets/GetThermal/blob/bb467924750a686cc3930f7e3a253818b755a2c0/src/dataformatter.cpp#L6
    """

    lut = np.zeros((256, 1, 3), dtype=np.uint8)

    #colorMaps
    colormap_grayscale = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 15, 15, 15, 16, 16, 16, 17, 17, 17, 18, 18, 18, 19, 19, 19, 20, 20, 20, 21, 21, 21, 22, 22, 22, 23, 23, 23, 24, 24, 24, 25, 25, 25, 26, 26, 26, 27, 27, 27, 28, 28, 28, 29, 29, 29, 30, 30, 30, 31, 31, 31, 32, 32, 32, 33, 33, 33, 34, 34, 34, 35, 35, 35, 36, 36, 36, 37, 37, 37, 38, 38, 38, 39, 39, 39, 40, 40, 40, 41, 41, 41, 42, 42, 42, 43, 43, 43, 44, 44, 44, 45, 45, 45, 46, 46, 46, 47, 47, 47, 48, 48, 48, 49, 49, 49, 50, 50, 50, 51, 51, 51, 52, 52, 52, 53, 53, 53, 54, 54, 54, 55, 55, 55, 56, 56, 56, 57, 57, 57, 58, 58, 58, 59, 59, 59, 60, 60, 60, 61, 61, 61, 62, 62, 62, 63, 63, 63, 64, 64, 64, 65, 65, 65, 66, 66, 66, 67, 67, 67, 68, 68, 68, 69, 69, 69, 70, 70, 70, 71, 71, 71, 72, 72, 72, 73, 73, 73, 74, 74, 74, 75, 75, 75, 76, 76, 76, 77, 77, 77, 78, 78, 78, 79, 79, 79, 80, 80, 80, 81, 81, 81, 82, 82, 82, 83, 83, 83, 84, 84, 84, 85, 85, 85, 86, 86, 86, 87, 87, 87, 88, 88, 88, 89, 89, 89, 90, 90, 90, 91, 91, 91, 92, 92, 92, 93, 93, 93, 94, 94, 94, 95, 95, 95, 96, 96, 96, 97, 97, 97, 98, 98, 98, 99, 99, 99, 100, 100, 100, 101, 101, 101, 102, 102, 102, 103, 103, 103, 104, 104, 104, 105, 105, 105, 106, 106, 106, 107, 107, 107, 108, 108, 108, 109, 109, 109, 110, 110, 110, 111, 111, 111, 112, 112, 112, 113, 113, 113, 114, 114, 114, 115, 115, 115, 116, 116, 116, 117, 117, 117, 118, 118, 118, 119, 119, 119, 120, 120, 120, 121, 121, 121, 122, 122, 122, 123, 123, 123, 124, 124, 124, 125, 125, 125, 126, 126, 126, 127, 127, 127, 128, 128, 128, 129, 129, 129, 130, 130, 130, 131, 131, 131, 132, 132, 132, 133, 133, 133, 134, 134, 134, 135, 135, 135, 136, 136, 136, 137, 137, 137, 138, 138, 138, 139, 139, 139, 140, 140, 140, 141, 141, 141, 142, 142, 142, 143, 143, 143, 144, 144, 144, 145, 145, 145, 146, 146, 146, 147, 147, 147, 148, 148, 148, 149, 149, 149, 150, 150, 150, 151, 151, 151, 152, 152, 152, 153, 153, 153, 154, 154, 154, 155, 155, 155, 156, 156, 156, 157, 157, 157, 158, 158, 158, 159, 159, 159, 160, 160, 160, 161, 161, 161, 162, 162, 162, 163, 163, 163, 164, 164, 164, 165, 165, 165, 166, 166, 166, 167, 167, 167, 168, 168, 168, 169, 169, 169, 170, 170, 170, 171, 171, 171, 172, 172, 172, 173, 173, 173, 174, 174, 174, 175, 175, 175, 176, 176, 176, 177, 177, 177, 178, 178, 178, 179, 179, 179, 180, 180, 180, 181, 181, 181, 182, 182, 182, 183, 183, 183, 184, 184, 184, 185, 185, 185, 186, 186, 186, 187, 187, 187, 188, 188, 188, 189, 189, 189, 190, 190, 190, 191, 191, 191, 192, 192, 192, 193, 193, 193, 194, 194, 194, 195, 195, 195, 196, 196, 196, 197, 197, 197, 198, 198, 198, 199, 199, 199, 200, 200, 200, 201, 201, 201, 202, 202, 202, 203, 203, 203, 204, 204, 204, 205, 205, 205, 206, 206, 206, 207, 207, 207, 208, 208, 208, 209, 209, 209, 210, 210, 210, 211, 211, 211, 212, 212, 212, 213, 213, 213, 214, 214, 214, 215, 215, 215, 216, 216, 216, 217, 217, 217, 218, 218, 218, 219, 219, 219, 220, 220, 220, 221, 221, 221, 222, 222, 222, 223, 223, 223, 224, 224, 224, 225, 225, 225, 226, 226, 226, 227, 227, 227, 228, 228, 228, 229, 229, 229, 230, 230, 230, 231, 231, 231, 232, 232, 232, 233, 233, 233, 234, 234, 234, 235, 235, 235, 236, 236, 236, 237, 237, 237, 238, 238, 238, 239, 239, 239, 240, 240, 240, 241, 241, 241, 242, 242, 242, 243, 243, 243, 244, 244, 244, 245, 245, 245, 246, 246, 246, 247, 247, 247, 248, 248, 248, 249, 249, 249, 250, 250, 250, 251, 251, 251, 252, 252, 252, 253, 253, 253, 254, 254, 254, 255, 255, 255];

    colormap_rainbow = [1, 3, 74, 0, 3, 74, 0, 3, 75, 0, 3, 75, 0, 3, 76, 0, 3, 76, 0, 3, 77, 0, 3, 79, 0, 3, 82, 0, 5, 85, 0, 7, 88, 0, 10, 91, 0, 14, 94, 0, 19, 98, 0, 22, 100, 0, 25, 103, 0, 28, 106, 0, 32, 109, 0, 35, 112, 0, 38, 116, 0, 40, 119, 0, 42, 123, 0, 45, 128, 0, 49, 133, 0, 50, 134, 0, 51, 136, 0, 52, 137, 0, 53, 139, 0, 54, 142, 0, 55, 144, 0, 56, 145, 0, 58, 149, 0, 61, 154, 0, 63, 156, 0, 65, 159, 0, 66, 161, 0, 68, 164, 0, 69, 167, 0, 71, 170, 0, 73, 174, 0, 75, 179, 0, 76, 181, 0, 78, 184, 0, 79, 187, 0, 80, 188, 0, 81, 190, 0, 84, 194, 0, 87, 198, 0, 88, 200, 0, 90, 203, 0, 92, 205, 0, 94, 207, 0, 94, 208, 0, 95, 209, 0, 96, 210, 0, 97, 211, 0, 99, 214, 0, 102, 217, 0, 103, 218, 0, 104, 219, 0, 105, 220, 0, 107, 221, 0, 109, 223, 0, 111, 223, 0, 113, 223, 0, 115, 222, 0, 117, 221, 0, 118, 220, 1, 120, 219, 1, 122, 217, 2, 124, 216, 2, 126, 214, 3, 129, 212, 3, 131, 207, 4, 132, 205, 4, 133, 202, 4, 134, 197, 5, 136, 192, 6, 138, 185, 7, 141, 178, 8, 142, 172, 10, 144, 166, 10, 144, 162, 11, 145, 158, 12, 146, 153, 13, 147, 149, 15, 149, 140, 17, 151, 132, 22, 153, 120, 25, 154, 115, 28, 156, 109, 34, 158, 101, 40, 160, 94, 45, 162, 86, 51, 164, 79, 59, 167, 69, 67, 171, 60, 72, 173, 54, 78, 175, 48, 83, 177, 43, 89, 179, 39, 93, 181, 35, 98, 183, 31, 105, 185, 26, 109, 187, 23, 113, 188, 21, 118, 189, 19, 123, 191, 17, 128, 193, 14, 134, 195, 12, 138, 196, 10, 142, 197, 8, 146, 198, 6, 151, 200, 5, 155, 201, 4, 160, 203, 3, 164, 204, 2, 169, 205, 2, 173, 206, 1, 175, 207, 1, 178, 207, 1, 184, 208, 0, 190, 210, 0, 193, 211, 0, 196, 212, 0, 199, 212, 0, 202, 213, 1, 207, 214, 2, 212, 215, 3, 215, 214, 3, 218, 214, 3, 220, 213, 3, 222, 213, 4, 224, 212, 4, 225, 212, 5, 226, 212, 5, 229, 211, 5, 232, 211, 6, 232, 211, 6, 233, 211, 6, 234, 210, 6, 235, 210, 7, 236, 209, 7, 237, 208, 8, 239, 206, 8, 241, 204, 9, 242, 203, 9, 244, 202, 10, 244, 201, 10, 245, 200, 10, 245, 199, 11, 246, 198, 11, 247, 197, 12, 248, 194, 13, 249, 191, 14, 250, 189, 14, 251, 187, 15, 251, 185, 16, 252, 183, 17, 252, 178, 18, 253, 174, 19, 253, 171, 19, 254, 168, 20, 254, 165, 21, 254, 164, 21, 255, 163, 22, 255, 161, 22, 255, 159, 23, 255, 157, 23, 255, 155, 24, 255, 149, 25, 255, 143, 27, 255, 139, 28, 255, 135, 30, 255, 131, 31, 255, 127, 32, 255, 118, 34, 255, 110, 36, 255, 104, 37, 255, 101, 38, 255, 99, 39, 255, 93, 40, 255, 88, 42, 254, 82, 43, 254, 77, 45, 254, 69, 47, 254, 62, 49, 253, 57, 50, 253, 53, 52, 252, 49, 53, 252, 45, 55, 251, 39, 57, 251, 33, 59, 251, 32, 60, 251, 31, 60, 251, 30, 61, 251, 29, 61, 251, 28, 62, 250, 27, 63, 250, 27, 65, 249, 26, 66, 249, 26, 68, 248, 25, 70, 248, 24, 73, 247, 24, 75, 247, 25, 77, 247, 25, 79, 247, 26, 81, 247, 32, 83, 247, 35, 85, 247, 38, 86, 247, 42, 88, 247, 46, 90, 247, 50, 92, 248, 55, 94, 248, 59, 96, 248, 64, 98, 248, 72, 101, 249, 81, 104, 249, 87, 106, 250, 93, 108, 250, 95, 109, 250, 98, 110, 250, 100, 111, 251, 101, 112, 251, 102, 113, 251, 109, 117, 252, 116, 121, 252, 121, 123, 253, 126, 126, 253, 130, 128, 254, 135, 131, 254, 139, 133, 254, 144, 136, 254, 151, 140, 255, 158, 144, 255, 163, 146, 255, 168, 149, 255, 173, 152, 255, 176, 153, 255, 178, 155, 255, 184, 160, 255, 191, 165, 255, 195, 168, 255, 199, 172, 255, 203, 175, 255, 207, 179, 255, 211, 182, 255, 216, 185, 255, 218, 190, 255, 220, 196, 255, 222, 200, 255, 225, 202, 255, 227, 204, 255, 230, 206, 255, 233, 208]

    colourmap_ironblack = [
        255, 255, 255, 253, 253, 253, 251, 251, 251, 249, 249, 249, 247, 247,
        247, 245, 245, 245, 243, 243, 243, 241, 241, 241, 239, 239, 239, 237,
        237, 237, 235, 235, 235, 233, 233, 233, 231, 231, 231, 229, 229, 229,
        227, 227, 227, 225, 225, 225, 223, 223, 223, 221, 221, 221, 219, 219,
        219, 217, 217, 217, 215, 215, 215, 213, 213, 213, 211, 211, 211, 209,
        209, 209, 207, 207, 207, 205, 205, 205, 203, 203, 203, 201, 201, 201,
        199, 199, 199, 197, 197, 197, 195, 195, 195, 193, 193, 193, 191, 191,
        191, 189, 189, 189, 187, 187, 187, 185, 185, 185, 183, 183, 183, 181,
        181, 181, 179, 179, 179, 177, 177, 177, 175, 175, 175, 173, 173, 173,
        171, 171, 171, 169, 169, 169, 167, 167, 167, 165, 165, 165, 163, 163,
        163, 161, 161, 161, 159, 159, 159, 157, 157, 157, 155, 155, 155, 153,
        153, 153, 151, 151, 151, 149, 149, 149, 147, 147, 147, 145, 145, 145,
        143, 143, 143, 141, 141, 141, 139, 139, 139, 137, 137, 137, 135, 135,
        135, 133, 133, 133, 131, 131, 131, 129, 129, 129, 126, 126, 126, 124,
        124, 124, 122, 122, 122, 120, 120, 120, 118, 118, 118, 116, 116, 116,
        114, 114, 114, 112, 112, 112, 110, 110, 110, 108, 108, 108, 106, 106,
        106, 104, 104, 104, 102, 102, 102, 100, 100, 100, 98, 98, 98, 96, 96,
        96, 94, 94, 94, 92, 92, 92, 90, 90, 90, 88, 88, 88, 86, 86, 86, 84, 84,
        84, 82, 82, 82, 80, 80, 80, 78, 78, 78, 76, 76, 76, 74, 74, 74, 72, 72,
        72, 70, 70, 70, 68, 68, 68, 66, 66, 66, 64, 64, 64, 62, 62, 62, 60, 60,
        60, 58, 58, 58, 56, 56, 56, 54, 54, 54, 52, 52, 52, 50, 50, 50, 48, 48,
        48, 46, 46, 46, 44, 44, 44, 42, 42, 42, 40, 40, 40, 38, 38, 38, 36, 36,
        36, 34, 34, 34, 32, 32, 32, 30, 30, 30, 28, 28, 28, 26, 26, 26, 24, 24,
        24, 22, 22, 22, 20, 20, 20, 18, 18, 18, 16, 16, 16, 14, 14, 14, 12, 12,
        12, 10, 10, 10, 8, 8, 8, 6, 6, 6, 4, 4, 4, 2, 2, 2, 0, 0, 0, 0, 0, 9,
        2, 0, 16, 4, 0, 24, 6, 0, 31, 8, 0, 38, 10, 0, 45, 12, 0, 53, 14, 0,
        60, 17, 0, 67, 19, 0, 74, 21, 0, 82, 23, 0, 89, 25, 0, 96, 27, 0, 103,
        29, 0, 111, 31, 0, 118, 36, 0, 120, 41, 0, 121, 46, 0, 122, 51, 0, 123,
        56, 0, 124, 61, 0, 125, 66, 0, 126, 71, 0, 127, 76, 1, 128, 81, 1, 129,
        86, 1, 130, 91, 1, 131, 96, 1, 132, 101, 1, 133, 106, 1, 134, 111, 1,
        135, 116, 1, 136, 121, 1, 136, 125, 2, 137, 130, 2, 137, 135, 3, 137,
        139, 3, 138, 144, 3, 138, 149, 4, 138, 153, 4, 139, 158, 5, 139, 163,
        5, 139, 167, 5, 140, 172, 6, 140, 177, 6, 140, 181, 7, 141, 186, 7,
        141, 189, 10, 137, 191, 13, 132, 194, 16, 127, 196, 19, 121, 198, 22,
        116, 200, 25, 111, 203, 28, 106, 205, 31, 101, 207, 34, 95, 209, 37,
        90, 212, 40, 85, 214, 43, 80, 216, 46, 75, 218, 49, 69, 221, 52, 64,
        223, 55, 59, 224, 57, 49, 225, 60, 47, 226, 64, 44, 227, 67, 42, 228,
        71, 39, 229, 74, 37, 230, 78, 34, 231, 81, 32, 231, 85, 29, 232, 88,
        27, 233, 92, 24, 234, 95, 22, 235, 99, 19, 236, 102, 17, 237, 106, 14,
        238, 109, 12, 239, 112, 12, 240, 116, 12, 240, 119, 12, 241, 123, 12,
        241, 127, 12, 242, 130, 12, 242, 134, 12, 243, 138, 12, 243, 141, 13,
        244, 145, 13, 244, 149, 13, 245, 152, 13, 245, 156, 13, 246, 160, 13,
        246, 163, 13, 247, 167, 13, 247, 171, 13, 248, 175, 14, 248, 178, 15,
        249, 182, 16, 249, 185, 18, 250, 189, 19, 250, 192, 20, 251, 196, 21,
        251, 199, 22, 252, 203, 23, 252, 206, 24, 253, 210, 25, 253, 213, 27,
        254, 217, 28, 254, 220, 29, 255, 224, 30, 255, 227, 39, 255, 229, 53,
        255, 231, 67, 255, 233, 81, 255, 234, 95, 255, 236, 109, 255, 238, 123,
        255, 240, 137, 255, 242, 151, 255, 244, 165, 255, 246, 179, 255, 248,
        193, 255, 249, 207, 255, 251, 221, 255, 253, 235, 255, 255, 24]

    def chunk(
            ulist, step): return map(
        lambda i: ulist[i: i + step],
        range(0, len(ulist),
               step))
    if (colorMapType == 1):
        chunks = chunk(colormap_rainbow, 3)
    elif (colorMapType == 2):
        chunks = chunk(colormap_grayscale, 3)
    else:
        chunks = chunk(colourmap_ironblack, 3)

    red = []
    green = []
    blue = []

    for chunk in chunks:
        red.append(chunk[0])
        green.append(chunk[1])
        blue.append(chunk[2])

    lut[:, 0, 0] = blue

    lut[:, 0, 1] = green

    lut[:, 0, 2] = red

    return lut

def ktoc(val):
  return (val - 27315) / 100.0

def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2BGR)

def rawToC(kel):
    celsius = round(((kel - 27315) / 100.0), 2)
    return celsius

def CToRaw(cel):
    kel = cel * 100 + 27315
    return kel

def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    X, Y = np.indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = np.sqrt(np.abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = np.sqrt(np.abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y

def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    params = moments(data)
    errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) -
                                 data)
    p, success = optimize.leastsq(errorfunction, params)
    return p

def gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height*np.exp(
                -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

BUF_SIZE = 2
q = Queue(BUF_SIZE)
PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(py_frame_callback)
tiff_frame = 1
colorMapType = 0

class TherCam(object):

    def __init__(self):
        pass

    def startStream(self):
      global devh
      global dev
      ctx = POINTER(uvc_context)()
      dev = POINTER(uvc_device)()
      devh = POINTER(uvc_device_handle)()
      ctrl = uvc_stream_ctrl()

      res = libuvc.uvc_init(byref(ctx), 0)
      # print(res)
      if res < 0:
        print("uvc_init error")
        #exit(1)

      try:
        res = libuvc.uvc_find_device(ctx, byref(dev), PT_USB_VID, PT_USB_PID, 0)
        if res < 0:
          print("uvc_find_device error")
          exit(1)

        try:
          res = libuvc.uvc_open(dev, byref(devh))
          if res < 0:
            print("uvc_open error")
            exit(1)

          print("device opened!")

          print_device_info(devh)
          print_device_formats(devh)

          frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
          if len(frame_formats) == 0:
            print("device does not support Y16")
            exit(1)

          libuvc.uvc_get_stream_ctrl_format_size(devh, byref(ctrl), UVC_FRAME_FORMAT_Y16,
            frame_formats[0].wWidth, frame_formats[0].wHeight, int(1e7 / frame_formats[0].dwDefaultFrameInterval)
          )

          res = libuvc.uvc_start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
          if res < 0:
            print("uvc_start_streaming failed: {0}".format(res))
            exit(1)

          print("done starting stream, displaying settings")
          print_shutter_info(devh)
          print("resetting settings to default")
          set_auto_ffc(devh)
          set_gain_high(devh)
          print("current settings")
          print_shutter_info(devh)

        except:
          libuvc.uvc_unref_device(dev)
          print('Failed to Open Device')
          exit(1)
      except:
        libuvc.uvc_exit(ctx)
        print('Failed to Find Device')
        exit(1)

    def saveThermalFilm(self, output):
        global dev
        global devh
        frame_width = 640
        frame_height = 480
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        writer = cv2.VideoWriter('{}.avi'.format(output), fourcc, 9, (frame_width, frame_height), True)

        try:
            while True:
                data = q.get(True, 500)
                if data is None:
                    break
                data = cv2.resize(data[:,:], (640, 480))

                # img = raw_to_8bit(data)
                img = cv2.LUT(raw_to_8bit(data), generate_colour_map())
               # img = cv2.LUT(raw_to_8bit(data), generate_colour_map())

                writer.write(img)
                cv2.imshow('Lepton Radiometry', img)
                # Press Q on keyboard to stop recording
                if cv2.waitKey(1) & 0xFF == ord('q'):
                  # When everything done, release the video capture and video write objects

                    writer.release()
                    # Closes all the frames
                    cv2.destroyAllWindows()
                    exit(1)

        finally:
            libuvc.uvc_stop_streaming(devh)

    def saveRawData(self, output, vminT, vmaxT):
        global dev
        global devh
        global tiff_frame
        f = h5py.File("./{}.hdf5".format(output), "w")

        import matplotlib as mpl
        mpl.rc('image', cmap='hot')

        fig = plt.figure()
        ax = plt.axes()

        fig.tight_layout()

        dummy = np.zeros([120, 160])

        img = ax.imshow(dummy, interpolation='nearest', vmin = vminT, vmax = vmaxT, animated = True)
        fig.colorbar(img)

        current_cmap = plt.cm.get_cmap()
        current_cmap.set_bad(color='black')

        try:
            while True:
                data = q.get(True, 500)
                if data is None:
                    print('Data is none')
                    exit(1)

                data = (data - 27315) / 100

                f.create_dataset(('image'+str(tiff_frame)), data=data)
                tiff_frame += 1

                under_threshold_indices = data < 5
                data[under_threshold_indices] = np.nan
                super_threshold_indices = data > 60
                data[super_threshold_indices] = np.nan
                # fig.clear()

                # img.set_data(data)
                ax.clear()
                ax.set_xticks([])
                ax.set_yticks([])

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.imshow(data, vmin = vminT, vmax = vmaxT)
                # print(data)
                plt.pause(0.0005)

                if keyboard.is_pressed('e'):
                    print('We are done')
                    f.close()
                    exit(1)

        finally:
            libuvc.uvc_stop_streaming(devh)

    def justStream(self):
        global dev
        global devh
        frame_width = 640
        frame_height = 480

        try:
            while True:
                # print('hola')
                data = q.get(True, 500)
                # print('adios')
                if data is None:
                    break
                data = cv2.resize(data[:,:], (640, 480))

                # img = raw_to_8bit(data)
                img = cv2.LUT(raw_to_8bit(data), generate_colour_map())
                # print(img)
               # img = cv2.LUT(raw_to_8bit(data), generate_colour_map())


                cv2.imshow('Just streaming thermal video...', img)
                # Press Q on keyboard to stop recording
                if cv2.waitKey(1) & 0xFF == ord('q'):
                  # When everything done, release the video capture and video write objects

                    # Closes all the frames
                    cv2.destroyAllWindows()
                    exit(1)

        finally:
            libuvc.uvc_stop_streaming(devh)

    def thresStream(self):
        global dev
        global devh
        frame_width = 640
        frame_height = 480

        try:
            while True:
                data = q.get(True, 500)
                if data is None:
                    break


                data = cv2.resize(data[:,:], (640, 480))

                # img = raw_to_8bit(data)
                img = cv2.LUT(raw_to_8bit(data), generate_colour_map())
                print(img)
               # img = cv2.LUT(raw_to_8bit(data), generate_colour_map())


                cv2.imshow('Just streaming thermal video...', img)
                # Press Q on keyboard to stop recording
                if cv2.waitKey(1) & 0xFF == ord('q'):
                  # When everything done, release the video capture and video write objects

                    # Closes all the frames
                    cv2.destroyAllWindows()
                    exit(1)

        finally:
            libuvc.uvc_stop_streaming(devh)

    def saveShutter(self, output):
        global dev
        global devh
        global tiff_frame
        f = h5py.File("./{}.hdf5".format(output), "w")

        try:
            while True:
                # time.sleep(0.01)
                data = q.get(True, 500)
                if data is None:
                    print('Data is none')
                    break

                # We save the data
                # print(type(data))

                f.create_dataset(('image'+str(tiff_frame)+'_'+str(globals.shutter_state)), data = data)
                print(globals.shutter_state)
                tiff_frame += 1
                # globals.counter += 1

                # We display the thermal image
                # data = cv2.resize(data[:,:], (640, 480))
                #
                # img = cv2.LUT(raw_to_8bit(data), generate_colour_map())

                # cv2.imshow('Lepton Radiometry', img)

                if keyboard.is_pressed('e'):  # globals.counter > globals.limit_counter:
                    #Close file in which we are saving the stuff
                    print('We are done')
                    # globals.counter = globals.limit_counter
                    f.close()
                    break

        finally:
            # print('Stop streaming')
            libuvc.uvc_stop_streaming(devh)

    def savePosMinShu(self, output, event1 = None):
        global dev
        global devh
        global tiff_frame
        import matplotlib as mpl
        f = h5py.File("./{}.hdf5".format(output), "w")

        # mpl.rc('image', cmap='hot')
        # fig = plt.figure()
        # ax1 = fig.add_subplot(111)
        # fig.tight_layout()
        # dummy = np.zeros([120, 160])
        # img1 = ax1.imshow(dummy, interpolation='nearest', vmin = 5, vmax = 40, animated = True)
        # fig.colorbar(img1)
        # current_cmap = plt.cm.get_cmap()

        try:
            # start = time.time()
            print('start')
            while True:
                # time.sleep(0.01)
                data = q.get(True, 500)
                if data is None:
                    print('Data is none')
                    break

                # We save the data
                minimoK = np.min(data)
                minimo = (minimoK - 27315) / 100
                print('Minimo: ' + str(minimo))
                globals.temp = minimo
                # print(globals.shutter_state)

                if globals.shutter_state == 'open':
                    # print(event1)
                    event1.set()

                posss = np.repeat(globals.posZ, len(data[0]))
                data_p = np.append(data, [posss], axis = 0)

                if globals.shutter_state == 'open':
                    shutter = np.repeat(1, len(data[0]))
                    data_pp = np.append(data_p, [shutter], axis = 0)

                elif globals.shutter_state == 'close':
                    shutter = np.repeat(0, len(data[0]))
                    data_pp = np.append(data_p, [shutter], axis = 0)


                f.create_dataset(('image'+str(tiff_frame)), data = data_pp)
                tiff_frame += 1

                # ax1.clear()
                #
                # ax1.imshow(data)
                # plt.pause(0.0005)


                if keyboard.is_pressed('e'):  # globals.counter > globals.limit_counter:
                    #Close file in which we are saving the stuff
                    print('We are done')
                    end = time.time()
                    print(end - start)
                    # globals.counter = globals.limit_counter
                    f.close()
                    break

        finally:
            print('Stop streaming')
            libuvc.uvc_stop_streaming(devh)

    def savePosMeanShu(self, output, r, event1 = None):
        global dev
        global devh
        global tiff_frame
        import matplotlib as mpl
        f = h5py.File("./{}.hdf5".format(output), "w")

        try:
            # start = time.time()
            print('start')
            while True:
                # time.sleep(0.01)
                data = q.get(True, 500)
                if data is None:
                    print('Data is none')
                    break

                # We save the data
                minimoK = np.min(data)
                minimoC = (minimoK - 27315) / 100
                dataC = (data - 27315) / 100

                xs = np.arange(0, 160)
                ys = np.arange(0, 120)

                indx, indy = np.where(dataC == minimoC)

                mask = (xs[np.newaxis,:]-indy[0])**2 + (ys[:,np.newaxis]-indx[0])**2 < r**2
                roiC = dataC[mask]
                globals.temp = round(np.mean(roiC), 2)
                print('Mean:' + str(round(np.mean(globals.temp), 2)))

                if globals.shutter_state == 'open':

                    event1.set()

                posss = np.repeat(globals.posZ, len(data[0]))
                data_p = np.append(data, [posss], axis = 0)

                if globals.shutter_state == 'open':
                    shutter = np.repeat(1, len(data[0]))
                    data_pp = np.append(data_p, [shutter], axis = 0)

                elif globals.shutter_state == 'close':
                    shutter = np.repeat(0, len(data[0]))
                    data_pp = np.append(data_p, [shutter], axis = 0)


                f.create_dataset(('image'+str(tiff_frame)), data = data_pp)
                tiff_frame += 1

                if keyboard.is_pressed('e'):  # globals.counter > globals.limit_counter:
                    #Close file in which we are saving the stuff
                    print('We are done')

                    f.close()
                    break

        finally:
            print('Stop streaming')
            libuvc.uvc_stop_streaming(devh)

    def savePosMeanShuFix(self, output, r, event1 = None):
        global dev
        global devh
        global tiff_frame
        import matplotlib as mpl
        f = h5py.File("./{}.hdf5".format(output), "w")

        try:
            # start = time.time()
            print('start')
            print(globals.indx_saved, globals.indy_saved)
            while True:
                # time.sleep(0.01)
                dataK = q.get(True, 500)
                if dataK is None:
                    print('Data is none')
                    break

                # We save the data
                # minimoK = np.min(dataK)
                # minimoC = (minimoK - 27315) / 100
                dataC = (dataK - 27315) / 100

                xs = np.arange(0, 160)
                ys = np.arange(0, 120)

                indx, indy = globals.indx_saved, globals.indy_saved

                mask = (xs[np.newaxis,:]-indy)**2 + (ys[:,np.newaxis]-indx)**2 < r**2
                roiC = dataC[mask]
                globals.temp = round(np.mean(roiC), 2)
                print('Mean:' + str(round(np.mean(globals.temp), 2)))

                if globals.shutter_state == 'open':

                    event1.set()

                posss = np.repeat(globals.posZ, len(dataC[0]))
                data_p = np.append(dataC, [posss], axis = 0)

                if globals.shutter_state == 'open':
                    shutter = np.repeat(1, len(dataC[0]))
                    data_pp = np.append(data_p, [shutter], axis = 0)

                elif globals.shutter_state == 'close':
                    shutter = np.repeat(0, len(dataC[0]))
                    data_pp = np.append(data_p, [shutter], axis = 0)

                coor = np.repeat([indx, indy], len(dataC[0]))
                data_ppp = np.append(data_pp, [coor], axis = 0)

                f.create_dataset(('image'+str(tiff_frame)), data = data_ppp)
                tiff_frame += 1

                if keyboard.is_pressed('e'):
                    #Close file in which we are saving the stuff
                    print('We are done')

                    f.close()
                    break

        finally:
            print('Stop streaming')
            libuvc.uvc_stop_streaming(devh)


    def plotLive(self, vminT, vmaxT):
        import matplotlib as mpl
        mpl.rc('image', cmap='hot')

        global dev
        global devh
        global tiff_frame

        # plt.ion()

        fig = plt.figure()
        ax = plt.axes()

        fig.tight_layout()

        dummy = np.zeros([120, 160])

        img = ax.imshow(dummy, interpolation='nearest', vmin = vminT, vmax = vmaxT, animated = True)
        fig.colorbar(img)

        current_cmap = plt.cm.get_cmap()
        current_cmap.set_bad(color='black')

        try:
            while True:
                # time.sleep(0.01)
                data = q.get(True, 500)
                if data is None:
                    print('Data is none')
                    exit(1)

                # We save the data
                minimoK = np.min(data)
                minimo = (minimoK - 27315) / 100
                # print('Minimo: ' + str(minimo))
                globals.temp = minimo

                data = (data - 27315) / 100

                # under_threshold_indices = data < 5
                # data[under_threshold_indices] = np.nan
                # super_threshold_indices = data > 60
                # data[super_threshold_indices] = np.nan
                # fig.clear()

                # img.set_data(data)
                ax.clear()
                ax.set_xticks([])
                ax.set_yticks([])

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.imshow(data, vmin = vminT, vmax = vmaxT)
                # print(data)
                plt.pause(0.0005)

                #
                # if cv2.waitKey(1) & 0xFF == ord('e'):
                #     cv2.destroyAllWindows()
                #     frame = 1
                #     print('We are done')
                #     exit(1)

                if cv2.waitKey(1) & keyboard.is_pressed('e'):
                    cv2.destroyAllWindows()
                    frame = 1
                    # print('We are done')
                    break

        except:
            pass
        #     # print('Stop streaming')
        #     libuvc.uvc_stop_streaming(devh)

    def plotLiveROI(self, vminT, vmaxT):
        import matplotlib as mpl
        mpl.rc('image', cmap='hot')

        global dev
        global devh
        global tiff_frame

        # plt.ion()

        fig = plt.figure()
        ax = plt.axes()

        fig.tight_layout()

        dummy = np.zeros([120, 160])

        img = ax.imshow(dummy, interpolation='nearest', vmin = vminT, vmax = vmaxT, animated = True)
        fig.colorbar(img)

        try:
            while True:
                # time.sleep(0.01)
                dataK = q.get(True, 500)
                if dataK is None:
                    print('Data is none')
                    exit(1)

                # We save the data
                minimoK = np.min(dataK)
                minimoC = (minimoK - 27315) / 100

                globals.temp = minimoC
                dataC = (dataK - 27315) / 100

                r = 20

                xs = np.arange(0, 160)
                ys = np.arange(0, 120)

                indx, indy = np.where(dataC == minimoC)

                mask = (xs[np.newaxis,:]-indy[0])**2 + (ys[:,np.newaxis]-indx[0])**2 < r**2
                roiC = dataC[mask]
                mean = round(np.mean(roiC), 2)

                circles = []

                for a, j in zip(indx, indy):
                    cirD = plt.Circle((j, a), r, color='b', fill = False)
                    circles.append(cirD)

                globals.indx0, globals.indy0  = indx[0], indy[0]

                ax.clear()
                ax.set_xticks([])
                ax.set_yticks([])

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.imshow(dataC, vmin = vminT, vmax = vmaxT)
                ax.add_artist(circles[0])
                # print(data)
                plt.pause(0.0005)

                if cv2.waitKey(1) & keyboard.is_pressed('e'):
                    cv2.destroyAllWindows()
                    frame = 1
                    # print('We are done')
                    break
        except Exception as e:
            print(e)
            # pass

    def LivePlotKernel(self, event1):

        global dev
        global devh
        global tiff_frame

        import matplotlib as mpl
        mpl.rc('image', cmap='hot')

        fig = plt.figure()

        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        fig.tight_layout()

        dummy = np.zeros([120, 160])

        img1 = ax1.imshow(dummy, interpolation='nearest', vmin = 5, vmax = 40, animated = True)
        img2 = ax1.imshow(dummy, interpolation='nearest', vmin = 5, vmax = 40, animated = True)

        fig.colorbar(img1)
        fig.colorbar(img2)

        current_cmap = plt.cm.get_cmap()
        current_cmap.set_bad(color='black')
        counter = 0

        try:
            while True:
                # time.sleep(0.01)
                data = q.get(True, 500)
                if data is None:
                    print('Data is none')
                    exit(1)

                data = (data - 27315) / 100

                under_threshold_indices = data < 18
                super_threshold_indices = data > 60

                maxC = 35
                data_absed = abs(data - maxC)

                data_absed[under_threshold_indices] = 0
                data_absed[super_threshold_indices] = 0

                Xin, Yin = np.mgrid[0:120, 0:160]
                paramsGau = moments(data_absed)
                dataGau = gaussian(*paramsGau)(Xin, Yin)
                event1.set()

                peak = paramsGau[0]
                peak =  maxC + 0 - peak
                globals.temp = peak
                print('Peak:  ' + str(round(peak)))
                # print('rolling')
                #
                ax1.clear()
                ax2.clear()

                # Raw Data

                ax1.set_xticks([])
                ax1.set_yticks([])

                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)
                ax1.spines['left'].set_visible(False)
                ax1.spines['bottom'].set_visible(False)
                ax1.imshow(data)
                plt.pause(0.0005)

                # Gaussian Kernel

                ax2.set_xticks([])
                ax2.set_yticks([])

                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_visible(False)
                ax2.spines['left'].set_visible(False)
                ax2.spines['bottom'].set_visible(False)
                ax2.imshow(dataGau)
                ### ax2.text(50, 10, 24, peak, color='black', fontsize = 12, weight = 'bold')
                plt.pause(0.0005)
                counter += 1
                event1.clear()

                if keyboard.is_pressed('e'):

                    print('We are done')
                    exit(1)

        finally:
            print('Stop streaming')
            libuvc.uvc_stop_streaming(devh)

    def testSkinWarm(self, output, vminT, vmaxT, r):
        global tiff_frame

        f = h5py.File("./{}.hdf5".format(output), "w")

        mpl.rc('image', cmap='hot')

        fig = plt.figure()
        ax = plt.axes()

        fig.tight_layout()

        xs = np.arange(0, 160)
        ys = np.arange(0, 120)

        dummy = np.zeros([120, 160])

        img = ax.imshow(dummy, interpolation='nearest', vmin = vminT, vmax = vmaxT, animated = True)
        fig.colorbar(img)

        try:
            while True:
                dataK = q.get(True, 500)
                if dataK is None:
                    print('Data is none')
                    exit(1)

                dataC = (dataK - 27315) / 100

                maxC = np.max(dataC)
                indx, indy = np.where(dataC == maxC)

                mask = (xs[np.newaxis,:]-indy[0])**2 + (ys[:,np.newaxis]-indx[0])**2 < r**2
                roiC = dataC[mask]
                meanC = round(np.mean(roiC), 2)
                # print(meanC)

                f.create_dataset(('image'+str(tiff_frame)), data=dataC)
                tiff_frame += 1

                ax.clear()
                ax.set_xticks([])
                ax.set_yticks([])

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.imshow(dataC, vmin = vminT, vmax = vmaxT)

                plt.pause(0.0005)

                # print(int(meanC * 100))

                globals.meanStr = str(int(meanC*100)) + '\n'
                # print(globals.meanStr)

                if keyboard.is_pressed('e'):
                    print('We are done')
                    f.close()
                    exit(1)

        finally:
            libuvc.uvc_stop_streaming(devh)

    def testSkinCold(self, output, vminT, vmaxT, r):
        global dev
        global devh
        global tiff_frame
        import matplotlib as mpl
        mpl.rc('image', cmap='hot')

        f = h5py.File("./{}.hdf5".format(output), "w")

        # fig = plt.figure()
        # ax = plt.axes()
        #
        # fig.tight_layout()
        #
        xs = np.arange(0, 160)
        ys = np.arange(0, 120)
        #
        # dummy = np.zeros([120, 160])
        #
        # img = ax.imshow(dummy, interpolation='nearest', vmin = vminT, vmax = vmaxT, animated = True)
        # fig.colorbar(img)

        try:
            print(globals.indx_saved, globals.indy_saved)
            while True:
                dataK = q.get(True, 500)
                if dataK is None:
                    print('Data is none')
                    exit(1)

                dataC = (dataK - 27315) / 100

                # maxC = np.max(dataC)
                indx, indy = globals.indx_saved, globals.indy_saved

                mask = (xs[np.newaxis,:]-indy)**2 + (ys[:,np.newaxis]-indx)**2 < r**2
                roiC = dataC[mask]
                meanC = round(np.mean(roiC), 2)
                # print(meanC)

                f.create_dataset(('image'+str(tiff_frame)), data=dataC)
                tiff_frame += 1

                # ax.clear()
                # ax.set_xticks([])
                # ax.set_yticks([])
                #
                # ax.spines['top'].set_visible(False)
                # ax.spines['right'].set_visible(False)
                # ax.spines['left'].set_visible(False)
                # ax.spines['bottom'].set_visible(False)
                # ax.imshow(dataC, vmin = vminT, vmax = vmaxT)

                # plt.pause(0.0005)

                # print(int(meanC * 100))

                if meanC > 29.00:
                    globals.meanStr = "open"
                elif meanC < 27.00:
                    globals.meanStr = "close"

                # print(globals.meanStr)
                print(meanC)

                if keyboard.is_pressed('e'):
                    print('We are done')
                    f.close()
                    exit(1)

        finally:
            libuvc.uvc_stop_streaming(devh)


frame = 1

class ReAnRaw(object):

    def __init__(self, input):
        self.read = h5py.File('{}.hdf5'.format(input), 'r')

    def play(self, solo = 'Y'):
        #This method plays the rawdata as a video
        global frame
        for i in np.arange(len(self.read.keys())):
            # print(frame)
            if solo == 'Y':
                data = self.read['image'+str(frame)][:]
                data = data[0:120]
                print(data)
            else:
                try:
                    data = self.read['image'+str(frame)+'_open'][:]
                except KeyError:
                    data = self.read['image'+str(frame)+'_close'][:]

            # data = cv2.resize(data[:,:], (480, 640))
            img = cv2.LUT(raw_to_8bit(data), generate_colour_map())
            # rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.imshow('Playing video', img)

            frame += 1
            time.sleep(0.1)

            if cv2.waitKey(9) & keyboard.is_pressed('e') & frame > len(self.read.keys()):
                cv2.destroyAllWindows()
                frame = 1
                exit(1)
        frame = 1

    def playPlot(self, solo = 'Y'):
        #This method plays the rawdata as a video
        global frame

        fig = plt.figure()
        ax = plt.axes()

        fig.tight_layout()

        dummy = np.zeros([120, 160])

        img = ax.imshow(dummy, interpolation='nearest', vmin = 5, vmax = 40, animated = True)
        fig.colorbar(img)

        current_cmap = plt.cm.get_cmap()
        current_cmap.set_bad(color='black')

        for i in np.arange(len(self.read.keys())):
            # print(frame)
            if solo == 'Y':
                data = self.read['image'+str(frame)][:]
                data = data[0:120]
                # print(data)
            else:
                try:
                    data = self.read['image'+str(frame)+'_open'][:]
                except KeyError:
                    data = self.read['image'+str(frame)+'_close'][:]

            # data = cv2.resize(data[:,:], (480, 640))
            ax.clear()
            ax.set_xticks([])
            ax.set_yticks([])

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.imshow(data)
            # print(data)
            plt.pause(0.0005)

            frame += 1
            time.sleep(0.13)

            if cv2.waitKey(9) & keyboard.is_pressed('e') & frame > len(self.read.keys()):
                cv2.destroyAllWindows()
                frame = 1
                exit(1)
        frame = 1

    def playSaveVideo(self, output, solo = 'Y'):
        #This method plays the raw data as a video and saves it as an avi. you need to specify the name of the output (.avi) file
        global frame
        frame_width = 640
        frame_height = 480

        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        writer = cv2.VideoWriter('./video_data/videos/{}.avi'.format(output), fourcc, 9, (frame_width, frame_height), True)


        for i in np.arange(len(self.read.keys())):
            # print(frame)
            if solo == 'Y':
                data = self.read['image'+str(frame)][:]
            else:
                try:
                    data = self.read['image'+str(frame)+'_open'][:]
                except KeyError:
                    data = self.read['image'+str(frame)+'_close'][:]


            data = cv2.resize(data[:,:], (640, 480))
            img = cv2.LUT(raw_to_8bit(data), generate_colour_map())
            # rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            writer.write(img)
            cv2.imshow('Playing video', img)

            frame += 1


            if cv2.waitKey(1) & keyboard.is_pressed('e') & frame > len(self.read.keys()):
                writer.release()
                cv2.destroyAllWindows()
                frame = 1
                exit(1)
        frame = 1

    def catchThres(self, thresh, solo = 'Y'):
        global frame
        self.mean_temps = []
        self.areas = []
        self.shutterOnOff = []
        self.thresholdChoise = thresh

        for i in np.arange(len(self.read.keys())):

            if solo == 'Y':
                raw_dum = self.read['image'+str(frame)][:]
            else:
                try:
                    raw_dum = self.read['image'+str(frame)+'_open'][:]
                    OnOff = 1
                    # ONE 1 is open
                except KeyError:
                    raw_dum = self.read['image'+str(frame)+'_close'][:]
                    OnOff = 0
                    #ZERO 0 is close

            threshold = CToRaw(thresh)

            super_threshold_indices = raw_dum > threshold
            meaning = raw_dum[raw_dum < threshold]
            raw_dum[super_threshold_indices] = 0

            area = np.count_nonzero(raw_dum)
            temp = np.mean(meaning)
            temp = rawToC(temp)

            self.areas.append(area)
            self.mean_temps.append(temp)
            self.shutterOnOff.append(OnOff)

            # data = cv2.resize(raw_dum[:,:], (640, 480))
            # img = cv2.LUT(raw_to_8bit(data), generate_colour_map())
            # rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            #
            # cv2.putText(rgbImage, 'A: {}'.format(area), (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0))
            # cv2.putText(rgbImage, 'T: {}'.format(temp), (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0))
            #
            # cv2.imshow('Playing video', rgbImage)
            # cv2.waitKey(1)

            frame += 1
        frame = 1

    def overThres(self, thresh, solo = 'Y'):
        global frame
        self.mean_temps = []
        self.areas = []

        for i in np.arange(len(self.read.keys())):
            if solo == 'Y':
                raw_dum = self.read['image'+str(frame)][:]
                original = self.read['image'+str(frame)][:]
            else:
                try:
                    raw_dum = self.read['image'+str(frame)+'_open'][:]
                    original = self.read['image'+str(frame)+'_open'][:]
                    OnOff = 1
                    # ONE 1 is open
                except KeyError:
                    raw_dum = self.read['image'+str(frame)+'_close'][:]
                    original = self.read['image'+str(frame)+'_close'][:]
                    OnOff = 0
                    #ZERO 0 is close

            threshold = CToRaw(thresh)

            super_threshold_indices = raw_dum > threshold
            print(threshold)
            meaning = raw_dum[raw_dum < threshold]
            # print(meaning)
            raw_dum[super_threshold_indices] = 0

            try:
                area = np.count_nonzero(raw_dum)
            except:
                area = 0

            try :
                temp = np.mean(meaning)
                temp = rawToC(temp)
            except RuntimeWarning:
                temp = 0

            self.areas.append(area)
            self.mean_temps.append(temp)

            raw_dum[np.nonzero(raw_dum)] = 255
            raw_dum = raw_to_8bit(raw_dum)

            original = cv2.LUT(raw_to_8bit(original), generate_colour_map())
            # Image_thres = cv2.cvtColor(raw_dum, cv2.COLOR_GRAY2RGB)

            # Image_thres = raw_dum #cv2.cvtColor(Image_thres, cv2.COLOR_RGB2HSV)
            # print(np.nonzero(raw_dum))
            cv2.putText(original, 'A: {}'.format(area), (100, 5), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0))
            cv2.putText(original, 'T: {}'.format(temp), (100, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0))

            # cv2.imshow('Playing video', cv2.resize(  | Image_thres, (640, 480), interpolation = cv2.INTER_CUBIC)))
            cv2.imshow('Playing video',  cv2.resize(raw_dum | original, (640, 480), interpolation = cv2.INTER_CUBIC))
            cv2.waitKey(1)

            frame += 1

        frame = 1

    def overThresSave(self, thresh, output, solo = 'Y'):
        global frame
        self.mean_temps = []
        self.areas = []
        frame_width = 640
        frame_height = 480

        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        writer = cv2.VideoWriter('./video_data/videos/{}.avi'.format(output), fourcc, 9, (frame_width, frame_height), True)

        for i in np.arange(len(self.read.keys())):
            if solo == 'Y':
                raw_dum = self.read['image'+str(frame)][:]
                original = self.read['image'+str(frame)][:]
            else:
                try:
                    raw_dum = self.read['image'+str(frame)+'_open'][:]
                    original = self.read['image'+str(frame)+'_open'][:]
                    OnOff = 1
                    # ONE 1 is open
                except KeyError:
                    raw_dum = self.read['image'+str(frame)+'_close'][:]
                    original = self.read['image'+str(frame)+'_close'][:]
                    OnOff = 0
                    #ZERO 0 is close

            threshold = CToRaw(thresh)

            super_threshold_indices = raw_dum > threshold
            print(threshold)
            meaning = raw_dum[raw_dum < threshold]
            # print(meaning)
            raw_dum[super_threshold_indices] = 0

            try:
                area = np.count_nonzero(raw_dum)
            except:
                area = 0

            try :
                temp = np.mean(meaning)
                temp = rawToC(temp)
            except RuntimeWarning:
                temp = 0

            self.areas.append(area)
            self.mean_temps.append(temp)

            raw_dum[np.nonzero(raw_dum)] = 255
            raw_dum = raw_to_8bit(raw_dum)

            original = cv2.LUT(raw_to_8bit(original), generate_colour_map())
            # Image_thres = cv2.cvtColor(raw_dum, cv2.COLOR_GRAY2RGB)

            # Image_thres = raw_dum #cv2.cvtColor(Image_thres, cv2.COLOR_RGB2HSV)
            # print(np.nonzero(raw_dum))
            cv2.putText(original, 'A: {}'.format(area), (100, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0))
            cv2.putText(original, 'T: {}'.format(temp), (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0))

            writer.write(cv2.resize(raw_dum | original, (640, 480), interpolation = cv2.INTER_CUBIC))
            cv2.imshow('Playing video',  cv2.resize(raw_dum | original, (640, 480), interpolation = cv2.INTER_CUBIC))

            if cv2.waitKey(1) & 0xFF == ord('q') & frame > len(self.read.keys):
                writer.release()
                cv2.destroyAllWindows()
                frame = 1
                exit(1)

            frame += 1

        frame = 1


    def plotShuArea(self, output):
        fig, ax = plt.subplots(figsize = (20, 10))
        plt.plot(np.arange(len(self.areas)), self.areas, color = 'r')

        ax.set_title('Total pixels below threshold: {} degree Celsius'.format(self.thresholdChoise))
        ax.set_ylabel('Number of pixels')
        ax.set_xlabel('Frames')


        ax2 = ax.twinx()
        lns_alc = ax2.plot(np.arange(len(self.areas)), self.shutterOnOff, color='k')
        ax2.set_ylim([0, 1.1])
        ax2.set_ylabel('Shutter state')

        ax2.yaxis.set_ticks(np.arange(0, 1, 0.9999))

        labels = [item.get_text() for item in ax2.get_yticklabels()]
        labels[0] = 'close'
        labels[1] = 'open'

        ax2.set_yticklabels(labels)


        ax.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)

        plt.savefig('./video_data/figures/{}.svg'.format(output), transparent = True, bbox_inches='tight')

    def plotShuTemp(self, output, minY, max):
        fig, ax = plt.subplots(figsize = (20, 10))
        plt.plot(np.arange(len(self.mean_temps)), self.mean_temps, color = 'b')

        ax.set_title('Mean temperature of pixels below threshold: {} degree Celsius'.format(self.thresholdChoise))
        ax.set_ylabel('Temperature (degree Celsius)')
        ax.set_xlabel('Frames')
        ax.set_ylim([minY, maxY])


        ax2 = ax.twinx()
        lns_alc = ax2.plot(np.arange(len(self.mean_temps)), self.shutterOnOff, color='k')
        ax2.set_ylim([0, 1.1])
        ax2.set_ylabel('Shutter state')

        ax2.yaxis.set_ticks(np.arange(0, 1, 0.9999))

        labels = [item.get_text() for item in ax2.get_yticklabels()]
        labels[0] = 'close'
        labels[1] = 'open'

        ax2.set_yticklabels(labels)


        ax.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)

        plt.savefig('./video_data/figures/{}.svg'.format(output), transparent = True, bbox_inches='tight')



######### Useuful links ###############

## Image analysis
# https://www.youtube.com/watch?v=-ZrDjwXZGxI

## https://lepton.flir.com/application-notes/people-finding-with-a-lepton/
## https://github.com/groupgets/pylepton/blob/master/pylepton/Lepton.py

##Windows
#https://lepton.flir.com/wp-content/uploads/2015/06/PureThermal-2-Basic-Lepton-Features.pdf
# https://lepton.flir.com/getting-started/quick-start-guide-getting-started-programing-with-python-sdk/
# https://lepton.flir.com/wp-content/uploads/2015/06/Advanced-Lepton-Usage-on-Windows.pdf

##Raspberr pi
# https://github.com/Kheirlb/purethermal1-uvc-capture
# https://lepton.flir.com/forums/topic/recording-and-viewing-raw-data/
#

## Video communication
# https://github.com/groupgets/purethermal1-uvc-capture


### For easy & dirty python scripts
# from ioctl_numbers_camera import _IOR, _IOW
# from fcntl import ioctl
#
# ############### Dirty and easy objects to control thermal camera that don't work ###########
# SPI_IOC_MAGIC   = ord("k")
#
# SPI_IOC_RD_MODE          = _IOR(SPI_IOC_MAGIC, 1, "=B")
# SPI_IOC_WR_MODE          = _IOW(SPI_IOC_MAGIC, 1, "=B")
#
# SPI_IOC_RD_LSB_FIRST     = _IOR(SPI_IOC_MAGIC, 2, "=B")
# SPI_IOC_WR_LSB_FIRST     = _IOW(SPI_IOC_MAGIC, 2, "=B")
#
# SPI_IOC_RD_BITS_PER_WORD = _IOR(SPI_IOC_MAGIC, 3, "=B")
# SPI_IOC_WR_BITS_PER_WORD = _IOW(SPI_IOC_MAGIC, 3, "=B")
#
# SPI_IOC_RD_MAX_SPEED_HZ  = _IOR(SPI_IOC_MAGIC, 4, "=I")
# SPI_IOC_WR_MAX_SPEED_HZ  = _IOW(SPI_IOC_MAGIC, 4, "=I")
#
# class Lepton(object):
#   """Communication class for FLIR Lepton module on SPI
#
#   Args:
#     spi_dev (str): Location of SPI device node. Default '/dev/spidev0.0'.
#   """
#
#   ROWS = 60
#   COLS = 80
#   VOSPI_FRAME_SIZE = COLS + 2
#   VOSPI_FRAME_SIZE_BYTES = VOSPI_FRAME_SIZE * 2
#   MODE = 0
#   BITS = 8
#   SPEED = 18000000
#
#   def __init__(self, spi_dev = "/dev/spidev0.0"):
#     self.__spi_dev = spi_dev
#     self.__txbuf = np.zeros(Lepton.VOSPI_FRAME_SIZE, dtype=np.uint16)
#
#     # struct spi_ioc_transfer {
#     #   __u64     tx_buf;
#     #   __u64     rx_buf;
#     #   __u32     len;
#     #   __u32     speed_hz;
#     #   __u16     delay_usecs;
#     #   __u8      bits_per_word;
#     #   __u8      cs_change;
#     #   __u8      tx_nbits;
#     #   __u8      rx_nbits;
#     #   __u16     pad;
#     # };
#     self.__xmit_struct = struct.Struct("=QQIIHBBBBH")
#     self.__xmit_buf = ctypes.create_string_buffer(self.__xmit_struct.size)
#     self.__msg = _IOW(SPI_IOC_MAGIC, 0, self.__xmit_struct.format)
#     self.__capture_buf = np.zeros((60, 82, 1), dtype=np.uint16)
#
#   def __enter__(self):
#     self.__handle = open(self.__spi_dev, "w+")
#
#     ioctl(self.__handle, SPI_IOC_RD_MODE, struct.pack("=B", Lepton.MODE))
#     ioctl(self.__handle, SPI_IOC_WR_MODE, struct.pack("=B", Lepton.MODE))
#
#     ioctl(self.__handle, SPI_IOC_RD_BITS_PER_WORD, struct.pack("=B", Lepton.BITS))
#     ioctl(self.__handle, SPI_IOC_WR_BITS_PER_WORD, struct.pack("=B", Lepton.BITS))
#
#     ioctl(self.__handle, SPI_IOC_RD_MAX_SPEED_HZ, struct.pack("=I", Lepton.SPEED))
#     ioctl(self.__handle, SPI_IOC_WR_MAX_SPEED_HZ, struct.pack("=I", Lepton.SPEED))
#
#     return self
#
#   def __exit__(self, type, value, tb):
#     self.__handle.close()
#
#   def capture(self, data_buffer = None):
#     """Capture a frame of data.
#
#     Captures 80x60 uint16 array of non-normalized (raw 12-bit) data. Returns that frame and a frame_id (which
#     is currently just the sum of all pixels). The Lepton will return multiple, identical frames at a rate of up
#     to ~27 Hz, with unique frames at only ~9 Hz, so the frame_id can help you from doing additional work
#     processing duplicate frames.
#
#     Args:
#       data_buffer (numpy.ndarray): Optional. If specified, should be ``(60,80,1)`` with `dtype`=``numpy.uint16``.
#
#     Returns:
#       tuple consisting of (data_buffer, frame_id)
#     """
#
#     if data_buffer is None:
#       data_buffer = np.ndarray((Lepton.ROWS, Lepton.COLS, 1), dtype=np.uint16)
#     elif data_buffer.ndim < 2 or data_buffer.shape[0] < Lepton.ROWS or data_buffer.shape[1] < Lepton.COLS or data_buffer.itemsize < 2:
#       raise Exception("Provided input array not large enough")
#
#     rxs = self.__capture_buf.ctypes.data
#     rxs_end = rxs + Lepton.ROWS * Lepton.VOSPI_FRAME_SIZE_BYTES
#     txs = self.__txbuf.ctypes.data
#     synced = False
#     while rxs < rxs_end:
#       self.__xmit_struct.pack_into(self.__xmit_buf, 0, txs, rxs, Lepton.VOSPI_FRAME_SIZE_BYTES, Lepton.SPEED, 0, Lepton.BITS, 0, Lepton.BITS, Lepton.BITS, 0)
#       ioctl(self.__handle, self.__msg, self.__xmit_buf)
#       if synced or self.__capture_buf[0,0] & 0x0f00 != 0x0f00:
#         synced = True
#         rxs += Lepton.VOSPI_FRAME_SIZE_BYTES
#
#     data_buffer[0:Lepton.ROWS,0:Lepton.COLS] = self.__capture_buf[0:Lepton.ROWS,2:Lepton.VOSPI_FRAME_SIZE]
#     data_buffer.byteswap(True)
#
#     # TODO: turn on telemetry to get real frame id, sum on this array is fast enough though (< 500us)
#     return data_buffer, data_buffer.sum()

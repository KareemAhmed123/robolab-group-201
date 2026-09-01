# !/usr/bin/env python3
import ev3dev.ev3 as ev3 # type: ignore
from time import sleep
import time
from enum import Enum
import math

class Odometry:
    def __init__(self):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
    
    def calibrate(self, data):
        total_right = 0
        total_left = 0
        for element in data:
            total_left += element[0]
            total_right += element[1]
        print("Total left", total_left, "Total right", total_right, "Ticks", len(data))

    def calculate_vector(self, data):
        alpha = 0
        delta_x = 0
        delta_y = 0
        a = 18 # Radabstand
        # Linkskurve hat negativen Winkel, Koordinatensystem zeigt mit y-achse in Fahrrichtung, x-Achse in Fahrrichtung rechts
        count = 0

        for element in data:
            distance_left = 83 / 4500 * element[0]
            distance_right = 83 / 4500 * element[1]
            delta_alpha = (distance_right - distance_left) / a
            if delta_alpha >= 0:
                delta_alpha *= 1
            else:
                delta_alpha *= 1
            alpha += delta_alpha
            if distance_left != distance_right:
                s = (a * (distance_right + distance_left) / (distance_right - distance_left)) * math.sin((distance_right - distance_left)/(2*a))
            else:
                s = distance_right
            delta_x += s * math.sin(alpha)
            delta_y += s * math.cos(alpha)

            count += 1
            if count % 2 == 0:
                print("alpha", alpha / 6.28 * 360, "delta x", delta_x, "delta_y", delta_y)
        self.calibrate(data)

        #print("Delta X", delta_x, "Dealta Y", delta_y)
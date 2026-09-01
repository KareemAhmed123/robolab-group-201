# !/usr/bin/env python3
import ev3dev.ev3 as ev3 # type: ignore
from time import sleep
import time
from enum import Enum
import random
from odometry import Odometry

class RobiMode(Enum):
    NOT_FINISHED = 1
    FINISHED = 2

class EndStatus(Enum):
    INTERRUPTED_BY_USER = 1
    REACHED_NEXT_NODE = 2
    RETURNED_BECAUSE_PATH_BLOCKED = 3
    REACHED_FIRST_NODE_AFTER_START_OF_MISSION = 4
    UNKNOWN = 5

class Mechanics:
    def __init__(self):
        """
        Initializes odometry module
        """
        # YOUR CODE FOLLOWS (remove pass, please!)
        self.r = ev3.LargeMotor("outA") # rechts
        self.l = ev3.LargeMotor("outB") # links
        self.r.reset()
        self.l.reset()
        self.stop()
        self.farbsensor = ev3.ColorSensor("in1")
        self.left_button = ev3.TouchSensor("in3")
        self.right_button = ev3.TouchSensor("in2")
        self.offset = 270 # 350

        with open('/sys/class/power_supply/lego-ev3-battery/voltage_now') as voltage_file:
            voltage = int(voltage_file.read())
    
        if voltage > 7.5:
            self.speed_for_360_turn = 100
        else:
            self.speed_for_360_turn = 104

        self.time_for_360_turn = 6.5 # 6.4
        self.us = ev3.UltrasonicSensor("in4")
        self.us.mode = 'US-DIST-CM'  # Continuous measurement in centimeters (for inch use US-DIST-IN)
        self.end_status = EndStatus.REACHED_FIRST_NODE_AFTER_START_OF_MISSION
        self.path_available = [-1,-1,-1,-1]
        self.blue = [33, 96, 48]

    def follow_line(self):
        sum = 0
        last_error = 0
        derivative = 0
        black_or_white_old = True # egal ob true oder false - geht dann eh um Wechsel von schwarz auf weiß
        saved_data_for_odometry = set()

        while 1:
            self.farbsensor.mode = 'RGB-RAW'
            color_rgb_array = self.farbsensor.raw
            light_value = color_rgb_array[0] + color_rgb_array[1] + color_rgb_array[2]
            error = light_value - self.offset
            sum = sum + error
            derivative = error - last_error
            if abs(sum) > 600:
                # Panikmodus - vom Weg abgekommen
                Tp = 80
                sum = sum * 0.7
                Kp = 12
                Ki = 3.1 * 1.6
                Kd = 16 * 1.6
                if ((light_value > self.offset) != black_or_white_old): # wieder auf dem Weg, integrales Gegensteuern weniger stark
                    sum = sum * 0.5
                    ()
                black_or_white_old = light_value > self.offset
            else:
                Tp = 110
                Kp = 12
                Ki = 1.5
                Kd = 16
            turn = Kp*error + Ki*sum + Kd*derivative
            correct = int(turn / 100)
            #print("Light sum:",light_value,"Correct:",correct,"Sum:",sum,"Tp:",Tp)
            self.l.speed_sp = (Tp - correct) * (1)
            self.l.command = "run-forever"
            self.r.speed_sp = (Tp + correct) * (1)
            self.r.command = "run-forever"
            saved_data_for_odometry.add((Tp - correct, Tp + correct))

            last_error = error

            if self.left_button.value() == 1 and self.right_button.value() == 1:
                self.stop()
                return EndStatus.INTERRUPTED_BY_USER

            self.farbsensor.mode = 'COL-COLOR'
            color_code = self.farbsensor.value()
            if ((self.blue[0] * 0.6 <= color_rgb_array[0] <= self.blue[0] * 1.4 and self.blue[1] * 0.6 <= color_rgb_array[1] <= self.blue[1] * 1.4 and self.blue[2] * 0.6 <= color_rgb_array[2] <= self.blue[2] * 1.4) or color_code == 5):
                tolerance = 600
                if abs(sum) < tolerance:
                    sum = 0
                else:
                    if sum >= tolerance:
                        sum -= tolerance
                    else:
                        sum += tolerance
                correct = int(sum / 100 * 0.8)
                #print("Driving to middle with correct",correct,", sum",sum,"at Tp",Tp)
                self.r.speed_sp = 80 * (1) + correct
                self.r.command = "run-forever"
                self.l.speed_sp = 80 * (1) - correct
                self.l.command = "run-forever"
                if Tp >= 90:
                    sleep(1.7) # 1.7
                else:
                    sleep(2.3) # 2.2
                self.stop()
                
                odometry = Odometry()
                odometry.calculate_vector(saved_data_for_odometry)
                return EndStatus.INTERRUPTED_BY_USER # REMOVE BEFORE EXAM!!!!
            
                if self.end_status == EndStatus.REACHED_FIRST_NODE_AFTER_START_OF_MISSION:
                    return EndStatus.REACHED_FIRST_NODE_AFTER_START_OF_MISSION
                
                if self.end_status == EndStatus.RETURNED_BECAUSE_PATH_BLOCKED:
                    return EndStatus.RETURNED_BECAUSE_PATH_BLOCKED

                break

            if self.us.value() < 85:
                self.stop()
                ev3.Sound.beep()
                sleep(0.2)
                ev3.Sound.beep()
                sleep(0.2)
                ev3.Sound.beep()
                print("Path is blocked, returning to former node")
                self.r.speed_sp = self.speed_for_360_turn
                self.r.command = "run-forever"
                self.l.speed_sp = -1 * self.speed_for_360_turn
                self.l.command = "run-forever"
                sleep(0.125 * self.time_for_360_turn)
                self.end_status = EndStatus.RETURNED_BECAUSE_PATH_BLOCKED
                self.return_to_line()
                self.follow_line()
                break

        return self.end_status
        

    
    def go_0_degrees(self):
        self.end_status = EndStatus.REACHED_NEXT_NODE
        self.r.speed_sp = -1 * self.speed_for_360_turn
        self.r.command = "run-forever"
        self.l.speed_sp = self.speed_for_360_turn
        self.l.command = "run-forever"
        sleep(0.125 * self.time_for_360_turn * 0.7)
        self.return_to_line()
        return self.follow_line()

    def go_90_degrees(self):
        self.end_status = EndStatus.REACHED_NEXT_NODE
        self.r.speed_sp = self.speed_for_360_turn
        self.r.command = "run-forever"
        self.l.speed_sp = -1 * self.speed_for_360_turn
        self.l.command = "run-forever"
        sleep(0.125 * self.time_for_360_turn)
        self.return_to_line()
        return self.follow_line()

    def go_180_degrees(self):
        self.end_status = EndStatus.REACHED_NEXT_NODE
        self.r.speed_sp = self.speed_for_360_turn
        self.r.command = "run-forever"
        self.l.speed_sp = -1 * self.speed_for_360_turn
        self.l.command = "run-forever"
        sleep(0.375 * self.time_for_360_turn)
        self.return_to_line()
        return self.follow_line()
    
    def go_270_degrees(self):
        self.end_status = EndStatus.REACHED_NEXT_NODE
        self.r.speed_sp = self.speed_for_360_turn
        self.r.command = "run-forever"
        self.l.speed_sp = -1 * self.speed_for_360_turn
        self.l.command = "run-forever"
        sleep(0.625 * self.time_for_360_turn)
        self.return_to_line()
        return self.follow_line()
    
    def return_to_line(self):
        light_value = self.farbsensor.raw[0] + self.farbsensor.raw[1] + self.farbsensor.raw[2]
        black_or_white = light_value > self.offset # 1 = white, 0 = black
        self.r.speed_sp = self.speed_for_360_turn * 0.5
        self.r.command = "run-forever"
        self.l.speed_sp = -1 * self.speed_for_360_turn * 0.5
        self.l.command = "run-forever"

        while 1:
            sleep(0.1)
            light_value = self.farbsensor.raw[0] + self.farbsensor.raw[1] + self.farbsensor.raw[2]
            if ((light_value > self.offset) != black_or_white): # Wechsel auf andere Farbe
                self.stop()
                break
            black_or_white = light_value > self.offset


    def melody(self):
        ev3.Sound.tone([(440, 200, 100), (494, 200, 100), (523, 200, 100),  (659, 200, 100),  (698, 200, 100),  (523, 200, 100), (784, 200)])  # list of (frequency (Hz), duration (ms), delay to next (ms)) tuples
    
    def scan_for_paths(self):
        start = time.time()
        self.farbsensor.mode = 'RGB-RAW'
        color_rgb_array = self.farbsensor.raw
        light_value = color_rgb_array[0] + color_rgb_array[1] + color_rgb_array[2]
        black_or_white = light_value > self.offset # 1 = white, 0 = black
        self.r.speed_sp = self.speed_for_360_turn
        self.r.command = "run-forever"
        self.l.speed_sp = -1 * self.speed_for_360_turn
        self.l.command = "run-forever"
        spotted_black_white_changes = []

        while time.time() < (start + self.time_for_360_turn):
            sleep(0.1)

            light_value = self.farbsensor.raw[0] + self.farbsensor.raw[1] + self.farbsensor.raw[2]

            if ((light_value > self.offset) != black_or_white): # Wechsel auf andere Farbe
                spotted_black_white_changes.append(time.time())

            black_or_white = light_value > self.offset


        # print("   Spotted",len(spotted_black_white_changes),"black-white-changes")
        self.stop()

        all_timestamps = []
        all_timestamps.append(start)
        all_timestamps.extend(spotted_black_white_changes)
        all_timestamps.append(time.time())
        time_diffs = []

        for i in range(len(all_timestamps)-1):
            time_diffs.append(all_timestamps[i+1]-all_timestamps[i])

        self.path_available = [-1,-1,-1,-1]
        position = 0

        if time_diffs[position] < 1 or time_diffs[len(time_diffs)-1] < 1:
            self.path_available[position] = 1

        for i in range(1,len(time_diffs)-1,1):
            if time_diffs[i] < 1:
                time_to_turn = time_diffs[i-1]
                if 0.125 * self.time_for_360_turn <= time_to_turn and time_to_turn <= 0.375 * self.time_for_360_turn:
                    # 90° Drehung
                    position += 1
                elif 0.375 * self.time_for_360_turn <= time_to_turn and time_to_turn <= 0.625 * self.time_for_360_turn:
                    # 180° Drehung
                    position += 2
                elif 0.625 * self.time_for_360_turn <= time_to_turn and time_to_turn <= 0.875 * self.time_for_360_turn:
                    # 270° Drehung
                    position += 3
                    
                if position < 4:
                    self.path_available[position] = 1
              
        # print(time_diffs)
        #print("   The following paths are available:",self.path_available)
        return self.path_available

    def calibrate_blue(self):
        print('Place Robi on a blue node and press a button') 
        while 1:
            sleep(0.1)
            if self.left_button.value() == 1 or self.right_button.value() == 1:
                ev3.Sound.beep()
                sleep(1)
                break
        self.farbsensor.mode = 'RGB-RAW'
        #self.blue = self.farbsensor.raw
        print("Blue was calibrated to",self.blue)

        print('Press a button to start mission') 
        while 1:
            sleep(0.1)
            if self.left_button.value() == 1 or self.right_button.value() == 1:
                ev3.Sound.beep()
                sleep(1)
                break
    
    def stop(self):
        self.l.stop()
        self.r.stop()
import ev3dev.ev3 as ev3
import random
from mechanics import Mechanics, EndStatus, RobiMode
import time
from time import sleep

from planet import Planet, Direction


class Integration:
    def __init__(self, communication,planet_object,logger):
        self.communication = communication
        self.planet = None
        self.start_x = None
        self.start_y = None
        self.start_point = None
        self.start_orientation = None
        
        self.node_y = None
        self.node_x = None
        self.node_orientation = None
        self.planet_object=planet_object
        self.scanned_nodes_and_unexplored_paths = dict()
        self.logger=logger
        self.target = None
        self.robi_mode = RobiMode.NOT_FINISHED

    def handle_message(self, messages, planet_object):
        queue_not_empty = True
        while not messages.empty():
            if messages.empty:
                queue_not_empty = False
            payload = messages.get()
            the_payload = payload["payload"]

            if payload["type"] == "planet":
                self.planet = the_payload["planetName"]
                self.start_x = the_payload["startX"]
                self.start_y = the_payload["startY"]
                self.start_point = (self.start_x, self.start_y)
                self.start_orientation = the_payload["startOrientation"]
                print(
                    f"Robi starts at Point {self.start_point} on the planet",
                    self.planet,
                    "and the direction is:",self.start_orientation
                )
                self.communication.set_planet(self.planet)
                self.set_node_x(self.start_x)
                self.set_node_y(self.start_y)
                self.communication.subscribe_for_planet(self.planet)
                self.set_node_orientation(self.start_orientation)
            if payload["type"] == "path":
                if the_payload["pathStatus"] == "free":
                    self.start_x = the_payload["startX"]
                    self.start_y = the_payload["startY"]
                    start_direction = the_payload["startDirection"]
                    end_x = the_payload["endX"]
                    end_y = the_payload["endY"]
                    end_direction = the_payload["endDirection"]
                    start = ((self.start_x, self.start_y), Direction(start_direction))
                    end = ((end_x, end_y), Direction(end_direction))
                    self.set_node_x(end_x)
                    self.set_node_y(end_y)
                    self.set_node_orientation(end_direction)

                    if "pathWeight" in the_payload:
                        weight = the_payload["pathWeight"]
                        #print(f"pathWight:{weight}")
                        #print(f"add path: {start},{end}")
                    else:
                        #print("path without pathWeight")
                        #print(f"add path: {start},{end}")
                        ()

                    planet_object.add_path(start, end, weight)


                if the_payload["pathStatus"] == "blocked":
                    self.start_x = the_payload["startX"]
                    self.start_y = the_payload["startY"]
                    start_direction = the_payload["startDirection"]
                    end_x = the_payload["endX"]
                    end_y = the_payload["endY"]
                    end_direction = the_payload["endDirection"]
                    start = ((self.start_x, self.start_y), Direction(start_direction))
                    end = ((end_x, end_y), Direction(end_direction))
                    weight = -1
                    # planet.add_path(start,end,weight)
                    #print(f"add blocked path: {start},{start},{weight}")
                    self.logger.debug(f"add blocked path: {start},{start},{weight}")

                    planet_object.add_path(start, end, weight)
            if payload["type"] == "pathUnveiled":
                unveiled_start_x = the_payload["startX"]
                unveiled_start_y = the_payload["startY"]
                unveiled_start_direction = the_payload["startDirection"]
                unveiled_end_x = the_payload["endX"]
                unveiled_end_y = the_payload["endY"]
                unveiled_end_direction = the_payload["endDirection"]
                unveiled_start = (
                    (unveiled_start_x, unveiled_start_y),
                    Direction(unveiled_start_direction),
                )
                unveiled_end = (
                    (unveiled_end_x, unveiled_end_y),
                    Direction(unveiled_end_direction),
                )

                if the_payload["pathStatus"] == "free":
                    weight = the_payload["pathWeight"]
                    #print(f"pathWight:{weight}")
                    #print(f"add unveiled path: {unveiled_start},{unveiled_end}")
                elif the_payload["pathStatus"] == "blocked":
                    weight = -1
                    #print(f"add unveiled blocked path: {unveiled_start},{unveiled_end}")

                planet_object.add_path(unveiled_start, unveiled_end, weight)
            if payload["type"] == "pathSelect":
                direction = the_payload["startDirection"]
                print("Robi is forced drive                                           ",direction)
                self.set_node_orientation(direction)

            if payload["type"] == "target":
                target_x = the_payload["targetX"]
                target_y = the_payload["targetY"]
                target = (target_x, target_y)
                print(f"YOUR TARGET IS: {target}")
                self.target = target
                

    def set_node_x(self, value):
        self.node_x = value

    def set_node_y(self, value):
        self.node_y = value

    def set_node_orientation(self, value):
        self.node_orientation = value

    def get_node_x(self):
        return self.node_x

    def get_node_y(self):
        return self.node_y

    def get_node_orientation(self):
        return self.node_orientation

    def start_robot(self, communication, mechanics, planet):
        print("Start mission")
        end_status = mechanics.follow_line()
        message = communication.server_messages

        while end_status != EndStatus.INTERRUPTED_BY_USER and self.robi_mode != RobiMode.FINISHED:
            # get_node_x/y/orientation is NOT UPDATED yet

            if end_status == EndStatus.REACHED_FIRST_NODE_AFTER_START_OF_MISSION:
                communication.ready_message()

            elif end_status == EndStatus.RETURNED_BECAUSE_PATH_BLOCKED:
                communication.path_message(self.get_node_x(), self.get_node_y(),
                                        self.get_node_orientation(), 
                                        self.get_node_x(), self.get_node_y(),
                                        self.get_node_orientation(), "blocked")

            else:
                communication.path_message(self.get_node_x(), self.get_node_y(),
                                            self.get_node_orientation(), # not updated yet, get_node_orientation contains start direction from former node
                                            0, 0, 
                                            0, "free") # 0, 0, 0 because odometry is missing
            
            self.handle_message(message, planet) # get_node_x/y/orientation is now UPDATED




            print("")
            print("")
            print("###    Robi arrived at (",self.get_node_x(),", ",self.get_node_y(),")    ###",sep="")





            print("Robi came from direction                                       ", self.get_node_orientation())
            orientation_of_robot = self.get_node_orientation()
            if end_status != EndStatus.REACHED_FIRST_NODE_AFTER_START_OF_MISSION:
                orientation_of_robot += 180
            orientation_of_robot = self.correct_to_range_0_270(orientation_of_robot)
            print("=> Orientation of robot                                        ", orientation_of_robot)

            planned_next_orientation = None # Robi does not know yet where to go next, he starts calculating this now





            if planned_next_orientation == None:
                if self.target != None:
                    if (self.get_node_x(), self.get_node_y()) == self.target:
                        print("")
                        print("Robi has reached it's final target")
                        self.robi_mode = RobiMode.FINISHED
                        communication.complete_message("Robi has reached it's final target","targetReached")
                        break
                    if planet.shortest_path_2((self.get_node_x(), self.get_node_y()), 
                                            self.target) != None: # target reachable
                        shortest_path_2 = planet.shortest_path_2((self.get_node_x(), self.get_node_y()), self.target)
                        print("Robi is now driving to it's final target ",shortest_path_2[len(shortest_path_2) -1][0]," calling at ",shortest_path_2[0][0],sep="")
                        planned_next_orientation = shortest_path_2[0][1].value



            if planned_next_orientation == None:
                if (self.get_node_x(), self.get_node_y()) not in self.scanned_nodes_and_unexplored_paths:
                    print("Start scanning")
                    available_paths = mechanics.scan_for_paths()
                    print("Available paths:",available_paths)
                    orientations_of_available_paths = []
                    for i in range(4):
                        if available_paths[i] == 1:
                            # path is available
                            orientation_of_availabe_path = orientation_of_robot + 90 * i
                            orientation_of_availabe_path = self.correct_to_range_0_270(orientation_of_availabe_path)
                            if 90 * i != 180:
                                orientations_of_available_paths.append(orientation_of_availabe_path)
                    self.scanned_nodes_and_unexplored_paths[
                        (self.get_node_x(), self.get_node_y())] = orientations_of_available_paths  # add
                    self.delete_from_unexplored()

                    if len(orientations_of_available_paths) > 0:
                        print("Robi scanned for unexplored paths and chosed a random available path to explore")
                        planned_next_orientation = self.correct_to_range_0_270(
                        orientations_of_available_paths[random.randint(0, len(orientations_of_available_paths) - 1)])
                    else:
                        print("Nodes that were scanned right now got unveiled by the mothership")

                else:
                    print("Robi has already scanned at this node, no scanning needed")
                    self.delete_from_unexplored()
                    orientations_of_available_paths = self.scanned_nodes_and_unexplored_paths.get((self.get_node_x(),self.get_node_y()))
                    
                    if len(orientations_of_available_paths) > 0:
                        print("There are paths to explore at the current node, choosing random one")
                        orientations_of_available_paths = self.scanned_nodes_and_unexplored_paths.get(
                            (self.get_node_x(), self.get_node_y()))
                        planned_next_orientation = self.correct_to_range_0_270(
                            orientations_of_available_paths[
                                random.randint(0, len(orientations_of_available_paths) - 1)])
                    else:
                        print("There are no more paths to explore at the current node")



            if planned_next_orientation == None:
                possible_return_nodes = []
                for scanned_node, unexplored_directions in self.scanned_nodes_and_unexplored_paths.items():
                    if len(unexplored_directions) > 0:
                        possible_return_nodes.append(scanned_node)

                all_paths = self.planet_object.get_paths()
                for node in all_paths.keys():
                    if node not in self.scanned_nodes_and_unexplored_paths: # nodes we know they exist but we haven't scanned them yet
                        possible_return_nodes.append(node)
                print("Possible return nodes:",possible_return_nodes)

                if possible_return_nodes != []:
                    shortest_path_2 = planet.shortest_path_2((self.get_node_x(), self.get_node_y()), 
                                                            planet.get_nearest_node((self.get_node_x(), self.get_node_y()), possible_return_nodes))
                    # print("Shortest path to nearest node:", shortest_path_2)
                    if shortest_path_2 != None:
                        print("Robi is returning to ",shortest_path_2[len(shortest_path_2) -1][0]," calling at ",shortest_path_2[0][0],sep="")
                        planned_next_orientation = shortest_path_2[0][1].value
                    else:
                        print("None of the possible return nodes is reachable")






            if planned_next_orientation != None:
                # Robi has an idea where to go next
                print("Scanned nodes and unexplored paths:", self.scanned_nodes_and_unexplored_paths)
                print("")
                print("=> Robi is asking the mothership for permission to drive       ",planned_next_orientation)
                
                communication.path_select_message(self.get_node_x(), self.get_node_y(),
                                                planned_next_orientation)
                self.set_node_orientation(planned_next_orientation)
                self.handle_message(message, planet)
                sleep(2)

                final_next_orientation = self.get_node_orientation() # maybe the nmothership overwrote this value
                final_next_orientation_to_start_driving = self.correct_to_range_0_270(
                    final_next_orientation - orientation_of_robot)

                print("-------------------------------------------------------------------")
                print("final next orientation according to the compass                ", final_next_orientation)
                print("final next orientation taking robot orientation into account   ", final_next_orientation_to_start_driving)
                
                ev3.Sound.beep()
                end_status = self.start_driving(final_next_orientation_to_start_driving, mechanics)
            
            else:
                print("")
                print("No target reachable and there are no more nodes to explore")
                communication.complete_message("No target reachable and there are no more nodes to explore","explorationCompleted")
                self.robi_mode = RobiMode.FINISHED
                break





        mechanics.stop()

        if self.robi_mode == RobiMode.FINISHED:
            mechanics.melody()
            print("Mission complete")
        else:
            print("Mission cancelled by user")
        
    
            


    def correct_to_range_0_270(self, orientation):
        while orientation < 0:
            orientation += 360
        while orientation >= 360:
            orientation -= 360
        return orientation
    
    def delete_from_unexplored(self):
        paths = self.planet_object.get_paths()
        for key, dictionary in paths.items():
            for direction, tuple in dictionary.items():
                try:
                    self.scanned_nodes_and_unexplored_paths.get(key).remove(direction.value)
                except:
                    ()
                try:
                    self.scanned_nodes_and_unexplored_paths.get(tuple[0]).remove(tuple[1].value)        
                except:
                    ()

    def start_driving(self, final_next_orientation_to_start_driving,mechanics):
        end_status = EndStatus.UNKNOWN
        if final_next_orientation_to_start_driving == 0:
            end_status = mechanics.go_0_degrees()
        if final_next_orientation_to_start_driving == 90:
            end_status = mechanics.go_90_degrees()
        if final_next_orientation_to_start_driving == 180:
            end_status = mechanics.go_180_degrees()
        if final_next_orientation_to_start_driving == 270:
            end_status = mechanics.go_270_degrees()
        return end_status
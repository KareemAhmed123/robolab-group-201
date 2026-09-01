import ev3dev.ev3 as ev3
import random
from mechanics import Mechanics, EndStatus, RobiMode
import time
from time import sleep

from planet import Planet, Direction


class Integration_old:
    def __init__(self, communication,planet_object,logger):
        self.communication = communication
        self.planet = None
        self.start_x = None
        self.start_y = None
        self.node_y = None
        self.node_x = None
        self.node_orientation = None
        self.start_point = None
        self.start_orientation = None
        self.planet_object=planet_object
        self.scanned_nodes_and_unexplored_paths = dict()
        self.logger=logger
        self.target = None
        self.robi_mode = RobiMode.UNKNOWN

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
                print(f"Mothership forces Robi to drive {direction}")

                self.set_node_orientation(direction)
            if payload["type"] == "target":
                target_x = the_payload["targetX"]
                target_y = the_payload["targetY"]
                target = (target_x, target_y)
                print(f"YOUR TARGET IS: {target}")
                if self.target != None and self.target != target:
                    self.robi_mode = RobiMode.EXPLORING

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
        end_status = mechanics.follow_line()
        message = communication.server_messages

        while end_status != EndStatus.INTERRUPTED_BY_USER and self.robi_mode != RobiMode.FINISHED:
            if (self.get_node_x(), self.get_node_y) == self.target:
                print("Robi has reached it's final target")
                self.robi_mode = RobiMode.FINISHED
                communication.complete_message("Robi has reached it's final target","targetReached")

            if end_status == EndStatus.REACHED_FIRST_NODE_AFTER_START_OF_MISSION:
                communication.ready_message()
                self.handle_message(message, planet)
                self.robi_mode = RobiMode.EXPLORING



            if self.robi_mode == RobiMode.EXPLORING:

                if end_status == EndStatus.REACHED_NEXT_NODE:
                    communication.path_message(self.get_node_x(), self.get_node_y(),
                                            self.get_node_orientation(), 0, 0, 0, "free")
                    self.handle_message(message, planet)

                if end_status == EndStatus.RETURNED_BECAUSE_PATH_BLOCKED:
                    communication.path_message(self.get_node_x(), self.get_node_y(),
                                            self.get_node_orientation(), self.get_node_x(),
                                            self.get_node_y(),
                                            self.correct_to_range_0_270(self.get_node_orientation()), "blocked")
                    self.handle_message(message, planet)


                if (end_status == EndStatus.REACHED_NEXT_NODE or 
                    end_status == EndStatus.REACHED_FIRST_NODE_AFTER_START_OF_MISSION or 
                    end_status == EndStatus.RETURNED_BECAUSE_PATH_BLOCKED or
                    end_status == EndStatus.STOPPED_DRIVING_TO_TARGET):
                    if self.target != None and planet.shortest_path_2((self.get_node_x(), self.get_node_y()), self.target) != None: # and target reachable:
                        shortest_path_2 = planet.shortest_path_2((self.get_node_x(), self.get_node_y()), self.target)
                        print(shortest_path_2)
                        self.robi_mode = RobiMode.DRIVING_TO_TARGET
                        print("Now driving to target")

                    if self.robi_mode == RobiMode.EXPLORING:
                        orientation_of_robot = self.get_node_orientation()
                        print("Robi came from direction:", orientation_of_robot)
                        if end_status == EndStatus.REACHED_NEXT_NODE or end_status == EndStatus.STOPPED_DRIVING_TO_TARGET:
                            orientation_of_robot += 180
                        if end_status == EndStatus.RETURNED_BECAUSE_PATH_BLOCKED:
                            orientation_of_robot -= 180
                        orientation_of_robot = self.correct_to_range_0_270(orientation_of_robot)
                        print("=> Orientation of robot  ", orientation_of_robot)
                        if (self.get_node_x(), self.get_node_y()) not in self.scanned_nodes_and_unexplored_paths:
                            print("Start scanning at (",self.get_node_x(),",",self.get_node_y(),")",sep="")
                            available_paths = mechanics.scan_for_paths()
                            print(available_paths)
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
                                planned_orientation_to_explore = self.correct_to_range_0_270(
                                orientations_of_available_paths[random.randint(0, len(orientations_of_available_paths) - 1)])
                            else:
                                print("There are no more paths to explore at the current node because we scanned and those paths got unveiled")
                                
                                possible_return_nodes = []
                                for explored_node, unexplored_directions in self.scanned_nodes_and_unexplored_paths.items():
                                    if len(unexplored_directions) > 0:
                                        possible_return_nodes.append(explored_node)

                                paths = self.planet_object.get_paths()
                                for key, dictionary in paths.items():
                                    if key not in self.scanned_nodes_and_unexplored_paths:
                                        possible_return_nodes.append(key)
                                        

                                print("Possible return nodes",possible_return_nodes)
                                if possible_return_nodes == []:
                                    communication.complete_message("No target was found and there are no more nodes to explore","explorationCompleted")
                                    self.robi_mode = RobiMode.FINISHED
                                    



                                if self.robi_mode != RobiMode.FINISHED:
                                    nearest_node = planet.get_nearest_node((self.get_node_x(), self.get_node_y()), possible_return_nodes)
                                    
                                    shortest_path_2 = planet.shortest_path_2((self.get_node_x(), self.get_node_y()), nearest_node)
                                    
                                    print("Shortest path:", shortest_path_2)
                                    self.robi_mode = RobiMode.DRIVING_SHORTEST_PATH_TO_NODE_WHERE_EXIST_PATHS_TO_EXPLORE
                            

                        else:
                            print("No scanning needed at (",self.get_node_x(),",",self.get_node_y(),")",sep="")
                            self.delete_from_unexplored()
                            orientations_of_available_paths = self.scanned_nodes_and_unexplored_paths.get((self.get_node_x(),self.get_node_y()))
                            
                            if len(orientations_of_available_paths) > 0:
                                print("There are paths to explore at the current node")
                                orientations_of_available_paths = self.scanned_nodes_and_unexplored_paths.get(
                                    (self.get_node_x(), self.get_node_y()))
                                planned_orientation_to_explore = self.correct_to_range_0_270(
                                    orientations_of_available_paths[
                                        random.randint(0, len(orientations_of_available_paths) - 1)])
                            else:
                                print("There are no more paths to explore at the current node")
                                possible_return_nodes = []
                                for explored_node, unexplored_directions in self.scanned_nodes_and_unexplored_paths.items():
                                    if len(unexplored_directions) > 0:
                                        possible_return_nodes.append(explored_node)

                                paths = self.planet_object.get_paths()
                                for key, dictionary in paths.items():
                                    if key not in self.scanned_nodes_and_unexplored_paths:
                                        possible_return_nodes.append(key)
                                        

                                print("Possible return nodes",possible_return_nodes)
                                if possible_return_nodes == []:
                                    communication.complete_message("No target was found and there are no more nodes to explore","explorationCompleted")
                                    self.robi_mode = RobiMode.FINISHED
                                    



                                if self.robi_mode != RobiMode.FINISHED:
                                    nearest_node = planet.get_nearest_node((self.get_node_x(), self.get_node_y()), possible_return_nodes)
                                    
                                    shortest_path_2 = planet.shortest_path_2((self.get_node_x(), self.get_node_y()), nearest_node)
                                    
                                    print("Shortest path:", shortest_path_2)
                                    self.robi_mode = RobiMode.DRIVING_SHORTEST_PATH_TO_NODE_WHERE_EXIST_PATHS_TO_EXPLORE


                            
                    if self.robi_mode == RobiMode.EXPLORING:

                        print("Scanned nodes and unexplored paths:", self.scanned_nodes_and_unexplored_paths)

                        communication.path_select_message(self.get_node_x(), self.get_node_y(),
                                                        planned_orientation_to_explore)
                        self.set_node_orientation(planned_orientation_to_explore)

                        self.handle_message(message, planet)
                        sleep(2)
                        planned_orientation_to_explore = self.correct_to_range_0_270(self.get_node_orientation())
                        planned_orientation_to_start_driving = self.correct_to_range_0_270(
                            planned_orientation_to_explore - orientation_of_robot)

                        print("Planned orientation following compass            ", planned_orientation_to_explore)
                        print("Planned orientation considering robot orientation", planned_orientation_to_start_driving)
                        try:
                            if planned_orientation_to_explore in self.scanned_nodes_and_unexplored_paths.get(
                                (self.get_node_x(), self.get_node_y())):
                                try:
                                    # Richtung in die jetzt gefahren wird, aus unerkundet löschen
                                    self.scanned_nodes_and_unexplored_paths.get((self.get_node_x(), self.get_node_y())).remove(
                                planned_orientation_to_explore)
                                except:
                                    ()
                        except:
                            ()

                        ev3.Sound.beep()

                        end_status = self.start_driving(planned_orientation_to_start_driving,mechanics)

            elif self.robi_mode == RobiMode.DRIVING_SHORTEST_PATH_TO_NODE_WHERE_EXIST_PATHS_TO_EXPLORE or self.robi_mode == RobiMode.DRIVING_TO_TARGET:            
                length = len(shortest_path_2)
                print("length",length)
                
                print("On way back to node", shortest_path_2[len(shortest_path_2)-1][0],"calling at", shortest_path_2[0][0], "heading",shortest_path_2[0][1].value)
                communication.path_select_message(self.get_node_x(), self.get_node_y(),
                                                shortest_path_2[0][1].value)
                self.set_node_orientation(shortest_path_2[0][1].value)

                self.handle_message(message, planet)
                sleep(2)
                
                planned_orientation_to_explore = self.get_node_orientation()

                real_direction = planned_orientation_to_explore

                planned_orientation_to_start_driving = self.correct_to_range_0_270(
                    planned_orientation_to_explore - orientation_of_robot)

                print("Planned orientation following compass            ", planned_orientation_to_explore)
                print("Planned orientation considering robot orientation", planned_orientation_to_start_driving)

                try:
                    if planned_orientation_to_explore in self.scanned_nodes_and_unexplored_paths.get(
                            (self.get_node_x(), self.get_node_y())):
                        # Richtung in die jetzt gefahren wird, aus unerkundet löschen
                        try:
                            self.scanned_nodes_and_unexplored_paths.get((self.get_node_x(), self.get_node_y())).remove(
                            planned_orientation_to_explore)
                        except:
                            ()
                except:
                    ()

                ev3.Sound.beep()

                end_status = self.start_driving(planned_orientation_to_start_driving,mechanics)

                
                for i in range(length):
                    if i == length-1:
                        print("Reached again node", shortest_path_2[len(shortest_path_2)-1][0],"arriving from",shortest_path_2[i][2].value)
                        orientation_of_robot = self.correct_to_range_0_270(shortest_path_2[i][2].value + 180)
                        
                        if self.robi_mode == RobiMode.DRIVING_SHORTEST_PATH_TO_NODE_WHERE_EXIST_PATHS_TO_EXPLORE:
                            end_status = EndStatus.STOPPED_DRIVING_TO_TARGET
                            self.robi_mode = RobiMode.EXPLORING

                            start_direction = real_direction

                            communication.path_message(self.get_node_x(), self.get_node_y(),
                                            start_direction, 
                                            
                                            shortest_path_2[i][0][0], shortest_path_2[i][0][1], 
                                            shortest_path_2[i][2].value, 
                                            "free")
                            self.handle_message(message, planet)


                            node_exists_in_planned_path = False
                            for element in shortest_path_2:
                                if element[0] == (self.get_node_x(), self.get_node_y()):
                                    node_exists_in_planned_path = True

                            if not node_exists_in_planned_path:
                                print("Robi was not on it's planned path")
                                if self.robi_mode == RobiMode.DRIVING_TO_TARGET:
                                    shortest_path_2 = planet.shortest_path_2((self.get_node_x(), self.get_node_y()), self.target)
                                elif self.robi_mode == RobiMode.DRIVING_SHORTEST_PATH_TO_NODE_WHERE_EXIST_PATHS_TO_EXPLORE:
                                    shortest_path_2 = planet.shortest_path_2((self.get_node_x(), self.get_node_y()), shortest_path_2[len(shortest_path_2)-1][0])
                                
                                break   

                        elif self.robi_mode == RobiMode.DRIVING_TO_TARGET:
                            print("Robi has reached it's final target")
                            self.robi_mode = RobiMode.FINISHED
                            communication.complete_message("Robi has reached it's final target","targetReached")
                    else:
                        print("On way back to node",shortest_path_2[len(shortest_path_2)-1][0],"calling at", shortest_path_2[i+1][0], "arriving from",shortest_path_2[i][2].value, "heading",shortest_path_2[i+1][1].value)
                        
                        start_direction = shortest_path_2[i][1].value

                        start_direction = real_direction

                        communication.path_message(self.get_node_x(), self.get_node_y(),
                                            start_direction, 
                                            
                                            shortest_path_2[i][0][0], shortest_path_2[i][0][1], 
                                            shortest_path_2[i][2].value, 
                                            "free")
                        self.handle_message(message, planet)
                        


                        node_exists_in_planned_path = False
                        for element in shortest_path_2:
                            if element[0] == (self.get_node_x(), self.get_node_y()):
                                print(self.get_node_x(), self.get_node_y(),"does not exist on planned path")
                                
                                node_exists_in_planned_path = True

                        if not node_exists_in_planned_path:
                            print("Robi was not on it's planned path")
                            if self.robi_mode == RobiMode.DRIVING_TO_TARGET:
                                shortest_path_2 = planet.shortest_path_2((self.get_node_x(), self.get_node_y()), self.target)
                            elif self.robi_mode == RobiMode.DRIVING_SHORTEST_PATH_TO_NODE_WHERE_EXIST_PATHS_TO_EXPLORE:
                                shortest_path_2 = planet.shortest_path_2((self.get_node_x(), self.get_node_y()), shortest_path_2[len(shortest_path_2)-1][0])
                            self.robi_mode = RobiMode.EXPLORING
                            end_status = EndStatus.STOPPED_DRIVING_TO_TARGET
                            break   
                        
                        communication.path_select_message(shortest_path_2[i][0][0], shortest_path_2[i][0][1],
                                                        shortest_path_2[i+1][1].value)
                        
                        
                        planned_orientation_to_explore = shortest_path_2[i+1][1].value
                        orientation_of_robot = self.correct_to_range_0_270(shortest_path_2[i][2].value + 180)
                    

                     


                    if self.robi_mode == RobiMode.DRIVING_SHORTEST_PATH_TO_NODE_WHERE_EXIST_PATHS_TO_EXPLORE or self.robi_mode == RobiMode.DRIVING_TO_TARGET:
                        
                        self.set_node_orientation(planned_orientation_to_explore)
                        self.handle_message(message, planet)
                        sleep(2)
                        planned_orientation_to_explore = self.get_node_orientation()
                        
                        real_direction = planned_orientation_to_explore # wenn Mutterschiff eingegriffen, dann start direction korrekt -> nächste Knoten korrekt erkannt und von Pfad abgekommen


                        planned_orientation_to_start_driving = self.correct_to_range_0_270(
                            planned_orientation_to_explore - orientation_of_robot)

                        print("Planned orientation following compass            ", planned_orientation_to_explore)
                        print("Planned orientation considering robot orientation", planned_orientation_to_start_driving)

                        try:
                            if planned_orientation_to_explore in self.scanned_nodes_and_unexplored_paths.get(
                                (self.get_node_x(), self.get_node_y())):
                                try:
                                    # Richtung in die jetzt gefahren wird, aus unerkundet löschen
                                    self.scanned_nodes_and_unexplored_paths.get((self.get_node_x(), self.get_node_y())).remove(
                                planned_orientation_to_explore)
                                except:
                                    ()
                        except:
                            ()

                        ev3.Sound.beep()

                        end_status = self.start_driving(planned_orientation_to_start_driving,mechanics)



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

    def start_driving(self, planned_orientation_to_start_driving,mechanics):
        if planned_orientation_to_start_driving == 0:
            end_status = mechanics.go_0_degrees()
        if planned_orientation_to_start_driving == 90:
            end_status = mechanics.go_90_degrees()
        if planned_orientation_to_start_driving == 180:
            end_status = mechanics.go_180_degrees()
        if planned_orientation_to_start_driving == 270:
            end_status = mechanics.go_270_degrees()
        return end_status
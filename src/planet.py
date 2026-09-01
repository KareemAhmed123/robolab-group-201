#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import Optional, List, Tuple, Dict


@unique
class Direction(IntEnum):
    """Directions in shortcut"""

    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""

Node = Tuple[int, int]
"""
Node represented by a tuple of two integers

First integer: x-coordinate
Second integer: y-coordinate
"""

OutgoingPaths = Dict[Direction, Tuple[Node, Direction, Weight]]

"""
Dictionary with all paths starting at a Node

Key: Direction of the path
Value: Tuple with (End-)Node, (End-)Direction and Weight of the path
"""

ShortestPath = List[Tuple[Node, Direction]]
"""
Path represented by a list of tuples, each with a Node and a Direction
"""


def set_shortest_distances(current_node, shortest_distances, smallest_distance, unvisited_nodes):
    for node in unvisited_nodes:
        if shortest_distances[node] < smallest_distance:
            smallest_distance = shortest_distances[node]
            current_node = node
    return current_node, smallest_distance


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self):
        """Initializes the data structure"""
        self.paths: Dict[Node, Dict[Direction, Tuple[Node, Direction, int]]] = {}

    # DO NOT EDIT THE METHOD SIGNATURE
    def add_path(
            self,
            start: Tuple[Node, Direction],
            target: Tuple[Node, Direction],
            weight: Weight,
    ):
        """
         Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it
        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """
        if start[0] not in self.paths:
            self.paths[start[0]] = {}
        if target[0] not in self.paths:
            self.paths[target[0]] = {}
        self.paths[start[0]][start[1]] = (target[0], target[1], weight)
        self.paths[target[0]][target[1]] = (start[0], start[1], weight)
        # YOUR CODE FOLLOWS (remove pass, please!)
        pass

    # DO NOT EDIT THE METHOD SIGNATURE
    def get_paths(self) -> Dict[Node, OutgoingPaths]:
        """
        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2),
                    Direction.WEST: ((0, 3), Direction.NORTH, 1)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """
        # print(self.paths)
        # YOUR CODE FOLLOWS (remove pass, please!)
        return self.paths
        pass

    # DO NOT EDIT THE METHOD SIGNATURE
    def shortest_path(self, start: Node, target: Node) -> Optional[ShortestPath]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: None, List[] or List[Tuple[Tuple[int, int], Direction]]
        """
        temp = start
        start = target
        target = temp
        if start in self.paths and target in self.paths:
            start_node = start
            target_node = target
        else:
            return None

        nodes_array = []
        unvisited_nodes = []
        previous_nodes: Dict[Node, Tuple[Node, Direction]] = {}
        shortest_distances: Dict[Node, float] = {}
        self.init_nodes_and_unvisited_nodes_and_shortest_distance(
            nodes_array, previous_nodes, shortest_distances, unvisited_nodes
        )

        shortest_distances[start_node] = 0

        while unvisited_nodes:
            current_node = None
            smallest_distance = float("inf")
            current_node, smallest_distance = set_shortest_distances(current_node, shortest_distances,
                                                                     smallest_distance, unvisited_nodes)
            if smallest_distance == float("inf"):
                break

            self.set_shortest_distance_from_start(current_node, previous_nodes, shortest_distances)

            unvisited_nodes.remove(current_node)

        shortest_path = []
        current_node = target_node

        while True:
            if previous_nodes[current_node] is None:
                if start == target:
                    return []
                if not shortest_path:
                    return None
                break
            shortest_path.insert(0, (current_node, previous_nodes[current_node][1]))
            current_node = previous_nodes[current_node][0]

        return shortest_path[::-1]
        pass

    # DO NOT EDIT THE METHOD SIGNATURE
    def shortest_path_2(
            self, start: Node, target: Node
    ) -> Optional[List[Tuple[Node, Direction, Direction]]]:
        """
        Returns the shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: None, List[] or List[Tuple[Tuple[int, int], Direction]]
        """

        if start in self.paths and target in self.paths:
            start_node = start
            target_node = target
        else:
            return None

        nodes_array = []
        unvisited_nodes = []
        previous_nodes: Dict[Node, Tuple[Node, Direction, Direction]] = {}
        shortest_distances: Dict[Node, float] = {}
        self.init_nodes_and_unvisited_nodes_and_shortest_distance(
            nodes_array, previous_nodes, shortest_distances, unvisited_nodes
        )

        shortest_distances[start_node] = 0

        while unvisited_nodes:
            current_node = None
            smallest_distance = float("inf")
            current_node, smallest_distance = set_shortest_distances(current_node, shortest_distances,
                                                                     smallest_distance, unvisited_nodes)
            if smallest_distance == float("inf"):
                break

            for direction in self.paths[current_node]:

                if self.paths[current_node][direction][0] not in self.paths:
                    continue
                neighboring_node = self.paths[current_node][direction][0]
                the_weight = self.paths[current_node][direction][2]
                if the_weight != -1:
                    weight = the_weight
                    path_weight = shortest_distances[current_node] + weight
                    if path_weight < shortest_distances[neighboring_node]:
                        shortest_distances[neighboring_node] = path_weight
                        previous_nodes[neighboring_node] = [
                            current_node,
                            direction,
                            self.paths[current_node][direction][1],
                        ]

            unvisited_nodes.remove(current_node)

        shortest_path = []
        current_node = target_node

        while True:
            if previous_nodes[current_node] is None:
                if not shortest_path:
                    return None
                break
            shortest_path.insert(
                0,
                (
                    current_node,
                    previous_nodes[current_node][1],
                    previous_nodes[current_node][2],
                ),
            )
            current_node = previous_nodes[current_node][0]

        return shortest_path
        pass

    def init_nodes_and_unvisited_nodes_and_shortest_distance(
            self, nodes_array, previous_nodes, shortest_distances, unvisited_nodes
    ):
        for node in self.paths:
            nodes_array.append(node)
            unvisited_nodes.append(node)
            if node not in shortest_distances:
                shortest_distances[node] = float("inf")
            if node not in previous_nodes:
                previous_nodes[node] = None

    def get_nearest_node(self, start: Node, targets: List[Node]):
        shortest_distances: Dict[Node, float] = {}
        start_node = start

        nodes_array = []
        unvisited_nodes = []
        previous_nodes: Dict[Node, Tuple[Node, Direction]] = {}
        self.init_nodes_and_unvisited_nodes_and_shortest_distance(
            nodes_array, previous_nodes, shortest_distances, unvisited_nodes
        )

        shortest_distances[start_node] = 0

        while unvisited_nodes:
            current_node = None
            smallest_distance = float("inf")
            current_node, smallest_distance = set_shortest_distances(current_node, shortest_distances,
                                                                     smallest_distance, unvisited_nodes)
            if smallest_distance == float("inf"):
                break

            self.set_shortest_distance_from_start(current_node, previous_nodes, shortest_distances)

            unvisited_nodes.remove(current_node)
        float("inf")
        keys_to_delete = []

        # print(shortest_distances)
        for key in shortest_distances:
            if key not in targets:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del shortest_distances[key]
        return min(shortest_distances, key=shortest_distances.get)

    def set_shortest_distance_from_start(self, current_node, previous_nodes, shortest_distances):
        for direction in self.paths[current_node]:
            if self.paths[current_node][direction][0] not in self.paths:
                continue
            neighboring_node = self.paths[current_node][direction][0]
            the_weight = self.paths[current_node][direction][2]
            if the_weight != -1:
                weight = the_weight
                path_weight = shortest_distances[current_node] + weight
                if path_weight < shortest_distances[neighboring_node]:
                    shortest_distances[neighboring_node] = path_weight

                    previous_nodes[neighboring_node] = [
                        current_node,
                        self.paths[current_node][direction][1],
                    ]

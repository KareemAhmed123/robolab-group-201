#!/usr/bin/env python3

import unittest

from planet import Direction, Planet


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 1)

    @unittest.skip("Example test, should not count in final test results")
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does     not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable

        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        """
        # Initialize your data structure here
        self.planet = Planet()

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        # OutgoingPaths = Dict[Direction, Tuple[Node, Direction, Weight]]
        # Dict[Node, OutgoingPaths]:
        self.planet.add_path([(1, 0), Direction.SOUTH], [(2, 0), Direction.SOUTH], 2)
        self.planet.add_path([(1, 0), Direction.EAST], [(4, 0), Direction.WEST], 8)
        paths = self.planet.get_paths()
        self.assertIsInstance(paths, dict)
        # self.assertIsInstance(next(iter(self.planet.get_paths())), Node)
        for key in paths.keys():
            self.assertIsInstance(key, tuple)
            out_going_path = paths[key]
            self.assertIsInstance(out_going_path, dict)
            self.assertIsInstance(out_going_path, dict)
            for _ in out_going_path.keys():
                self.assertIsInstance(_, Direction)
                current_direction = out_going_path[_]
                self.assertIsInstance(current_direction, tuple)
                self.assertIsInstance(current_direction[0], tuple)
                self.assertIsInstance(current_direction[1], Direction)
                self.assertIsInstance(current_direction[2], int)

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        paths = self.planet.get_paths()
        self.assertEqual(paths, {})

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        self.planet.add_path([(1, 0), Direction.SOUTH], [(2, 0), Direction.SOUTH], 2)
        self.planet.add_path([(1, 0), Direction.EAST], [(4, 0), Direction.WEST], 8)
        self.planet.add_path([(2, 0), Direction.NORTH], [(3, 0), Direction.SOUTH], 6)
        self.planet.add_path([(2, 0), Direction.EAST], [(4, 0), Direction.EAST], 5)
        self.planet.add_path([(3, 0), Direction.NORTH], [(5, 0), Direction.WEST], 1)
        self.planet.add_path([(3, 0), Direction.WEST], [(4, 0), Direction.SOUTH], 3)
        self.planet.add_path([(3, 0), Direction.EAST], [(6, 0), Direction.WEST], 9)
        self.planet.add_path([(4, 0), Direction.NORTH], [(5, 0), Direction.WEST], 2)
        self.planet.add_path([(5, 0), Direction.EAST], [(6, 0), Direction.EAST], 3)
        shortest_path = self.planet.shortest_path((1, 0), (6, 0))
        self.assertEqual(shortest_path,
                         [((1, 0), Direction.SOUTH),
                          ((2, 0), Direction.EAST),
                          ((4, 0), Direction.NORTH),
                          ((5, 0), Direction.EAST)])

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        self.planet.add_path([(1, 0), Direction.SOUTH], [(2, 0), Direction.SOUTH], 2)
        self.planet.add_path([(4, 0), Direction.SOUTH], [(3, 0), Direction.SOUTH], 2)
        shortest_path = self.planet.shortest_path((1, 0), (4, 0))
        self.assertEqual(shortest_path, None)
        shortest_path_2 = self.planet.shortest_path((1, 0), (5, 0))
        self.assertEqual(shortest_path_2, None)

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        self.planet.add_path([(1, 0), Direction.SOUTH], [(2, 0), Direction.SOUTH], 2)
        self.planet.add_path([(1, 0), Direction.EAST], [(4, 0), Direction.WEST], 2)

        self.planet.add_path([(4, 0), Direction.EAST], [(3, 0), Direction.WEST], 2)

        self.planet.add_path([(2, 0), Direction.EAST], [(5, 0), Direction.EAST], 1)
        self.planet.add_path([(5, 0), Direction.EAST], [(3, 0), Direction.EAST], 1)

        shortest_path = self.planet.shortest_path((1, 0), (3, 0))

        self.assertEqual(len(shortest_path), 2)
        shortest_path = self.planet.shortest_path_2((1, 0), (3, 0))
        self.assertEqual(len(shortest_path), 2)

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        self.planet.paths = {(68, 421): {Direction.EAST: ((68, 421), Direction.EAST, -1),
                                         Direction.NORTH: ((68, 422), Direction.SOUTH, 1)},
                             (69, 421): {Direction.WEST: ((69, 421), Direction.WEST, -1),
                                         Direction.SOUTH: ((69, 421), Direction.SOUTH, 1),
                                         Direction.NORTH: ((69, 421), Direction.NORTH, 1),
                                         Direction.EAST: ((70, 421), Direction.WEST, 4)},
                             (70, 421): {Direction.WEST: ((69, 421), Direction.EAST, 4),
                                         Direction.EAST: ((71, 421), Direction.WEST, 1)},
                             (68, 422): {Direction.SOUTH: ((68, 421), Direction.NORTH, 1)},
                             (71, 421): {Direction.NORTH: ((70, 422), Direction.EAST, 5),
                                         Direction.WEST: ((70, 421), Direction.EAST, 1),
                                         Direction.SOUTH: ((70, 420), Direction.EAST, 1)},
                             (70, 422): {Direction.EAST: ((71, 421), Direction.NORTH, 5)},
                             (70, 420): {Direction.EAST: ((71, 421), Direction.SOUTH, 1),
                                         Direction.WEST: ((70, 420), Direction.WEST, -1)}, (80, 30): {}}

        shortest_path = self.planet.shortest_path((70, 420), (70, 422))

        self.assertEqual(shortest_path,
                         [((70, 420), Direction.EAST), ((71, 421), Direction.NORTH)])

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.planet.paths = {(68, 421): {Direction.EAST: ((68, 421), Direction.EAST, -1),
                                         Direction.NORTH: ((68, 422), Direction.SOUTH, 1)},
                             (69, 421): {Direction.WEST: ((69, 421), Direction.WEST, -1),
                                         Direction.SOUTH: ((69, 421), Direction.SOUTH, 1),
                                         Direction.NORTH: ((69, 421), Direction.NORTH, 1),
                                         Direction.EAST: ((70, 421), Direction.WEST, 4)},
                             (70, 421): {Direction.WEST: ((69, 421), Direction.EAST, 4),
                                         Direction.EAST: ((71, 421), Direction.WEST, 1)},
                             (68, 422): {Direction.SOUTH: ((68, 421), Direction.NORTH, 1)},
                             (71, 421): {Direction.NORTH: ((70, 422), Direction.EAST, 5),
                                         Direction.WEST: ((70, 421), Direction.EAST, 1),
                                         Direction.SOUTH: ((70, 420), Direction.EAST, 1)},
                             (70, 422): {Direction.EAST: ((71, 421), Direction.NORTH, 5)},
                             (70, 420): {Direction.EAST: ((71, 421), Direction.SOUTH, 1),
                                         Direction.WEST: ((70, 420), Direction.WEST, -1)}, (80, 30): {}}

        shortest_path = self.planet.shortest_path((70, 420), (80, 30))

        self.assertEqual(shortest_path,
                         None)

    def test_target_reachable_loop_2(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """

        self.planet.paths = {(68, 421): {Direction.EAST: ((68, 421), Direction.EAST, -1),
                                         Direction.NORTH: ((68, 422), Direction.SOUTH, 1)},
                             (69, 421): {Direction.WEST: ((69, 421), Direction.WEST, -1),
                                         Direction.SOUTH: ((69, 421), Direction.SOUTH, 1),
                                         Direction.NORTH: ((69, 421), Direction.NORTH, 1),
                                         Direction.EAST: ((70, 421), Direction.WEST, 4)},
                             (70, 421): {Direction.WEST: ((69, 421), Direction.EAST, 4),
                                         Direction.EAST: ((71, 421), Direction.WEST, 1)},
                             (68, 422): {Direction.SOUTH: ((68, 421), Direction.NORTH, 1)},
                             (71, 421): {Direction.NORTH: ((70, 422), Direction.EAST, 5),
                                         Direction.WEST: ((70, 421), Direction.EAST, 1),
                                         Direction.SOUTH: ((70, 420), Direction.EAST, 1)},
                             (70, 422): {Direction.EAST: ((71, 421), Direction.NORTH, 5)},
                             (70, 420): {Direction.EAST: ((71, 421), Direction.SOUTH, 1),
                                         Direction.WEST: ((70, 420), Direction.WEST, -1)}}
        shortest_path = self.planet.shortest_path_2((70, 420), (70, 422))

        self.assertEqual(shortest_path,
                         [((71, 421), Direction.EAST, Direction.SOUTH),
                          ((70, 422), Direction.NORTH, Direction.EAST)])
        self.planet.paths = {(1, 10): {Direction.NORTH: ((1, 12), Direction.SOUTH, 9)},
                             (1, 12): {Direction.SOUTH: ((1, 10), Direction.NORTH, 9),
                                       Direction.NORTH: ((1, 13), Direction.SOUTH, 12)},
                             (1, 13): {Direction.SOUTH: ((1, 12), Direction.NORTH, 12),
                                       Direction.NORTH: ((0, 14), Direction.EAST, 7),
                                       Direction.WEST: ((0, 12), Direction.NORTH, 6)},
                             (0, 12): {Direction.WEST: ((-1, 12), Direction.EAST, 5),
                                       Direction.SOUTH: ((0, 11), Direction.NORTH, 7),
                                       Direction.NORTH: ((1, 13), Direction.WEST, 6)},
                             (-1, 12): {Direction.EAST: ((0, 12), Direction.WEST, 5)},
                             (0, 11): {Direction.NORTH: ((0, 12), Direction.SOUTH, 7)},
                             (0, 14): {Direction.EAST: ((1, 13), Direction.NORTH, 7),
                                       Direction.WEST: ((0, 14), Direction.WEST, -1),
                                       Direction.SOUTH: ((0, 14), Direction.SOUTH, 5)}}
        shortest_path = self.planet.shortest_path_2((0, 14), (0, 12))

        self.assertEqual(shortest_path,
                         [((1, 13), Direction.EAST, Direction.NORTH),
                          ((0, 12), Direction.WEST, Direction.NORTH)])


if __name__ == "__main__":
    unittest.main()

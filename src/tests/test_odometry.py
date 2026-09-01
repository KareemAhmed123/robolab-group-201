#!/usr/bin/env python3

import unittest

from src.odometry import Odometry


class TestRoboLabOdo(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        """
        # Initialize your data structure here
        self.odo = Odometry()

    def test_coordinates(self):
        positions = [(0, 13), (15, 57), (41, 75), (67, 88), (82, 101), (102, 122), (120, 136), (140, 150), (156, 163),
                     (171, 177), (189, 195), (203, 209), (222, 229), (238, 243), (252, 258), (269, 273), (283, 289),
                     (300, 305), (321, 326), (342, 348), (366, 369), (388, 389), (405, 409), (418, 424), (433, 440),
                     (450, 456), (463, 472), (479, 486), (498, 503), (516, 521), (531, 538), (547, 554), (563, 570),
                     (580, 586), (595, 601), (610, 620), (626, 636), (644, 651), (661, 667), (676, 681), (690, 696),
                     (706, 711), (720, 727), (738, 743), (756, 762), (776, 781), (790, 799), (808, 816), (825, 832),
                     (841, 849), (859, 866), (882, 885), (902, 905), (920, 923), (939, 943), (956, 961), (970, 977),
                     (988, 993), (1008, 1010), (1025, 1028), (1038, 1045), (1055, 1066), (1074, 1081), (1091, 1096),
                     (1108, 1116), (1125, 1135), (1140, 1152), (1158, 1170), (1176, 1188)]
        for i in positions:
            self.odo.add_positions(i[0], i[1])
        self.odo.calculate_all()



if __name__ == "__main__":
    unittest.main()

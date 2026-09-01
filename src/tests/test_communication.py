#!/usr/bin/env python3

import unittest.mock
import paho.mqtt.client as mqtt
import uuid
import json

from src.communication import Communication
"""
IMPORTANT: THOSE TESTS ARE NOT REQUIRED FOR THE EXAM AND USED ONLY FOR DEVELOPMENT
ASK YOUR TUTOR FOR SPECIFIC DETAILS ABOUT THIS!
"""


class TestRoboLabCommunication(unittest.TestCase):
    @unittest.mock.patch('logging.Logger')
    def setUp(self, mock_logger):
        """
        Instantiates the communication class
        """
        client_id = '201' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
        client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                             clean_session=False,  # We want to be remembered
                             protocol=mqtt.MQTTv311  # Define MQTT protocol version
                             )

        # Initialize your data structure here
        self.communication = Communication(client, mock_logger)
        self.communication.client.publish = unittest.mock.Mock()

    def test_message_ready(self):
        """
        This test should check the syntax of the message type "ready"
        """
        self.communication.ready_message()

        expected_topic = "explorer/201"
        #message = unittest.mock.Mock()
        expected_msg = {"from": "client", "type": "ready"}
        #message.payload = json.dumps(msg).encode('utf-8')
        self.communication.client.publish.assert_called_with(expected_topic, json.dumps(expected_msg))

    def test_message_path(self):
        """
        This test should check the syntax of the message type "path"
        """
        self.communication.path_message(25, -19, 0, 26, -17, 0, "free")
        expected_topic = "planet/Forever/201"
        expected_msg = {
                        "from": "client",
                        "type": "path",
                        "payload": {
                            "startX": 25,
                            "startY": -19,
                            "startDirection": 0,
                            "endX": 26,
                           # "endY": nd_y,
                            #"endDirection": end_direction,
                            #"pathStatus": path_status
                        }
                    }

    def test_message_path_invalid(self):
        """
        This test should check the syntax of the message type "path" with errors/invalid data
        """
        self.fail('implement me!')

    def test_message_select(self):
        """
        This test should check the syntax of the message type "pathSelect"
        """
        self.fail('implement me!')

    def test_message_complete(self):
        """
        This test should check the syntax of the message type "explorationCompleted" or "targetReached"
        """
        self.fail('implement me!')


if __name__ == "__main__":
    unittest.main()

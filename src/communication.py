#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import ssl
from time import sleep
import time
from planet import Direction, Planet
from queue import Queue


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    server_messages = Queue()

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler
        # Add your client setup here
        self.planet = None

        self.client.tls_insecure_set(False)
        self.logger = logger
        self.client.subscribe(f"explorer/201")
        self.client.subscribe(f"comtest/201")

        self.client.username_pw_set(
            "201", password="qJAmEdCXJ1"
        )  # Your group credentials, see the python skill-test for your group password
        self.client.connect("mothership.inf.tu-dresden.de", port=8883)
        self.client.loop_start()

        self.retainFlag = False
        self.client.subscribe(f"explorer/201")

        self.test_planet_message("Examinator-X-42b")

    def __del__(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        planet = Planet()

        payload = json.loads(message.payload.decode("utf-8"))

        if "payload" in payload:

            if payload["from"] == "debug":
                # print(f"Message received: {message.topic} -> {message.payload.decode('utf-8')}")
                ()

            if payload["from"] == "server":
                # print(f"Message received: {message.topic} -> {message.payload.decode('utf-8')}")
                self.server_messages.put(payload)

            self.logger.debug(json.dumps(payload, indent=2))

    def subscribe_for_planet(self, planet):
        self.client.subscribe(f"explorer/201")
        self.client.subscribe(f"comtest/201")

        self.client.subscribe(f"planet/{planet}/201")

    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        # print(f"Send Message : {topic} -> {message}")
        self.logger.debug("Send to: " + topic)
        self.logger.debug(json.dumps(message, indent=2))
        self.client.publish(topic, payload=message, qos=2, retain=self.retainFlag)

        # YOUR CODE FOLLOWS (remove pass, please!)

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback

            traceback.print_exc()
            raise

    def test_planet_message(self, planet_name):

        msg = {
            "from": "client",
            "type": "testPlanet",
            "payload": {"planetName": planet_name},
        }
        self.send_message("explorer/201", json.dumps(msg, indent=2))
        time.sleep(2)

    def ready_message(self):
        msg = {"from": "client", "type": "ready"}

        self.send_message("explorer/201", json.dumps(msg, indent=2))
        time.sleep(2)

    def path_message(
            self,
            start_x,
            start_y,
            start_direction,
            end_x,
            end_y,
            end_direction,
            path_status,
    ):
        msg = {
            "from": "client",
            "type": "path",
            "payload": {
                "startX": start_x,
                "startY": start_y,
                "startDirection": start_direction,
                "endX": end_x,
                "endY": end_y,
                "endDirection": end_direction,
                "pathStatus": path_status,
            },
        }
        # print(self.planet)
        self.send_message(f"planet/{self.planet}/201", json.dumps(msg, indent=2))
        time.sleep(2)

    def path_select_message(self, start_x, start_y, start_direction):
        msg = {
            "from": "client",
            "type": "pathSelect",
            "payload": {
                "startX": start_x,
                "startY": start_y,
                "startDirection": start_direction,
            },
        }
        # print(self.planet)
        self.send_message(f"planet/{self.planet}/201", json.dumps(msg, indent=2))
        # self.set_node_orientation(msg["payload"]["startDirection"])
        time.sleep(2)

    def complete_message(self, text, complete_type):
        msg = {"from": "client", "type": complete_type, "payload": {"message": text}}
        # print(self.planet)
        self.send_message(f"explorer/201", json.dumps(msg, indent=2))
        time.sleep(2)

    def set_planet(self, planet):
        self.planet = planet

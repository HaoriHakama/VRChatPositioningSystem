import argparse
from pythonosc import udp_client
from state import State


class OscClient:

    def __init__(self, state : State) -> None:
        self.state = state

    def launch_osc_client(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default=self.state.ip_of_server, help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=9000, help="The port of the OSC server is listening on")

        args = parser.parse_args()

        self.state.client = udp_client.SimpleUDPClient(args.ip, args.port)
        
        print("クライアント起動成功")
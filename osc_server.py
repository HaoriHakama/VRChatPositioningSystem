import argparse
from pythonosc import dispatcher
from pythonosc import osc_server
from state import State
import position_explore


class OscServer:

    def __init__(self, state : State) -> None:
        self.state = state

    # OSCサーバーの起動・実行
    def launch_osc_server(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1",help="The ip to listen on")
        parser.add_argument("--port", type=int, default=9001,help="The port to listen on")
        args = parser.parse_args()

        dpt = dispatcher.Dispatcher()
        dpt.map("/avatar/parameters/VRCPS*", self.on_VRCPS_received)

        self.server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dpt)
        print("Serving on {}".format(self.server.server_address))
        self.server.serve_forever()

    def on_VRCPS_received(self, address: str, *args: list[any]):
        if address == "/avatar/parameters/VRCPS_measure":
            if args[0] == True:
                position_explore.start_position_explore(self.state)
                self.state.position_explore = None
        else:
            position_explore.on_VRCPS_received(address, args[0], self.state)
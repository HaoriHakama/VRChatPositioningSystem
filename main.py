from osc_server import OscServer
from osc_client import OscClient
from state import State
from threading import Thread


state = State()
state.server = OscServer(state)
state.client = OscClient(state)

server_thread = Thread(target=state.server.launch_osc_server)
client_thread = Thread(target=state.client.launch_osc_client)

server_thread.start()
client_thread.start()

server_thread.join()
client_thread.join()
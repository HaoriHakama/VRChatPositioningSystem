


# osc_server, client間で共有する変数を保存するクラス
class State:

    def __init__(self) -> None:
        # server
        self.server = None

        # client
        self.client = None
        self.ip_of_server = "192.168.11.2"

        # position_explore.PositionExploreのインスタンス
        self.position_explore = None
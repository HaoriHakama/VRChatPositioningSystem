import numpy as np
import math
import time
from threading import Thread
from state import State
import random


# 外部から呼び出される部分
# ########################################################################
# position_exploreの実行
def start_position_explore(state: State):
    print("nya")
    if state.position_explore != None:
        print("Eroor: position_exploreを実行中です")
        return
    
    state.position_explore = PositionExplore(state)

    thread1 = Thread(target=state.position_explore.get_position)
    thread1.start()
    thread1.join()

    state.client.send_message("/avatar/parameters/VRCPS_measure", False)

    print("{0[0]:.2f}, {0[1]:.2f}, {0[2]:.2f}".format(state.position_explore.pos_player))
    
    return state.position_explore.pos_player

def on_VRCPS_received(address: str, param, state : State):
    if state.position_explore == None:
        return
    else:
        state.position_explore.on_osc_reseived(address, param)

# ########################################################################
# 外部から呼び出される部分


# プレイヤーの絶対座標を取得するクラス
class PositionExplore:

    POS_SATELLITE = [
            [50 ,0, 0],
            [-50, 0, 0],
            [0, 50, 0],
            [0, -50, 0],
            [0, 0, 50],
            [0, 0, -50]
        ]
    
    def __init__(self, state: State) -> None:
        self.state = state
        self.client = state.client
        # プレイヤー座標の初期化
        self.pos_player = [None, None, None]
        # サテライトの数
        self.number_of_satellite = len(PositionExplore.POS_SATELLITE)
        # ContactReseiverの移動量の初期化
        self.receiver_movement = 0
        # 各サテライトからの距離の初期化
        self.distances = [None for _ in range(self.number_of_satellite)]
        # 各衛星から受信するパラメータの初期化
        # 各衛星から2回受信する
        self.contact_signal = [
            [{"movement" : None, "contact" : None}, {"movement" : None, "contact" : None}] for _ in range(self.number_of_satellite)
        ]
        # 探索終了時Trueになる
        self.explore_end = False
    
    def __del__(self):
        pass

    # OSCの受信時の処理
    def on_osc_reseived(self, address: str, param):
        
        # contact_receiverに関するパラメーターを受け取った場合の処理を記述した内部メソッド
        def __on_contact_received(index, param):
            if self.distances[index] != None:
                return
            elif self.contact_signal[index][0]["movement"] == None:
                self.contact_signal[index][0]["movement"] = self.receiver_movement
                self.contact_signal[index][0]["contact"] = param
                return
            elif self.contact_signal[index][1]["movement"] == None:
                if self.receiver_movement == self.contact_signal[index][0]['movement']:
                    return
                self.contact_signal[index][1]["movement"] = self.receiver_movement
                self.contact_signal[index][1]["contact"] = param
            
            # ここの計算は[後で作る]を参照
            t1 = self.contact_signal[index][0]["movement"]
            t2 = self.contact_signal[index][1]["movement"]
            r1 = 1 - self.contact_signal[index][0]["contact"] + 0.005
            r2 = 1 - self.contact_signal[index][1]["contact"] + 0.005

            _x = (r1**2 - r2**2) / (-2*t1 + 2*t2) + (t1 + t2) / 2
            _y2 = r1**2 - (_x - t1)**2

            self.distances[index] = math.sqrt(_x**2 + _y2)
        
        ###にゃん###
        if address == "/avatar/parameters/VRCPS_receiver_movement":
            self.receiver_movement = param * 1000
            return
        for index in range(self.number_of_satellite):
            _address = "/avatar/parameters/VRCPS_satellite_" + str(index) + "_contact"
            if address == _address and param > 0:
                __on_contact_received(index, param)
        
        # n点以上測定できた場合、探索を終了
        MIN_NUMBER_OF_SATELLITE = 5
        count = 0
        for dist in self.distances:
            if dist != None:
                count += 1
            if count > MIN_NUMBER_OF_SATELLITE:
                self.explore_end = True
                return
        return

    def get_position(self):
        self.__explore()
        _ = self.__calc_position()

    def __explore(self):
        movement = 0.0
        while self.explore_end == False:
            if movement < 1000:
                self.__move_receiver(movement)
                time.sleep(0.0005)
                movement += 0.5
            else:
                break

    def __move_receiver(self, movement):
        # パラメータが0のとき移動量は0m
        # パラメータが1のとき移動量は1000m
        param = movement * 0.001
        self.client.send_message("/avatar/parameters/VRCPS_receiver_movement", param)
        return
    
    def __calc_position(self):

        LIMIT = 0.00000001
        measured_distances = []
        pos_satellite = []

        # 測定結果の整形
        count = 0
        for i in range(self.number_of_satellite):
            if self.distances[i] != None:
                measured_distances.append(self.distances[i])
                pos_satellite.append(PositionExplore.POS_SATELLITE[i])
                count += 1
        if count < 4:
            print("position_explore: 測定結果が不足しています")
            return
        
        def dist(p1, p2):
            return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2 +
            (p1[2] - p2[2]) ** 2
        )

        R = measured_distances
        X = np.array([5.0, 2.0, 3.0, 1.0])

        for _ in range(1000):
            DR = np.array([r - dist(X, p) for r, p in zip(R, pos_satellite)])

            A = np.array([
                [
                    - (p[0] - X[0]) / dist(X, p), 
                    - (p[1] - X[1]) / dist(X, p), 
                    - (p[2] - X[2]) / dist(X, p), 
                    1
                ] for p in pos_satellite
            ])

            DX = (np.linalg.inv(A.T @ A) @ A.T) @ DR
            # print(f"DX: {DX}")
            if np.inner(DX[:3], DX[:3]) < LIMIT:
                self.pos_player[0] = X[0]
                self.pos_player[1] = X[1]
                self.pos_player[2] = X[2]
                return X

            if np.isnan(X[0]):
                break
            X[:3] += DX[:3]

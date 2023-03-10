# VRChatPositioningSystem(VRChat測位システム)
VRChat Avatar for getting absolute coordinates relative to the world origin using OSC  
OSCで絶対座標(x, y, z)を取得するためのアバターです  

## 導入方法
  1. リポジトリ内のすべてのファイルをDL
  2. VRchat Creator CompanionでAvatar Projectを作成し、unitypackageをインポートし、アバターをVRChatにアップロード
  3. state.pyを開き、プライベートipアドレスを書き換え
## 使用方法
  1. VRChatでOSCをEnableにする
  2. main.pyを実行
  3. 止まる <- ここ重要!!!!
  3. ExpressionMenuのVRCPS_Avatar -> 現在座標の測定
  4. 現在座標がターミナル表示されます

## 使用パラメーター
  * Expression Parameter
    * VRCPS_measure: Bool
    * VRCPS_receiver_movement: Float
  * Fxレイヤー
    * 同上
  
## 別アバターへの導入
  * 可及的速やかに実装いたします

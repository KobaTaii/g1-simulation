import os
import sys
import time
import json
import zmq
import pandas as pd
import termios
import tty

CSV_PATH = "assets/g1_motion.csv"

def get_key_nonblocking():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    if not os.path.exists(CSV_PATH):
        print(f"エラー: {CSV_PATH} が存在しません。先に `uv run python scripts/download_assets.py` を実行してください。")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://127.0.0.1:5555")

    print("\n==========================================")
    print(" 's' キーを押すと、G1 モーション再生を開始します。")
    print("==========================================")

    while True:
        key = get_key_nonblocking()
        if key.lower() == 's':
            print("\n>> G1 モーション再生を開始します...")
            break
        elif key == '\x03':  # Ctrl+C
            print("\n中止しました。")
            return

    time.sleep(0.5)

    for index, row in df.iterrows():
        timestamp = float(row.iloc[0])
        joint_positions = row.iloc[1:].values.astype(float).tolist()

        payload = {
            "timestamp": timestamp,
            "qpos": joint_positions,
            "end_of_stream": False
        }

        socket.send_string(json.dumps(payload))
        time.sleep(0.02)  # 50Hz (20ms周期)

    socket.send_string(json.dumps({"end_of_stream": True}))

    print("\n------------------------------------------")
    print("再生が終わりました")
    print("------------------------------------------")

    socket.close()
    context.term()

if __name__ == "__main__":
    main()

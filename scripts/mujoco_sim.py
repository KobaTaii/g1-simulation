import os
import sys
import time
import json
import zmq
import mujoco
import mujoco.viewer

# g1.xml ではなく scene.xml を指定
MODEL_PATH = "assets/g1/scene.xml"

def main():
    if not os.path.exists(MODEL_PATH):
        print(f"エラー: {MODEL_PATH} が存在しません。先に `uv run python scripts/download_assets.py` を実行してください。")
        sys.exit(1)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.bind("tcp://127.0.0.1:5555")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.setsockopt(zmq.RCVTIMEO, 10)

    print(f"MuJoCo で G1 シーンモデル ({MODEL_PATH}) を読み込んでいます...")
    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    data = mujoco.MjData(model)

    print("G1 シミュレータ起動完了。ZMQ 経由のモーションデータを受信待ち...")
    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            step_start = time.time()

            try:
                msg = socket.recv_string()
                payload = json.loads(msg)

                if payload.get("end_of_stream"):
                    print("[Sim] モーションストリームが終了しました。")
                else:
                    qpos_targets = payload.get("qpos", [])
                    for i, target in enumerate(qpos_targets):
                        if i < model.nu:
                            data.ctrl[i] = target

            except zmq.Again:
                pass

            mujoco.mj_step(model, data)
            viewer.sync()

            time_until_next_step = model.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)

    socket.close()
    context.term()

if __name__ == "__main__":
    main()

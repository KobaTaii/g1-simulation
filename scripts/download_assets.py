import os
import sys
import subprocess
import shutil
import numpy as np
import pandas as pd

def setup_g1_model(assets_dir: str):
    g1_dir = os.path.join(assets_dir, "g1")
    g1_xml = os.path.join(g1_dir, "g1.xml")
    scene_xml = os.path.join(g1_dir, "scene.xml")

    print(">> MuJoCo Menagerie から Unitree G1 モデルを取得中...")
    menagerie_dir = os.path.join(assets_dir, "menagerie")
    if not os.path.exists(menagerie_dir):
        cmd = [
            "git", "clone", "--depth", "1",
            "https://github.com/google-deepmind/mujoco_menagerie.git",
            menagerie_dir
        ]
        subprocess.run(cmd, check=True)

    src_g1 = os.path.join(menagerie_dir, "unitree_g1")
    if os.path.exists(src_g1):
        os.makedirs(g1_dir, exist_ok=True)
        for item in os.listdir(src_g1):
            s = os.path.join(src_g1, item)
            d = os.path.join(g1_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        for p_xml in ["g1.xml", "g1_29dof.xml"]:
            if os.path.exists(os.path.join(g1_dir, p_xml)):
                if p_xml != "g1.xml":
                    shutil.copy2(os.path.join(g1_dir, p_xml), g1_xml)
                break

    # MuJoCo 3.x スキーマに完全適合した scene.xml を生成
    scene_content = """<mujoco model="g1_scene">
  <include file="g1.xml"/>

  <statistic center="0 0 0.8" extent="2.0"/>

  <visual>
    <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>
  </visual>

  <worldbody>
    <light pos="0 0 3.5" dir="0 0 -1" directional="true"/>
    <geom name="floor" type="plane" size="10 10 0.1" rgba="0.8 0.8 0.8 1"/>
  </worldbody>
</mujoco>
"""
    with open(scene_xml, "w", encoding="utf-8") as f:
        f.write(scene_content)

    print("G1 3D メッシュモデルおよび scene.xml の準備が完了しました。")

def generate_real_g1_motion_csv(csv_path: str):
    if os.path.exists(csv_path):
        print(f"[{csv_path}] モーションデータは既に存在します。")
        return

    print(">> Unitree G1 用の 29関節 50Hz モーション CSV データを構築中...")
    
    joint_names = [
        "left_hip_pitch_joint", "left_hip_roll_joint", "left_hip_yaw_joint",
        "left_knee_joint", "left_ankle_pitch_joint", "left_ankle_roll_joint",
        "right_hip_pitch_joint", "right_hip_roll_joint", "right_hip_yaw_joint",
        "right_knee_joint", "right_ankle_pitch_joint", "right_ankle_roll_joint",
        "waist_yaw_joint", "waist_roll_joint", "waist_pitch_joint",
        "left_shoulder_pitch_joint", "left_shoulder_roll_joint", "left_shoulder_yaw_joint",
        "left_elbow_joint", "left_wrist_roll_joint", "left_wrist_pitch_joint", "left_wrist_yaw_joint",
        "right_shoulder_pitch_joint", "right_shoulder_roll_joint", "right_shoulder_yaw_joint",
        "right_elbow_joint", "right_wrist_roll_joint", "right_wrist_pitch_joint", "right_wrist_yaw_joint"
    ]

    dt = 0.02
    duration = 5.0
    t = np.arange(0, duration, dt)
    num_frames = len(t)

    data = {"time": t}
    for j_name in joint_names:
        if "knee" in j_name:
            data[j_name] = 0.4 + 0.3 * np.sin(2 * np.pi * 0.5 * t)
        elif "hip_pitch" in j_name:
            data[j_name] = -0.2 - 0.2 * np.sin(2 * np.pi * 0.5 * t)
        elif "ankle_pitch" in j_name:
            data[j_name] = -0.2 + 0.1 * np.sin(2 * np.pi * 0.5 * t)
        elif "elbow" in j_name:
            data[j_name] = 0.3 + 0.2 * np.cos(2 * np.pi * 0.5 * t)
        else:
            data[j_name] = np.zeros(num_frames)

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    print(f"成功: [{csv_path}] に 29関節モーション CSV を保存しました。")

def main():
    assets_dir = "assets"
    os.makedirs(assets_dir, exist_ok=True)
    setup_g1_model(assets_dir)
    generate_real_g1_motion_csv(os.path.join(assets_dir, "g1_motion.csv"))

if __name__ == "__main__":
    main()

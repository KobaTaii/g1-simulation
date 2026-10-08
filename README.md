# Unitree G1 Motion Simulation with MuJoCo & GEAR-SONIC / GR00T-WBC

MuJoCo シミュレータ上で ZeroMQ (ZMQ) 通信を用いて Unitree G1 ロボットの CSV モーションデータを送信・再生するプロジェクトです。
本環境は NVIDIA の [GR00T-WholeBodyControl (GEAR-SONIC) Tutorial](https://nvlabs.github.io/GR00T-WholeBodyControl/tutorials/zmq.html) に準拠しており、**Docker** および **uv** をベースとした構成で **WSL2** および **Ubuntu (Native)** の両環境に対応しています。

---

## 📁 プロジェクト構成

ホスト PC と Docker コンテナ内は共有ボリュームマウント（バインドマウント）されているため、ホスト上のエディタ（VS Code 等）で `scripts/` 内を編集するとリアルタイムでコンテナ内に反映されます。

```text
.
├── Dockerfile
├── compose.yaml
├── pyproject.toml
├── README.md
├── assets/                    # 自動ダウンロード・生成される資材
│   ├── g1/                    # Unitree G1 MJCF モデルおよび scene.xml
│   └── g1_motion.csv         # 29関節モーションデータ (50Hz)
└── scripts/                   # ホストから編集可能な共有ボリューム
    ├── download_assets.py    # G1 3Dモデル & モーションデータの準備
    ├── mujoco_sim.py         # MuJoCo G1 シミュレータ + ZMQ受信用ノード
    └── send_motion.py        # CSV読み込み・`s`キー入力受付・ZMQ送信ノード
```

---

## 🛠 動作要件

* **OS**: Ubuntu (Native) または WSL2 (Windows Subsystem for Linux)
* **GPU**: NVIDIA GPU（NVIDIA Container Toolkit インストール済み）
* **Docker**: Docker Engine & Docker Compose v2

---

## 🚀 1. 事前準備 (ホスト PC 側)

### GUI 画面表示 (X11 / Wayland) アクセス許可
MuJoCo 3D ビューアをコンテナ内から描画するため、ホスト PC のターミナルで事前に以下を実行してください。

```bash
xhost +local:root
```

---

## 📦 2. Docker コンテナの起動

コンテナのビルドとバックグラウンド起動を行います。

```bash
docker compose up -d --build
```

コンテナの動作状態を確認します。

```bash
docker compose ps
```
*STATUS が `Up` になっていることを確認してください。*

---

## ⬇️ 3. モデルおよびモーション資材の準備

コンテナ内で資材取得スクリプトを実行し、Unitree G1 の 3D メッシュモデルおよび 29 関節 50Hz モーション CSV データをダウンロード/生成します。

```bash
docker compose exec g1-sim uv run python scripts/download_assets.py
```

---

## 🎮 4. シミュレーションの実行

実行には **2つのターミナル** を使用します。

### Step 1: MuJoCo シミュレータの起動 (ターミナル 1)
1つ目のターミナルで以下のコマンドを実行します。

```bash
docker compose exec g1-sim uv run python scripts/mujoco_sim.py
```
*※ MuJoCo 3D ビューアが立ち上がり、床の上に Unitree G1 ロボットが直立して待機状態になります。*

### Step 2: モーションの送信と再生 (ターミナル 2)
新しいターミナルを開き、送信スクリプトを実行します。

```bash
docker compose exec g1-sim uv run python scripts/send_motion.py
```

画面に以下のメッセージが表示されます。

```text
==========================================
 's' キーを押すと、G1 モーション再生を開始します。
==========================================
```

**`s` キー** を押すと、シミュレータ上の G1 が CSV データに基づいて動作（屈伸・歩行アクション）を開始します。全フレームの再生完了後、ターミナルに以下が表示されて正常終了します。

```text
------------------------------------------
再生が終わりました
------------------------------------------
```

---

## 💡 トラブルシューティング

* **画面が表示されない / OpenGL エラーが発生する**:
  * ホスト側で `xhost +local:root` を実行しているか確認してください。
  * `nvidia-smi` が正常に実行できるか確認してください。
* **コンテナがすぐに終了してしまう**:
  * `compose.yaml` 内の `tty: true` および `stdin_open: true` が有効になっているか確認してください。

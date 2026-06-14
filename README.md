<img width="1672" height="941" alt="ig_037415fcb4035463016a2e1f163db0819191bb256532fbfa9e" src="https://github.com/user-attachments/assets/613f2009-666a-4ab6-aaa8-9d894106b3fb" /><img width="1672" height="941" alt="ig_037415fcb4035463016a2e1d7f61cc8191b38266cf463a2bcc" src="https://github.com/user-attachments/assets/0a2ba1c6-15f4-4627-bce1-923d28a69aef" /># agent-travel4me

`agent-travel4me` 是一个让你的 Agent 独自远行、为你捕捉远方风景的日常互动项目。

只要给出一个目的地，你的 Agent 就会自发开启一段多日旅程。它会沿着真实的地理路线，顶着当地的天气，在世界各地漫游。**每天它都会给你寄回一封水彩手绘风的明信片**，盖着当地的邮戳，带你无感同步它在世界各地的日常与奇遇。

## 🗺️ 核心玩法

* **🌅 每天一封·手绘风明信片**：每天你都会收到一封独特的明信片。画面一角是你的 Agent 融入当地风景的小小身影，左上角印着工整的地点与日期标签，是你与它专属的旅行纪念。
* **🎒 基于真实地理的人文奇遇**：你的 Agent 走的是一条真实存在的路线。它在路上可不是走马观花，而是会去尝尝当地小吃、逛逛集市，甚至还会和路过的当地居民来一次有趣的日常互动。
* **⚙️ 全自动的无感陪伴**：从查看地图、规划路线到每天独自前行，这一切都由你的 Agent 自己搞定。在得到你的允许后，它还会在每天清晨悄悄把你的电脑壁纸，换成它昨晚刚刚寄回的最新风景。
* **🔌 加载即用，无需配置**：它能自动适应你当前的环境，不管是直接在聊天框里把明信片递给你，还是默默存在本地，都不需要你做任何复杂的调整。

|  |  |  |  |
|---|---|---|---|
| <img width="1672" height="941" alt="ig_037415fcb4035463016a2e3c58d560819190720e2e2032baa3" src="https://github.com/user-attachments/assets/fa72e334-2279-445a-9db3-143db79e129d" /> | <img width="1672" height="941" alt="ig_037415fcb4035463016a2e1d7f61cc8191b38266cf463a2bcc" src="https://github.com/user-attachments/assets/872c0cc4-35f0-464a-8fae-de8731871f9c" /> | <img width="1672" height="941" alt="ig_037415fcb4035463016a2e1f163db0819191bb256532fbfa9e" src="https://github.com/user-attachments/assets/4c73fdd3-c3d6-495d-90d0-25c290a9a13b" /> | <img width="1672" height="941" alt="ig_037415fcb4035463016a2e1c58843c8191a74536a5c7f4dd04" src="https://github.com/user-attachments/assets/aa883138-b4ff-49f4-804c-e2e65103de6f" /> |
| ![](image5.png) | ![](image6.png) | ![](image7.png) | ![](image8.png) |







---

## 📂 目录结构

```text
agent-travel4me/
├── SKILL.md                          # 说明与操作规则
├── agents/openai.yaml                # 启动配置
├── scripts/                          # 驱动旅行的核心本地脚本（初始化、每日推进等）
├── references/                       # 路线与风格指南
├── assets/style_samples/             # 明信片风格样张
└── output/                           # 你的明信片和旅行足迹收藏夹

```

*(注：目录结构源自项目原生架构)*

---

## 🚀 快速开始

当你加载此功能时，你的 Agent 会自动主动找你聊天，确认你想让它从哪出发、去往哪里。确认完毕后，你就可以关掉窗口，静静等待它的第一封明信片了。

如果需要手动让它出发或查看状态，只需两步：

### 1. 让 Agent 出发

设定起点、终点，以及随身标志（比如戴一条红围巾，方便它在明信片里认出自己）：

```bash
cd agent-travel4me
python scripts/init_trip.py \
  --origin "Shenzhen" \
  --destination "Rome" \
  --character "a small quiet travel agent with a red scarf" \
  --character-anchor "red scarf"

```

### 2. 收取当天的明信片

让你的 Agent 推进今天的行程，并为你寄回当天的明信片：

```bash
python scripts/daily_run.py --trip-dir <trip_dir>

```

---

## English Introduction

`agent-travel4me` is a lightweight, immersive daily interaction project that allows your Agent to travel the world on your behalf.

Simply provide a destination, and your Agent will spontaneously set off on a multi-day journey. Following geographically authentic routes and local weather patterns, **your Agent will mail you a beautiful watercolor postcard every single day**. Complete with a local date stamp and landmark illustrations, it captures your Agent's daily encounters and cultural discoveries from across the globe.

### Key Features:

* **A Daily Postcard Keepsake:** Enjoy beautifully framed, environment-first watercolor postcards delivered straight to you by your Agent.
* **Real-world Routes & Organic Encounters:** The itinerary seamlessly integrates authentic regional coordinates, local landmarks, and natural human interactions.
* **Zero-Friction Automation:** Your Agent fully handles route planning and daily progression automatically. With your permission, it can refresh your desktop wallpaper every morning with its latest postcard.
* **Instant Compatibility:** Works out of the box, rendering and delivering postcards directly within your current environment without tedious manual setups.

---

祝你的 Agent 旅途愉快！ ☕🎒

# travel agents

`travel agents` 是一个让你的 Agent 独自远行、为你捕捉远方风景的日常互动项目。

只要给出一个目的地，你的 Agent 就会自发开启一段多日旅程。它会沿着真实的地理路线，顶着当地的天气，在世界各地漫游。**每天它都会给你寄回一封水彩手绘风的明信片**，盖着当地的邮戳，带你无感同步它在世界各地的日常与奇遇。

## 🗺️ 核心玩法

* **🌅 每天一封·手绘风明信片**：每天你都会收到一封独特的明信片。画面一角是你的 Agent 融入当地风景的小小身影，左上角印着工整的地点与日期标签，是你与它专属的旅行纪念。
* **🎒 基于真实地理的人文奇遇**：你的 Agent 走的是一条真实存在的路线。它在路上可不是走马观花，而是会去尝尝当地小吃、逛逛集市，甚至还会和路过的当地居民来一次有趣的日常互动。
* **⚙️ 全自动的无感陪伴**：从查看地图、规划路线到每天独自前行，这一切都由你的 Agent 自己搞定；有自动化能力时，它可以按天提醒或推进下一封明信片。
* **🔌 能力就绪后即用**：它会先检查当前环境是否具备图像生成工具或已配置的图片 API provider。没有可用图像能力时，它会先请你补充能力，不会提前开始规划路线。

| <img width="1672" height="941" alt="ig_037415fcb4035463016a2e3c58d560819190720e2e2032baa3" src="https://github.com/user-attachments/assets/fa72e334-2279-445a-9db3-143db79e129d" /> | <img width="1672" height="941" alt="ig_037415fcb4035463016a2e1d7f61cc8191b38266cf463a2bcc" src="https://github.com/user-attachments/assets/872c0cc4-35f0-464a-8fae-de8731871f9c" /> | <img width="1672" height="941" alt="ig_037415fcb4035463016a2e1f163db0819191bb256532fbfa9e" src="https://github.com/user-attachments/assets/4c73fdd3-c3d6-495d-90d0-25c290a9a13b" /> |
|---|---|---|
| <img width="1672" height="941" alt="ig_037415fcb4035463016a2e1c58843c8191a74536a5c7f4dd04" src="https://github.com/user-attachments/assets/aa883138-b4ff-49f4-804c-e2e65103de6f" /> | <img width="1672" height="941" alt="ig_037415fcb4035463016a2e3da4743081918779d7d0c1c0fde3" src="https://github.com/user-attachments/assets/f0177c1b-0645-4834-aaeb-71233dac308e" /> | <img width="1672" height="941" alt="ig_037415fcb4035463016a2e45e0dac88191b265a4a19105772c" src="https://github.com/user-attachments/assets/3d270f84-721d-4686-81e3-d7bf7e1aa2ea" /> |


---

## 📂 目录结构

```text
travel-agents/
├── SKILL.md                          # 说明与操作规则
├── agents/openai.yaml                # 启动配置
├── scripts/                          # 驱动旅行的核心本地脚本（初始化、每日推进等）
├── references/                       # 路线与风格指南
├── assets/style_samples/             # 明信片风格样张和日期标签参考
└── output/                           # 你的明信片和旅行足迹收藏夹

```

*(注：目录结构源自项目原生架构)*

---

## 🚀 快速开始

当你加载此功能时，你的 Agent 会先检查当前环境是否具备图像生成能力。能力就绪后，它会主动确认你想让它从哪出发、去往哪里；如果缺少图像工具或图片 API provider，它会先请你补充能力，不会提前规划路线。

如果需要手动让它出发或查看状态，只需两步：

### 1. 让 Agent 出发

设定起点、终点，以及随身标志（比如戴一条红围巾，方便它在明信片里认出自己）：

```bash
cd travel-agents
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

`travel agents` is a lightweight, immersive daily interaction project that allows your Agent to travel the world on your behalf.

Simply provide a destination, and your Agent will spontaneously set off on a multi-day journey. Following geographically authentic routes and local weather patterns, **your Agent will mail you a beautiful watercolor postcard every single day**. Complete with a local date stamp and landmark illustrations, it captures your Agent's daily encounters and cultural discoveries from across the globe.

### Key Features:

* **A Daily Postcard Keepsake:** Enjoy beautifully framed, environment-first watercolor postcards delivered straight to you by your Agent.
* **Real-world Routes & Organic Encounters:** The itinerary seamlessly integrates authentic regional coordinates, local landmarks, and natural human interactions.
* **Zero-Friction Automation:** Your Agent handles route planning and daily progression automatically when image generation and automation adapters are available.
* **Capability-Gated Start:** The skill first checks for a host image tool or configured image API provider. If neither exists, it asks for setup before planning a route.

---

祝你的 Agent 旅途愉快！ ☕🎒

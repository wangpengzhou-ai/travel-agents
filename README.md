# agent-travel4me

## 中文介绍

`agent-travel4me` 是一个面向编码代理的旅行壁纸 Skill。它会根据用户给定的出发地、目的地、Agent 形象和视觉风格，规划一条多日旅行路线，并为每天生成可用于桌面的旅行壁纸提示词、路线数据和图片产物。

这个项目的核心目标不是做一个固定 UI，而是提供一套可移植的本地工作流：编码代理可以调用脚本检测环境、初始化旅程、生成角色参考图、逐日生成壁纸、调整图片尺寸，并在用户明确允许后设置桌面壁纸。

### 主要能力

- 检测本地环境、屏幕尺寸、图片生成 Provider、桌面壁纸和自动化能力。
- 根据起点、终点和距离估算旅行天数，生成旅程状态文件。
- 维护小型、连续出现的 Agent 旅行者形象，让它在不同地点自然互动。
- 输出每日壁纸提示词、路线 GeoJSON 和图片文件。
- 支持 OpenAI、Gemini、Seedream 或外部命令形式的图片生成 Provider。
- 可选地安装每日自动运行计划，或在用户授权后设置本机壁纸。

### 目录结构

- `agent-travel4me/SKILL.md`: Skill 入口说明和操作规则。
- `agent-travel4me/scripts/`: 本地工作流脚本。
- `agent-travel4me/references/`: 路线规划、提示词契约、视觉风格和平台说明。
- `agent-travel4me/assets/style_samples/`: 内置视觉风格样张。
- `style-samples/`: 早期风格探索样张。
- `output/`: 生成结果示例和路线壁纸样张。
- `agent-travel4me-project-plan.md`: 项目计划和设计记录。

### 快速开始

```bash
cd agent-travel4me
python scripts/detect_environment.py --json
```

初始化一次旅程：

```bash
python scripts/init_trip.py \
  --origin "Shenzhen" \
  --destination "Rome" \
  --character "a small quiet travel agent with a red scarf" \
  --style watercolor_postcard
```

生成角色参考图或每日壁纸前，可以先 dry run：

```bash
python scripts/generate_character_reference.py --trip-dir <trip_dir> --dry-run
python scripts/daily_run.py --trip-dir <trip_dir> --dry-run
```

实时图片生成需要本地配置对应环境变量，例如 `OPENAI_API_KEY`、`GOOGLE_API_KEY`、`GEMINI_API_KEY`、`SEEDREAM_API_KEY` 或 `TRAVEL4ME_IMAGE_COMMAND`。项目不会要求用户把 API Key 粘贴到对话里。

## English

`agent-travel4me` is a coding-agent skill for running a daily AI wallpaper journey. Given an origin, destination, Agent identity, and visual style, it plans a multi-day route and produces daily wallpaper prompts, route data, and image artifacts.

The project is intentionally local and portable. It does not assume a fixed UI. A coding agent can run the scripts to detect the environment, initialize a trip, generate a character reference, produce daily wallpapers, resize outputs, and set the desktop wallpaper only after explicit user approval.

### Key Features

- Detects local environment, screen size, image providers, wallpaper support, and automation options.
- Estimates journey length from the route distance and creates trip state files.
- Keeps a small recurring Agent traveler consistent across daily scenes.
- Exports daily wallpaper prompts, route GeoJSON, and generated images.
- Supports OpenAI, Gemini, Seedream, or a custom command hook for image generation.
- Can optionally install a daily run schedule or set the local wallpaper after user approval.

### Repository Layout

- `agent-travel4me/SKILL.md`: Skill entry point and operating rules.
- `agent-travel4me/scripts/`: Local workflow scripts.
- `agent-travel4me/references/`: Route planning, prompt contract, visual styles, and platform notes.
- `agent-travel4me/assets/style_samples/`: Bundled visual style samples.
- `style-samples/`: Early visual exploration samples.
- `output/`: Example generated outputs and route wallpaper samples.
- `agent-travel4me-project-plan.md`: Project plan and design notes.

### Quick Start

```bash
cd agent-travel4me
python scripts/detect_environment.py --json
```

Initialize a trip:

```bash
python scripts/init_trip.py \
  --origin "Shenzhen" \
  --destination "Rome" \
  --character "a small quiet travel agent with a red scarf" \
  --style watercolor_postcard
```

Dry run before generating live images:

```bash
python scripts/generate_character_reference.py --trip-dir <trip_dir> --dry-run
python scripts/daily_run.py --trip-dir <trip_dir> --dry-run
```

Live image generation requires local environment variables such as `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GEMINI_API_KEY`, `SEEDREAM_API_KEY`, or `TRAVEL4ME_IMAGE_COMMAND`. The workflow should not ask users to paste API keys into chat.

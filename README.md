# agent-travel4me

## 中文介绍

`agent-travel4me` 是一个面向编码代理的“Agent 替我旅行”Skill。它会根据用户给定的出发地、目的地和 Agent 形象，规划一条多日旅程，并以明信片风格为每天生成路线状态、地点信息、场景提示词和可选图片产物。

这个项目提供一套可移植的本地工作流：编码代理可以调用脚本检测环境、初始化旅程、生成角色参考图、逐日推进路线、生成当天场景素材，并在用户明确允许后把图片作为桌面壁纸使用。

### 主要能力

- 检测本地环境、屏幕尺寸、图片生成 Provider、桌面壁纸和自动化能力。
- 根据起点、终点和距离估算旅行天数，生成旅程状态文件。
- 维护小型、连续出现的 Agent 旅行者形象，让它每天尽量参与当地特色活动，并与当地人产生小互动。
- 输出每日场景提示词、路线 GeoJSON、地点/日期标签、天气上下文和可选图片文件。
- 支持宿主 coding agent 原生生图、本地 OpenAI/Gemini/Seedream Provider，或外部命令形式的图片生成 Provider。
- 可选地安装每日自动运行计划，或在用户授权后设置本机壁纸。

### 目录结构

- `agent-travel4me/SKILL.md`: Skill 入口说明和操作规则。
- `agent-travel4me/agents/openai.yaml`: Skill UI 元数据和默认启动 prompt。
- `agent-travel4me/scripts/`: 本地工作流脚本。
- `agent-travel4me/references/`: 路线规划、提示词契约、明信片风格和平台说明。
- `agent-travel4me/assets/style_samples/`: 明信片风格样张。
- `style-samples/`: 早期风格探索样张。
- `output/`: 生成结果示例和路线视觉样张。
- `agent-travel4me-project-plan.md`: 项目计划和设计记录。

### 快速开始

安装后，从 Skill 入口启动时应直接进入提问流程：先问目的地、确认出发地，并主动推荐 3 个具体、可画的 Agent 形象供用户选择或改写，例如小猫、小狗、小机器人这类有稳定外观锚点的旅行者。

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
  --character-anchor "red scarf"
```

生成角色参考图或每日场景图前，可以先 dry run：

```bash
python scripts/generate_character_reference.py --trip-dir <trip_dir> --dry-run
python scripts/validate_route.py --trip-dir <trip_dir>
python scripts/daily_run.py \
  --trip-dir <trip_dir> \
  --weather "<daily local weather summary>" \
  --label-location "<short place label>" \
  --dry-run
```

实时图片生成有两条路径：如果宿主 coding agent 有原生生图能力，使用 dry-run 产出的 prompt 生图，再用 `scripts/import_generated_image.py` 登记结果；如果没有原生生图能力，则通过本地环境变量配置 `OPENAI_API_KEY`、`GOOGLE_API_KEY`、`GEMINI_API_KEY`、`SEEDREAM_API_KEY` 或 `TRAVEL4ME_IMAGE_COMMAND`。

天气是可选增强信息。生成最终明信片、每日场景图或壁纸前，如果已经查询到或用户提供了当天当地天气，可以通过 `--weather` 或 `waypoint.weather` 写入 prompt；缺天气时继续生成，不阻塞流程。

如果 `validate_route.py` 报告路线仍是占位内容，先让 coding agent 补齐真实地点、坐标、地标、视觉元素，并把具体的当地活动和人际互动直接写进路线，再用 `scripts/apply_route_enrichment.py` 写回旅程状态。

## English

`agent-travel4me` is a coding-agent skill for running an "Agent travels for me" journey. Given an origin, destination, and Agent identity, it plans a multi-day route and produces durable journey state, postcard-style daily scene prompts, route data, and optional image artifacts.

The project is intentionally local and portable. A coding agent can run the scripts to detect the environment, initialize a trip, generate a character reference, advance the daily route, produce scene assets, resize outputs, and set the desktop wallpaper only after explicit user approval.

### Key Features

- Detects local environment, screen size, image providers, wallpaper support, and automation options.
- Estimates journey length from the route distance and creates trip state files.
- Keeps a small recurring Agent traveler consistent across daily scenes, usually joining local activities and interacting with local people.
- Exports daily scene prompts, route GeoJSON, place/date labels, weather context, and optional generated images.
- Supports host-agent native image generation, local OpenAI/Gemini/Seedream providers, or a custom command hook.
- Can optionally install a daily run schedule or set the local wallpaper after user approval.

### Repository Layout

- `agent-travel4me/SKILL.md`: Skill entry point and operating rules.
- `agent-travel4me/agents/openai.yaml`: Skill UI metadata and default start prompt.
- `agent-travel4me/scripts/`: Local workflow scripts.
- `agent-travel4me/references/`: Route planning, prompt contract, postcard style, and platform notes.
- `agent-travel4me/assets/style_samples/`: Bundled postcard style sample.
- `style-samples/`: Early visual exploration samples.
- `output/`: Example generated outputs and route visual samples.
- `agent-travel4me-project-plan.md`: Project plan and design notes.

### Quick Start

After installation, launching the skill should start the setup questions directly: destination, origin confirmation, and three concrete, drawable Agent identity candidates for the user to choose or revise, such as a small cat, small dog, or tiny robot with stable visual anchors.

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
  --character-anchor "red scarf"
```

Dry run before generating live images:

```bash
python scripts/generate_character_reference.py --trip-dir <trip_dir> --dry-run
python scripts/validate_route.py --trip-dir <trip_dir>
python scripts/daily_run.py \
  --trip-dir <trip_dir> \
  --weather "<daily local weather summary>" \
  --label-location "<short place label>" \
  --dry-run
```

Live image generation has two paths: if the host coding agent has native image generation, use the dry-run prompt and then register the generated image with `scripts/import_generated_image.py`; otherwise configure local environment variables such as `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GEMINI_API_KEY`, `SEEDREAM_API_KEY`, or `TRAVEL4ME_IMAGE_COMMAND`.

Weather is optional enhancement context. Before generating final postcards, daily scene images, or wallpapers, write the day's local weather into the prompt through `--weather` or `waypoint.weather` when it is already available or user-provided; missing weather does not block generation.

If `validate_route.py` reports placeholder route content, ask the coding agent to enrich the route with real places, coordinates, landmarks, local visual elements, and place-specific local activities and human interactions written directly into the route, then apply it with `scripts/apply_route_enrichment.py`.

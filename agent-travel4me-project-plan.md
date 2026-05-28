# agent-travel4me 通用 Skill 项目方案

## 1. 定位

`agent-travel4me` 是一个面向通用 coding agent 的 skill，不绑定 Codex，也不提供独立客户端。它是一组可被 coding agent 加载的指令、脚本和素材：

- skill 负责和用户对话、做旅行规划、组织 prompt、调用脚本。
- 本地脚本负责生成图片、裁切壁纸、保存状态、尝试设置系统壁纸。
- 每日运行依赖 agent 所在环境的定时能力，例如 cron、launchd、Windows Task Scheduler、GitHub Actions/self-hosted runner，或某个 agent 平台自己的 scheduled run。

核心体验：用户告诉 agent 最想去哪里，以及自己的 Agent 形象。agent 先生成角色参考图让用户确认，再每天生成一张“Agent 替我旅行”的高清壁纸。Agent 在画面里始终只是一个小角色，不喧宾夺主。

## 2. 关键调研结论

### 通用 skill 要先检测运行环境

不同 coding agent 能力差异很大，skill 启动后必须先做环境探测，再决定要不要问用户要 API key 或配置定时任务。

需要探测：

- 是否有 agent 原生生图工具，例如 Codex 当前会话里的 `image_gen`/imagegen 能力。
- 是否已有图像 API key，例如 `OPENAI_API_KEY`、`GOOGLE_API_KEY`、`FAL_KEY`、`REPLICATE_API_TOKEN`、`SEEDREAM_API_KEY`。
- 是否能调用本地 shell 和 Python。
- 是否能安装或运行依赖。
- 是否有定时能力：agent 平台 automation、macOS `launchd`、Linux cron/systemd timer、Windows Task Scheduler。
- 是否处在本机交互式桌面会话中，决定能不能可靠设置壁纸和检测屏幕。

决策：

- 有原生生图工具：优先用原生工具生成角色参考图和样张；正式壁纸仍要检查它是否支持明确尺寸，不支持就本地 resize/crop。
- 没有原生生图工具但有 API key：走脚本调用图像 API。
- 两者都没有：只在此时提示用户配置图像 API key。不要让用户把 key 粘贴到聊天里，让用户设置本地环境变量。
- 没有定时能力：仍可生成当日壁纸，但只能提示用户手动运行 `daily_run.py` 或稍后配置系统定时器。

当前验证：本会话的内建 imagegen 可以生成图片，但没有暴露明确尺寸参数。四张 16:9 样张实际输出都是 `1672x941`。所以不能承诺“直接通过内建 imagegen 精确生成 `2560x1440`”。如果需要 `2560x1440`，应优先使用支持尺寸参数的 API/CLI；或先生成接近比例的图，再用 `Pillow` 裁切、扩边或放大到 `2560x1440`。

生图供应商优先级：

1. `gpt-image-2`
2. Nano Banana 2 / Gemini 3.1 Flash Image
3. Seedream 当前最新可用模型，运行时从供应商文档或配置解析；截至本方案记录时，公开资料显示为 Seedream 5.0 Lite

不要因为优先级而强行要求用户配置所有 key。只选择当前环境中可用的最高优先级供应商。

### 能否通过 coding agent 自动换壁纸？

可以，但前提是 agent 运行在用户本机的交互式桌面会话里，并且有必要的系统权限。

这不要求有图形客户端。CLI 里的 coding agent 可以做到，条件是它的 CLI 进程运行在用户已经登录的桌面会话里，例如用户在自己 Mac/Windows/Linux 桌面上打开 Terminal 并运行 agent。不能可靠做到的是无头服务器、远程 CI、隔离沙箱、没有 GUI session 的 SSH 环境，或被系统权限限制的 runner。

换句话说：

- `CLI + 本机桌面会话`：可以尝试设置壁纸和检测屏幕。
- `CLI + 远程/无头/沙箱`：通常只能生成图片，不能可靠设置壁纸。
- `GUI agent`：不自动等于可以换壁纸，仍然要看系统权限。

macOS 可行路径：

- 使用 AppKit `NSWorkspace.setDesktopImageURL(... for: screen ...)` 设置桌面图。
- 或使用 AppleScript/JXA 让 Finder/System Events 设置桌面背景。
- 风险点：如果走 AppleScript/JXA，macOS 会把它视为“一个应用控制另一个应用”，需要用户在隐私与安全设置中授权。Apple 官方支持文档明确有“允许应用控制其他应用”的设置；Apple 开发者文档也有 Apple Events 自动化 entitlement。
- 结论：能做，但首次运行要预期出现权限弹窗；如果 agent 运行在无 GUI、沙箱或远程 runner 里，则不能保证成功。

Windows 可行路径：

- 使用 Win32 `SystemParametersInfoW`，传入 `SPI_SETDESKWALLPAPER`。
- 一般不需要像 macOS 那样的 Automation 权限，但必须运行在用户桌面会话中。企业策略、锁屏策略或受限账户可能阻止修改。

Linux 可行路径：

- GNOME 可用 `gsettings set org.gnome.desktop.background picture-uri file:///...`，深色模式还要设置 `picture-uri-dark`。
- KDE、XFCE、Sway/Hyprland 等需要各自 adapter。
- 结论：Linux 能做，但必须按桌面环境分支，不适合首版承诺“全 Linux 通用”。

### 屏幕尺寸能否自动识别？

可以 best-effort 自动识别，但不能 100% 保证。

macOS：

- 优先用 AppKit `NSScreen.screens` 获取每块屏幕的 frame 和 scale。
- 备选 `system_profiler SPDisplaysDataType`。
- 当前测试环境中，coding agent 没有暴露可见屏幕：`system_profiler` 只返回 GPU，`NSScreen.screens` 返回空数组。这说明在沙箱、远程、无 GUI session 中必须 fallback。

Windows：

- 可用 .NET/PowerShell 读取 `System.Windows.Forms.Screen.AllScreens`。
- 也可用 WMI/CIM 查询显卡和显示器信息，但准确壁纸尺寸仍以桌面会话 API 更可靠。

Linux：

- X11 可用 `xrandr --current`。
- Wayland 下要按桌面环境尝试 `gsettings`、`wlr-randr` 等。

结论：skill 不应该把屏幕尺寸作为首轮问题。先自动检测；检测失败则默认 `16:9`，生成 `3840x2160` 或供应商支持的接近尺寸，并允许用户后续用一句话覆盖，例如“我的屏幕是 3024x1964”。

## 3. 交互流程

目标是减少问题。首轮只问真正必要的信息。

### 环境检查

skill 被触发后先做第 0 步，不向用户提问：

1. 检测 agent 是否有直接生图能力。
2. 检测是否已有可用图像 API key。
3. 检测操作系统、桌面会话、屏幕尺寸。
4. 检测壁纸设置 adapter 是否可用。
5. 检测定时任务能力。
6. 尝试从可用 Memory 中推断起点城市，但只能作为候选，不能当作已确认事实。

然后给用户一个简短状态说明，例如：

`我先看了一下我的背包：我现在可以直接画草稿；屏幕尺寸没拿到，我会先按 16:9 做；换壁纸这件事等第一张图出来后再问你授权。`

### 首次运行

1. 问目的地：`我想替你走一趟。你最想让我去哪里？`
2. 问 Agent 形象，但口吻要拟人化：`在你眼中，我是什么形象？我可以先试着成为……`

如果起点无法从上下文获得，再问：

3. `从哪里出发？只给城市就可以。`

起点大概率不能从上下文获得。skill 可以先查 agent 可读 Memory，例如用户常驻城市、最近提到的出发地、系统 locale/timezone，但必须用低打扰方式确认：

`我猜你可能从深圳出发。如果不是，告诉我真正的出发城市就好。`

Agent 形象不做同质化默认值。skill 应根据用户的 memory、偏好、语气和目的地给出 2-4 个候选，并允许用户直接改。候选应该有具体可复用的视觉锚点。

示例候选：

- `永远是同一只浅灰色短毛猫，蓝色小背包，红色围巾，安静但好奇。`
- `一只白色蓝眼德文猫，小蓝背包，耳朵很大，走路像在认真考察世界。`
- `一只奶油色小狗，绿色披肩，背着旧相机，永远在画面角落看风景。`
- `一只黑耳白兔，黄色雨衣，小帆布包，像刚从车站出发。`

如果 agent 有可读 memory，应鼓励它发挥：例如用户偏好简洁、克制、城市感，就推荐更安静的猫；用户偏好童话或温暖感，就推荐兔子或小狗。不要每次都推荐同一套“猫 + 蓝背包 + 红围巾”。

不问旅行节奏。天数由距离和路线复杂度自动估算。

不问屏幕尺寸。脚本先自动检测，失败就用默认宽屏比例。

### 角色确认

首次不要直接进入每日壁纸。先生成一张 Agent 角色参考图：

- 纯角色图或简单背景。
- 不作为最终壁纸。
- 让用户确认“就是这只 Agent 吗？”

用户确认后，把这张图保存为 `character_reference.png`。之后每天生成都把它作为参考图或 prompt 锁定对象。如果图像供应商不支持参考图输入，就保存角色描述、首图和 prompt 历史，尽量用文字保持一致。

### 旅程初始化

确认角色后：

1. 自动检测屏幕尺寸。
2. 规划起点到目的地的虚拟路线。
3. 估算天数，最长 30 天。
4. 向用户确认是否要更快抵达。
5. 用户确认天数后生成每日 waypoint。
6. 生成第 1 天壁纸。
7. 询问是否允许设置为当前壁纸。

天数确认口吻：

`我算了一下，从 {origin} 到 {destination}，我大概需要 {days} 天能抵达。你想让我更快一点吗？如果想，告诉我你希望几天内到，我会换更快的交通工具。`

自动换壁纸不要在首轮直接开启。建议在第一张正式壁纸生成后问：

`这张要不要我替你换成壁纸？如果你愿意，我以后每天到一个新地方，就把当天的照片换上；也可以只生成，不动你的桌面。`

## 4. 每日运行流程

每天定时任务执行：

1. 读取 `trip.json`。
2. 找到当天 waypoint。
3. 读取 `character_reference.png` 和风格 preset。
4. 生成当天 prompt。
5. 调用图像生成 API。
6. 保存原图、壁纸图、prompt、metadata。
7. 如果 `auto_set_wallpaper=true`，调用系统 adapter 设置壁纸。
8. 写入当天结果并推进 day index。

如果换壁纸失败：

- 不要重复弹权限或反复执行。
- 保存图片成功即可。
- 在结果中报告失败原因和手动设置路径。

## 5. 生图 Prompt 策略

Prompt 要同时服务三件事：地点可识别、旅程连续、Agent 一致且不抢画面。

### Prompt 组成

每张壁纸 prompt 按这个顺序拼：

1. `style_bible`：风格媒介、光照、色彩、质感。
2. `location_context`：当天城市/自然节点、国家/区域、时间段。
3. `landmarks`：1-3 个可识别地标。
4. `landscape_type`：城市、水面、山地、沙漠、海岸、森林、古城等。
5. `local_visual_elements`：当地建筑材料、植物、交通工具、街道物件、纹样、色彩。
6. `agent_identity`：同一只 Agent 的固定外观。
7. `agent_activity`：Agent 和当地环境发生的小互动。
8. `agent_composition_rule`：Agent 很小、偏离中心、自然嵌入环境，不固定站在左下角或右下角。
9. `wallpaper_layout`：留白、安全区域、不要让主体挡桌面图标。
10. `negative_constraints`：避免文字、水印、logo、错误地标、Agent 居中或变成主角。

### Agent 互动与构图约束

Agent 必须作为小角色存在，不能在画面中央，也不能每张都固定站在左下角或右下角。Prompt 生成器要先从当天地点的视觉元素里挑一个自然动作，让 Agent 参与环境；同时保留一部分纯看风景的安静画面，避免动作过满。

互动动作不是固定模板，而是启发式生成：

- 从 `local_visual_elements` 里找可互动对象：屋檐、桥、车站、河岸、茶摊、市场、船、山路、长椅、阳台、台阶、热气球、渡轮、雨棚、地图、电脑、相机、当地食物。
- 动作要符合地点气质：工作氛围浓的城市可以短暂打工；山水节点可以写生、等船、踩水、看地图；古城节点可以坐在台阶边休息；海港节点可以等渡轮；沙漠节点可以整理背包或躲在阴影里。
- 不要让每张都在“吃东西”或“坐交通工具”。每天只选一个小动作。
- 动作必须小，不改变主视觉。地点和地标仍是画面主体。
- 允许约 30%-40% 的日子只是看风景，用来保持旅程呼吸感。

推荐硬性描述：

```text
The agent character is a small traveler naturally participating in the local environment,
occupying less than 6% of the image area.
Vary the placement and activity across days; do not repeatedly put the agent in the same lower-left or lower-right standing pose.
Do not place the agent in the center.
Do not create a centered portrait, close-up, mascot poster, or hero character shot.
The agent may sit, walk, work, ride, taste local food, wait under a roof, sketch, read a map, or quietly watch the scenery when appropriate.
The destination landscape and landmark are the main subject.
```

中文约束：

```text
Agent 只作为画面里的小旅人，面积小于 6%，自然参与当地环境。
不要每张都让 Agent 固定站在左下角或右下角；每天的位置和动作要变化。
不要把 Agent 放在画面中央，不要做成头像、海报主角或近景特写。
Agent 可以坐着、走路、打工、乘坐交通工具、尝当地食物、躲在屋檐下、写生、看地图，或在合适的时候只是安静看风景。
当天地点、地标和景观才是主视觉。
```

### 地点识别策略

每天至少写入：

- 一个主要地标。
- 一个自然或城市地貌。
- 三个当地视觉元素。

例如里斯本：

```text
Belém Tower, Tagus River, Alfama red rooftops,
azulejo blue-and-white tiles, yellow tram, limestone mosaic pavement,
Atlantic wind, warm late-afternoon light.
```

### 自然景观配额

路线中不能全是城市。Prompt 层也要强制景观变化：

- 30 天路线中至少 10 天以自然或半自然景观为主，例如山、河、湖、沙漠、海岸、峡谷、森林、草原。
- 15-24 天路线中至少 7 天以自然或半自然景观为主。
- 连续 3 天不能都以城市街景/建筑为主。
- 如果路线本身穿过大城市密集区，要把其中一些天转成河岸、海港、丘陵、湿地、山口、海峡、岛屿或乡野视角。

### 示例 Prompt 骨架

```text
Create a 16:9 travel wallpaper in {style_name}.
Scene: Day {day}/{total}, {location}, {country_or_region}.
Main visual subject: {landscape_type} with {landmarks}.
Local visual elements: {local_visual_elements}.
Journey continuity: the same tiny agent traveler is passing through this place on the way from {origin} to {destination}.
Agent: {character_identity}. The agent is small, off-center, occupying less than 6% of the image.
Agent activity: {one context-aware interaction with local_visual_elements, varied from previous days}.
Composition: wide landscape wallpaper, destination and environment are the main subject, clear negative space for desktop icons.
Avoid: centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, readable text, logos, watermarks, wrong landmarks, generic tourist collage.
```

## 6. 风格体系

首版保留 4 种风格。每个风格要有一张样片和一段固定 style bible。

### 高品质 3D 动画

圆润、非写实、电影级 3D 动画质感，适合表现现代城市和 Agent 的可爱感。prompt 中使用“original high-quality 3D animated movie look”，避免直接要求模仿具体商业工作室或现有角色。

代表样张：纽约，Brooklyn waterfront、Manhattan skyline、Brooklyn Bridge。

### 国风水墨

水墨笔触、宣纸肌理、留白、淡彩点染。适合把真实城市或地貌转译成更诗意的旅行画面。

代表样张：瓜纳华托，山城层叠彩色房屋、教堂穹顶、群山。

### 风光大片

真实风景、宽画幅、强空间层次、电影级光线。Agent 是远景中的小旅行者。

代表样张：悉尼，Opera House、Harbour Bridge、海港夜色。

### 水彩明信片

水彩纸纹、轻墨线、旅行手账感。避免生成不可读文字。

代表样张：罗马，Colosseum、伞松、古城石路。

## 7. 一致性方案

一致性不能只靠一句 prompt。

### Agent 一致性

保存：

- `character_reference.png`
- `character.json`
- `character_prompt.txt`

`character.json` 包括：

- 物种。
- 毛色/眼睛/耳朵/体型。
- 固定服饰，例如蓝色小背包。
- 出镜规则：始终是小角色，偏离中心，通常在画面下三分之一或边缘，不做主视觉。

示例角色：

```json
{
  "species": "Devon Rex cat",
  "fur": "pure white",
  "eyes": "blue",
  "accessory": "small blue travel backpack",
  "scale_rule": "small off-center character in the lower third or near one side, never the dominant subject"
}
```

### 风格一致性

保存：

- `style_id`
- `style_bible.md`
- `style_sample.png`

每日 prompt 必须包含同一组风格约束：媒介、色彩、光照、构图、禁止项。

### 旅程一致性

每天保存：

- day index。
- waypoint。
- prompt。
- model。
- size。
- image response id。
- reference image path。
- final wallpaper path。

如果供应商支持 seed 或基于参考图编辑，优先使用。否则靠角色参考图、固定 style bible 和 prompt 历史减小漂移。

## 8. 路线与天数估算

不问旅行节奏，自动估算。

输入：

- 起点城市。
- 目的地。

步骤：

1. 地理编码起点和目的地。
2. 计算直线距离。
3. 根据距离映射天数。
4. 按路线方向和地貌生成 waypoint。

默认天数：

- 0-100 km：3 天。
- 100-800 km：5-8 天。
- 800-2500 km：9-14 天。
- 2500-8000 km：15-24 天。
- 跨洲或超过 8000 km：25-30 天。

硬上限：30 天。估算结果超过 30 天时必须压到 30 天以内。

确认规则：

- 先告诉用户估算天数。
- 问是否要更快抵达。
- 如果用户给出目标天数，例如“10 天内”，重新压缩 waypoint，并把叙事交通工具改快，例如步行/火车/轮船/飞机/热气球/夜行列车等。
- 不问“旅行节奏”这类抽象配置。

这是一条叙事路线，不是交通建议。

## 9. 路线设计策略

路线不是简单按距离等分。每一天都应该能产出一张有地方感的壁纸，所以节点要围绕“可识别地标 + 景观变化 + 当地视觉元素”来设计。

### 节点字段

每个 day waypoint 至少包含：

- `location`：城市、区域或自然地貌，不用“某个小镇”这类泛称。
- `coordinates`：`lat`、`lon`，必须保存，后续用于路线可视化网站。
- `role`：当天在旅程中的叙事作用，例如出发、穿越山地、抵达海港。
- `landmarks`：1-3 个可识别地标或地点。
- `landscape_type`：现代城市、河流、喀斯特、雪山、沙漠、古城、海港、草原、峡湾等。
- `local_visual_elements`：建筑材料、植物、街道物件、交通工具、服饰/纹样、色彩。
- `palette`：当天主色调。
- `agent_position`：Agent 在画面里的位置，通常是画面下三分之一的小角色。
- `prompt_focus`：当天最应该被画出来的主体。
- `avoid`：避免文字、logo、错误地标混搭、把 Agent 放成主角等。

### 选点规则

1. 起点和终点必须保留。
2. 每个节点必须有具体视觉锚点，优先真实地标、独特地貌和当地建筑。
3. 连续 3 天内不能都是同一种景观。例如不能连续 3 天都是“老城街道”。
4. 每 5-7 天要出现一次明显的地理转场，例如城市到山地、山地到平原、平原到沙漠、沙漠到海港。
5. 城市景观不能占比过高。15-24 天路线至少 7 天以自然或半自然景观为主；25-30 天路线至少 10 天以自然或半自然景观为主。
6. 跨文化路线要体现渐变，不要突然从深圳跳到巴黎再跳回西亚。
7. 地标密度要足够高：每天至少有一个“用户看图能说出这是哪里”的视觉线索。
8. 当某天是长距离跨越，可以把当天画成交通/过境主题，例如夜行列车、海峡渡轮、高空航线、沙漠公路，但仍要有地点线索。
9. 对敏感或宗教场景保持尊重，避免让 Agent 站在不合适的位置或做滑稽动作。
10. 每个节点必须保存城市/地点名和坐标，后续可以直接输出 `route.geojson` 给网站使用。

### 打分策略

候选节点按 5 个维度打分：

- `recognizability`：地标是否一眼可识别。
- `visual_diversity`：和前后两天是否有明显景观差异。
- `route_progress`：是否沿起点到终点持续推进，少走回头路。
- `local_specificity`：是否有当地特色元素，而不是通用旅游明信片。
- `wallpaper_quality`：是否有开阔天空、水面、墙面或远景留白，适合做桌面。

推荐权重：

```text
score = recognizability * 0.30
      + visual_diversity * 0.25
      + route_progress * 0.20
      + local_specificity * 0.15
      + wallpaper_quality * 0.10
```

### 压缩路线

如果用户想更快抵达，不要简单截断后半段。压缩规则：

1. 保留起点、终点、最大地理转场节点和最高识别度地标。
2. 删除相似景观的中间节点。
3. 把相邻节点合并成“交通日”或“远眺日”。
4. 重新分配每日画面，让景观变化仍然完整。

例如 24 天压到 14 天时，应保留深圳、桂林、滇西、蒲甘/恒河、拉贾斯坦沙漠、伊斯法罕/卡帕多奇亚、伊斯坦布尔、地中海、伊比利亚、里斯本这些大转场。

### 路线数据输出

路线规划完成后必须保存两份数据：

```text
trip.json
route.geojson
```

`trip.json` 供每日生成使用，`route.geojson` 供后续可视化网站使用。

waypoint 示例：

```json
{
  "day": 2,
  "location": "Guilin / Yangshuo",
  "country_or_region": "China",
  "coordinates": {
    "lat": 25.2736,
    "lon": 110.2900
  },
  "role": "leaving the modern city and entering karst river landscapes",
  "landmarks": ["Li River", "Yangshuo karst peaks", "Yulong River"],
  "landscape_type": "karst river valley",
  "local_visual_elements": ["bamboo rafts", "morning mist", "limestone peaks", "riverside villages"],
  "palette": ["mist blue", "limestone gray", "soft green"],
  "agent_position": "small off-center traveler near the lower left riverbank",
  "prompt_focus": "misty Li River valley with karst silhouettes"
}
```

GeoJSON 输出：

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [110.29, 25.2736]},
      "properties": {"day": 2, "location": "Guilin / Yangshuo", "landscape_type": "karst river valley"}
    }
  ]
}
```

## 10. 深圳到里斯本试跑

输入：

- 起点：深圳。
- 目的地：里斯本。
- 直线距离：约 10,997 km。
- 叙事路线估算距离：约 13,825 km。
- 估算天数：24 天。

确认话术：

`我算了一下，从深圳到里斯本，我大概需要 24 天能抵达。你想让我更快一点吗？如果想，告诉我你希望几天内到，我会换更快的交通工具。`

试跑路线：

| Day | 节点 | 地标/景观 | 当地视觉元素 | 壁纸画面重点 |
| --- | --- | --- | --- | --- |
| 1 | 深圳 | 深圳湾、平安金融中心、滨海步道 | 玻璃幕墙、红树林、城市夜景、共享单车 | Agent 从现代海湾城市出发 |
| 2 | 桂林/阳朔 | 漓江、喀斯特山峰、遇龙河 | 竹筏、薄雾、青绿山水、江边村落 | 城市转入山水，画面留大片晨雾 |
| 3 | 昆明/石林 | 石林、滇池远景 | 石灰岩尖峰、红嘴鸥、云南花市色彩 | 奇石森林中的远行感 |
| 4 | 大理/洱海 | 洱海、苍山、白族民居 | 白墙青瓦、扎染蓝、湖边风、骑行路 | 湖面开阔，Agent 在湖边小路 |
| 5 | 丽江/玉龙雪山 | 玉龙雪山、丽江古城屋顶 | 纳西木楼、石板路、雪山、经幡色彩 | 从古城望向雪山，进入高地 |
| 6 | 曼德勒 | 乌本桥、伊洛瓦底江 | 柚木桥、僧袍橙、河面倒影、金色日落 | 长桥剪影，Agent 很小地走在桥端 |
| 7 | 蒲甘 | 佛塔平原、热气球、伊洛瓦底河 | 砖红佛塔、晨雾、热气球、干原树影 | 古塔海和低空晨雾 |
| 8 | 瓦拉纳西 | 恒河河坛、晨浴台阶、木船 | 砂岩台阶、油灯、纱丽色彩、河雾 | 河岸清晨，尊重安静，不做滑稽动作 |
| 9 | 斋浦尔 | 风之宫殿、琥珀堡、粉红城 | 粉砂岩、拱窗、黄铜、彩色布料 | 粉红城市街角，Agent 在阴影里 |
| 10 | 杰伊瑟尔梅尔/塔尔沙漠 | 金色城堡、沙丘、沙漠公路 | 黄色砂岩、骆驼剪影、蓝色夜幕、星空 | 从宫殿城进入沙漠 |
| 11 | 亚兹德 | 风塔、土坯老城、沙漠边缘 | 泥砖墙、风塔、蓝陶、窄巷光影 | 沙漠城镇的午后阴影 |
| 12 | 伊斯法罕 | 伊玛目广场、蓝色清真寺穹顶、拱廊 | 青金石瓷砖、几何纹样、喷泉、拱门 | 蓝色穹顶和广场留白 |
| 13 | 设拉子/波斯波利斯 | 波斯波利斯遗址、庭院花园 | 石柱浮雕、玫瑰、柏树、暖色石材 | 古遗址与花园过渡 |
| 14 | 卡帕多奇亚 | 精灵烟囱、洞穴屋、热气球 | 凝灰岩、洞穴窗、彩色气球、晨光 | 奇岩地貌中的小小旅人 |
| 15 | 伊斯坦布尔 | 博斯普鲁斯海峡、圣索菲亚、蓝色清真寺 | 海鸥、渡轮、圆顶、尖塔、土耳其蓝 | 从亚洲望向欧洲的海峡转场 |
| 16 | 雅典 | 卫城、帕台农神庙、爱琴海天光 | 白色石材、橄榄树、蓝白色调、山城街巷 | 古典石柱和开阔天空 |
| 17 | 杜布罗夫尼克 | 古城墙、亚得里亚海、红屋顶 | 石灰岩城墙、橙红屋瓦、碧蓝海水 | 海边城墙上的远眺 |
| 18 | 威尼斯 | 大运河、里亚托桥、窄巷水道 | 贡多拉、旧墙面、水波反光、拱桥 | 水城黄昏，Agent 在桥边 |
| 19 | 佛罗伦萨/托斯卡纳 | 圣母百花大教堂、阿诺河、丘陵 | 赤陶屋顶、柏树、石桥、金色田野 | 文艺复兴城市和乡野转场 |
| 20 | 巴塞罗那 | 圣家堂、地中海街区 | 彩色马赛克、棕榈树、阳台、暖色墙面 | 现代主义建筑剪影 |
| 21 | 瓦伦西亚 | 艺术科学城、海岸湿地 | 白色未来建筑、浅水倒影、橙树 | 未来感建筑和海风 |
| 22 | 格拉纳达 | 阿尔罕布拉宫、内华达山远景 | 摩尔纹样、红墙、喷泉庭院、柏树 | 宫殿庭院与山影 |
| 23 | 塞维利亚 | 西班牙广场、瓜达尔基维尔河、橘树街 | 彩瓷、拱廊、马车、橘树、暖黄石材 | 伊比利亚南部的金色傍晚 |
| 24 | 里斯本 | 贝伦塔、阿尔法玛、特茹河、黄色电车 | 蓝白瓷砖、红屋顶、石灰石路面、海风 | 抵达大西洋边的终点壁纸 |

这条路线的景观序列是：现代海湾城市 -> 喀斯特水乡 -> 高原石林 -> 湖泊雪山 -> 东南亚河桥 -> 佛塔平原 -> 恒河河岸 -> 王宫古城 -> 沙漠城堡 -> 波斯沙漠城 -> 蓝色穹顶 -> 古遗址 -> 奇岩热气球 -> 海峡城市 -> 古典遗迹 -> 亚得里亚海城墙 -> 水城 -> 托斯卡纳丘陵 -> 地中海现代主义 -> 未来海岸 -> 摩尔宫殿 -> 安达卢西亚广场 -> 大西洋终点。

## 11. 推荐目录结构

```text
agent-travel4me/
├── SKILL.md
├── scripts/
│   ├── init_trip.py
│   ├── detect_environment.py
│   ├── detect_screen.py
│   ├── plan_route.py
│   ├── export_route_geojson.py
│   ├── generate_character_reference.py
│   ├── generate_wallpaper.py
│   ├── resize_wallpaper.py
│   ├── set_wallpaper.py
│   ├── wallpaper_macos.py
│   ├── wallpaper_windows.py
│   ├── wallpaper_gnome.py
│   └── daily_run.py
├── references/
│   ├── prompt_contract.md
│   ├── style_presets.md
│   ├── route_planning.md
│   ├── environment_detection.md
│   ├── screen_detection.md
│   └── wallpaper_platforms.md
└── assets/
    └── style_samples/
        ├── 3d-animation-new-york.png
        ├── chinese-ink-guanajuato.png
        ├── cinematic-landscape-sydney.png
        └── watercolor-postcard-rome.png
```

不放客户端代码。不做后台服务。skill 只假设 coding agent 能读写本地文件、执行脚本、调用网络 API。

## 12. 依赖

### 必需

- Python 3.11+。
- `Pillow`：裁切、扩边、转换格式。
- `httpx` 或 `requests`：API 调用。
- 本地文件系统写权限。

### 条件必需

- 如果 agent 没有原生生图能力，需要图像生成 API key。优先级是 `gpt-image-2` 对应 key，其次 Nano Banana 2/Gemini 3.1 Flash Image 对应 key，再其次 Seedream 当前最新模型对应 key。
- 如果走 API key 路径，需要对应供应商 SDK，例如 `openai`。
- 如果要精确请求 `2560x1440`、`3840x2160` 等尺寸，必须使用支持明确尺寸参数的图像 API/CLI；内建生图工具不一定支持。

### 推荐

- 地理编码/地图服务：
  - Mapbox。
  - Google Maps。
  - OpenRouteService。
  - OpenStreetMap/Nominatim，但要遵守调用限制。
- 定时运行能力：
  - macOS `launchd`。
  - Linux cron/systemd timer。
  - Windows Task Scheduler。
  - agent 平台自己的 scheduled task。

### 平台相关

macOS：

- AppKit/Swift、PyObjC 或 AppleScript/JXA。
- Automation/Apple Events 权限，取决于实现路径。

Windows：

- PowerShell 或 Python `ctypes` 调用 `SystemParametersInfoW`。

Linux：

- GNOME: `gsettings`。
- X11: `xrandr` 可用于探测屏幕。
- KDE/其他桌面：后续 adapter。

## 13. 用户需要提供或授权

首轮尽量只要：

- 目的地。
- Agent 在用户眼中的形象，或从候选里选一个。

必要时再要：

- 起点城市。先从 Memory best-effort 猜测并请用户确认，猜不到再问。
- 图像 API key 的本地环境变量配置，仅当环境里没有原生生图能力、也没有现成 key。
- 自动换壁纸授权。
- 更快抵达的目标天数，仅当用户不满意自动估算天数。

不应该要求用户在聊天里粘贴 API key。只提示用户在本机设置环境变量。

## 14. MVP 范围

首版做：

1. 通用 skill 文件夹。
2. Python 脚本。
3. 角色参考图生成和确认。
4. 四种风格样片。
5. 自动屏幕检测，失败则默认 16:9。
6. 自动天数估算，上限 30 天，确认是否要更快抵达。
7. macOS 壁纸设置 adapter。
8. Windows 壁纸设置 adapter。
9. GNOME 壁纸设置 adapter。
10. 环境检测报告。
11. 本地 JSON 状态。
12. 路线坐标持久化和 `route.geojson` 导出。

首版不做：

- 独立客户端。
- 移动端自动换壁纸。
- 真实导航或交通方案。
- 多供应商复杂抽象。
- 云同步。
- 用户账号。
- 社交分享。

## 15. 验证标准

### 角色确认

给定“纯白蓝眼德文猫”，能生成参考图，用户可确认或要求重试。

### 环境检测

能区分：

- 有原生生图工具。
- 无原生生图工具但有 API key。
- 两者都没有，需要用户配置 key。
- 有定时能力。
- 没有定时能力，只能手动运行。

### 屏幕检测

在有 GUI session 的 macOS/Windows/GNOME 中能拿到主屏尺寸。

在无 GUI 或探测失败时，能 fallback 到默认尺寸并继续生成。

### 壁纸设置

macOS：

- 用户授权后能设置当前桌面壁纸。
- 未授权时失败信息明确，不误报成功。

Windows：

- 用户桌面会话中能设置壁纸。

GNOME：

- 能设置 light/dark 两套 background URI。

### 每日生成

连续运行 3 天，Agent 仍然是同一只小白猫，背包、位置尺度和风格保持稳定。

### 天数确认

任意路线估算结果不超过 30 天。估算后必须向用户确认是否要更快抵达；用户给出目标天数后，路线压缩并重新生成 waypoint。

### 路线质量

每天都有具体地标、景观类型、当地视觉元素和坐标。连续 3 天内不能都是同一类景观；跨洲路线必须体现地理和文化渐变；15-24 天路线至少 7 天以自然或半自然景观为主。

### Prompt 质量

Agent 不能在画面中央，不能是近景特写，不能成为主视觉。Prompt 必须明确地点主视觉、当地视觉元素、Agent 小角色位置和 negative constraints。

## 16. 当前示意图

已用“纯白蓝眼德文猫 + 蓝色小背包 + 小角色”生成四张风格示意图，保存在：

```text
style-samples/3d-animation-new-york.png
style-samples/chinese-ink-guanajuato.png
style-samples/cinematic-landscape-sydney.png
style-samples/watercolor-postcard-rome.png
```

这些图只是风格感受图，还不是最终角色参考图。正式实现时应先生成单独的 `character_reference.png`，用户确认后再进入旅程壁纸生成。

## 17. 资料来源

- Apple `NSWorkspace.setDesktopImageURL`: https://developer.apple.com/documentation/appkit/nsworkspace/setdesktopimageurl(_:for:options:)
- Apple “Allow apps to control other apps on Mac”: https://support.apple.com/guide/mac-help/allow-apps-to-control-other-apps-on-mac-mchl07817563/mac
- Microsoft `SystemParametersInfoW`: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow
- GNOME desktop background admin guide: https://help.gnome.org/admin/system-admin-guide/stable/desktop-background.html.en
- OpenAI image generation docs: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI gpt-image-2 model docs: https://developers.openai.com/api/docs/models/gpt-image-2
- Google Nano Banana 2 / Gemini 3.1 Flash Image announcement: https://blog.google/technology/google-deepmind/nano-banana-2/
- ByteDance Seedream 5.0 Lite announcement: https://seed.bytedance.com/en/blogs/seedream-5-0-lite

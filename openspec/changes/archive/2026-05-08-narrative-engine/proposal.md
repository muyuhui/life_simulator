## Why

当前游戏的核心循环是"点「下一年」→ 看数值波动 → 继续点"。事件虽有骨架（转机、小事件、节日事件），但每个事件只是 `{title, effect}` 的键值对——它通知玩家发生了什么，却不给玩家参与其中的机会。6 个关键年龄选择是仅有的决策点，但间隔太远，选项干巴巴。人物（伴侣、子女）只是字符串，没有名字、没有关系演化、没有情感重量。这导致游戏缺乏"再玩一年"的钩子和重玩动力。

## What Changes

- **事件卡片系统**：将关键年龄选择、转机事件、小事件统一改造为"事件卡片"格式。每张卡包含情境描述（2-3 句叙事文字）、2-4 个选项、每个选项的明确后果（数值变化 + 叙事影响）。第一版 20 张事件卡，覆盖 18-60+ 岁各人生阶段。
- **storyFlags 追踪**：新增叙事状态标记系统（~30 个 flag）。每次选择设置的 flag 会影响后续事件池的筛选条件。游戏结束时 flag 集合被翻译为个性化的人生总结文字。
- **人物关系系统**：不再存 `spouse: "小美"` 字符串，改为 `relationships` 数组。每局 3-5 个核心人物 + ~10 个配角，各有名字、性格标签、关系值（-100~100）、共同经历历史。事件选项会影响关系值，关系值反过来影响后续事件的可用选项。
- **日常小事系统**：没有事件卡触发的年份，生成小型二选一事件作为叙事填充，保持每一年都有互动。
- **事件链**：部分事件卡设置 `follow_up` 字段，确保因果链在后续年份自然延续（如"创业第一年"→"创业第二年"）。
- **结局生成**：根据 storyFlags 组合生成个性化人生总结，替代当前的单一 summaryMessage。
- **前端事件卡片 UI 改造**：modal 组件增强为沉浸式卡片展示，含情境文字、选项后果预览、涉及人物头像/关系变化提示。

## Capabilities

### New Capabilities
- `event-card-system`: 事件卡片数据结构、条件筛选引擎、事件池管理、优先级排序
- `character-relationships`: 人物数据模型、关系值变化、关系历史追踪、人物生成
- `story-flags`: 叙事标记的存储、条件匹配（flags_any/flags_none）、结局文字生成
- `daily-events`: 日常小事池、微型二选一、概率控制

### Modified Capabilities
_无。现有核心规则（数值衰减、收入计算、死亡检查、转机逻辑）保持不变。next_year() 的事件分发部分重构，但数值模拟层不变。_

## Impact

- `core.py` — GameState 新增 relationships、storyFlags、pendingEvents 字段；next_year() 重构事件分发逻辑；新增事件引擎核心方法
- `config.py` — 新增 EVENT_CARDS（20 张）、DAILY_EVENTS 池、RELATIONSHIP_CONFIG（性格标签等）；KEY_AGE_CHOICES 和 TURNING_POINT_EVENTS 迁移到事件卡系统中
- `server.py` — 新增 `/api/handle_event_choice` 端点处理事件选择
- `web/js/game-vue.js` — 增强 showEventModal 支持沉浸式卡片展示；新增人物关系面板组件；增强 applyServerResponse 处理关系变化
- `web/css/style.css` — 新增事件卡片、关系面板、关系变化提示的样式
- `web/index.html` — 可能需要新增关系面板区域

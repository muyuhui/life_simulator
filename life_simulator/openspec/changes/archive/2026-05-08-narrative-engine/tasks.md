# Tasks: Narrative Engine

## Phase 1: Data Layer (config.py + core.py)

- [x] **1.1** 在 `config.py` 中定义 `STORY_FLAGS` 字典（30 个 flag 及其中文描述）
- [x] **1.2** 在 `config.py` 中定义 `CHARACTER_NAMES` 名字池和 `PERSONALITY_TRAITS` 性格标签
- [x] **1.3** 在 `config.py` 中编写 20 张 `EVENT_CARDS`（按人生阶段分配：18-21 岁 4 张、22-29 岁 7 张、30-49 岁 6 张、50+ 岁 3 张）
- [x] **1.4** 在 `config.py` 中编写 30-40 条 `DAILY_EVENTS`（按类别分配权重）
- [x] **1.5** 在 `GameState.default_data()` 中新增 `storyFlags`、`relationships`、`pendingEvent`、`triggeredEvents` 字段
- [x] **1.6** 实现 `match_conditions(conditions, game_state) -> bool` 条件匹配函数
- [x] **1.7** 实现 `interpolate_flavor(flavor_text, game_state) -> str` 模板变量插值
- [x] **1.8** 实现 `select_event(game_state) -> EventCard` 事件选择引擎（5 级优先级）
- [x] **1.9** 实现 `resolve_event_choice(game_state, card, choice_index) -> dict` 选择结果处理
- [x] **1.10** 重构 `next_year()`：移除旧的 `check_key_age_choice`/`check_small_event`/`check_holiday_event`/`check_turning_point` 调用，统一走 `select_event` → 返回事件卡
- [x] **1.11** 实现 `generate_ending(game_state) -> str` 结局文字生成
- [x] **1.12** 更新 `to_dict()` / `from_dict()` 序列化逻辑（set → list for JSON）

## Phase 2: API Layer (server.py)

- [x] **2.1** 新增 `POST /api/handle_event_choice` 端点（接收 `choiceIndex`，调用 `resolve_event_choice`）
- [x] **2.2** 在 session 中暂存当前事件卡 ID 用于校验（防止重放）
- [x] **2.3** 更新 `next_year` 端点返回格式，支持 `event_card` 结果类型

## Phase 3: Frontend (web/)

- [x] **3.1** 在 `game-vue.js` 中新增 `relationshipList`、`currentEventCard` 响应式状态
- [x] **3.2** 增强 `showEventModal()` 渲染沉浸式事件卡片（flavor 文字、角色提及高亮、选项后果预览）
- [x] **3.3** 新增 `handleEventChoice(idx)` 方法（调用 `/api/handle_event_choice`）
- [x] **3.4** 拆分 `handleChoice()` 逻辑：区分 key_choice（保留兼容）、event_choice、asset_choice
- [x] **3.5** 在游戏界面新增"人物网络"面板（显示核心人物、关系值条、最近互动）
- [x] **3.6** 更新 `applyServerResponse()` 处理 `event_card` 和 `choice_result` 类型
- [x] **3.7** 在 CSS 中新增事件卡片沉浸式样式、关系面板样式、关系变化动画
- [x] **3.8** 在 index.html 游戏屏幕中新增关系面板区域

## Phase 4: Integration & Polish

- [x] **4.1** 端到端测试：完整走一遍"创建角色 → 推进 20 年 → 选择 → 结局"流程
- [x] **4.2** 调整 20 张事件卡的条件范围，确保每局 18-60 岁约触发 12-15 张
- [x] **4.3** 调优日常小事的权重分配和重复率
- [x] **4.4** 验证结局文字生成的 flag 组合覆盖率
- [x] **4.5** 将旧的 KEY_AGE_CHOICES 数据标记为 deprecated（保留但不再被调用）

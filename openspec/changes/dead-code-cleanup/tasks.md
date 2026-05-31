# Tasks: Dead Code Cleanup & Test Harness

## 1. Dead Code Removal — core.py

- [x] 1.1 从 `core.py` 删除 `check_key_age_choice()` 方法（L351-358）
- [x] 1.2 从 `core.py` 删除 `handle_key_choice()` 方法（L360-370）
- [x] 1.3 从 `core.py` 删除 `check_small_event()` 方法（L430-437）
- [x] 1.4 从 `core.py` 删除 `check_holiday_event()` 方法（L439-450）
- [x] 1.5 从 `core.py` 删除 `SMALL_EVENTS` 数据定义（L58-L128，约70行）和 `HOLIDAY_EVENTS` 数据定义（L130-L198，约68行）
- [x] 1.6 从 `core.py` 移除 `KEY_AGE_CHOICES` import
- [x] 1.7 在 `config.py` 末尾添加 `SMALL_EVENTS` 和 `HOLIDAY_EVENTS`（标记 `# DEPRECATED` 注释）
- [x] 1.8 验证 `_handle_special()` 和 `handle_choice()` 仍正常工作（它们不依赖上述删除的方法）

## 2. Dead Code Removal — server.py

- [x] 2.1 删除 `@app.route("/api/handle_key_choice")` 端点及其 handler 函数（`server.py` L117-126）
- [x] 2.2 验证 `POST /api/handle_event_choice` 是事件选择的唯一端点

## 3. Frontend Module Split

- [x] 3.1 从 `game-vue.js` 提取状态管理到 `web/js/game-state.js`：`SAVE_KEY`、`DEFAULT_CONFIG`、`gameState`、`newGameData`、`mergeReactive`、`saveGame`、`resetGame`、`loadConfig` 中的 `config` 合并逻辑
- [x] 3.2 从 `game-vue.js` 提取 API 层到 `web/js/game-api.js`：`apiCall`、`handleApiError`、`backendOnline`、`loadConfig`、`checkBackend`
- [x] 3.3 从 `game-vue.js` 提取 UI 层到 `web/js/game-ui.js`：`showEventModal`、`showEventCardModal`、`applyServerResponse`、`handleChoice`、`handleEventChoice`、`closeModal`、`notifyAchievements`、`setNotice`、`effectName`、`describeEffects`
- [x] 3.4 重构 `game-vue.js` 为入口文件：import 三个模块，`createApp({ setup() }})` 只做组件注册和组装
- [x] 3.5 从 `game-vue.js` 删除 `pendingKeyChoice` 状态和 `key_choice` 分支处理（`handleChoice` 中 L462-469）
- [x] 3.6 从 `game-vue.js` 删除 `applyServerResponse` 中 `key_choice` 类型分支（L307-309）
- [x] 3.7 更新 `web/index.html`：将单个 `<script src="js/game-vue.js">` 改为按依赖顺序引入 ES module（或改为 `type="module"` 入口）

## 4. Test Harness

- [x] 4.1 安装 pytest：`pip install pytest`
- [x] 4.2 创建 `test_core.py`，导入 `GameState` 和 `config` 模块
- [x] 4.3 编写 `test_death_triggers_turning_point`：health=0 时多次采样，验证 10% 死亡 / 90% 转机比例（`random.seed(42)` 固定种子）
- [x] 4.4 编写 `test_death_directly_kills`：health=0 且 random < 0.1 时 isDead=True
- [x] 4.5 编写 `test_consecutive_turning_super_event`：consecutiveTurning≥2 触发人生逆袭效果校验
- [x] 4.6 编写 `test_match_conditions_age`：年龄范围匹配/不匹配
- [x] 4.7 编写 `test_match_conditions_flags`：flags_any / flags_all / flags_none 组合校验
- [x] 4.8 编写 `test_select_event_falls_back_to_daily`：无事件卡匹配时返回日常小事
- [x] 4.9 编写 `test_resolve_event_choice_applies_all_side_effects`：effects + flags + relationships + follow_up 全链路
- [x] 4.10 运行 `pytest test_core.py -v` 确保全部通过

## 5. Legacy Files

- [x] 5.1 在 `game.py` 文件头添加 DEPRECATED 注释块
- [x] 5.2 在 `gui.py` 文件头添加 DEPRECATED 注释块

## 6. Integration & Verification

- [x] 6.1 启动 `python server.py`，创建新角色，验证无报错、事件卡正常触发
- [x] 6.2 验证快捷操作（彩票等）正常
- [x] 6.3 验证 API 端点正常（new_game / next_year / lottery / handle_event_choice）
- [x] 6.4 前端 ES module 拆分完成（game-state.js + game-api.js + game-ui.js + game-vue.js）
- [x] 6.5 验证 `/api/handle_key_choice` 返回 404（已删除）
- [x] 6.6 验证 game.py 和 gui.py 仍能 import（仅展示废弃警告，不报错）

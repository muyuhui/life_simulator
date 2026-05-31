## Why

叙事引擎重构（2026-05-08 归档）已将事件分发统一到 `select_event()` → `EVENT_CARDS` 路径，但旧系统的大量代码（`KEY_AGE_CHOICES`、`SMALL_EVENTS`、`HOLIDAY_EVENTS` 及对应方法/API 端点/前端分支）仍全线保留。同时 `core.py`（933 行）和 `game-vue.js`（558 行）分别承担了规则引擎和前端逻辑，零测试覆盖导致后续迭代风险累积。本次清理扫清技术债，并建起安全网。

## What Changes

- **移除** `check_key_age_choice()`、`handle_key_choice()`、`check_small_event()`、`check_holiday_event()` 四个方法及配套数据定义
- **移除** `server.py` 中 `/api/handle_key_choice` 端点（`next_year()` 已不再触发 key_choice）
- **移除** 前端 `game-vue.js` 中 `key_choice` 分支和 `pendingKeyChoice` 状态
- **迁移** `core.py` 中 `SMALL_EVENTS`、`HOLIDAY_EVENTS` 到 `config.py`（标记 deprecated，供后续版本裁剪参考）
- **移除** `core.py` 对 `KEY_AGE_CHOICES` 的 import
- **拆分** `web/js/game-vue.js` 为 `game-state.js` + `game-api.js` + `game-ui.js`，入口保留组装职责
- **新增** `test_core.py` 覆盖关键路径：死亡→转机、连续转机→逆袭、事件选择优先级链、事件卡条件校验
- **标记** `game.py` 和 `gui.py` 为废弃（添加文件头注释，后续移入 archive/）

## Capabilities

### New Capabilities
- `test-harness`: 为 core.py 关键路径建立 pytest 测试框架，覆盖死亡/转机/事件选择/条件匹配
- `frontend-modules`: 将 game-vue.js 拆分为状态管理、API 层、UI 渲染三个独立模块

### Modified Capabilities
_无。本次清理不改任何规则逻辑或 spec 级行为。现有 event-card-system、character-relationships、story-flags、daily-events 的 spec 保持不变。_

## Impact

- `core.py` — 删除 ~150 行死代码（4 个废弃方法 + SMALL_EVENTS/HOLIDAY_EVENTS 数据），减少 3 个 import
- `config.py` — 新增 SMALL_EVENTS 和 HOLIDAY_EVENTS（标记 deprecated，预计 +80 行）
- `server.py` — 删除 `/api/handle_key_choice` 端点（~15 行）
- `web/js/game-vue.js` — 拆为 4 个文件，总行数不变但可维护性提升
- `web/js/game-state.js` — 新文件，状态管理 + 存档
- `web/js/game-api.js` — 新文件，API 封装
- `web/js/game-ui.js` — 新文件，事件卡/modal 渲染
- `web/index.html` — 新增 3 个 `<script>` 标签
- `game.py` / `gui.py` — 添加废弃标记注释
- `test_core.py` — 新文件，pytest 测试（预计 ~100 行）
- `requirements.txt` — 新增 pytest

## Context

叙事引擎重构（2026-05-08 归档，schema: spec-driven）完成后，`next_year()` 已统一走 `select_event()` → `EVENT_CARDS` 路径。但旧系统的代码、数据、API 端点、前端分支仍全线保留，与活跃代码并存。同时 `core.py`（933行单文件）从未有过自动化测试，任何规则修改都靠手工点。

## Goals / Non-Goals

**Goals:**
- 删除所有不再被 `next_year()` 调用的旧事件系统代码（方法、数据、API 端点、前端分支）
- 将 `core.py` 中 `SMALL_EVENTS`/`HOLIDAY_EVENTS` 定义迁移到 `config.py`，统一配置入口
- 为 `core.py` 关键路径建立 pytest 测试框架
- 拆分 `game-vue.js` 为状态/API/UI 三个模块，降低单文件复杂度
- 标记 `game.py` 和 `gui.py` 为废弃

**Non-Goals:**
- 不改任何游戏规则逻辑（数值衰减、收入计算、死亡检查、转机概率、事件条件匹配均不动）
- 不修改 `EVENT_CARDS` / `DAILY_EVENTS` 数据内容
- 不新增 UI 功能或修改 CSS
- 不重构 Flask session 机制
- 不处理 `archive/` 目录下的历史文件

## Decisions

### 1. 死代码删除范围

| 位置 | 删除内容 | 理由 |
|------|---------|------|
| `core.py` | `check_key_age_choice()` + `handle_key_choice()` | `next_year()` 不再调用，前端应走 `event_card` 流程 |
| `core.py` | `check_small_event()` + `check_holiday_event()` | 被 `select_event()` 日常小事 fallback 替代 |
| `core.py` | `SMALL_EVENTS` 和 `HOLIDAY_EVENTS` 数据定义 | 迁移到 config.py 后删除 |
| `core.py` | `KEY_AGE_CHOICES` import | 不再使用 |
| `server.py` | `/api/handle_key_choice` 端点 | 前端应走 `/api/handle_event_choice` |
| `web/js/game-vue.js` | `pendingKeyChoice` 状态 + `key_choice` 处理分支 | 统一走到 `event_card` 分支 |

**保留不删**：`_handle_special()` 方法（被 `resolve_event_choice()` 和 `handle_choice()` 使用）、`KEY_AGE_CHOICES` 在 config.py 中的数据（标记 deprecated 但保留，供数据迁移参考）。

### 2. 前端拆分策略

```
当前结构:
  game-vue.js (558行, 单文件)

拆分后:
  game-state.js    ← 状态定义 (ref/reactive)、存档管理、mergeReactive
  game-api.js      ← apiCall()、handleApiError()、config 加载
  game-ui.js       ← showEventModal()、showEventCardModal()、applyServerResponse()、
                      handleChoice()、handleEventChoice()、notifyAchievements()
  game-vue.js      ← createApp + setup() 入口，import 上述三个模块
```

选择 ES module 还是 IIFE？选 **ES module**（`type="module"`）。Vue 3 CDN 版支持 module 导入，无需构建工具。所有现代浏览器都支持。

### 3. 测试框架选择

选用 **pytest**（Python 生态最主流），不需要 mock 框架——GameState 是纯状态机，测试直接构造状态→调用方法→断言。

测试覆盖 4 条关键路径：
- `test_death_check_triggers_turning_point` — health ≤ 0 时 90% 概率走转机
- `test_death_check_actually_kills` — health ≤ 0 时 10% 概率死亡
- `test_consecutive_turning_super_event` — consecutiveTurning ≥ 2 + 10% → 人生逆袭
- `test_match_conditions_*` — 参数化测试各条件字段
- `test_select_event_returns_daily_fallback` — 无匹配事件卡时回退到日常小事
- `test_resolve_event_choice_applies_effects` — 选择后批量生效

### 4. 配置文件入口统一

目前 `core.py` 和 `config.py` 都在定义事件数据。规则：**所有静态数据进 config.py，core.py 只做 import**。迁移 `SMALL_EVENTS` 和 `HOLIDAY_EVENTS` 到 config.py（但标记 `# DEPRECATED: 已被 EVENT_CARDS + DAILY_EVENTS 替代`）。

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| 删除 `/api/handle_key_choice` 后，有人用了旧版前端缓存 → 请求 404 | 前端已统一走 `event_card` 分支；`key_choice` 只在旧 archive 代码中出现 |
| `game.py` / `gui.py` 标记废弃后，有人还在跑它们 | 添加文件头注释 `⚠️ DEPRECATED: 规则已不同步，请用 server.py + web/`，不改代码 |
| 前端拆分引入 module 加载问题 | `type="module"` 在 Chrome/Firefox/Edge/Safari 均支持；index.html 加 defer 顺序 |
| 测试依赖随机数 → flaky | 用 `random.seed(42)` 固定种子 + 多次采样验证统计比例 |
| SMALL_EVENTS 中 `effect` 字段格式与 core.py 的 `apply_effect` 兼容 | 迁移时不改字段格式 |

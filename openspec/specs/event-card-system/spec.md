# Event Card System

事件卡片是叙事引擎的核心数据结构。每张卡片代表一个需要玩家做出选择的情境。

## Data Model

```python
EventCard = {
    "id": str,                    # 唯一标识，如 "career_crossroads_25"
    "category": str,              # career / relationship / family / moral / opportunity / life_key
    "title": str,                 # 卡片标题
    "flavor": str,                # 情境描述（2-3句，支持 {var} 模板变量插值）
    "conditions": {               # 触发条件（所有条件 AND）
        "age": [min, max],        # 年龄范围
        "has_job": bool | None,
        "has_spouse": bool | None,
        "has_children": bool | None,
        "education": [min, max] | None,
        "career": [min, max] | None,
        "health": [min, max] | None,
        "happiness": [min, max] | None,
        "money": [min, max] | None,
        "flags_any": [str] | None,    # 拥有任一 flag 则可触发
        "flags_all": [str] | None,    # 必须拥有全部 flag
        "flags_none": [str] | None,   # 不能拥有这些 flag
    },
    "priority": int,              # 0=日常 5=重要 10=人生关键，高优先级优先触发
    "repeatable": bool,           # 是否可重复触发（默认 False）
    "choices": [EventChoice],     # 2-4 个选项
    "follow_up": str | None,      # 明年优先触发的事件 ID（连锁事件）
    "unlock_pool": str | None,    # 解锁事件池标签（后续事件用 conditions.flags_any 匹配）
}
```

## Selection Engine

每一年的事件选择逻辑（优先级从高到低）：

1. **pendingEvent** — 如果上一年选择的 `follow_up` 设置了待触发事件，且条件仍满足，则触发
2. **关键年龄** — 检查 `priority >= 10` 且 `conditions.age` 匹配
3. **高优先级事件** — 从 `priority >= 5` 且条件匹配的事件池中随机抽取
4. **通用事件** — 从条件匹配的普通事件池中随机抽取
5. **日常小事** — 无事件卡匹配时，从 `DAILY_EVENTS` 池中抽取

抽取概率：符合条件的卡片按 priority 加权随机抽取。已被触发过的非 repeatable 卡片不再出现。

## Event Choice

```python
EventChoice = {
    "text": str,                  # 选项文本（按钮上显示）
    "flavor": str | None,         # 选项的叙事补充
    "effects": {                  # 数值变化
        "money": int | None,
        "health": int | None,
        "happiness": int | None,
        "career": int | None,
    },
    "flags_set": [str] | None,    # 设置这些 storyFlags
    "flags_clear": [str] | None,  # 清除这些 storyFlags
    "relationship_changes": {     # 关系值变化
        "<character_id>": int,    # 正数为增加，负数为减少
    },
    "special": str | None,        # 触发特殊逻辑（沿用现有 _handle_special 机制）
    "follow_up": str | None,      # 设置下次优先触发的事件 ID
    "unlock_pool": str | None,    # 解锁事件池
}
```

## Requirements

### Requirement: Event Card Data Model
系统 SHALL 支持事件卡片数据结构，每张卡片包含 id、category、title、flavor（情境描述）、conditions（触发条件）、priority、choices（2-4 个选项）。

#### Scenario: 创建一张事件卡
- **WHEN** 定义事件卡时提供所有必需字段
- **THEN** 事件卡可用于事件选择引擎

### Requirement: Event Selection Engine
每一年 SHALL 按优先级选择事件：pendingEvent（最高）、关键年龄事件（priority >= 10）、高优先级事件（priority >= 5）、通用事件、日常小事（最低）。

#### Scenario: 存在连锁事件时优先触发
- **GIVEN** 上一年选择设置了 follow_up 事件 ID
- **AND** 该事件的 conditions 仍满足
- **WHEN** 玩家点击"下一年"
- **THEN** 返回该连锁事件卡

#### Scenario: 无匹配事件时回退到日常小事
- **GIVEN** 当前年份没有任何事件卡的条件被满足
- **WHEN** 玩家点击"下一年"
- **THEN** 返回一条日常小事（含两个选项）

### Requirement: Choice Resolution
玩家选择后 SHALL 批量应用 effects（数值变化）、flags_set/flags_clear（叙事标记）、relationship_changes（关系值变化）、follow_up（设置下次事件）。

#### Scenario: 选择一个选项后应用所有后果
- **GIVEN** 当前事件卡有 3 个选项
- **WHEN** 玩家选择第 2 个选项
- **THEN** 该选项的 effects 生效、flags 被设置/清除、关系值被更新、follow_up 写入 pendingEvent

### Requirement: Template Variable Interpolation
flavor 文本中 SHALL 支持模板变量（如 `{spouse_name}`），渲染时替换为实际数据。

#### Scenario: 已婚玩家的 flavor 文本包含伴侣名
- **GIVEN** 玩家已婚，伴侣名为"小美"
- **AND** 事件卡 flavor 包含 `{spouse_name}`
- **WHEN** 渲染该事件卡
- **THEN** `{spouse_name}` 被替换为"小美"

### Requirement: Non-repeatable Events
非 repeatable 事件卡触发后 SHALL 记录到 triggeredEvents 集合，后续不再出现。

#### Scenario: 已触发的事件不再出现
- **GIVEN** 事件卡 E1 的 repeatable 为 false
- **AND** E1 已在 25 岁时触发过
- **WHEN** 后续年份进行事件选择
- **THEN** E1 不会出现在候选事件池中

# Event Card System

## ADDED Requirements

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

# Daily Events

## ADDED Requirements

### Requirement: Daily Event Fallback
没有事件卡触发的年份 SHALL 自动从 DAILY_EVENTS 池中抽取一条作为叙事填充，确保每一年至少有一次玩家互动（二选一）。

#### Scenario: 无事件卡的年份触发日常小事
- **GIVEN** 当前年份 select_event() 无任何事件卡匹配
- **WHEN** 玩家点击"下一年"
- **THEN** 返回一条日常小事（含 flavor 描述和 2 个选项）

### Requirement: Category Distribution
日常小事 SHALL 按权重分配类别：social 25%、work 20%、family 20%、health 15%、happy 10%、sad 5%、random 5%。

#### Scenario: 小概率事件自然稀有
- **GIVEN** random 类别权重为 5%
- **WHEN** 进行 100 次日常小事抽取
- **THEN** random 类别事件出现约 5 次

### Requirement: Generic Fallback Pool
至少 5 条日常小事 SHALL 不设置任何 conditions（无条件触发），确保所有年份都有可用的日常事件。

#### Scenario: 极端年份仍有日常事件
- **GIVEN** 玩家年龄 120 岁（超出大部分条件范围）
- **WHEN** select_event() 查找日常小事
- **THEN** 从无条件限制的通用池中找到至少一条可用事件

### Requirement: No Follow-up Chains
日常小事 SHALL NOT 设置 follow_up 字段，不启动连锁事件。

#### Scenario: 日常选择不连锁
- **WHEN** 玩家完成日常小事选择
- **THEN** pendingEvent 被清空（或保持原值，不被日常小事覆盖）

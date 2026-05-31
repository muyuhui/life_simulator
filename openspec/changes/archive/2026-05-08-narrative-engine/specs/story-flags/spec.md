# Story Flags

## ADDED Requirements

### Requirement: Flag Storage
GameState SHALL 存储 `storyFlags` 字段（序列化为 `list[str]`，运行时为 `set[str]`），追踪玩家人生中的关键选择标记。

#### Scenario: 选择"上大学"后 flag 被设置
- **GIVEN** storyFlags 当前为 {}
- **WHEN** 18 岁事件中选择"高考-努力备考"（flags_set: ["went_to_college"]）
- **THEN** storyFlags 包含 "went_to_college"

### Requirement: Condition Matching with Flags
事件条件匹配 SHALL 支持 `flags_any`（OR）、`flags_all`（AND）、`flags_none`（NOT）三种模式，三者之间为 AND 关系。

#### Scenario: flags_any 匹配
- **GIVEN** storyFlags 包含 "went_to_college"
- **WHEN** 事件条件为 `flags_any: ["went_to_college", "went_to_grad_school"]`
- **THEN** 条件匹配成功

#### Scenario: flags_none 排斥
- **GIVEN** storyFlags 包含 "divorced"
- **WHEN** 事件条件为 `flags_none: ["divorced", "never_married"]`
- **THEN** 条件匹配失败

### Requirement: Ending Generation
游戏结束时 SHALL 根据 storyFlags 组合生成个性化人生总结（2-3 句中文）。

#### Scenario: 创业者的结局
- **GIVEN** storyFlags 包含 went_to_college, started_business, took_big_risk
- **WHEN** 游戏结束
- **THEN** generate_ending() 返回包含"创业"和"风险"主题的总结文字

### Requirement: Flag Clear
事件选项 SHALL 支持 `flags_clear` 字段，清除不再适用的标记。

#### Scenario: 离婚后清除婚姻相关 flag
- **GIVEN** storyFlags 包含 "married_early"
- **WHEN** 触发离婚事件
- **THEN** "married_early" 被清除，"divorced" 被设置

# Character Relationships

## ADDED Requirements

### Requirement: Character Data Model
系统 SHALL 存储有名有姓的人物数据，每个角色包含 id、name、role、personality、affection（-100~100）、history、first_met_age、status、age。

#### Scenario: 创建一个关系角色
- **WHEN** 相亲事件成功后生成伴侣角色
- **THEN** relationships 数组中新增一个 role=spouse 的 Character 对象，name 从名字池中随机选取

### Requirement: Affection Changes
事件选择中的 relationship_changes SHALL 实时更新对应角色的 affection 值，并记录到 history。

#### Scenario: 帮助朋友后关系值上升
- **GIVEN** 与李维当前 affection 为 40
- **WHEN** 事件中选择"倾力帮助李维"（relationship_changes: {"liwei": 20}）
- **THEN** 李维的 affection 变为 60，history 新增一条记录

### Requirement: Core Characters
每局游戏 SHALL 自动生成父母角色（开局即存在），并通过关键事件引入伴侣和挚友。核心人物数量控制在 3-5 个。

#### Scenario: 开局时自动创建父母
- **GIVEN** 玩家创建新角色开始游戏
- **WHEN** GameState.new() 被调用
- **THEN** relationships 包含 father 和 mother 两个角色，affection 初始 70

### Requirement: Frontend Relationship Panel
游戏界面 SHALL 展示"人物网络"区域，显示核心人物的名字、角色标签、关系值条。

#### Scenario: 查看当前人际关系
- **GIVEN** 玩家有 4 个关系角色（父亲、母亲、李维-朋友、小美-伴侣）
- **WHEN** 玩家查看游戏主界面
- **THEN** 人物网络面板显示 4 个角色的名字、关系值条、最近互动

### Requirement: Affection-driven Event Gates
affection >= 80 SHALL 解锁"深厚关系"事件池，affection <= -60 SHALL 可能触发"关系破裂"事件。

#### Scenario: 高亲密度解锁特殊事件
- **GIVEN** 小美 affection 为 85
- **AND** 事件池中有 conditions.flags_any: ["high_affection_spouse"] 的事件
- **WHEN** 某年事件选择时
- **THEN** 该特殊事件进入候选池

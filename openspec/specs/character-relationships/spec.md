# Character Relationships

有名有姓的人物系统，替代当前无状态的 spouse/children 字符串。

## Data Model

```python
Character = {
    "id": str,                    # 唯一标识，如 "liwei", "xiaomei"
    "name": str,                  # 中文名
    "role": str,                  # spouse / child / parent / friend / mentor / rival / colleague / ex / stranger
    "personality": str,           # warm / cold / ambitious / kind / sarcastic / loyal / pragmatic / romantic
    "affection": int,             # 关系值 -100 ~ 100
    "history": [RelationshipEvent],  # 共同经历
    "first_met_age": int,         # 认识时的年龄
    "status": str,                # alive / dead / estranged / distant / close
    "age": int | None,            # 人物年龄（可空）
}

RelationshipEvent = {
    "age": int,                   # 发生时的年龄
    "summary": str,               # 一句话总结这件事
}
```

## Relationship Rules

- `affection` 范围 -100（极度厌恶）到 100（无条件信任）
- 初始值根据角色类型：父母 70、朋友 40、伴侣 60（婚后）、同事 20
- 每次事件选择中的 `relationship_changes` 叠加到 affection
- affection 低于 -60 时触发"关系破裂"事件的可能性
- affection 高于 80 时解锁"深厚关系"事件池
- 角色 `status` 根据事件结果变化：alive → estranged（疏远）、alive → dead（死亡事件）
- 关系历史记录每次有 `relationship_changes` 的事件概要

## Character Generation

- 核心人物（伴侣、挚友）通过关键事件引入（如 dating 事件、大学事件）
- 配角按需生成：父母在开局时自动创建（id: "father", "mother"）
- 人物名字从预设名字池中随机抽取，避免重复
- 人物性格从 8 种标签中按角色类型加权分配
- 子女在 `has_children` 事件中生成，名字可预设或随机

## Requirements

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

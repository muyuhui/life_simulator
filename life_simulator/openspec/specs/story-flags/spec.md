# Story Flags

叙事状态标记系统，追踪玩家在人生中的关键选择，影响后续事件池和结局生成。

## Data Model

```python
# GameState 中新增字段
storyFlags: set[str]  # 如 {"went_to_college", "started_business", "married_early"}

# 预设 flag 目录（第一版约 30 个）
STORY_FLAGS = {
    # 教育路线
    "went_to_college": "考上大学",
    "went_to_grad_school": "读研深造",
    "dropped_out": "辍学",
    "no_higher_edu": "没上过大学",

    # 职业路线
    "started_business": "创过业",
    "job_hopped": "频繁跳槽",
    "loyal_employee": "在一家公司干到老",
    "got_fired": "被裁员过",
    "changed_career": "转行",

    # 关系路线
    "married_early": "早婚（25岁前）",
    "married_late": "晚婚（35岁后）",
    "never_married": "终身未婚",
    "divorced": "离过婚",
    "has_children": "有子女",
    "childfree": "选择不生",
    "lost_child": "失去过孩子",

    # 道德/性格路线
    "took_big_risk": "冒过大险",
    "played_safe": "一生求稳",
    "chose_money": "选择了金钱",
    "chose_love": "选择了爱情",
    "helped_friend": "帮过朋友大忙",
    "betrayed_friend": "背叛过朋友",
    "helped_stranger": "帮助过陌生人",
    "told_truth": "坚守诚实",
    "told_lie": "说过大谎",
    "reconciled_with_parents": "与父母和解",

    # 机会/命运
    "won_lottery": "中过大奖",
    "inherited_money": "继承过遗产",
    "got_scammed": "被骗过大钱",
    "discovered_talent": "发现了隐藏天赋",
    "near_death": "经历过生死边缘",

    # 逆袭/转机
    "comeback_king": "逆袭者",        # 已有（lifeLabels）
    "survivor": "绝境逢生",           # 已有（turningPoints >= 5）
}
```

## Condition Matching

事件卡的 conditions 中使用三种 flag 匹配模式：

```python
"conditions": {
    "flags_any": ["went_to_college", "went_to_grad_school"],  # OR
    "flags_all": ["started_business", "has_children"],        # AND
    "flags_none": ["divorced", "never_married"],              # NOT
}
```

匹配逻辑：`flags_any` 和 `flags_all` 和 `flags_none` 三者 AND（所有指定的都满足）。

## Ending Generation

游戏结束时，根据 storyFlags 集合生成个性化人生总结：

```python
def generate_ending(game_state) -> str:
    """
    根据 flags 组合生成 2-3 句简短总结。
    规则优先级：特定组合 > 单类标记 > 通用总结。
    """
```

总结生成规则示例：
- `{went_to_college, started_business, took_big_risk}` → "你受过高等教育，却不甘于按部就班。创业的路上你赌过、输过、也赢过。"
- `{no_higher_edu, loyal_employee, played_safe}` → "你没有耀眼的学历，但几十年如一日的踏实，为家人撑起了一片天。"
- `{divorced, chose_love, helped_stranger}` → "你在爱情里受过伤，但从未因此变得冷漠。有人记得你伸出的手。"

## Requirements

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

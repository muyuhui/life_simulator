# Daily Events

没有事件卡触发的年份，生成小型二选一事件作为叙事填充，确保每一年都有互动。

## Data Model

```python
DailyEvent = {
    "id": str,
    "category": str,              # happy / sad / social / work / family / health / random
    "flavor": str,                # 1-2 句情境描述
    "conditions": {               # 触发条件（同 EventCard 的条件结构，简化版）
        "age": [min, max],
        "has_job": bool | None,
        "has_spouse": bool | None,
        "has_children": bool | None,
    },
    "choices": [
        {
            "text": str,
            "flavor": str | None,
            "effects": {
                "money": int | None,
                "health": int | None,
                "happiness": int | None,
                "career": int | None,
            },
            "flags_set": [str] | None,
            "relationship_changes": {"<character_id>": int} | None,
        },
        # 第二个选项
    ],
}
```

## Categories & Probabilities

日常小事的类别分配：

| 类别 | 权重 | 示例 |
|------|------|------|
| social | 25% | 朋友聚会、同事互动、邻里事件 |
| work | 20% | 加班、请假、项目抉择 |
| family | 20% | 家人电话、家务琐事、孩子教育小事 |
| health | 15% | 锻炼、生病、饮食选择 |
| happy | 10% | 意外惊喜、节日气氛 |
| sad | 5% | 丢失物品、小磕碰 |
| random | 5% | 极小概率事件（彩票、星探等，整体概率 <5%） |

## Requirements

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

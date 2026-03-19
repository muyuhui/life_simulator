#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
熬过去 - 人生模拟器 统一配置
所有游戏配置数据集中管理，避免多文件重复
"""

# ============ 基础配置 ============

BACKGROUNDS = {
    "1": {"name": "小镇青年", "money": 5000, "happiness": 70, "career": 20},
    "2": {"name": "城市中产", "money": 50000, "happiness": 60, "career": 50},
    "3": {"name": "富二代", "money": 200000, "happiness": 80, "career": 30},
    "4": {"name": "农村出身", "money": 2000, "happiness": 60, "career": 10},
}

TALENTS = {
    "1": {"name": "学习天赋", "effect": {"studyBonus": 0.3}},
    "2": {"name": "社交达人", "effect": {"socialBonus": 0.2}},
    "3": {"name": "财运亨通", "effect": {"moneyBonus": 0.3}},
    "4": {"name": "健康体质", "effect": {"healthDecay": 0.5}},
}

PERSONALITIES = {
    "1": {"name": "稳健型", "effect": {"riskReduction": 0.2}},
    "2": {"name": "冒险型", "effect": {"riskBonus": 0.3}},
    "3": {"name": "佛系型", "effect": {"happinessDecay": 0.3}},
}

DIFFICULTIES = {
    "1": {"name": "普通模式", "turningRate": 0.9},
    "2": {"name": "硬核模式", "turningRate": 0.7},
    "3": {"name": "休闲模式", "turningRate": 1.0},
}

# ============ 转机事件 ============

TURNING_POINT_EVENTS = [
    {"title": "贵人相助", "desc": "在你最困难的时候，有人伸出了援手", "result": {"money": 30000, "happiness": 20}, "type": "平淡回归"},
    {"title": "奇迹康复", "desc": "医生说这是医学奇迹", "result": {"health": 60}, "type": "平淡回归"},
    {"title": "继承遗产", "desc": "远方亲戚去世了，留给你一笔遗产", "result": {"money": 50000, "happiness": 15}, "type": "小改善"},
    {"title": "中彩票", "desc": "你随手买的彩票居然中了！", "result": {"money": 100000, "happiness": 30}, "type": "中改善"},
    {"title": "遇到真爱", "desc": "在最孤单的时候，你遇到了对的人", "result": {"happiness": 40, "money": 10000}, "type": "平淡回归"},
    {"title": "想通了", "desc": "经历了这么多，你突然想通了一些事", "result": {"happiness": 30, "health": 10}, "type": "平淡回归"},
]

# 出身专属转机
BACKGROUND_TURNING_EVENTS = {
    "4": [
        {"title": "同乡介绍高薪零工", "desc": "老家同乡给你介绍了一份高薪工作", "effect": {"money": 30000, "career": 10}},
        {"title": "老家征地补偿", "desc": "老家土地被征用，得到一笔补偿", "effect": {"money": 80000}},
        {"title": "亲戚帮扶创业", "desc": "亲戚出资帮你创业", "effect": {"money": 50000, "career": 15}},
    ],
    "1": [
        {"title": "老同学推荐工作", "desc": "老同学给你推荐了一份好工作", "effect": {"money": 30000, "career": 20}},
        {"title": "家乡特产带货", "desc": "你把家乡特产做成了生意", "effect": {"money": 40000, "happiness": 10}},
        {"title": "父母介绍对象", "desc": "父母给你介绍了一个不错的对象", "effect": {"happiness": 15}},
    ],
    "2": [
        {"title": "前同事推荐跳槽", "desc": "前同事推荐你去一家更好的公司", "effect": {"money": 80000, "career": 25}},
        {"title": "理财盈利", "desc": "之前的投资获得了丰厚回报", "effect": {"money": 100000}},
        {"title": "技能证书补贴", "desc": "考取的证书获得了补贴", "effect": {"money": 20000, "career": 18}},
    ],
    "3": [
        {"title": "家族创业资源", "desc": "利用家族资源创业成功", "effect": {"money": 150000, "career": 40}},
        {"title": "海外投资收益", "desc": "海外投资获得了高回报", "effect": {"money": 200000}},
        {"title": "长辈赠予资产", "desc": "长辈直接赠予你一笔资产", "effect": {"money": 300000}},
    ],
}

# 转机代价（统一添加 desc 字段）
TURNING_COSTS = {
    "borrow_money": {
        "desc": "借款度过难关",
        "condition": lambda s: s.get("money", 0) < -50000,
        "chance": 0.3,
        "effect": {"money": 50000},
        "costEffect": {"debt": 0.1}
    },
    "family_support": {
        "desc": "家人支持",
        "condition": lambda s: s.get("health", 100) < 20 or s.get("happiness", 100) < 10,
        "chance": 0.25,
        "effect": {"health": 25, "happiness": 25}
    },
    "stranger_kindness": {
        "desc": "陌生人帮助",
        "chance": 0.15,
        "effect": {"happiness": 15}
    },
    "old_friend_help": {
        "desc": "老朋友援助",
        "condition": lambda s: s.get("happiness", 100) < 10,
        "chance": 0.2,
        "effect": {"happiness": 30}
    },
}

# 关键年龄选择
KEY_AGE_CHOICES = {
    18: [
        {"text": "🎓 高考 - 努力备考", "desc": "参加高考，冲击名校", "effect": {"money": -5000}, "special": "gaokao", "outcome": "考大学"},
        {"text": "💰 高考 - 打工赚钱", "desc": "不参加高考，直接去打工", "effect": {"money": 10000}, "special": "work_no_edu", "outcome": "学历高中"},
        {"text": "✈️ Gap Year旅行", "desc": "休息一年去旅行", "effect": {"money": -5000, "happiness": 30}, "special": "gap_year", "outcome": "见多识广buff"},
    ],
    22: [
        {"text": "📚 考研深造", "desc": "继续读研究生", "effect": {"money": -20000}, "special": "kaoyan", "outcome": "学历+1"},
        {"text": "💼 直接工作", "desc": "步入社会工作", "effect": {"happiness": 10}, "special": "find_job", "outcome": "找工作"},
    ],
    25: [
        {"text": "深耕现有职业", "desc": "在现有领域继续发展", "effect": {"career": 15}, "special": "career_stay", "outcome": "职业成长+2%"},
        {"text": "跨行业转行", "desc": "换一个赛道重新开始", "effect": {"career": -10, "happiness": -5}, "special": "career_change", "outcome": "新职业池"},
        {"text": "创业试水", "desc": "拿出积蓄尝试创业", "effect": {"money": -50000}, "special": "startup", "outcome": "创业成功率+10%"},
    ],
    28: [
        {"text": "📚 考博深造", "desc": "继续读博士", "effect": {"money": -30000}, "special": "kaobo", "outcome": "学历+1"},
        {"text": "💼 直接工作", "desc": "步入社会工作", "effect": {"happiness": 10}, "special": "find_job", "outcome": "找工作"},
    ],
    35: [
        {"text": "求稳为主", "desc": "保守策略，降低风险", "effect": {}, "special": "stability_first", "outcome": "失业风险-15%"},
        {"text": "孤注一掷", "desc": "全力冲击事业巅峰", "effect": {"career": -5}, "special": "all_in", "outcome": "创业收益x1.5"},
        {"text": "培养新人", "desc": "指导后辈，获得成就感", "effect": {"career": -5}, "special": "mentor", "outcome": "导师buff"},
    ],
    50: [
        {"text": "提前退休", "desc": "享受生活", "effect": {"happiness": 20}, "special": "early_retire", "outcome": "收入-50%"},
        {"text": "继续打拼", "desc": "老骥伏枥", "effect": {"happiness": -10}, "special": "keep_working", "outcome": "事业+4%"},
        {"text": "发展兴趣", "desc": "培养业余爱好", "effect": {"career": -5, "happiness": 25}, "special": "hobby_career", "outcome": "兴趣职业"},
    ],
}

# ============ 通用函数 ============

def clamp(value, min_val=0, max_val=100):
    return max(min_val, min(max_val, value))

def format_money(amount):
    if amount >= 10000:
        return f"{amount/10000:.1f}万"
    return str(amount)

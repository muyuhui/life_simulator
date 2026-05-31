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

# 关键年龄选择（DEPRECATED: 已迁移到 EVENT_CARDS 事件卡片系统，保留此数据仅供向后兼容）
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

# ============ 叙事引擎配置 ============

STORY_FLAGS = {
    "went_to_college": "考上大学",
    "went_to_grad_school": "读研深造",
    "no_higher_edu": "没上大学",
    "started_business": "创过业",
    "job_hopped": "频繁跳槽",
    "loyal_employee": "从一而终",
    "got_fired": "被裁员过",
    "changed_career": "转过行",
    "married_early": "早婚",
    "married_late": "晚婚",
    "never_married": "终身未婚",
    "divorced": "离过婚",
    "has_children": "有子女",
    "childfree": "选择不生",
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
    "won_lottery": "中过大奖",
    "inherited_money": "继承过遗产",
    "got_scammed": "被骗过大钱",
    "discovered_talent": "发现了隐藏天赋",
    "near_death": "经历过生死边缘",
    "comeback_king": "逆袭者",
}

CHARACTER_NAMES = {
    "male": ["李维", "王磊", "张伟", "刘洋", "陈浩", "赵峰", "周宇", "吴凯"],
    "female": ["小美", "小红", "小丽", "小芳", "小雪", "小雨", "小月", "小琳"],
    "family": ["李明", "王芳", "张建国", "刘秀英", "陈志远", "赵秀兰"],
}

PERSONALITY_TRAITS = {
    "warm": {"name": "热情", "desc": "对人真诚，乐于助人"},
    "cold": {"name": "冷淡", "desc": "不善言辞，保持距离"},
    "ambitious": {"name": "有野心", "desc": "目标明确，不满足于现状"},
    "kind": {"name": "善良", "desc": "心软，不忍心伤害他人"},
    "sarcastic": {"name": "毒舌", "desc": "嘴上不饶人，心里有杆秤"},
    "loyal": {"name": "重义", "desc": "对朋友两肋插刀"},
    "pragmatic": {"name": "务实", "desc": "不看虚的，只看实在的"},
    "romantic": {"name": "浪漫", "desc": "相信爱情，追求美好"},
}

EVENT_CARDS = [
    # ═══════ 18-21岁：初入社会 (4张) ═══════
    {
        "id": "edu_path_18",
        "category": "life_key",
        "title": "人生的分岔口",
        "flavor": "高中毕业了。教室外的蝉鸣还没停，你已经站在了人生的第一个十字路口。父母说考大学是唯一的出路，但班上几个同学已经南下打工了。",
        "conditions": {"age": [18, 18]},
        "priority": 10,
        "repeatable": False,
        "choices": [
            {"text": "📚 努力备考高考", "flavor": "再拼一年，考个好大学", "effects": {"money": -5000}, "flags_set": ["went_to_college"], "special": "gaokao", "follow_up": None},
            {"text": "💰 直接打工赚钱", "flavor": "不读书了，早点赚钱养家", "effects": {"money": 10000, "happiness": -10}, "flags_set": ["no_higher_edu"], "special": "work_no_edu", "follow_up": None},
            {"text": "✈️ 休息一年去旅行", "flavor": "给自己一个 Gap Year", "effects": {"money": -5000, "happiness": 30}, "flags_set": ["went_to_college"], "special": "gap_year", "follow_up": None},
        ],
    },
    {
        "id": "leave_hometown_19",
        "category": "life_key",
        "title": "离开还是留下",
        "flavor": "你站在熟悉的街角，看着这座生活了十几年的小城。去大城市的同学说那里机会多，但房租贵、节奏快。留在老家，日子安稳，但一眼望得到头。",
        "conditions": {"age": [19, 21]},
        "priority": 8,
        "repeatable": False,
        "choices": [
            {"text": "🚄 去大城市闯荡", "flavor": "机会多，风险也大", "effects": {"career": 10, "happiness": -5}, "flags_set": ["took_big_risk"], "follow_up": "first_job_21"},
            {"text": "🏡 留在家乡发展", "flavor": "日子稳，知根知底", "effects": {"happiness": 10, "money": 5000}, "flags_set": ["played_safe"], "follow_up": "first_job_21"},
        ],
    },
    {
        "id": "first_job_21",
        "category": "career",
        "title": "第一份工作",
        "flavor": "投了十几份简历，终于有两家公司给了回音。一家是稳定的大公司，起薪一般但福利好。另一家是刚成立的小创业公司，老板很有激情，但工资都发得不太稳定。",
        "conditions": {"age": [20, 23], "flags_none": ["started_business"]},
        "priority": 7,
        "repeatable": False,
        "choices": [
            {"text": "🏢 去大公司", "flavor": "稳定起步，慢慢积累", "effects": {"career": 5, "happiness": 5}, "flags_set": ["played_safe"], "special": "find_job", "follow_up": None},
            {"text": "🚀 去创业公司", "flavor": "赌一把，跟对人", "effects": {"career": 15, "money": -3000}, "flags_set": ["took_big_risk"], "special": "find_job", "follow_up": None},
        ],
    },
    {
        "id": "meet_someone_22",
        "category": "relationship",
        "title": "遇到一个人",
        "flavor": "在一次朋友的聚会上，你注意到了一个特别的人。你们聊了很久，话题从喜欢的音乐聊到对未来的想法。散场时，你想去要联系方式，但突然有点紧张。",
        "conditions": {"age": [21, 24], "flags_none": ["married_early", "never_married"]},
        "priority": 6,
        "repeatable": False,
        "choices": [
            {"text": "💕 主动走近", "flavor": "错过可能就是一辈子", "effects": {"happiness": 20, "money": -500}, "flags_set": ["chose_love"], "special": "dating", "follow_up": None},
            {"text": "🤔 随缘吧", "flavor": "现在还不是时候", "effects": {"happiness": -5}, "flags_set": ["played_safe"], "follow_up": None},
        ],
    },

    # ═══════ 22-29岁：青年发展 (7张) ═══════
    {
        "id": "career_first_choice_24",
        "category": "career",
        "title": "职场第一个坎",
        "flavor": "干了两年，你开始觉得每天重复同样的事。隔壁组在招人，工资高一些但要从头学起。这时候，你听说行业内一家新公司在招人。",
        "conditions": {"age": [23, 26], "has_job": True, "flags_none": ["started_business"]},
        "priority": 6,
        "repeatable": False,
        "choices": [
            {"text": "📈 深耕当前方向", "flavor": "积累才有厚度", "effects": {"career": 15}, "flags_set": ["loyal_employee"], "special": "career_stay", "follow_up": None},
            {"text": "🔄 跳槽去新公司", "flavor": "换个环境试试", "effects": {"money": 15000, "career": 5}, "flags_set": ["job_hopped"], "special": "find_job", "follow_up": None},
            {"text": "🎓 回头去读书", "flavor": "还想再学点东西", "effects": {"money": -20000, "career": -5}, "flags_set": ["went_to_grad_school"], "special": "kaoyan", "follow_up": None},
        ],
    },
    {
        "id": "friend_needs_help_25",
        "category": "relationship",
        "title": "朋友来借钱",
        "flavor": "一个认识多年的朋友突然打来电话。他声音疲惫，说家里出了点事，急需用钱。数目不小——大概是你两个月的工资。他说半年内还你，但你知道他现在的经济状况不太好。",
        "conditions": {"age": [24, 28]},
        "priority": 5,
        "repeatable": False,
        "choices": [
            {"text": "🤝 借给他", "flavor": "朋友有难，不能不帮", "effects": {"money": -15000}, "flags_set": ["helped_friend"], "relationship_changes": {"friend": 25}, "follow_up": "friend_repay_27"},
            {"text": "😔 委婉拒绝", "flavor": "我也很难，实在帮不了", "effects": {"happiness": -10}, "flags_set": ["chose_money"], "relationship_changes": {"friend": -20}, "follow_up": None},
        ],
    },
    {
        "id": "friend_repay_27",
        "category": "relationship",
        "title": "旧事重提",
        "flavor": "两年过去了。那个朋友突然请你吃饭。他瘦了一些，但眼神比那时候有光了。他从包里拿出一个信封，说里面是欠你的钱，还有利息。",
        "conditions": {"age": [26, 30], "flags_all": ["helped_friend"]},
        "priority": 8,
        "repeatable": False,
        "choices": [
            {"text": "💰 收下本金就好", "flavor": "利息就不用了，你走出来就好", "effects": {"money": 15000, "happiness": 15}, "flags_set": ["chose_love"], "relationship_changes": {"friend": 15}, "follow_up": None},
            {"text": "🎁 这笔钱不用还了", "flavor": "当年帮你不是为了让你还", "effects": {"happiness": 25}, "flags_set": ["chose_love"], "relationship_changes": {"friend": 25}, "follow_up": None},
        ],
    },
    {
        "id": "parents_expectation_26",
        "category": "family",
        "title": "父母的电话",
        "flavor": "过年回家，母亲做了一桌子菜。吃到一半，她小心翼翼地开口：你二姨家的女儿今年考上了公务员，工作稳定。你爸在旁边咳嗽了两声，说隔壁老李家抱孙子了。",
        "conditions": {"age": [25, 29], "flags_none": ["reconciled_with_parents", "married_early"]},
        "priority": 5,
        "repeatable": False,
        "choices": [
            {"text": "😤 坚持自己的生活节奏", "flavor": "我的人生我说了算", "effects": {"happiness": -10, "career": 10}, "flags_set": ["took_big_risk"], "follow_up": None},
            {"text": "🤗 试着理解他们", "flavor": "他们只是关心我", "effects": {"happiness": 5}, "flags_set": ["reconciled_with_parents"], "follow_up": None},
        ],
    },
    {
        "id": "windfall_27",
        "category": "opportunity",
        "title": "一笔意外之财",
        "flavor": "你在抽屉里翻到了一张旧银行卡，抱着试试的心态去查了一下余额——里面竟然还有一笔钱。是几年前一个兼职项目打来的尾款，你完全忘记了。不算多，但也足够做点什么。",
        "conditions": {"age": [26, 30], "flags_none": ["got_scammed"]},
        "priority": 5,
        "repeatable": False,
        "choices": [
            {"text": "💰 买点东西犒劳自己", "flavor": "辛苦这么久，该享受一下", "effects": {"happiness": 20, "money": 10000}, "flags_set": ["chose_money"], "follow_up": None},
            {"text": "📈 投资理财", "flavor": "钱生钱才是正道", "effects": {"money": 30000}, "flags_set": ["chose_money"], "follow_up": None},
            {"text": "👨‍👩‍👧 给父母寄去", "flavor": "他们为我付出了太多", "effects": {"money": -10000, "happiness": 10}, "flags_set": ["reconciled_with_parents"], "follow_up": None},
        ],
    },
    {
        "id": "love_crossroads_28",
        "category": "relationship",
        "title": "感情的分叉口",
        "flavor": "你们在一起有几年了。最近吵架的次数变多了，都是些小事——谁洗碗、周末去哪、要不要换城市。但你也知道，不是因为洗碗。是两个人都在想：这个人，是那个要一起过一辈子的人吗？",
        "conditions": {"age": [27, 31], "has_spouse": True, "flags_none": ["married_early", "divorced", "never_married"]},
        "priority": 7,
        "repeatable": False,
        "choices": [
            {"text": "💍 求婚 / 答应求婚", "flavor": "就是这个人了", "effects": {"happiness": 25, "money": -30000}, "flags_set": ["married_early", "chose_love"], "relationship_changes": {"spouse": 20}, "follow_up": None},
            {"text": "💔 分手", "flavor": "我们可能真的不合适", "effects": {"happiness": -25, "career": 5}, "flags_set": ["divorced"], "relationship_changes": {"spouse": -80}, "follow_up": "post_breakup_30"},
            {"text": "⏳ 再想想", "flavor": "不急这一两年", "effects": {"happiness": -5}, "flags_set": ["played_safe"], "follow_up": None},
        ],
    },
    {
        "id": "study_opportunity_28",
        "category": "career",
        "title": "深造的机会",
        "flavor": "一个老同事说他准备去读 MBA，问你要不要一起。学费不菲，但他说班上的同学来自各行各业，学到的东西让他对工作有了全新的理解。你的工作正处于瓶颈期。",
        "conditions": {"age": [28, 32], "has_job": True, "flags_none": ["went_to_grad_school", "started_business"]},
        "priority": 5,
        "repeatable": False,
        "choices": [
            {"text": "🎓 辞职去读", "flavor": "投资自己永远不会亏", "effects": {"money": -50000, "career": 20, "happiness": 10}, "flags_set": ["went_to_grad_school", "took_big_risk"], "follow_up": None},
            {"text": "💼 在职坚持", "flavor": "边工作边学习", "effects": {"money": -20000, "career": 10, "health": -10}, "flags_set": ["loyal_employee"], "follow_up": None},
        ],
    },

    # ═══════ 30-49岁：中年沉淀 (6张) ═══════
    {
        "id": "child_decision_30",
        "category": "family",
        "title": "要不要孩子",
        "flavor": "这个话题在家里越来越频繁地被提起。你看着身边有孩子的朋友——他们的朋友圈全是晒娃，出来聚会也总是提前离场。但他们说起孩子的第一声'爸爸妈妈'时，眼里的光是真的。",
        "conditions": {"age": [29, 33], "has_spouse": True, "flags_none": ["has_children", "childfree", "divorced"]},
        "priority": 6,
        "repeatable": False,
        "choices": [
            {"text": "👶 要一个孩子", "flavor": "生命需要延续", "effects": {"happiness": 30, "money": -30000}, "flags_set": ["has_children"], "relationship_changes": {"spouse": 15}, "follow_up": None},
            {"text": "⏸️ 现在不是时候", "flavor": "等事业再稳定一点", "effects": {"happiness": -5}, "flags_set": ["played_safe"], "follow_up": None},
            {"text": "✖️ 我们决定不要孩子", "flavor": "两个人也很好", "effects": {"happiness": 10}, "flags_set": ["childfree"], "follow_up": None},
        ],
    },
    {
        "id": "career_bottleneck_33",
        "category": "career",
        "title": "中年的天花板",
        "flavor": "你已经在这个行业干了快十年。技术上越来越熟练，但激情在消退。年轻的新人像打了鸡血一样，你看着他们，想起了十年前的自己。你开始怀疑：这真的是我想要做一辈子的事吗？",
        "conditions": {"age": [32, 38], "has_job": True, "flags_none": ["started_business", "changed_career"]},
        "priority": 7,
        "repeatable": False,
        "choices": [
            {"text": "🚀 辞职创业", "flavor": "与其等死，不如博一把", "effects": {"money": -80000, "happiness": 10}, "flags_set": ["started_business", "took_big_risk"], "special": "startup", "follow_up": "startup_result_36"},
            {"text": "🔄 换个行业", "flavor": "新领域，重新开始", "effects": {"career": -20, "happiness": 5}, "flags_set": ["changed_career", "took_big_risk"], "special": "find_job", "follow_up": None},
            {"text": "😌 熬着吧", "flavor": "家里还有房贷呢", "effects": {"happiness": -15, "money": 10000}, "flags_set": ["played_safe"], "follow_up": None},
        ],
    },
    {
        "id": "startup_result_36",
        "category": "career",
        "title": "创业的答案",
        "flavor": "创业这几年，你把积蓄都投了进去。最惨的时候卡里只剩三位数。但现在，公司终于有了起色——或者没有。但无论如何，这段经历改变了你。",
        "conditions": {"age": [34, 39], "flags_all": ["started_business"]},
        "priority": 8,
        "repeatable": False,
        "choices": [
            {"text": "📈 继续做大", "flavor": "势头不错，加大投入", "effects": {"money": 100000, "career": 30, "happiness": 15}, "flags_set": ["took_big_risk"], "follow_up": None},
            {"text": "💰 见好就收", "flavor": "把公司卖了，落袋为安", "effects": {"money": 200000, "happiness": 20}, "flags_set": ["chose_money"], "follow_up": None},
        ],
    },
    {
        "id": "marriage_crisis_35",
        "category": "relationship",
        "title": "争吵之后",
        "flavor": "又是一场大吵。起因已经不重要了——可能是谁忘了关灯，也可能是这些年积攒的所有小事。房间里安静得可怕。你知道，有些话说出口就收不回来了。",
        "conditions": {"age": [32, 40], "has_spouse": True, "flags_none": ["divorced"]},
        "priority": 6,
        "repeatable": False,
        "choices": [
            {"text": "💬 坐下来好好谈谈", "flavor": "我们的问题需要面对", "effects": {"happiness": -10}, "flags_set": ["told_truth"], "relationship_changes": {"spouse": 10}, "follow_up": None},
            {"text": "😶 算了，我让一步", "flavor": "有些架不值得吵", "effects": {"happiness": -5, "health": -5}, "flags_set": ["played_safe"], "follow_up": None},
            {"text": "🚪 提出分居", "flavor": "我们需要冷静一下", "effects": {"happiness": -20, "money": -30000}, "flags_set": ["divorced", "took_big_risk"], "relationship_changes": {"spouse": -60}, "follow_up": None},
        ],
    },
    {
        "id": "parents_aging_38",
        "category": "family",
        "title": "父母老了",
        "flavor": "视频电话里，你注意到父亲的头发全白了。他说没事，就是最近血压有点高，已经吃药了。母亲在旁边插嘴：你爸又不按时吃药，说了多少次了。你突然意识到，他们不会永远在那里。",
        "conditions": {"age": [35, 42]},
        "priority": 6,
        "repeatable": False,
        "choices": [
            {"text": "🏠 接他们过来一起住", "flavor": "我来照顾你们", "effects": {"money": -20000, "happiness": 15}, "flags_set": ["reconciled_with_parents", "chose_love"], "follow_up": None},
            {"text": "💼 请专业的护工", "flavor": "专业的事交给专业的人", "effects": {"money": -30000}, "flags_set": ["chose_money"], "follow_up": None},
            {"text": "🏡 经常打电话多回去", "flavor": "尽量两头兼顾", "effects": {"money": -10000, "happiness": 5}, "flags_set": ["played_safe"], "follow_up": None},
        ],
    },
    {
        "id": "moral_choice_40",
        "category": "moral",
        "title": "良心与利益",
        "flavor": "你发现了一个漏洞——一个可以让你获得不少好处，但可能会伤害到一些人的漏洞。没有人会发现是你。但你心里清楚，这是错的。",
        "conditions": {"age": [36, 46]},
        "priority": 5,
        "repeatable": False,
        "choices": [
            {"text": "⚖️ 守住底线", "flavor": "有些东西比钱重要", "effects": {"happiness": 10, "career": 5}, "flags_set": ["told_truth"], "follow_up": None},
            {"text": "💰 做了再说", "flavor": "这世界本来就不公平", "effects": {"money": 80000, "happiness": -20}, "flags_set": ["told_lie", "chose_money"], "follow_up": None},
        ],
    },

    # ═══════ 50+岁：暮年回首 (3张) ═══════
    {
        "id": "how_to_age_50",
        "category": "life_key",
        "title": "如何老去",
        "flavor": "五十岁生日那天，你照镜子，看到了自己年轻时的轮廓——但眼角多了皱纹，鬓角染了霜。你想起二十岁时做的那些梦，有的实现了，有的没实现。剩下的路，怎么走？",
        "conditions": {"age": [50, 54]},
        "priority": 8,
        "repeatable": False,
        "choices": [
            {"text": "🏖️ 提前退休，享受生活", "flavor": "辛苦大半辈子了", "effects": {"happiness": 20, "health": 10}, "flags_set": ["played_safe"], "special": "early_retire", "follow_up": None},
            {"text": "🔥 继续打拼", "flavor": "我不服老", "effects": {"happiness": -10, "career": 10}, "flags_set": ["took_big_risk"], "special": "keep_working", "follow_up": None},
            {"text": "🎨 发展新兴趣", "flavor": "人生还有下半场", "effects": {"career": -5, "happiness": 25}, "flags_set": ["discovered_talent"], "follow_up": None},
        ],
    },
    {
        "id": "reconcile_with_kids_58",
        "category": "family",
        "title": "与子女对话",
        "flavor": "孩子长大了，有了自己的生活。你们之间的对话越来越短——吃的什么、天气冷了多穿衣服、工作忙不忙。你想说更多，但不知道从何说起。",
        "conditions": {"age": [55, 65], "flags_all": ["has_children"]},
        "priority": 6,
        "repeatable": False,
        "choices": [
            {"text": "📞 主动多说一些", "flavor": "有些话不说就来不及了", "effects": {"happiness": 20}, "flags_set": ["reconciled_with_parents", "chose_love"], "follow_up": None},
            {"text": "🤐 保持距离，各自安好", "flavor": "他们有自己的人生", "effects": {"happiness": -5}, "flags_set": ["played_safe"], "follow_up": None},
        ],
    },
    {
        "id": "legacy_65",
        "category": "life_key",
        "title": "留下什么",
        "flavor": "你开始想一个问题：你走了之后，这个世界会记得你什么？是银行账户里的数字？是你做过的那件被人记住的事？还是你爱过的那几个人？",
        "conditions": {"age": [60, 70]},
        "priority": 7,
        "repeatable": False,
        "choices": [
            {"text": "💰 把财富留给子女", "flavor": "让他们过得轻松一点", "effects": {"happiness": 15}, "flags_set": ["chose_money"], "follow_up": None},
            {"text": "📝 写下自己的人生故事", "flavor": "经历比钱更值得传承", "effects": {"happiness": 25}, "flags_set": ["chose_love", "told_truth"], "follow_up": None},
            {"text": "🏥 捐给需要帮助的人", "flavor": "让钱做点好事", "effects": {"money": -100000, "happiness": 30}, "flags_set": ["helped_stranger", "chose_love"], "follow_up": None},
        ],
    },
]

DAILY_EVENTS = [
    # ── social (25%) ──
    {"id": "daily_001", "category": "social", "flavor": "老同学群里有人提议周末聚会。上次见面还是两年前，有些人的名字你已经快对不上脸了。",
     "choices": [{"text": "去！叙叙旧", "effects": {"happiness": 10, "money": -500}}, {"text": "算了，在家休息", "effects": {"happiness": -5}}]},
    {"id": "daily_002", "category": "social", "flavor": "邻居在楼下碰到你，说他们家做了点特产，非要塞给你一袋。",
     "choices": [{"text": "收下，改天回礼", "effects": {"happiness": 8}}, {"text": "婉拒，不想欠人情", "effects": {"happiness": -3}}]},
    {"id": "daily_003", "category": "social", "flavor": "同事提议下班后一起去吃火锅。你正好饿了，但手头还有些工作没做完。",
     "choices": [{"text": "去！工作明天再说", "effects": {"happiness": 12, "money": -300}}, {"text": "加班把事做完", "effects": {"career": 5, "happiness": -5}}]},
    {"id": "daily_004", "category": "social", "flavor": "一个很久没联系的朋友在朋友圈发了条丧丧的状态。你犹豫要不要发个消息。",
     "choices": [{"text": "发消息问问", "effects": {"happiness": 5}, "flags_set": ["helped_friend"]}, {"text": "点个赞就好", "effects": {}}]},
    {"id": "daily_005", "category": "social", "flavor": "有人发来微信说'在吗'，然后就没下文了。你最怕这种消息了。",
     "choices": [{"text": "回复：在，怎么了？", "effects": {"happiness": -2}}, {"text": "装作没看见", "effects": {"happiness": 3}}]},
    {"id": "daily_006", "category": "social", "flavor": "朋友圈刷到大学同学的婚礼照片。全班好像就你还没结婚了。",
     "choices": [{"text": "点个赞，随个份子", "effects": {"happiness": -3, "money": -1000}}, {"text": "划走不看", "effects": {"happiness": -8}}]},
    {"id": "daily_007", "category": "social", "flavor": "公司团建活动——去郊外拓展训练。上次有人摔了一跤，但这次听说伙食不错。",
     "choices": [{"text": "积极参与", "effects": {"happiness": 10, "health": 5}}, {"text": "请假不去", "effects": {"happiness": 3, "career": -3}}]},

    # ── work (20%) ──
    {"id": "daily_008", "category": "work", "flavor": "老板在群里发了一个'有空聊一下'，然后就不说话了。你开始回想自己最近有没有做错什么。",
     "choices": [{"text": "主动去找老板", "effects": {"career": 5, "happiness": -5}}, {"text": "等老板来找你", "effects": {"happiness": -8, "health": -3}}]},
    {"id": "daily_009", "category": "work", "flavor": "下午三点了，你盯着屏幕，一行代码都没写出来。大脑像死机了一样。",
     "choices": [{"text": "去楼下走一圈", "effects": {"health": 3, "happiness": 3}}, {"text": "再喝一杯咖啡硬撑", "effects": {"health": -3, "happiness": -5}}]},
    {"id": "daily_010", "category": "work", "flavor": "一个项目出了岔子，虽然不是你的责任，但你是最熟悉这块的人。同事们的目光看向你。",
     "choices": [{"text": "主动接手解决", "effects": {"career": 8, "happiness": -5}}, {"text": "指出是谁的责任", "effects": {"career": -3, "happiness": -3}}]},
    {"id": "daily_011", "category": "work", "flavor": "收到了一个猎头的消息，说有个不错的机会想聊聊。你看了下，确实比现在的工资高。",
     "choices": [{"text": "聊聊又不会死", "effects": {"happiness": 5}, "flags_set": ["job_hopped"]}, {"text": "删掉消息", "effects": {"happiness": -3}, "flags_set": ["loyal_employee"]}]},
    {"id": "daily_012", "category": "work", "flavor": "年度绩效评估到了。你觉得自己干得不错，但不知道老板怎么想。",
     "choices": [{"text": "准备一份详细的总结", "effects": {"career": 5}}, {"text": "佛系面对，顺其自然", "effects": {"health": 3}}]},
    {"id": "daily_013", "category": "work", "flavor": "一个新同事在会议上提出了一个大胆的方案。你觉得有问题，但不好直接反驳。",
     "choices": [{"text": "私下找ta聊", "effects": {"happiness": 5, "career": 3}}, {"text": "会上直接说", "effects": {"career": 8, "happiness": -5}}]},

    # ── family (20%) ──
    {"id": "daily_014", "category": "family", "flavor": "妈妈打电话来说家里的冰箱坏了。她说不用管，已经找人修了。但你知道那台冰箱用了十几年了。",
     "choices": [{"text": "寄钱回去买新的", "effects": {"money": -5000, "happiness": 10}}, {"text": "叮嘱她注意安全", "effects": {"happiness": -5}}]},
    {"id": "daily_015", "category": "family", "flavor": "周末回家吃饭，爸爸做了你小时候最爱吃的红烧肉。味道和记忆里一模一样。",
     "choices": [{"text": "多吃一碗饭", "effects": {"health": 5, "happiness": 15}}, {"text": "说自己在减肥", "effects": {"happiness": -5}}]},
    {"id": "daily_016", "category": "family", "flavor": "家庭群里又在转发养生文章，说吃某种食物会致癌。你很想发一篇辟谣文章。",
     "choices": [{"text": "发！不能让他们被骗", "effects": {"happiness": 3, "health": 2}}, {"text": "算了，说了也不听", "effects": {"happiness": -3}}]},
    {"id": "daily_017", "category": "family", "flavor": "过年回家抢到了火车票。座位是靠过道的，但至少能回去了。",
     "choices": [{"text": "多带点年货回去", "effects": {"money": -3000, "happiness": 15}}, {"text": "轻装简行", "effects": {"happiness": 5}}]},
    {"id": "daily_018", "category": "family", "flavor": "父亲发来一篇文章《三十岁前必须明白的十件事》。你点开看了一下，是标题党。",
     "choices": [{"text": "认真回复：知道了爸", "effects": {"happiness": 8}}, {"text": "不回，假装没看到", "effects": {"happiness": -5}}]},
    {"id": "daily_019", "category": "family", "flavor": "弟妹/表兄妹找你借钱，说是要交房租，发了工资就还。数目不大。",
     "choices": [{"text": "借了", "effects": {"money": -2000, "happiness": 5}}, {"text": "说自己也紧张", "effects": {"happiness": -8}}]},

    # ── health (15%) ──
    {"id": "daily_020", "category": "health", "flavor": "早上起来脖子落枕了，转头的时候疼得龇牙咧嘴。",
     "choices": [{"text": "请假在家休息一天", "effects": {"health": 8, "happiness": 5}}, {"text": "贴个膏药去上班", "effects": {"health": 2, "career": 3}}]},
    {"id": "daily_021", "category": "health", "flavor": "体检查出了一项指标偏高。医生说问题不大，建议多运动、少熬夜。",
     "choices": [{"text": "开始规律运动", "effects": {"health": 10, "happiness": -5, "money": -2000}}, {"text": "该吃吃该喝喝", "effects": {"health": -8, "happiness": 3}}]},
    {"id": "daily_022", "category": "health", "flavor": "连着加了一周班，你感觉身体快撑不住了。咖啡已经没什么用了。",
     "choices": [{"text": "周末好好补一觉", "effects": {"health": 10, "happiness": 5}}, {"text": "继续靠红牛续命", "effects": {"health": -10, "happiness": -5}}]},
    {"id": "daily_023", "category": "health", "flavor": "路过一家新开的健身房，销售小哥热情地递了一张传单，说首月免费体验。",
     "choices": [{"text": "试试看，不行再退", "effects": {"health": 5, "happiness": 3}}, {"text": "微笑拒绝，快步离开", "effects": {}}]},
    {"id": "daily_024", "category": "health", "flavor": "牙开始隐隐作痛。你知道该去看牙医了，但上次的钻头声还在脑子里回响。",
     "choices": [{"text": "咬牙去看", "effects": {"health": 8, "money": -1500, "happiness": -10}}, {"text": "吃点止痛药再说", "effects": {"health": -5}}]},

    # ── happy (10%) ──
    {"id": "daily_025", "category": "happy", "flavor": "下班路上遇到了卖糖葫芦的小贩。红色的山楂在夕阳下泛着光，你突然想起小学门口那个老爷爷。",
     "choices": [{"text": "买一串！找回童年", "effects": {"money": -10, "happiness": 8}}, {"text": "微笑路过", "effects": {}}]},
    {"id": "daily_026", "category": "happy", "flavor": "快递到了！拆开的那一刻比下单的时候还开心。",
     "choices": [{"text": "立刻拆开试用", "effects": {"happiness": 5}}, {"text": "放一边先吃饭", "effects": {}}]},
    {"id": "daily_027", "category": "happy", "flavor": "在地铁上给一个老奶奶让了座，她笑着说谢谢你小伙子/姑娘。",
     "choices": [{"text": "微笑说不客气", "effects": {"happiness": 8}}, {"text": "戴上耳机继续听歌", "effects": {"happiness": 3}}]},

    # ── sad (5%) ──
    {"id": "daily_028", "category": "sad", "flavor": "手机屏幕碎了。才买了三个月。摔下去的那一刻你的心也碎了。",
     "choices": [{"text": "去修", "effects": {"money": -1500, "happiness": -5}}, {"text": "就这样用，反正还能亮", "effects": {"happiness": -8}}]},
    {"id": "daily_029", "category": "sad", "flavor": "下雨天，没带伞。你站在便利店门口等了二十分钟，雨越下越大。",
     "choices": [{"text": "冲回去！反正会干", "effects": {"health": -3, "happiness": 3}}, {"text": "买把伞再走", "effects": {"money": -30, "happiness": -3}}]},

    # ── random (5%) — 小概率事件 ──
    {"id": "daily_030", "category": "random", "flavor": "你在便利店随手买了一张刮刮乐。刮开的那一刻，你揉了揉眼睛——上面写着'一等奖 ¥10,000'。",
     "conditions": {"age": [18, 80]},
     "choices": [{"text": "大喊一声！", "effects": {"money": 10000, "happiness": 25}, "flags_set": ["won_lottery"]},
                 {"text": "淡定地兑奖", "effects": {"money": 10000, "happiness": 10}, "flags_set": ["won_lottery"]}]},
    {"id": "daily_031", "category": "random", "flavor": "走在街上，一个自称星探的人递给你名片，说你的形象很适合拍一个广告。你仔细看了名片——好像是真的。",
     "conditions": {"age": [18, 35]},
     "choices": [{"text": "去试试看", "effects": {"money": 20000, "happiness": 15, "career": 5}, "flags_set": ["discovered_talent", "took_big_risk"]},
                 {"text": "笑着拒绝，可能是骗子", "effects": {"happiness": -3}, "flags_set": ["played_safe"]}]},
    {"id": "daily_032", "category": "random", "flavor": "一个远房亲戚去世了，律师通知你——他在遗嘱里留了一笔遗产给你。你甚至不记得上次见他是什么时候。",
     "conditions": {"age": [30, 70]},
     "choices": [{"text": "惊讶地接受", "effects": {"money": 50000, "happiness": 5}, "flags_set": ["inherited_money"]},
                 {"text": "捐掉一部分做慈善", "effects": {"money": 30000, "happiness": 20}, "flags_set": ["inherited_money", "helped_stranger"]}]},

    # ── 通用无条件备选（5条）──
    {"id": "daily_033", "category": "social", "flavor": "路边有只流浪猫冲你叫了一声。你对它喵了回去。它又叫了一声。你们就这样聊了三分钟。",
     "choices": [{"text": "给它买根火腿肠", "effects": {"money": -5, "happiness": 8}}, {"text": "撸一把就走", "effects": {"happiness": 5}}]},
    {"id": "daily_034", "category": "happy", "flavor": "今天天气特别好。阳光暖洋洋的，你在窗边坐了一会儿，什么都不想。",
     "choices": [{"text": "偷得浮生半日闲", "effects": {"happiness": 10, "health": 3}}, {"text": "还是找点事做吧", "effects": {"career": 3}}]},
    {"id": "daily_035", "category": "sad", "flavor": "翻到了十年前的照片。那时候你好年轻，眼神里有种现在没有的东西。",
     "choices": [{"text": "怀旧一会儿", "effects": {"happiness": -3, "health": 2}}, {"text": "合上相册，继续生活", "effects": {"happiness": 3}}]},
    {"id": "daily_036", "category": "work", "flavor": "今天效率特别高，一口气把拖了很久的事全做完了。",
     "choices": [{"text": "奖励自己一杯奶茶", "effects": {"money": -30, "happiness": 10}}, {"text": "继续趁热打铁", "effects": {"career": 5}}]},
    {"id": "daily_037", "category": "social", "flavor": "排队的时候前面的人帮你挡了一下门。你微笑道谢。他点了点头。一个小小的善意瞬间。",
     "choices": [{"text": "心情莫名好起来", "effects": {"happiness": 5}}, {"text": "心想今天运气不错", "effects": {"happiness": 3}}]},
]

# ============ 通用函数 ============

def clamp(value, min_val=0, max_val=100):
    return max(min_val, min(max_val, value))

def format_money(amount):
    if amount >= 10000:
        return f"{amount/10000:.1f}万"
    return str(amount)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
"熬过去"人生模拟器 - 文本原型
核心机制：很难死掉，绝境会自动触发转机
"""

import random
import time
import json
import os

# ============ 基础配置 ============

BACKGROUNDS = {
    "1": ("小镇青年", {"money": 5000, "happiness": 70, "career": 20}),
    "2": ("城市中产", {"money": 50000, "happiness": 60, "career": 50}),
    "3": ("富二代", {"money": 200000, "happiness": 80, "career": 30}),
    "4": ("农村出身", {"money": 2000, "happiness": 60, "career": 10}),
}

TALENTS = {
    "1": ("学习天赋", "考试/学习相关事件成功率+30%"),
    "2": ("社交达人", "人际关系事件结果+20%"),
    "3": ("财运亨通", "金钱相关事件结果+30%"),
    "4": ("健康体质", "健康下降-50%"),
}

PERSONALITIES = {
    "1": ("稳健型", "风险事件发生率-20%"),
    "2": ("冒险型", "高风险高回报事件+30%"),
    "3": ("佛系型", "快乐值衰减-30%"),
}

# ============ 事件库 ============

# 普通事件（每年随机触发）
NORMAL_EVENTS = [
    {
        "title": "找工作",
        "desc": "你发现一个工作机会",
        "choices": [
            ("接受", {"money": 5000, "happiness": 5, "career": 10}),
            ("拒绝", {"happiness": -5}),
        ]
    },
    {
        "title": "投资理财",
        "desc": "有人推荐你一个投资项目",
        "choices": [
            ("投入试试", {"money": -5000, "happiness": 10}),  # 随机结果
            ("不投", {}),
        ]
    },
    {
        "title": "朋友聚会",
        "desc": "老朋友约你聚会",
        "choices": [
            ("去参加", {"money": -500, "happiness": 15}),
            ("不去", {"happiness": -5}),
        ]
    },
    {
        "title": "身体检查",
        "desc": "每年体检结果出来了",
        "choices": [
            ("去体检", {"money": -500}, "check_health"),  # 特殊处理
            ("不去了", {}),
        ]
    },
    {
        "title": "学习进修",
        "desc": "有个培训课程",
        "choices": [
            ("报名学习", {"money": -10000, "career": 20, "happiness": 5}),
            ("不学", {"happiness": -5}),
        ]
    },
    {
        "title": "相亲对象",
        "desc": "有人给你介绍对象",
        "choices": [
            ("去见面", {"money": -500, "happiness": 10}, "dating"),
            ("不见", {}),
        ]
    },
]

# 危机事件（低健康/低金钱时触发）
CRISIS_EVENTS = [
    {
        "title": "突发重病",
        "desc": "你得了场大病，需要治疗",
        "choices": [
            ("积极治疗", {"money": -20000, "health": 30}),
            ("硬扛", {"health": -20, "money": -2000}),
        ]
    },
    {
        "title": "失业",
        "desc": "公司倒闭了",
        "choices": [
            ("找工作", {"money": -3000, "happiness": -10, "career": 5}),
            ("创业", {"money": -50000, "happiness": 10}, "risky_entrepreneur"),
        ]
    },
    {
        "title": "财务危机",
        "desc": "入不敷出，欠了不少钱",
        "choices": [
            ("努力还债", {"money": -5000, "happiness": -15}),
            ("借钱度日", {"money": -10000, "happiness": -5}),
        ]
    },
]

# 转折点事件（绝境时触发，转机）
TURNING_POINT_EVENTS = [
    {
        "title": "贵人相助",
        "desc": "在你最困难的时候，有人伸出了援手",
        "result": {"money": 30000, "happiness": 20},
        "type": "平淡回归",  # 回归平淡
    },
    {
        "title": "奇迹康复",
        "desc": "医生说这是医学奇迹",
        "result": {"health": 60},
        "type": "平淡回归",
    },
    {
        "title": "继承遗产",
        "desc": "远方亲戚去世了，留给你一笔遗产",
        "result": {"money": 50000, "happiness": 15},
        "type": "小改善",
    },
    {
        "title": "中彩票",
        "desc": "你随手买的彩票居然中了！",
        "result": {"money": 100000, "happiness": 30},
        "type": "中改善",
    },
    {
        "title": "遇到真爱",
        "desc": "在最孤单的时候，你遇到了对的人",
        "result": {"happiness": 40, "money": 10000},
        "type": "平淡回归",
    },
    {
        "title": "想通了",
        "desc": "经历了这么多，你突然想通了一些事",
        "result": {"happiness": 30, "health": 10},
        "type": "平淡回归",
    },
]

# ============ 核心类 ============

class Player:
    def __init__(self, name, background, talent, personality, auto=False):
        self.name = name
        self.background = background
        self.talent = talent
        self.personality = personality
        
        # 基础数值
        self.age = 18
        self.health = 80
        self.money = BACKGROUNDS[background][1]["money"]
        self.happiness = BACKGROUNDS[background][1]["happiness"]
        self.career = BACKGROUNDS[background][1]["career"]
        
        # 记录
        self.events_log = []
        self.achievements = []
        self.dead = False
        self.death_reason = ""
        self.auto = auto
    
    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "health": self.health,
            "money": self.money,
            "happiness": self.happiness,
            "career": self.career,
            "background": self.background,
        }

    def show_status(self):
        print(f"\n{'='*50}")
        print(f"📅 年龄: {self.age}岁 | 💰 金钱: {self.money:,} | ❤️ 健康: {self.health} | 😊 快乐: {self.happiness} | 💼 事业: {self.career}")
        print(f"{'='*50}")

    def apply_effect(self, effects):
        """应用事件效果"""
        for key, value in effects.items():
            if key == "health":
                self.health = max(0, min(100, self.health + value))
            elif key == "money":
                self.money += value
            elif key == "happiness":
                self.happiness = max(0, min(100, self.happiness + value))
            elif key == "career":
                self.career = max(0, min(100, self.career + value))
    
    def check_death(self):
        """检查是否死亡（概率很低）"""
        if self.health <= 0:
            # 10% 概率直接死亡，90% 概率触发转机
            if random.random() < 0.1:
                self.dead = True
                self.death_reason = "因病去世"
                return True
            else:
                # 触发转机
                self.trigger_turning_point("健康")
                return False
        return False
    
    def check_turning_point(self):
        """检测是否触发转折点"""
        # 30% 概率在绝境时触发转机
        if not random.random() < 0.3:
            return None
        
        # 检测绝境
        crisis_type = None
        if self.health < 20:
            crisis_type = "健康"
        elif self.money < -50000:
            crisis_type = "金钱"
        elif self.happiness < 10:
            crisis_type = "快乐"
        
        if crisis_type:
            return self.trigger_turning_point(crisis_type)
        return None
    
    def trigger_turning_point(self, crisis_type):
        """触发转折点"""
        event = random.choice(TURNING_POINT_EVENTS)
        
        print(f"\n🌟 【转折点】{event['title']} 🌟")
        print(f"   {event['desc']}")
        print(f"   → {event['type']}")
        
        self.apply_effect(event["result"])
        
        # 记录
        self.events_log.append({
            "age": self.age,
            "title": f"[转折] {event['title']}",
            "type": event["type"]
        })
        
        if "成就" not in self.achievements:
            self.achievements.append("触发转折点")
        
        return event


# ============ 游戏引擎 ============

def create_player(auto=False):
    """创建角色"""
    print("\n" + "="*50)
    print("【熬过去】人生模拟器")
    print("="*50)
    print("\n核心机制：这是一个很难死掉的人生模拟器")
    print("每次绝境，大概率会迎来转机...")
    
    if auto:
        # 自动模式，用默认选项
        name = "测试玩家"
        bg = "1"
        talent = "1"
        personality = "1"
        print(f"\n[自动模式] 名字: {name}")
    else:
        name = input("\n你的名字: ").strip() or "玩家"
    
        print("\n【选择出身】")
        for k, v in BACKGROUNDS.items():
            print(f"  {k}. {v[0]} (金钱:{v[1]['money']}, 快乐:{v[1]['happiness']}, 事业:{v[1]['career']})")
        bg = input("选择 (1-4): ").strip() or "1"
        
        print("\n【选择天赋】")
        for k, v in TALENTS.items():
            print(f"  {k}. {v[0]} - {v[1]}")
        talent = input("选择 (1-4): ").strip() or "1"
        
        print("\n【选择性格】")
        for k, v in PERSONALITIES.items():
            print(f"  {k}. {v[0]} - {v[1]}")
        personality = input("选择 (1-3): ").strip() or "1"
    
    return Player(name, bg, talent, personality, auto=auto)


def process_event(player):
    """处理随机事件"""
    # 优先检测转折点
    turning = player.check_turning_point()
    if turning:
        return
    
    # 随机选择1-2个普通事件
    num_events = random.randint(1, 2)
    for _ in range(num_events):
        event = random.choice(NORMAL_EVENTS)
        
        print(f"\n【事件】{event['title']}")
        print(f"   {event['desc']}")
        
        for i, choice in enumerate(event["choices"]):
            print(f"   {i+1}. {choice[0]}")
        
        # 自动模式默认选0
        if player.auto:
            idx = 0
            print(f"\n[自动选择]")
        else:
            # 特殊事件处理
            if len(event["choices"][0]) > 2:
                choice_idx = input("\n选择: ").strip()
                if choice_idx == "1":
                    special = event["choices"][0][2]
                    if special == "check_health":
                        health_change = random.randint(-10, 20)
                        player.apply_effect({"health": health_change})
                        print(f"   → 体检结果: 健康{'+' if health_change > 0 else ''}{health_change}")
                        player.events_log.append({"age": player.age, "title": event["title"]})
                        continue
            
            # 普通选择
            try:
                idx = int(input("\n选择: ").strip()) - 1
                if idx < 0 or idx >= len(event["choices"]):
                    idx = 0
            except:
                idx = 0
        
        # 特殊处理：投资可能有不同结果（先不应用choice中的效果）
        if "投资" in event["title"]:
            if random.random() < 0.5:  # 50% 赚钱
                effects = {"money": 10000, "happiness": 10}
                print("   → 投资成功！赚了10000")
            else:
                effects = {"money": -5000, "happiness": -10}
                print("   → 投资失败！亏了5000")
        else:
            choice = event["choices"][idx]
            effects = choice[1] if len(choice) > 1 else {}
        
        player.apply_effect(effects)
        
        # 记录
        player.events_log.append({
            "age": player.age,
            "title": event["title"],
            "choice": choice[0]
        })


def year_pass(player):
    """度过一年"""
    player.age += 1
    
    # 每年自然变化
    player.health -= random.randint(2, 8)  # 健康自然衰减
    player.happiness -= random.randint(2, 8)  # 快乐自然衰减
    player.money += player.career * 100  # 工资
    player.money -= 5000  # 基础开支
    
    # 检查死亡
    if player.check_death():
        return
    
    # 处理事件
    process_event(player)


def show_life_summary(player):
    """显示人生总结"""
    print("\n" + "="*50)
    print("📖 人生总结")
    print("="*50)
    print(f"\n姓名: {player.name}")
    print(f"享年: {player.age}岁")
    print(f"最终存款: {player.money:,}")
    print(f"最终快乐: {player.happiness}")
    
    if player.dead:
        print(f"\n💀 死因: {player.death_reason}")
    else:
        print("\n🌟 你安详地度过了一生")
    
    print(f"\n📝 人生事件数: {len(player.events_log)}")
    
    # 显示部分重要事件
    turning_events = [e for e in player.events_log if "[转折]" in e.get("title", "")]
    if turning_events:
        print(f"\n【转折点事件】: {len(turning_events)}个")
        for e in turning_events[:5]:
            print(f"   {e['age']}岁: {e['title']}")


def play(auto=False, years=10):
    """主游戏循环
    auto: 自动模式，无需输入，直接运行指定年数
    years: 自动模式运行年数
    """
    player = create_player(auto=auto)
    
    if auto:
        # 非交互式自动运行
        for i in range(years):
            if player.dead or player.age >= 100:
                break
            year_pass(player)
    else:
        # 交互式
        while not player.dead and player.age < 100:
            player.show_status()
            print("\n[按回车继续下一年，q退出]")
            cmd = input("> ").strip().lower()
            if cmd == 'q':
                break
            
            year_pass(player)
            
            # 检查死亡
            if player.dead:
                break
    
    show_life_summary(player)
    
    # 保存存档
    save_data = player.to_dict()
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savegame.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    print("\n💾 游戏已自动保存到 savegame.json")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="自动模式")
    parser.add_argument("--years", type=int, default=10, help="自动模式运行年数")
    args = parser.parse_args()
    
    play(auto=args.auto, years=args.years)

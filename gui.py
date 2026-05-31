#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"熬过去"人生模拟器 - GUI版本
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
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
            ("投入试试", {"money": -5000, "happiness": 10}),
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
            ("去体检", {"money": -500}),
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
            ("去见面", {"money": -500, "happiness": 10}),
            ("不见", {}),
        ]
    },
]

# 特殊事件（随机触发，全局影响）
SPECIAL_EVENTS = [
    {
        "title": "金融危机",
        "desc": "全球金融危机爆发，你的投资大幅缩水！",
        "type": "negative",
        "effect": {"money": -50000, "happiness": -20},
    },
    {
        "title": "房价暴跌",
        "desc": "房地产泡沫破裂，房价跌入谷底。",
        "type": "negative",
        "effect": {"money": -30000, "happiness": -10},
    },
    {
        "title": "疫情爆发",
        "desc": "一场突如其来的疫情影响了全世界。",
        "type": "negative",
        "effect": {"health": -20, "money": -10000},
    },
    {
        "title": "科技革命",
        "desc": "你所在的行业迎来技术革新！事业迎来爆发期。",
        "type": "positive",
        "effect": {"career": 30, "money": 20000, "happiness": 15},
    },
    {
        "title": "房价飙升",
        "desc": "房地产价格上涨，你之前买的房子增值了！",
        "type": "positive",
        "effect": {"money": 50000, "happiness": 20},
    },
    {
        "title": "行业风口",
        "desc": "你所在的行业成为下一个风口！",
        "type": "positive",
        "effect": {"career": 25, "money": 30000},
    },
    {
        "title": "意外遗产",
        "desc": "远方的亲戚去世了，给你留下了一笔遗产。",
        "type": "positive",
        "effect": {"money": 80000, "happiness": 25},
    },
    {
        "title": "重病康复",
        "desc": "一场大病后，你奇迹般地康复了。",
        "type": "positive",
        "effect": {"health": 40, "happiness": 20},
    },
]

# 成就定义
ACHIEVEMENTS = [
    {"id": "millionaire", "name": "百万富翁", "desc": "拥有100万现金", "icon": "💰"},
    {"id": "centenarian", "name": "百岁老人", "desc": "活到100岁", "icon": "🎂"},
    {"id": "rich_and_happy", "name": "人生赢家", "desc": "金钱、快乐、事业都达到80+", "icon": "🏆"},
    {"id": "turning_point_5", "name": "绝境逢生", "desc": "触发5次转折点", "icon": "🌟"},
    {"id": "married", "name": "结婚", "desc": "找到伴侣", "icon": "💑"},
    {"id": "three_children", "name": "儿女成群", "desc": "有3个孩子", "icon": "👨‍👩‍👧‍👦"},
    {"id": "early_death", "name": "英年早逝", "desc": "30岁前去世", "icon": "💀"},
    {"id": "lottery_win", "name": "彩票中奖", "desc": "中一次彩票", "icon": "🎰"},
]

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
            ("创业", {"money": -50000, "happiness": 10}),
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

TURNING_POINT_EVENTS = [
    {"title": "贵人相助", "desc": "在你最困难的时候，有人伸出了援手", "result": {"money": 30000, "happiness": 20}, "type": "平淡回归"},
    {"title": "奇迹康复", "desc": "医生说这是医学奇迹", "result": {"health": 60}, "type": "平淡回归"},
    {"title": "继承遗产", "desc": "远方亲戚去世了，留给你一笔遗产", "result": {"money": 50000, "happiness": 15}, "type": "小改善"},
    {"title": "中彩票", "desc": "你随手买的彩票居然中了！", "result": {"money": 100000, "happiness": 30}, "type": "中改善"},
    {"title": "遇到真爱", "desc": "在最孤单的时候，你遇到了对的人", "result": {"happiness": 40, "money": 10000}, "type": "平淡回归"},
    {"title": "想通了", "desc": "经历了这么多，你突然想通了一些事", "result": {"happiness": 30, "health": 10}, "type": "平淡回归"},
]


class Player:
    def __init__(self, name, background, talent, personality):
        self.name = name
        self.background = background
        self.talent = talent
        self.personality = personality
        
        self.age = 18
        self.health = 80
        self.money = BACKGROUNDS[background][1]["money"]
        self.happiness = BACKGROUNDS[background][1]["happiness"]
        self.career = BACKGROUNDS[background][1]["career"]
        
        # 关系系统
        self.spouse = None  # 配偶名字
        self.children = []  # 子女列表 [{"name": "xxx", "age": 0}]
        
        # 成就系统
        self.achievements = []
        
        # 人生记录
        self.diary = []  # [{"age": 18, "text": "xxx"}]
        
        self.events_log = []
        self.dead = False
        self.death_reason = ""
        self.turning_count = 0  # 修复：在__init__中初始化转折点计数
    
    def apply_effect(self, effects):
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
        if self.health <= 0:
            if random.random() < 0.1:
                self.dead = True
                self.death_reason = "因病去世"
                return True
            else:
                return "turning"
        return False
    
    def check_turning_point(self):
        if not random.random() < 0.3:
            return None
        
        crisis_type = None
        if self.health < 20:
            crisis_type = "健康"
        elif self.money < -50000:
            crisis_type = "金钱"
        elif self.happiness < 10:
            crisis_type = "快乐"
        
        if crisis_type:
            return self.trigger_turning_point()
        return None
    
    def trigger_turning_point(self):
        event = random.choice(TURNING_POINT_EVENTS)
        self.apply_effect(event["result"])
        self.events_log.append({"age": self.age, "title": f"[转折] {event['title']}", "type": event["type"]})
        
        # 记录转折点次数
        self.turning_count += 1
        
        return event


class LifeSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("熬过去 - 人生模拟器")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a2e")
        
        self.player = None
        self.current_event = None
        
        self.setup_styles()
        self.show_start_screen()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Title.TLabel", font=("微软雅黑", 24, "bold"), foreground="#fff", background="#1a1a2e")
        style.configure("Normal.TLabel", font=("微软雅黑", 12), foreground="#ccc", background="#1a1a2e")
        style.configure("Stat.TLabel", font=("微软雅黑", 14), foreground="#fff", background="#1a1a2e")
        
        # 按钮样式 - 带颜色和 hover 效果
        style.configure("Game.TButton", 
                        font=("微软雅黑", 12, "bold"), 
                        padding=10,
                        background="#4a90d9",
                        foreground="#fff",
                        borderwidth=1)
        style.map("Game.TButton",
                  background=[("active", "#6ba3e0"), ("pressed", "#3a7bc8")],
                  foreground=[("active", "#fff")])
        
        style.configure("Choice.TButton", 
                        font=("微软雅黑", 11), 
                        padding=8,
                        background="#3a3a5c",
                        foreground="#fff",
                        borderwidth=1)
        style.map("Choice.TButton",
                  background=[("active", "#5a5a8c"), ("pressed", "#2a2a4c")],
                  foreground=[("active", "#fff")])
    
    def show_start_screen(self):
        self.clear_screen()
        
        # 标题
        title = ttk.Label(self.root, text="熬过去", style="Title.TLabel")
        title.pack(pady=40)
        
        subtitle = ttk.Label(self.root, text="人生模拟器", style="Normal.TLabel")
        subtitle.pack()
        
        desc = ttk.Label(self.root, text="核心机制：这是一个很难死掉的人生模拟器\n每次绝境，大概率会迎来转机...", style="Normal.TLabel", justify="center")
        desc.pack(pady=20)
        
        # 开始按钮 - 用 tk.Button 更容易控制样式
        btn = tk.Button(self.root, text="开始新人生", font=("微软雅黑", 14, "bold"),
                       bg="#4a90d9", fg="#fff", activebackground="#6ba3e0", activeforeground="#fff",
                       relief=tk.RAISED, borderwidth=3, padx=20, pady=10,
                       command=self.show_create_screen)
        btn.pack(pady=30)
        
        # 读取存档（使用绝对路径）
        try:
            save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savegame.json")
            with open(save_path, "r", encoding="utf-8") as f:
                save_data = json.load(f)
            btn_load = tk.Button(self.root, text="继续上局", font=("微软雅黑", 12),
                                bg="#3a3a5c", fg="#fff", activebackground="#5a5a8c", activeforeground="#fff",
                                relief=tk.RAISED, borderwidth=3, padx=20, pady=8,
                                command=lambda: self.load_game(save_data))
            btn_load.pack(pady=10)
        except:
            pass
    
    def show_create_screen(self):
        self.clear_screen()
        
        ttk.Label(self.root, text="创建角色", style="Title.TLabel").pack(pady=20)
        
        # 名字
        ttk.Label(self.root, text="名字:", style="Normal.TLabel").pack()
        self.name_entry = tk.Entry(self.root, font=("微软雅黑", 12), width=20, bg="#2a2a4c", fg="#fff", insertbackground="#fff")
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, "玩家")
        
        # 出身
        ttk.Label(self.root, text="\n选择出身:", style="Normal.TLabel").pack()
        self.bg_var = tk.StringVar(value="1")
        for k, v in BACKGROUNDS.items():
            rb = tk.Radiobutton(self.root, text=f"{v[0]} (💰:{v[1]['money']} 😊:{v[1]['happiness']} 💼:{v[1]['career']})", 
                                variable=self.bg_var, value=k,
                                bg="#1a1a2e", fg="#fff", selectcolor="#4a90d9", activebackground="#1a1a2e", activeforeground="#fff",
                                font=("微软雅黑", 11))
            rb.pack(pady=2)
        
        # 天赋
        ttk.Label(self.root, text="\n选择天赋:", style="Normal.TLabel").pack()
        self.talent_var = tk.StringVar(value="1")
        for k, v in TALENTS.items():
            rb = tk.Radiobutton(self.root, text=f"{v[0]} - {v[1]}", 
                                variable=self.talent_var, value=k,
                                bg="#1a1a2e", fg="#fff", selectcolor="#27ae60", activebackground="#1a1a2e", activeforeground="#fff",
                                font=("微软雅黑", 11))
            rb.pack(pady=2)
        
        # 性格
        ttk.Label(self.root, text="\n选择性格:", style="Normal.TLabel").pack()
        self.pers_var = tk.StringVar(value="1")
        for k, v in PERSONALITIES.items():
            rb = tk.Radiobutton(self.root, text=f"{v[0]} - {v[1]}", 
                                variable=self.pers_var, value=k,
                                bg="#1a1a2e", fg="#fff", selectcolor="#9b59b6", activebackground="#1a1a2e", activeforeground="#fff",
                                font=("微软雅黑", 11))
            rb.pack(pady=2)
        
        # 按钮
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="开始游戏", font=("微软雅黑", 12, "bold"),
                 bg="#27ae60", fg="#fff", activebackground="#2ecc71", activeforeground="#fff",
                 relief=tk.RAISED, borderwidth=3, padx=20, pady=8,
                 command=self.start_game).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="返回", font=("微软雅黑", 12),
                 bg="#3a3a5c", fg="#fff", activebackground="#5a5a8c", activeforeground="#fff",
                 relief=tk.RAISED, borderwidth=3, padx=20, pady=8,
                 command=self.show_start_screen).pack(side=tk.LEFT, padx=10)
    
    def start_game(self):
        name = self.name_entry.get().strip() or "玩家"
        self.player = Player(name, self.bg_var.get(), self.talent_var.get(), self.pers_var.get())
        self.show_game_screen()
    
    def load_game(self, data):
        self.player = Player(data.get("name", "玩家"), data.get("background", "1"), "1", "1")
        self.player.age = data.get("age", 18)
        self.player.health = data.get("health", 80)
        self.player.money = data.get("money", 5000)
        self.player.happiness = data.get("happiness", 70)
        self.player.career = data.get("career", 20)
        self.player.spouse = data.get("spouse", None)
        self.player.children = data.get("children", [])
        self.player.achievements = data.get("achievements", [])
        self.player.diary = data.get("diary", [])
        self.player.turning_count = data.get("turning_count", 0)  # 修复：加载转折点计数
        self.show_game_screen()
    
    def show_game_screen(self):
        self.clear_screen()
        
        # 状态栏
        status_frame = ttk.Frame(self.root, style="Stat.TFrame")
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.age_label = ttk.Label(status_frame, text=f"年龄: {self.player.age}岁", style="Stat.TLabel")
        self.age_label.pack(side=tk.LEFT, padx=20)
        
        self.money_label = ttk.Label(status_frame, text=f"💰 金钱: {self.player.money:,}", style="Stat.TLabel")
        self.money_label.pack(side=tk.LEFT, padx=20)
        
        self.health_label = ttk.Label(status_frame, text=f"❤️ 健康: {self.player.health}", style="Stat.TLabel")
        self.health_label.pack(side=tk.LEFT, padx=20)
        
        self.happiness_label = ttk.Label(status_frame, text=f"😊 快乐: {self.player.happiness}", style="Stat.TLabel")
        self.happiness_label.pack(side=tk.LEFT, padx=20)
        
        self.career_label = ttk.Label(status_frame, text=f"💼 事业: {self.player.career}", style="Stat.TLabel")
        self.career_label.pack(side=tk.LEFT, padx=20)
        
        # 关系状态
        self.relation_label = ttk.Label(status_frame, text="", style="Stat.TLabel")
        self.relation_label.pack(side=tk.LEFT, padx=20)
        
        # 进度条
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=40, pady=5)
        
        ttk.Label(progress_frame, text="人生进度:", style="Normal.TLabel").pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(progress_frame, length=400, mode="determinate")
        self.progress["value"] = (self.player.age - 18) / 82 * 100
        self.progress.pack(side=tk.LEFT, padx=10)
        
        # 事件区域
        self.event_frame = ttk.Frame(self.root)
        self.event_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 操作按钮
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        
        # 主要按钮 - 带明显样式
        def make_btn(text, cmd, color="#4a90d9"):
            return tk.Button(btn_frame, text=text, font=("微软雅黑", 10), bg=color, fg="#fff",
                           activebackground="#6ba3e0", activeforeground="#fff",
                           relief=tk.RAISED, borderwidth=2, padx=12, pady=6, command=cmd)
        
        make_btn("度过一年", self.year_pass, "#27ae60").pack(side=tk.LEFT, padx=8)
        make_btn("🏥 医院", self.go_hospital).pack(side=tk.LEFT, padx=8)
        make_btn("🧠 心理医生", self.go_therapy).pack(side=tk.LEFT, padx=8)
        make_btn("🎰 彩票", self.buy_lottery).pack(side=tk.LEFT, padx=8)
        make_btn("💕 相亲", self.date_matchmaking).pack(side=tk.LEFT, padx=8)
        make_btn("🏆 成就", self.show_achievements).pack(side=tk.LEFT, padx=8)
        make_btn("📖 履历", self.show_diary).pack(side=tk.LEFT, padx=8)
        make_btn("保存退出", self.save_and_exit, "#e74c3c").pack(side=tk.LEFT, padx=8)
        
        # 初始显示
        self.update_status()
        self.show_welcome_event()
    
    def update_status(self):
        self.age_label.config(text=f"年龄: {self.player.age}岁")
        self.money_label.config(text=f"💰 金钱: {self.player.money:,}")
        self.health_label.config(text=f"❤️ 健康: {self.player.health}")
        self.happiness_label.config(text=f"😊 快乐: {self.player.happiness}")
        self.career_label.config(text=f"💼 事业: {self.player.career}")
        self.progress["value"] = (self.player.age - 18) / 82 * 100
        
        # 更新关系状态
        relation_text = ""
        if self.player.spouse:
            relation_text += f"💑 {self.player.spouse}"
        if self.player.children:
            relation_text += f" | 👶 {len(self.player.children)}个孩子"
        self.relation_label.config(text=relation_text)
        
        # 检测成就
        self.check_achievements()
    
    def check_achievements(self):
        """检测成就达成"""
        # 百万富翁
        if self.player.money >= 1000000 and "millionaire" not in self.player.achievements:
            self.player.achievements.append("millionaire")
            self.show_achievement_popup("millionaire")
        
        # 百岁老人
        if self.player.age >= 100 and "centenarian" not in self.player.achievements:
            self.player.achievements.append("centenarian")
            self.show_achievement_popup("centenarian")
        
        # 人生赢家
        if (self.player.money >= 80000 and self.player.happiness >= 80 and self.player.career >= 80 
            and "rich_and_happy" not in self.player.achievements):
            self.player.achievements.append("rich_and_happy")
            self.show_achievement_popup("rich_and_happy")
        
        # 绝境逢生 - 5次转折点
        if hasattr(self.player, "turning_count") and self.player.turning_count >= 5:
            if "turning_point_5" not in self.player.achievements:
                self.player.achievements.append("turning_point_5")
                self.show_achievement_popup("turning_point_5")
        
        # 结婚
        if self.player.spouse and "married" not in self.player.achievements:
            self.player.achievements.append("married")
            self.show_achievement_popup("married")
        
        # 儿女成群
        if len(self.player.children) >= 3 and "three_children" not in self.player.achievements:
            self.player.achievements.append("three_children")
            self.show_achievement_popup("three_children")
        
        # 英年早逝
        if self.player.dead and self.player.age < 30 and "early_death" not in self.player.achievements:
            self.player.achievements.append("early_death")
    
    def show_achievement_popup(self, achievement_id):
        """显示成就弹窗"""
        for ach in ACHIEVEMENTS:
            if ach["id"] == achievement_id:
                messagebox.showinfo(f"🏆 成就解锁: {ach['name']}", f"{ach['icon']} {ach['name']}\n{ach['desc']}")
                break
    
    def show_achievements(self):
        """显示成就界面"""
        self.clear_event_area()
        
        ttk.Label(self.event_frame, text="🏆 成就列表", font=("微软雅黑", 18, "bold"), 
                  foreground="#ffd700", background="#1a1a2e").pack(pady=20)
        
        for ach in ACHIEVEMENTS:
            unlocked = ach["id"] in self.player.achievements
            color = "#2ecc71" if unlocked else "#666"
            icon = ach["icon"] if unlocked else "🔒"
            status = "已解锁" if unlocked else "未解锁"
            
            ttk.Label(self.event_frame, text=f"{icon} {ach['name']} - {ach['desc']} [{status}]", 
                      font=("微软雅黑", 10), foreground=color, background="#1a1a2e").pack(pady=3)
        
        btn = ttk.Button(self.event_frame, text="返回", style="Game.TButton", command=self.show_game_after_event)
        btn.pack(pady=20)
    
    def show_diary(self):
        """显示/写人生履历"""
        self.clear_event_area()
        
        ttk.Label(self.event_frame, text="📖 人生履历", font=("微软雅黑", 18, "bold"), 
                  foreground="#fff", background="#1a1a2e").pack(pady=20)
        
        # 写新记录
        ttk.Label(self.event_frame, text="记录今年的一句话:", style="Normal.TLabel").pack()
        
        self.diary_entry = ttk.Entry(self.event_frame, font=("微软雅黑", 11), width=40)
        self.diary_entry.pack(pady=5)
        
        btn_write = ttk.Button(self.event_frame, text="写下今年", style="Game.TButton", command=self.write_diary)
        btn_write.pack(pady=5)
        
        # 显示已有记录
        if self.player.diary:
            ttk.Label(self.event_frame, text="\n--- 过去的记录 ---", style="Normal.TLabel").pack(pady=10)
            
            # 创建滚动条
            canvas = tk.Canvas(self.event_frame, bg="#1a1a2e", highlightthickness=0, height=200)
            scrollbar = ttk.Scrollbar(self.event_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=(20,0))
            scrollbar.pack(side="right", fill="y", padx=(0,20))
            
            for entry in self.player.diary:
                ttk.Label(scrollable_frame, text=f"【{entry['age']}岁】 {entry['text']}", 
                          font=("微软雅黑", 9), foreground="#ccc", background="#1a1a2e").pack(pady=2, anchor="w")
        else:
            ttk.Label(self.event_frame, text="\n还没有任何记录...", style="Normal.TLabel").pack(pady=10)
        
        btn = ttk.Button(self.event_frame, text="返回", style="Game.TButton", command=self.show_game_after_event)
        btn.pack(pady=10)
    
    def write_diary(self):
        """写下人生记录"""
        text = self.diary_entry.get().strip()
        if text:
            self.player.diary.append({"age": self.player.age, "text": text})
            messagebox.showinfo("记录", "记录成功！")
            self.show_diary()  # 刷新显示
        else:
            messagebox.showwarning("提示", "请输入内容！")
    
    def clear_event_area(self):
        for widget in self.event_frame.winfo_children():
            widget.destroy()
    
    def show_welcome_event(self):
        self.clear_event_area()
        
        ttk.Label(self.event_frame, text=f"欢迎，{self.player.name}！", font=("微软雅黑", 16, "bold"), foreground="#fff", background="#1a1a2e").pack(pady=20)
        ttk.Label(self.event_frame, text=f"你出生于{BACKGROUNDS[self.player.background][0]}，今年18岁。", 
                  style="Normal.TLabel").pack()
        ttk.Label(self.event_frame, text="点击「度过一年」开始你的人生旅程...", style="Normal.TLabel").pack(pady=10)
    
    def show_event(self, event):
        self.clear_event_area()
        
        title = ttk.Label(self.event_frame, text=f"【{event['title']}】", font=("微软雅黑", 14, "bold"), 
                          foreground="#ff6b6b", background="#1a1a2e")
        title.pack(pady=10)
        
        desc = ttk.Label(self.event_frame, text=event["desc"], style="Normal.TLabel")
        desc.pack(pady=5)
        
        # 按钮
        for i, choice in enumerate(event["choices"]):
            btn = ttk.Button(self.event_frame, text=choice[0], style="Choice.TButton",
                           command=lambda idx=i: self.handle_choice(idx))
            btn.pack(pady=5, fill=tk.X, padx=100)
    
    def show_turning_point(self, event):
        self.clear_event_area()
        
        ttk.Label(self.event_frame, text="🌟 转折点！🌟", font=("微软雅黑", 16, "bold"), 
                  foreground="#ffd700", background="#1a1a2e").pack(pady=20)
        
        ttk.Label(self.event_frame, text=f"【{event['title']}】", font=("微软雅黑", 14, "bold"), 
                  foreground="#fff", background="#1a1a2e").pack()
        
        ttk.Label(self.event_frame, text=event["desc"], style="Normal.TLabel").pack(pady=10)
        
        ttk.Label(self.event_frame, text=f"→ {event['type']}", font=("微软雅黑", 12), 
                  foreground="#4ecdc4", background="#1a1a2e").pack(pady=10)
        
        btn = ttk.Button(self.event_frame, text="继续", style="Game.TButton", command=self.show_game_after_event)
        btn.pack(pady=20)
    
    def show_special_event(self, event):
        """显示特殊事件"""
        self.clear_event_area()
        
        emoji = "🔴" if event["type"] == "negative" else "🟢"
        color = "#ff4757" if event["type"] == "negative" else "#2ecc71"
        
        ttk.Label(self.event_frame, text=f"{emoji} 特殊事件 {emoji}", font=("微软雅黑", 16, "bold"), 
                  foreground=color, background="#1a1a2e").pack(pady=20)
        
        ttk.Label(self.event_frame, text=f"【{event['title']}】", font=("微软雅黑", 14, "bold"), 
                  foreground="#fff", background="#1a1a2e").pack()
        
        ttk.Label(self.event_frame, text=event["desc"], style="Normal.TLabel").pack(pady=10)
        
        # 显示属性变化
        effects = event["effect"]
        effect_text = ""
        if "money" in effects:
            effect_text += f"💰 金钱: {effects['money']:+}\n"
        if "health" in effects:
            effect_text += f"❤️ 健康: {effects['health']:+}\n"
        if "happiness" in effects:
            effect_text += f"😊 快乐: {effects['happiness']:+}\n"
        if "career" in effects:
            effect_text += f"💼 事业: {effects['career']:+}\n"
        
        ttk.Label(self.event_frame, text=effect_text, font=("微软雅黑", 12, "bold"), 
                  foreground=color, background="#1a1a2e").pack(pady=10)
        
        btn = ttk.Button(self.event_frame, text="继续", style="Game.TButton", command=self.show_game_after_event)
        btn.pack(pady=20)
    
    def show_game_after_event(self):
        self.clear_event_area()
        ttk.Label(self.event_frame, text="继续度过你的人生...", style="Normal.TLabel").pack(pady=20)
    
    def year_pass(self):
        self.player.age += 1
        
        # 自然变化
        self.player.health -= random.randint(2, 8)
        self.player.happiness -= random.randint(2, 8)
        self.player.money += self.player.career * 100
        self.player.money -= 5000
        
        # 配偶影响
        if self.player.spouse:
            self.player.money -= 3000  # 家庭开支
            self.player.happiness = min(100, self.player.happiness + 5)  # 有伴
        
        # 子女影响
        if self.player.children:
            for child in self.player.children:
                self.player.money -= 2000  # 养育费用
            self.player.happiness = min(100, self.player.happiness + len(self.player.children) * 3)
        
        # 子女成长
        if self.player.children:
            self.update_children_age()
        
        # 检查死亡
        death_result = self.player.check_death()
        if death_result == "turning":
            event = self.player.trigger_turning_point()
            self.update_status()
            self.show_turning_point(event)
            return
        elif self.player.dead:
            self.update_status()
            self.show_death_screen()
            return
        
        # 检测转折点
        turning = self.player.check_turning_point()
        if turning:
            self.update_status()
            self.show_turning_point(turning)
            return
        
        # 特殊事件（10%概率触发）
        if random.random() < 0.1:
            special_event = random.choice(SPECIAL_EVENTS)
            self.player.apply_effect(special_event["effect"])
            self.player.events_log.append({"age": self.player.age, "title": f"[特殊] {special_event['title']}"})
            self.update_status()
            self.show_special_event(special_event)
            return
        
        # 随机事件
        event = random.choice(NORMAL_EVENTS)
        self.current_event = event
        self.player.events_log.append({"age": self.player.age, "title": event["title"]})
        
        self.update_status()
        self.show_event(event)
    
    def handle_choice(self, idx):
        choice = self.current_event["choices"][idx]
        effects = choice[1] if len(choice) > 1 else {}
        
        # 特殊处理投资
        if "投资" in self.current_event["title"]:
            if random.random() < 0.5:
                effects = {"money": 10000, "happiness": 10}
            else:
                effects = {"money": -5000, "happiness": -10}
        
        self.player.apply_effect(effects)
        
        # 检查死亡
        if self.player.health <= 0:
            death_result = self.player.check_death()
            if death_result == "turning":
                event = self.player.trigger_turning_point()
                self.update_status()
                self.show_turning_point(event)
                return
            elif self.player.dead:
                self.update_status()
                self.show_death_screen()
                return
        
        self.update_status()
        self.show_game_after_event()
    
    def show_death_screen(self):
        self.clear_event_area()
        
        ttk.Label(self.event_frame, text="💀 游戏结束 💀", font=("微软雅黑", 20, "bold"), 
                  foreground="#ff4757", background="#1a1a2e").pack(pady=30)
        
        ttk.Label(self.event_frame, text=f"享年: {self.player.age}岁", style="Stat.TLabel").pack()
        ttk.Label(self.event_frame, text=f"死因: {self.player.death_reason}", style="Normal.TLabel").pack(pady=10)
        ttk.Label(self.event_frame, text=f"最终存款: {self.player.money:,}", style="Normal.TLabel").pack()
        
        # 关系状态
        if self.player.spouse or self.player.children:
            relation_text = ""
            if self.player.spouse:
                relation_text += f"💑 配偶: {self.player.spouse}"
            if self.player.children:
                relation_text += f" | 👶 子女: {len(self.player.children)}人"
                for child in self.player.children:
                    relation_text += f"\n   - {child['name']} ({child['age']}岁)"
            ttk.Label(self.event_frame, text=relation_text, style="Normal.TLabel").pack(pady=10)
        
        # 人生事件
        ttk.Label(self.event_frame, text=f"\n经历的事件数: {len(self.player.events_log)}", style="Normal.TLabel").pack(pady=10)
        
        # 人生履历
        if self.player.diary:
            ttk.Label(self.event_frame, text=f"\n人生记录: {len(self.player.diary)}条", style="Normal.TLabel").pack(pady=5)
        
        btn_frame = ttk.Frame(self.event_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="重新开始", style="Game.TButton", command=self.show_start_screen).pack(side=tk.LEFT, padx=10)
    
    def go_hospital(self):
        """去医院看病"""
        if self.player.money < 2000:
            messagebox.showwarning("钱不够", "去医院需要2000元！")
            return
        
        # 治疗效果
        health_gain = random.randint(15, 35)
        self.player.money -= 2000
        self.player.health = min(100, self.player.health + health_gain)
        
        self.update_status()
        self.clear_event_area()
        
        ttk.Label(self.event_frame, text="🏥 医院", font=("微软雅黑", 16, "bold"), 
                  foreground="#4ecdc4", background="#1a1a2e").pack(pady=20)
        ttk.Label(self.event_frame, text=f"医生给你做了全面检查和治疗", style="Normal.TLabel").pack()
        ttk.Label(self.event_frame, text=f"健康 +{health_gain}", font=("微软雅黑", 14, "bold"), 
                  foreground="#2ecc71", background="#1a1a2e").pack(pady=10)
        ttk.Label(self.event_frame, text=f"花费: 2000元", style="Normal.TLabel").pack()
        
        btn = ttk.Button(self.event_frame, text="返回", style="Game.TButton", command=self.show_game_after_event)
        btn.pack(pady=20)
    
    def go_therapy(self):
        """去看心理医生"""
        if self.player.money < 1000:
            messagebox.showwarning("钱不够", "看心理医生需要1000元！")
            return
        
        # 治疗效果
        happiness_gain = random.randint(10, 25)
        self.player.money -= 1000
        self.player.happiness = min(100, self.player.happiness + happiness_gain)
        
        self.update_status()
        self.clear_event_area()
        
        ttk.Label(self.event_frame, text="🧠 心理医生", font=("微软雅黑", 16, "bold"), 
                  foreground="#9b59b6", background="#1a1a2e").pack(pady=20)
        ttk.Label(self.event_frame, text="心理医生帮你梳理情绪", style="Normal.TLabel").pack()
        ttk.Label(self.event_frame, text=f"快乐 +{happiness_gain}", font=("微软雅黑", 14, "bold"), 
                  foreground="#2ecc71", background="#1a1a2e").pack(pady=10)
        ttk.Label(self.event_frame, text=f"花费: 1000元", style="Normal.TLabel").pack()
        
        btn = ttk.Button(self.event_frame, text="返回", style="Game.TButton", command=self.show_game_after_event)
        btn.pack(pady=20)
    
    def buy_lottery(self):
        """买彩票"""
        cost = 100
        if self.player.money < cost:
            messagebox.showwarning("钱不够", f"买彩票只需要{cost}元！")
            return
        
        self.player.money -= cost
        
        # 彩票结果
        roll = random.random()
        
        self.update_status()
        self.clear_event_area()
        
        ttk.Label(self.event_frame, text="🎰 彩票", font=("微软雅黑", 16, "bold"), 
                  foreground="#f1c40f", background="#1a1a2e").pack(pady=20)
        
        if roll < 0.0001:  # 0.01% 特等奖
            prize = 100000
            self.player.money += prize
            self.player.happiness = min(100, self.player.happiness + 50)
            ttk.Label(self.event_frame, text="🎉 特等奖！！！ 🎉", font=("微软雅黑", 18, "bold"), 
                      foreground="#ffd700", background="#1a1a2e").pack(pady=10)
            ttk.Label(self.event_frame, text=f"你中了100万！", style="Normal.TLabel").pack()
            # 成就
            if "lottery_win" not in self.player.achievements:
                self.player.achievements.append("lottery_win")
                self.show_achievement_popup("lottery_win")
        elif roll < 0.001:  # 0.1% 一等奖
            prize = 10000
            self.player.money += prize
            self.player.happiness = min(100, self.player.happiness + 20)
            ttk.Label(self.event_frame, text="🏆 一等奖！", font=("微软雅黑", 16, "bold"), 
                      foreground="#f1c40f", background="#1a1a2e").pack(pady=10)
            ttk.Label(self.event_frame, text=f"你中了1万元！", style="Normal.TLabel").pack()
            if "lottery_win" not in self.player.achievements:
                self.player.achievements.append("lottery_win")
                self.show_achievement_popup("lottery_win")
        elif roll < 0.01:  # 1% 幸运奖
            prize = 1000
            self.player.money += prize
            self.player.happiness = min(100, self.player.happiness + 5)
            ttk.Label(self.event_frame, text="🎁 幸运奖", font=("微软雅黑", 14, "bold"), 
                      foreground="#2ecc71", background="#1a1a2e").pack(pady=10)
            ttk.Label(self.event_frame, text=f"中了1000元！", style="Normal.TLabel").pack()
            if "lottery_win" not in self.player.achievements:
                self.player.achievements.append("lottery_win")
                self.show_achievement_popup("lottery_win")
        else:
            ttk.Label(self.event_frame, text="谢谢参与...", style="Normal.TLabel").pack()
            ttk.Label(self.event_frame, text="再接再厉！", style="Normal.TLabel").pack(pady=10)
        
        ttk.Label(self.event_frame, text=f"花费: {cost}元", style="Normal.TLabel").pack(pady=10)
        
        # 记录
        self.player.events_log.append({"age": self.player.age, "title": "买彩票"})
        
        self.update_status()
        
        btn = ttk.Button(self.event_frame, text="返回", style="Game.TButton", command=self.show_game_after_event)
        btn.pack(pady=20)
    
    def date_matchmaking(self):
        """相亲/约会"""
        if self.player.spouse:
            # 已结婚，可以尝试生孩子
            self.try_have_child()
            return
        
        if self.player.age < 18:
            messagebox.showwarning("年龄不够", "你还未成年，不能相亲！")
            return
        
        if self.player.money < 500:
            messagebox.showwarning("钱不够", "相亲需要500元！")
            return
        
        self.player.money -= 500
        
        # 相亲结果
        roll = random.random()
        
        self.update_status()
        self.clear_event_area()
        
        ttk.Label(self.event_frame, text="💕 相亲", font=("微软雅黑", 16, "bold"), 
                  foreground="#e91e63", background="#1a1a2e").pack(pady=20)
        
        if roll < 0.3:  # 30% 成功率
            spouse_names = ["小美", "小红", "小丽", "小芳", "小兰", "阿花", "阿珍", "阿玲"]
            spouse_name = random.choice(spouse_names)
            self.player.spouse = spouse_name
            self.player.happiness = min(100, self.player.happiness + 30)
            
            ttk.Label(self.event_frame, text="🎉 相亲成功！ 🎉", font=("微软雅黑", 16, "bold"), 
                      foreground="#e91e63", background="#1a1a2e").pack(pady=10)
            ttk.Label(self.event_frame, text=f"你认识了 {spouse_name}，你们在一起了！", style="Normal.TLabel").pack()
            ttk.Label(self.event_frame, text="快乐 +30", font=("微软雅黑", 12, "bold"), 
                      foreground="#2ecc71", background="#1a1a2e").pack(pady=5)
            
            self.player.events_log.append({"age": self.player.age, "title": f"与{spouse_name}结婚"})
        else:
            ttk.Label(self.event_frame, text="相亲失败...", style="Normal.TLabel").pack()
            ttk.Label(self.event_frame, text="看来缘分还没到，再接再厉！", style="Normal.TLabel").pack(pady=10)
        
        ttk.Label(self.event_frame, text=f"花费: 500元", style="Normal.TLabel").pack(pady=5)
        
        self.update_status()
        
        btn = ttk.Button(self.event_frame, text="返回", style="Game.TButton", command=self.show_game_after_event)
        btn.pack(pady=20)
    
    def try_have_child(self):
        """尝试生孩子"""
        if len(self.player.children) >= 3:
            messagebox.showwarning("不能生了", "你们已经有3个孩子了！")
            return
        
        cost = 10000
        if self.player.money < cost:
            messagebox.showwarning("钱不够", f"养孩子需要{cost}元！")
            return
        
        # 生孩子结果
        roll = random.random()
        
        if roll < 0.4:  # 40% 成功率
            self.player.money -= cost
            child_names = ["小明", "小红", "小华", "小军", "小芳", "小娟", "小强", "小玲"]
            child_name = random.choice(child_names)
            self.player.children.append({"name": child_name, "age": 0})
            self.player.happiness = min(100, self.player.happiness + 20)
            
            self.clear_event_area()
            ttk.Label(self.event_frame, text="👶 孩子出生！", font=("微软雅黑", 16, "bold"), 
                      foreground="#e91e63", background="#1a1a2e").pack(pady=20)
            ttk.Label(self.event_frame, text=f"你们的孩子出生了，取名叫 {child_name}！", style="Normal.TLabel").pack()
            ttk.Label(self.event_frame, text="快乐 +20", font=("微软雅黑", 12, "bold"), 
                      foreground="#2ecc71", background="#1a1a2e").pack(pady=5)
            ttk.Label(self.event_frame, text=f"花费: {cost}元", style="Normal.TLabel").pack()
            
            self.player.events_log.append({"age": self.player.age, "title": f"孩子{child_name}出生"})
        else:
            self.clear_event_area()
            ttk.Label(self.event_frame, text="备孕中...", style="Normal.TLabel").pack()
            ttk.Label(self.event_frame, text="暂时没有好消息，再接再厉！", style="Normal.TLabel").pack(pady=10)
            ttk.Label(self.event_frame, text=f"花费: {cost//2}元（检查费）", style="Normal.TLabel").pack()
            self.player.money -= cost // 2
            self.player.events_log.append({"age": self.player.age, "title": "备孕失败（检查费）"})  # 修复：记录费用去向
        
        self.update_status()
        
        btn = ttk.Button(self.event_frame, text="返回", style="Game.TButton", command=self.show_game_after_event)
        btn.pack(pady=20)
    
    def update_children_age(self):
        """子女成长事件"""
        for child in self.player.children:
            child["age"] += 1
            
            # 子女成长随机事件
            if child["age"] == 18:
                # 成年，可能离家
                if random.random() < 0.3:
                    self.player.happiness = max(0, self.player.happiness - 10)
                    self.player.events_log.append({"age": self.player.age, "title": f"孩子{child['name']}离家出走"})
                else:
                    self.player.money += 5000  # 孩子打工赚钱
                    self.player.events_log.append({"age": self.player.age, "title": f"孩子{child['name']}成年了"})
            elif child["age"] % 5 == 0:
                # 每5年，子女可能给钱或惹事
                if random.random() < 0.5:
                    self.player.money += 3000
                    self.player.happiness = min(100, self.player.happiness + 5)
                else:
                    self.player.money -= 2000
                    self.player.happiness = max(0, self.player.happiness - 5)
    
    def save_and_exit(self):
        save_data = {
            "name": self.player.name,
            "age": self.player.age,
            "health": self.player.health,
            "money": self.player.money,
            "happiness": self.player.happiness,
            "career": self.player.career,
            "background": self.player.background,
            "spouse": self.player.spouse,
            "children": self.player.children,
            "achievements": self.player.achievements,
            "diary": self.player.diary,
            "turning_count": self.player.turning_count,  # 修复：保存转折点计数
        }
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savegame.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        messagebox.showinfo("保存", "游戏已保存！")
        self.root.quit()
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    app = LifeSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

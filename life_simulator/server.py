#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
熬过去 - 人生模拟器 后端API服务 v2.0
支持: 出身专属转机、关键年龄选择、小确幸事件、资产精细化、人际关系、节日事件
"""

import json
import random
import os
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from config import (
    BACKGROUNDS, TALENTS, PERSONALITIES, DIFFICULTIES,
    TURNING_POINT_EVENTS, BACKGROUND_TURNING_EVENTS, TURNING_COSTS,
    KEY_AGE_CHOICES, clamp, format_money
)

app = Flask(__name__, static_folder='web', static_url_path='/static')
app.secret_key = os.environ.get('LIFE_SIMULATOR_SECRET', 'life_simulator_secret_key_2024')
CORS(app, supports_credentials=True)

# ============ 额外配置数据 ============

JOBS = {
    "工人": {"income": 150, "risk": 0.15, "growth": 0.02},
    "服务员": {"income": 120, "risk": 0.10, "growth": 0.015},
    "司机": {"income": 180, "risk": 0.12, "growth": 0.02},
    "教师": {"income": 200, "risk": 0.05, "growth": 0.03},
    "会计": {"income": 200, "risk": 0.05, "growth": 0.025},
    "程序员": {"income": 300, "risk": 0.08, "growth": 0.05},
    "医生": {"income": 350, "risk": 0.10, "growth": 0.04},
    "律师": {"income": 400, "risk": 0.08, "growth": 0.04},
    "公务员": {"income": 220, "risk": 0.02, "growth": 0.02},
    "网红": {"income": 250, "risk": 0.20, "growth": 0.08},
    "创业者": {"income": 300, "risk": 0.40, "growth": 0.10},
    "经理": {"income": 400, "risk": 0.10, "growth": 0.03},
}

EDUCATIONS = {0: {"name": "高中", "baseIncome": 100}, 1: {"name": "本科", "baseIncome": 200}, 2: {"name": "硕士", "baseIncome": 350}, 3: {"name": "博士", "baseIncome": 500}}

# 小确幸/小确丧
SMALL_EVENTS = {
    "happy": [
        {"title": "买到喜欢的奶茶", "effect": {"happiness": 2}},
        {"title": "加班费到账", "effect": {"money": 500}},
        {"title": "宠物撒娇", "effect": {"happiness": 3}},
        {"title": "捡到钱", "effect": {"money": 100, "happiness": 1}},
        {"title": "同事分享零食", "effect": {"happiness": 2}},
    ],
    "sad": [
        {"title": "上班迟到", "effect": {"money": -200}},
        {"title": "错过消息", "effect": {"happiness": -2}},
        {"title": "健身拉伤", "effect": {"health": -5}},
        {"title": "外卖撒漏", "effect": {"happiness": -3}},
        {"title": "下雨没带伞", "effect": {"health": -2, "happiness": -1}},
    ],
}

# 资产配置
PROPERTIES = {
    "house": {
        "none": {"name": "无房", "cost": 0},
        "small": {"name": "小户型", "cost": 100000, "happiness": 10},
        "large": {"name": "大户型", "cost": 500000, "happiness": 20},
        "villa": {"name": "别墅", "cost": 2000000, "happiness": 40},
    },
    "car": {
        "none": {"name": "无车", "cost": 0},
        "economy": {"name": "代步车", "cost": 50000, "happiness": 5},
        "luxury": {"name": "豪车", "cost": 500000, "happiness": 10},
    },
}

# 伴侣类型
SPOUSE_TYPES = {
    "frugal": {"name": "节俭型", "buff": "省10%开支"},
    "optimistic": {"name": "乐观型", "buff": "快乐衰减-10%"},
    "career": {"name": "事业型", "buff": "职业+2%"},
    "family": {"name": "顾家型", "buff": "健康-10%"},
}

# 节日
HOLIDAY_EVENTS = {
    "birthday": {
        "young": [
            {"text": "朋友庆祝", "effect": {"happiness": 15, "money": -1000}},
            {"text": "独自度过", "effect": {"happiness": 5}},
        ],
        "old": [
            {"text": "子女祝寿", "effect": {"happiness": 30, "money": 20000}},
            {"text": "回忆人生", "effect": {"happiness": 10}},
        ],
    },
}

ACHIEVEMENTS = [
    {"id": "millionaire", "name": "百万富翁", "icon": "💰", "condition": lambda s: s.get("money", 0) >= 1000000},
    {"id": "centenarian", "name": "百岁老人", "icon": "🎂", "condition": lambda s: s.get("age", 0) >= 100},
    {"id": "winner", "name": "人生赢家", "icon": "🏆", "condition": lambda s: s.get("money", 0) >= 100000 and s.get("happiness", 0) >= 80 and s.get("career", 0) >= 80},
    {"id": "survivor", "name": "绝境逢生", "icon": "🌟", "condition": lambda s: s.get("turningPoints", 0) >= 5},
    {"id": "married", "name": "结婚", "icon": "💑", "condition": lambda s: s.get("spouse") is not None},
    {"id": "family", "name": "儿女成群", "icon": "👨‍👩‍👧‍👦", "condition": lambda s: len(s.get("children", [])) >= 3},
    {"id": "homeowner", "name": "有房一族", "icon": "🏠", "condition": lambda s: s.get("house", False)},
    {"id": "petOwner", "name": "铲屎官", "icon": "🐱", "condition": lambda s: s.get("pet", False)},
    {"id": "comeback", "name": "否极泰来", "icon": "🌈", "condition": lambda s: "逆袭者" in s.get("lifeLabels", [])},
    {"id": "carOwner", "name": "有车一族", "icon": "🚗", "condition": lambda s: s.get("car") and s.get("car") != "none"},
]


# ============ 工具函数 ============

def random_int(min_val, max_val): return random.randint(min_val, max_val)
def random_choice(arr): return random.choice(arr)


# ============ 游戏核心类 ============

class GameState:
    def __init__(self):
        self.data = {
            "name": "", "age": 18, "background": "1", "talent": "1", "personality": "1", "difficulty": "1",
            "money": 5000, "health": 80, "happiness": 70, "career": 20, "education": 0, "job": None, "year": 1,
            "isGameOver": False, "isDead": False, "deathReason": "", "achievements": [], "events": [],
            "timeline": [{"age": 18, "event": "开启人生旅程"}],
            "spouse": None, "spouseType": None, "children": [], "house": False, "houseType": "none",
            "car": "none", "pet": False, "countries": [], "turningPoints": 0, "consecutiveTurning": 0,
            "lifeLabels": [], "debt": 0, "keyChoices": {"age18": None, "age25": None, "age35": None, "age50": None},
            "specialBuffs": {},
        }
    
    def apply_effect(self, effect):
        if "money" in effect: self.data["money"] += effect["money"]
        if "health" in effect: self.data["health"] = clamp(self.data["health"] + effect["health"])
        if "happiness" in effect: self.data["happiness"] = clamp(self.data["happiness"] + effect["happiness"])
        if "career" in effect: self.data["career"] = clamp(self.data["career"] + effect["career"])
        if "house" in effect: self.data["house"] = True
        if "pet" in effect: self.data["pet"] = True
    
    def check_death(self):
        if self.data["health"] <= 0:
            if random.random() < 0.1:
                self.data["isDead"] = True
                self.data["deathReason"] = "因病去世"
                self.data["isGameOver"] = True
                return True
            else:
                self.trigger_turning_point()
        return False
    
    def check_turning_point(self):
        diff = DIFFICULTIES[self.data["difficulty"]]
        crisis = self.data["health"] < 20 or self.data["money"] < -50000 or self.data["happiness"] < 10
        
        if crisis and random.random() < diff["turningRate"] * 0.3:
            self.data["turningPoints"] += 1
            self.data["consecutiveTurning"] += 1
            
            # 人生逆袭
            if self.data["consecutiveTurning"] >= 2 and random.random() < 0.1:
                self.apply_effect({"money": 100000, "health": 50, "happiness": 50, "career": 30})
                self.data["lifeLabels"].append("逆袭者")
                self.data["consecutiveTurning"] = 0  # 逆袭后重置
                return {"type": "turning", "title": "人生逆袭！", "desc": "连续绝境触发超级转机！", "effects": {"money": 100000}}
            
            # 出身专属转机（80%概率）
            bg = self.data["background"]
            if bg in BACKGROUND_TURNING_EVENTS and random.random() < 0.8:
                event = random_choice(BACKGROUND_TURNING_EVENTS[bg])
                self.apply_effect(event["effect"])
                self.data["timeline"].append({"age": self.data["age"], "event": f"🌟 {event['title']}"})
                self.data["consecutiveTurning"] = 0  # 修复：触发转机后重置计数器
                return {"type": "turning", "title": event["title"], "desc": event.get("desc", ""), "effects": event["effect"]}
            
            # 代价转机
            for cost_data in TURNING_COSTS.values():
                if "condition" not in cost_data or cost_data["condition"](self.data):
                    if random.random() < cost_data.get("chance", 0.3):
                        self.apply_effect(cost_data["effect"])
                        self.data["timeline"].append({"age": self.data["age"], "event": f"🌟 转折"})
                        self.data["consecutiveTurning"] = 0  # 修复：触发转机后重置计数器
                        return {"type": "turning", "title": cost_data.get("desc", "度过难关"), "effects": cost_data["effect"]}
            
            # 通用转机
            event = random_choice(TURNING_POINT_EVENTS)
            self.apply_effect(event["effect"])
            self.data["timeline"].append({"age": self.data["age"], "event": f"🌟 {event['title']}"})
            self.data["consecutiveTurning"] = 0  # 修复：触发转机后重置计数器
            return {"type": "turning", "title": event["title"], "effects": event["effect"]}
        else:
            self.data["consecutiveTurning"] = 0
        return None
    
    def trigger_turning_point(self):
        event = random_choice(TURNING_POINT_EVENTS)
        self.apply_effect(event["effect"])
        self.data["turningPoints"] += 1
        self.data["timeline"].append({"age": self.data["age"], "event": f"🌟 {event['title']}"})
    
    def check_key_age_choice(self):
        age = self.data["age"]
        if age in KEY_AGE_CHOICES:
            key = f"age{age}"
            if not self.data["keyChoices"].get(key):
                return {"type": "key_choice", "age": age, "choices": KEY_AGE_CHOICES[age]}
        return None
    
    def handle_key_choice(self, choice_index):
        age = self.data["age"]
        choices = KEY_AGE_CHOICES[age]
        if choice_index >= len(choices): return None
        
        choice = choices[choice_index]
        self.data["keyChoices"][f"age{age}"] = choice["text"]
        if "effect" in choice: self.apply_effect(choice["effect"])
        
        special = choice.get("special", "")
        special_buffs = self.data.get("specialBuffs", {})
        
        # 处理学历相关选择
        if special == "gaokao":
            # 高考：50%成功率，有学习天赋+30%
            talent = TALENTS[self.data["talent"]]
            success_rate = 0.5 + talent["effect"].get("studyBonus", 0)
            if random.random() < success_rate:
                self.data["education"] = 1
                self.data["happiness"] = clamp(self.data["happiness"] + 30)
                self.data["timeline"].append({"age": self.data["age"], "event": "🎓 考上大学！"})
            else:
                self.data["happiness"] = clamp(self.data["happiness"] - 20)
                self.data["timeline"].append({"age": self.data["age"], "event": "🎓 高考落榜..."})
        
        elif special == "work_no_edu":
            self.data["specialBuffs"]["eduLocked"] = True
            self.data["timeline"].append({"age": self.data["age"], "event": "💼 直接工作"})
        
        elif special == "kaoyan":
            # 考研：基础40%成功率，学习天赋+30%，gap_year社交加成+15%
            talent = TALENTS[self.data["talent"]]
            gap_year_bonus = special_buffs.get("socialBonus", 0)  # 修复：gap_year社交加成现在会生效
            success_rate = 0.4 + talent["effect"].get("studyBonus", 0) + gap_year_bonus
            if random.random() < success_rate:
                self.data["education"] = 2
                self.data["happiness"] = clamp(self.data["happiness"] + 30)
                self.data["timeline"].append({"age": self.data["age"], "event": "🎓 考上研究生！"})
            else:
                self.data["happiness"] = clamp(self.data["happiness"] - 15)
                self.data["timeline"].append({"age": self.data["age"], "event": "🎓 考研落榜..."})
        
        elif special == "kaobo":
            # 考博：基础30%成功率，学习天赋+30%，gap_year社交加成+15%
            talent = TALENTS[self.data["talent"]]
            gap_year_bonus = special_buffs.get("socialBonus", 0)  # 修复：gap_year社交加成现在会生效
            success_rate = 0.3 + talent["effect"].get("studyBonus", 0) + gap_year_bonus
            if random.random() < success_rate:
                self.data["education"] = 3
                self.data["happiness"] = clamp(self.data["happiness"] + 30)
                self.data["timeline"].append({"age": self.data["age"], "event": "🎓 考上博士！"})
            else:
                self.data["happiness"] = clamp(self.data["happiness"] - 15)
                self.data["timeline"].append({"age": self.data["age"], "event": "🎓 考博落榜..."})
        
        elif special == "find_job":
            jobs_list = [j for j in JOBS.keys()]
            self.data["job"] = random_choice(jobs_list)
            self.data["happiness"] = clamp(self.data["happiness"] + 15)
            self.data["timeline"].append({"age": self.data["age"], "event": f"💼 成为{self.data['job']}"})
        
        elif special == "gap_year":
            self.data["specialBuffs"]["socialBonus"] = 0.15
        elif special == "career_stay":
            self.data["specialBuffs"]["careerGrowth"] = 0.02
        elif special == "startup":
            self.data["specialBuffs"]["entrepreneurBonus"] = 0.10
        elif special == "early_retire":
            self.data["specialBuffs"]["earlyRetire"] = True
        elif special == "keep_working":
            self.data["specialBuffs"]["elderGrowth"] = 0.04
        elif special == "mentor":
            self.data["specialBuffs"]["mentorBuff"] = 0.03
        
        self.data["timeline"].append({"age": self.data["age"], "event": f"🎯 {choice['text']}"})
        return {"type": "choice_result", "result": choice.get("outcome", "")}
    
    def check_small_event(self):
        if random.random() < 0.15:
            is_happy = random.random() < 0.6
            events = SMALL_EVENTS["happy"] if is_happy else SMALL_EVENTS["sad"]
            event = random_choice(events)
            self.apply_effect(event["effect"])
            self.data["timeline"].append({"age": self.data["age"], "event": event["title"]})
            return {"type": "small_event", "event": event}
        return None
    
    def check_holiday_event(self):
        if random.random() < 0.1:
            is_young = self.data["age"] < 30
            events = HOLIDAY_EVENTS["birthday"]["young"] if is_young else HOLIDAY_EVENTS["birthday"]["old"]
            event = random_choice(events)
            self.apply_effect(event["effect"])
            self.data["timeline"].append({"age": self.data["age"], "event": f"🎂 {event['text']}"})
            return {"type": "holiday", "event": event}
        return None
    
    def next_year(self):
        self.data["year"] += 1
        self.data["age"] += 1
        
        # 属性衰减
        health_change = -random_int(2, 8)
        happiness_change = -random_int(2, 8)
        
        if self.data["personality"] == "3": happiness_change *= 0.7
        if self.data["talent"] == "4": health_change *= 0.5
        if self.data["pet"]: happiness_change += 5
        if self.data["house"]: happiness_change += 5
        
        # 特殊buff
        if self.data.get("specialBuffs", {}).get("earlyRetire"):
            happiness_change *= 0.5
            health_change *= 0.7
        
        self.data["health"] = clamp(self.data["health"] + health_change)
        self.data["happiness"] = clamp(self.data["happiness"] + happiness_change)
        
        # 事业
        career_change = random_int(-2, 5)
        if self.data["personality"] == "4": career_change *= 1.2
        if self.data.get("specialBuffs", {}).get("careerGrowth"): career_change *= 1.02
        if self.data.get("specialBuffs", {}).get("elderGrowth"): career_change += 4
        self.data["career"] = clamp(self.data["career"] + career_change)
        
        # 收入
        income = EDUCATIONS[self.data["education"]]["baseIncome"] * (1 + self.data["career"] / 100)
        if self.data["job"] and self.data["job"] in JOBS:
            job_data = JOBS[self.data["job"]]
            income = job_data["income"] * (1 + self.data["career"] / 100)
            if random.random() < job_data["growth"]:
                self.data["career"] = clamp(self.data["career"] + 5)
            if random.random() < job_data["risk"] * 0.1:
                self.data["job"] = None
                self.data["timeline"].append({"age": self.data["age"], "event": "💸 失业"})
        
        if self.data["talent"] == "3": income *= 1.3
        
        self.data["money"] += int(income)
        
        # 家庭开支
        if self.data["spouse"]:
            self.data["money"] -= 3000
            self.data["happiness"] = clamp(self.data["happiness"] + 5)
        for child in self.data["children"]:
            self.data["money"] -= 2000
        
        self.data["timeline"].append({"age": self.data["age"], "event": f"年收入 {format_money(int(income))}"})
        
        if self.check_death():
            return {"type": "death", "reason": self.data["deathReason"]}
        
        # 先检查关键年龄选择（最重要的事件）
        key_choice = self.check_key_age_choice()
        if key_choice: return key_choice
        
        # 再检查转机
        turning = self.check_turning_point()
        if turning: return turning
        
        small_event = self.check_small_event()
        if small_event: return small_event
        
        holiday = self.check_holiday_event()
        if holiday: return holiday
        
        if random.random() < 0.3:
            return {"type": "normal", "message": f"{self.data['age']}岁"}
        
        return {"type": "normal", "message": f"年龄: {self.data['age']}"}
    
    def check_achievements(self):
        new = []
        for ach in ACHIEVEMENTS:
            if ach["id"] not in self.data["achievements"] and ach["condition"](self.data):
                self.data["achievements"].append(ach["id"])
                new.append(ach)
        return new
    
    def to_dict(self):
        return self.data.copy()


# ============ 路由 ============

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>熬过去 - 人生模拟器</title>
        <link rel="stylesheet" href="/static/css/style.css">
        <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    </head>
    <body>
        <div id="app">
            <!-- 欢迎界面 -->
            <div v-if="currentScreen === 'welcome'" class="screen active">
                <div class="welcome-container">
                    <h1>🎮 熬过去</h1>
                    <p class="subtitle">人生模拟器</p>
                    <p class="tagline">熬过去就会好 ✨</p>
                    <div class="welcome-buttons">
                        <button class="btn btn-primary" @click="startNewGame">新游戏</button>
                        <button v-if="hasSave" class="btn btn-secondary" @click="continueGame">继续游戏</button>
                    </div>
                </div>
            </div>

            <!-- 创建角色 -->
            <div v-if="currentScreen === 'create'" class="screen active">
                <div class="create-container">
                    <h2>👤 创建角色</h2>
                    <div class="form-group">
                        <label>名字</label>
                        <input type="text" v-model="newGameData.name" placeholder="请输入名字" maxlength="10">
                    </div>
                    <div class="option-section">
                        <h3>🏠 出身</h3>
                        <div class="options-grid">
                            <div v-for="(bg, key) in config.backgrounds" :key="key"
                                 class="option-card" :class="{selected: newGameData.background === key}"
                                 @click="newGameData.background = key">
                                <div class="option-icon">{{ getBgIcon(key) }}</div>
                                <div class="option-name">{{ bg.name }}</div>
                            </div>
                        </div>
                    </div>
                    <div class="option-section">
                        <h3>⭐ 天赋</h3>
                        <div class="options-grid">
                            <div v-for="(talent, key) in config.talents" :key="key"
                                 class="option-card" :class="{selected: newGameData.talent === key}"
                                 @click="newGameData.talent = key">
                                <div class="option-icon">📚</div>
                                <div class="option-name">{{ talent.name }}</div>
                            </div>
                        </div>
                    </div>
                    <div class="option-section">
                        <h3>🧑 性格</h3>
                        <div class="options-grid">
                            <div v-for="(pers, key) in config.personalities" :key="key"
                                 class="option-card" :class="{selected: newGameData.personality === key}"
                                 @click="newGameData.personality = key">
                                <div class="option-icon">{{ getPersIcon(key) }}</div>
                                <div class="option-name">{{ pers.name }}</div>
                            </div>
                        </div>
                    </div>
                    <div class="option-section">
                        <h3>🎯 难度</h3>
                        <div class="options-grid">
                            <div v-for="(diff, key) in config.difficulties" :key="key"
                                 class="option-card" :class="{selected: newGameData.difficulty === key}"
                                 @click="newGameData.difficulty = key">
                                <div class="option-icon">{{ getDiffIcon(key) }}</div>
                                <div class="option-name">{{ diff.name }}</div>
                            </div>
                        </div>
                    </div>
                    <button class="btn btn-primary btn-large" @click="confirmCreate">开始游戏</button>
                </div>
            </div>

            <!-- 游戏界面 -->
            <div v-if="currentScreen === 'game'" class="screen active">
                <div class="game-container">
                    <div class="game-header">
                        <div class="player-info">
                            <span class="player-name">{{ gameState.name }}</span>
                            <span class="player-age">{{ gameState.age }}岁</span>
                        </div>
                    </div>
                    <div class="stats-container">
                        <div class="stat-item">
                            <div class="stat-label"><span>💰 金钱</span><span>{{ formatMoney(gameState.money) }}</span></div>
                            <div class="stat-bar"><div class="stat-fill money" :style="{width: Math.min(100, gameState.money / 10000) + '%'}"></div></div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label"><span>❤️ 健康</span><span>{{ gameState.health }}</span></div>
                            <div class="stat-bar"><div class="stat-fill health" :style="{width: gameState.health + '%'}"></div></div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label"><span>😊 快乐</span><span>{{ gameState.happiness }}</span></div>
                            <div class="stat-bar"><div class="stat-fill happiness" :style="{width: gameState.happiness + '%'}"></div></div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label"><span>💼 事业</span><span>{{ gameState.career }}</span></div>
                            <div class="stat-bar"><div class="stat-fill career" :style="{width: gameState.career + '%'}"></div></div>
                        </div>
                    </div>
                    <div class="status-tags">
                        <span v-if="gameState.spouse" class="status-tag spouse">💑 {{ gameState.spouse }}</span>
                        <span v-if="gameState.children?.length" class="status-tag children">👶 {{ gameState.children.length }}个孩子</span>
                        <span v-if="gameState.house" class="status-tag house">🏠 有房</span>
                        <span v-if="gameState.car && gameState.car !== 'none'" class="status-tag car">🚗 有车</span>
                        <span v-if="gameState.pet" class="status-tag pet">🐱 有宠</span>
                    </div>
                    <div class="quick-actions">
                        <button class="quick-btn" @click="hospital">🏥</button>
                        <button class="quick-btn" @click="psychologist">🧠</button>
                        <button class="quick-btn" @click="lottery">🎰</button>
                        <button class="quick-btn" @click="showDating">💕</button>
                        <button class="quick-btn" @click="buyHouse">🏠</button>
                        <button class="quick-btn" @click="getPet">🐱</button>
                        <button class="quick-btn" @click="travel">✈️</button>
                        <button class="quick-btn" @click="showStock">📈</button>
                        <button class="quick-btn" @click="showJobSearch">💼</button>
                    </div>
                    <div class="next-year-section">
                        <button class="btn btn-primary btn-large" @click="nextYear" :disabled="gameState.isGameOver">
                            {{ gameState.isGameOver ? '游戏结束' : '下一年 ⏭️' }}
                        </button>
                    </div>
                    <div class="timeline-section">
                        <h3>📖 人生履历</h3>
                        <div class="timeline">
                            <div v-for="(item, index) in gameState.timeline.slice(-15)" :key="index" class="timeline-item">
                                <div class="timeline-dot"></div>
                                <div class="timeline-content">
                                    <span class="timeline-age">{{ item.age }}岁</span>
                                    <span class="timeline-event">{{ item.event }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 事件弹窗 -->
            <div v-if="showModal" class="modal active" @click.self="closeModal">
                <div class="modal-content">
                    <div class="event-header">
                        <span class="event-type">{{ modalType }}</span>
                        <h3>{{ modalTitle }}</h3>
                    </div>
                    <p class="event-desc">{{ modalDesc }}</p>
                    <div class="event-choices">
                        <button v-for="(choice, idx) in modalChoices" :key="idx"
                                class="event-choice-btn" @click="handleChoice(idx)">
                            {{ choice.text }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- 游戏结束 -->
            <div v-if="currentScreen === 'summary'" class="screen active">
                <div class="summary-container">
                    <h1>🎮 游戏结束</h1>
                    <div class="summary-card">
                        <p class="summary-name">{{ gameState.name }}</p>
                        <p class="summary-age">享年: {{ gameState.age }}岁</p>
                        <p class="summary-money">总资产: {{ formatMoney(gameState.money) }}</p>
                        <p class="summary-message">{{ summaryMessage }}</p>
                    </div>
                    <button class="btn btn-primary" @click="resetGame">重新开始</button>
                </div>
            </div>
        </div>
        <script src="/static/js/game-vue.js"></script>
    </body>
    </html>
    '''


@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        "backgrounds": BACKGROUNDS, "talents": TALENTS, "personalities": PERSONALITIES,
        "difficulties": DIFFICULTIES, "jobs": JOBS, "educations": EDUCATIONS,
        "achievements": [{"id": a["id"], "name": a["name"], "icon": a["icon"]} for a in ACHIEVEMENTS],
        "properties": PROPERTIES, "spouseTypes": SPOUSE_TYPES
    })


@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.json
    game = GameState()
    game.data["name"] = data.get("name", "玩家")
    game.data["background"] = data.get("background", "1")
    game.data["talent"] = data.get("talent", "1")
    game.data["personality"] = data.get("personality", "1")
    game.data["difficulty"] = data.get("difficulty", "1")
    
    bg = BACKGROUNDS[game.data["background"]]
    game.data["money"] = bg["money"]
    game.data["happiness"] = bg["happiness"]
    game.data["career"] = bg["career"]
    
    session['game'] = game.data
    return jsonify({"success": True, "game": game.to_dict()})


@app.route('/api/load_game', methods=['GET'])
def load_game():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    return jsonify({"success": True, "game": game_data})


@app.route('/api/next_year', methods=['POST'])
def next_year():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    
    game = GameState()
    game.data = game_data
    
    result = game.next_year()
    new_achievements = game.check_achievements()
    
    if game.data["isGameOver"]:
        result = {"type": "game_over", "reason": game.data.get("deathReason", "未知"), "age": game.data["age"]}
    
    session['game'] = game.data
    return jsonify({"success": True, "game": game.to_dict(), "result": result, "newAchievements": new_achievements})


@app.route('/api/handle_key_choice', methods=['POST'])
def handle_key_choice():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    
    data = request.json
    choice_index = data.get("choiceIndex", 0)
    
    game = GameState()
    game.data = game_data
    
    result = game.handle_key_choice(choice_index)
    new_achievements = game.check_achievements()
    
    session['game'] = game.data
    return jsonify({"success": True, "game": game.to_dict(), "result": result, "newAchievements": new_achievements})


@app.route('/api/handle_choice', methods=['POST'])
def handle_choice():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    
    data = request.json
    effect = data.get("effect", {})
    special = data.get("special", "")
    
    game = GameState()
    game.data = game_data
    game.apply_effect(effect)
    
    # 考试处理
    if special == "college_exam":
        talent = TALENTS[game.data["talent"]]
        success_rate = 0.5 + talent["effect"].get("studyBonus", 0)
        success_rate += game.data.get("specialBuffs", {}).get("eduSuccessBonus", 0)
        if random.random() < success_rate:
            game.data["education"] = 1
            game.data["happiness"] = clamp(game.data["happiness"] + 30)
            game.data["timeline"].append({"age": game.data["age"], "event": "🎓 考上大学"})
        else:
            game.data["happiness"] = clamp(game.data["happiness"] - 20)
            game.data["timeline"].append({"age": game.data["age"], "event": "🎓 高考落榜"})
    
    elif special == "find_job":
        jobs_list = [j for j, v in JOBS.items()]
        game.data["job"] = random_choice(jobs_list)
        game.data["happiness"] = clamp(game.data["happiness"] + 15)
        game.data["timeline"].append({"age": game.data["age"], "event": f"💼 成为{game.data['job']}"})
    
    if game.check_death():
        result = {"type": "game_over", "reason": game.data.get("deathReason", "未知")}
    else:
        result = game.check_turning_point() or {"type": "continue"}
    
    new_achievements = game.check_achievements()
    session['game'] = game.data
    return jsonify({"success": True, "game": game.to_dict(), "result": result, "newAchievements": new_achievements})


@app.route('/api/hospital', methods=['POST'])
def hospital():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    if game_data.get("money", 0) < 2000: return jsonify({"success": False, "error": "钱不够"})
    
    game_data["money"] -= 2000
    health_gain = random_int(15, 35)
    game_data["health"] = clamp(game_data["health"] + health_gain)
    session['game'] = game_data
    return jsonify({"success": True, "game": game_data, "message": f"治疗完成，健康+{health_gain}"})


@app.route('/api/psychologist', methods=['POST'])
def psychologist():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    if game_data.get("money", 0) < 1000: return jsonify({"success": False, "error": "钱不够"})
    
    game_data["money"] -= 1000
    happiness_gain = random_int(10, 25)
    game_data["happiness"] = clamp(game_data["happiness"] + happiness_gain)
    session['game'] = game_data
    return jsonify({"success": True, "game": game_data, "message": f"咨询完成，快乐+{happiness_gain}"})


@app.route('/api/lottery', methods=['POST'])
def lottery():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    if game_data.get("money", 0) < 10: return jsonify({"success": False, "error": "钱不够"})
    
    game_data["money"] -= 10
    rand = random.random()
    if rand < 0.005: prize, msg = 100000, "恭喜中一等奖10万元！"
    elif rand < 0.015: prize, msg = 10000, "恭喜中二等奖1万元！"
    elif rand < 0.05: prize, msg = 1000, "恭喜中三等奖1000元！"
    else: prize, msg = 0, "很遗憾，没有中奖..."
    
    game_data["money"] += prize
    if prize > 0: game_data["events"].append({"type": "lottery_win", "age": game_data["age"]})
    session['game'] = game_data
    return jsonify({"success": True, "game": game_data, "message": msg, "prize": prize})


@app.route('/api/dating', methods=['POST'])
def dating():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    if game_data.get("spouse"): return jsonify({"success": False, "error": "已婚"})
    if game_data.get("money", 0) < 500: return jsonify({"success": False, "error": "钱不够"})
    
    game_data["money"] -= 500
    talent = TALENTS[game_data.get("talent", "1")]
    success_rate = 0.3 + talent["effect"].get("socialBonus", 0)
    
    if random.random() < success_rate:
        names = ["小美", "小红", "小丽", "小芳", "小明", "小张"]
        game_data["spouse"] = random_choice(names)
        game_data["spouseType"] = random_choice(list(SPOUSE_TYPES.keys()))
        game_data["happiness"] = clamp(game_data["happiness"] + 20)
        game_data["timeline"].append({"age": game_data["age"], "event": f"💑 遇到{game_data['spouse']}"})
        message = f"相亲成功！你认识了{game_data['spouse']}！"
        
        if random.random() < 0.4:
            child_names = ["小明", "小红", "小华"]
            game_data["children"].append({"name": random_choice(child_names), "age": 0})
            game_data["happiness"] = clamp(game_data["happiness"] + 10)
            game_data["timeline"].append({"age": game_data["age"], "event": "👶 有了孩子"})
    else:
        message = "没有遇到合适的人..."
    
    session['game'] = game_data
    return jsonify({"success": True, "game": game_data, "message": message})


@app.route('/api/buy_property', methods=['POST'])
def buy_property():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    
    data = request.json
    prop_type = data.get("type", "house")
    prop_key = data.get("key", "small")
    
    prop = PROPERTIES.get(prop_type, {}).get(prop_key, {})
    cost = prop.get("cost", 0)
    
    if game_data.get("money", 0) < cost: return jsonify({"success": False, "error": "钱不够"})
    
    game_data["money"] -= cost
    if prop_type == "house":
        game_data["house"] = True
        game_data["houseType"] = prop_key
        game_data["happiness"] = clamp(game_data["happiness"] + prop.get("happiness", 0))
        game_data["timeline"].append({"age": game_data["age"], "event": f"🏠 买房"})
    elif prop_type == "car":
        game_data["car"] = prop_key
        game_data["happiness"] = clamp(game_data["happiness"] + prop.get("happiness", 0))
        game_data["timeline"].append({"age": game_data["age"], "event": f"🚗 买车"})
    
    session['game'] = game_data
    return jsonify({"success": True, "game": game_data, "message": f"购买成功！"})


@app.route('/api/buy_house', methods=['POST'])
def buy_house():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    if game_data.get("house"): return jsonify({"success": False, "error": "已有房"})
    if game_data.get("money", 0) < 100000: return jsonify({"success": False, "error": "钱不够"})
    
    game_data["money"] -= 100000
    game_data["house"] = True
    game_data["happiness"] = clamp(game_data["happiness"] + 30)
    game_data["timeline"].append({"age": game_data["age"], "event": "🏠 买房"})
    session['game'] = game_data
    return jsonify({"success": True, "game": game_data, "message": "恭喜买房！"})


@app.route('/api/get_pet', methods=['POST'])
def get_pet():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    if game_data.get("pet"): return jsonify({"success": False, "error": "已有宠物"})
    if game_data.get("money", 0) < 3000: return jsonify({"success": False, "error": "钱不够"})
    
    game_data["money"] -= 3000
    game_data["pet"] = True
    game_data["happiness"] = clamp(game_data["happiness"] + 20)
    game_data["timeline"].append({"age": game_data["age"], "event": "🐱 养宠物"})
    session['game'] = game_data
    return jsonify({"success": True, "game": game_data, "message": "你领养了一只可爱的小猫！"})


@app.route('/api/travel', methods=['POST'])
def travel():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    
    options = [
        {"name": "周边游", "cost": 3000, "happiness": 10},
        {"name": "国内游", "cost": 8000, "happiness": 20},
        {"name": "出境游", "cost": 30000, "happiness": 30},
    ]
    
    trip = random_choice(options)
    if game_data.get("money", 0) < trip["cost"]: return jsonify({"success": False, "error": "钱不够"})
    
    game_data["money"] -= trip["cost"]
    game_data["happiness"] = clamp(game_data["happiness"] + trip["happiness"])
    game_data["timeline"].append({"age": game_data["age"], "event": f"✈️ {trip['name']}"})
    session['game'] = game_data
    return jsonify({"success": True, "game": game_data, "message": f"去{trip['name']}玩了一圈，心情愉快！"})


@app.route('/api/stock', methods=['POST'])
def stock():
    game_data = session.get('game')
    if not game_data: return jsonify({"success": False, "error": "没有存档"})
    
    data = request.json
    percent = data.get("percent", 0.2)
    amount = int(game_data.get("money", 0) * percent)
    if amount <= 0: return jsonify({"success": False, "error": "没有足够的资金"})
    
    change = random.uniform(-0.3, 0.5)
    profit = int(amount * change)
    game_data["money"] += profit
    
    if profit > 0: game_data["stocks"] = game_data.get("stocks", 0) + profit
    message = f"股票赚了{format_money(profit)}！" if profit > 0 else f"股票赔了{format_money(-profit)}..."
    game_data["timeline"].append({"age": game_data["age"], "event": f"📈 股票{'盈利' if profit > 0 else '亏损'}"})
    session['game'] = game_data
    return jsonify({"success": True, "game": game_data, "message": message, "profit": profit})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
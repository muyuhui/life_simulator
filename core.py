#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared game rules for the life simulator.

The Flask API, local saves, and any future UI shell should call this module
instead of carrying their own copy of the game mechanics.
"""

from __future__ import annotations

import copy
import random
from typing import Any, Callable

from config import (
    BACKGROUNDS,
    BACKGROUND_TURNING_EVENTS,
    CHARACTER_NAMES,
    DAILY_EVENTS,
    DIFFICULTIES,
    EVENT_CARDS,
    PERSONALITIES,
    PERSONALITY_TRAITS,
    STORY_FLAGS,
    TALENTS,
    TURNING_COSTS,
    TURNING_POINT_EVENTS,
    clamp,
    format_money,
)


SCHEMA_VERSION = 1

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

EDUCATIONS = {
    0: {"name": "高中", "baseIncome": 100},
    1: {"name": "本科", "baseIncome": 200},
    2: {"name": "硕士", "baseIncome": 350},
    3: {"name": "博士", "baseIncome": 500},
}

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

SPOUSE_TYPES = {
    "frugal": {"name": "节俭型", "buff": "节省10%开支"},
    "optimistic": {"name": "乐观型", "buff": "快乐衰减-10%"},
    "career": {"name": "事业型", "buff": "事业成长+2%"},
    "family": {"name": "顾家型", "buff": "健康衰减-10%"},
}


def _achievement(id_: str, name: str, icon: str, condition: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    return {"id": id_, "name": name, "icon": icon, "condition": condition}


ACHIEVEMENTS = [
    _achievement("millionaire", "百万富翁", "💵", lambda s: s.get("money", 0) >= 1000000),
    _achievement("centenarian", "百岁老人", "🎂", lambda s: s.get("age", 0) >= 100),
    _achievement(
        "winner",
        "人生赢家",
        "🏆",
        lambda s: s.get("money", 0) >= 100000 and s.get("happiness", 0) >= 80 and s.get("career", 0) >= 80,
    ),
    _achievement("survivor", "绝境逢生", "🌟", lambda s: s.get("turningPoints", 0) >= 5),
    _achievement("married", "结婚", "💑", lambda s: s.get("spouse") is not None),
    _achievement("family", "儿女成群", "👨‍👩‍👧‍👦", lambda s: len(s.get("children", [])) >= 3),
    _achievement("homeowner", "有房一族", "🏠", lambda s: bool(s.get("house"))),
    _achievement("petOwner", "铲屎官", "🐱", lambda s: bool(s.get("pet"))),
    _achievement("comeback", "否极泰来", "🌈", lambda s: "逆袭者" in s.get("lifeLabels", [])),
    _achievement("carOwner", "有车一族", "🚗", lambda s: bool(s.get("car")) and s.get("car") != "none"),
]


def public_achievements() -> list[dict[str, str]]:
    return [{"id": a["id"], "name": a["name"], "icon": a["icon"]} for a in ACHIEVEMENTS]


def public_config() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "backgrounds": BACKGROUNDS,
        "talents": TALENTS,
        "personalities": PERSONALITIES,
        "difficulties": DIFFICULTIES,
        "jobs": JOBS,
        "educations": EDUCATIONS,
        "achievements": public_achievements(),
        "properties": PROPERTIES,
        "spouseTypes": SPOUSE_TYPES,
    }


class GameState:
    """A versioned, serializable game state."""

    def __init__(self, data: dict[str, Any] | None = None):
        self.data = self.default_data()
        if data:
            self.data.update(copy.deepcopy(data))
        self.normalize()

    @classmethod
    def new(
        cls,
        name: str = "玩家",
        background: str = "1",
        talent: str = "1",
        personality: str = "1",
        difficulty: str = "1",
    ) -> "GameState":
        game = cls()
        game.data.update(
            {
                "name": name.strip() or "玩家",
                "background": background if background in BACKGROUNDS else "1",
                "talent": talent if talent in TALENTS else "1",
                "personality": personality if personality in PERSONALITIES else "1",
                "difficulty": difficulty if difficulty in DIFFICULTIES else "1",
            }
        )
        bg = BACKGROUNDS[game.data["background"]]
        game.data["money"] = bg["money"]
        game.data["happiness"] = bg["happiness"]
        game.data["career"] = bg["career"]
        game.data["relationships"] = [
            {"id": "father", "name": random.choice(CHARACTER_NAMES["family"][:3]),
             "role": "parent", "personality": random.choice(["pragmatic", "kind", "cold"]),
             "affection": 70, "history": [], "first_met_age": 0, "status": "alive", "age": 45 + random.randint(0, 5)},
            {"id": "mother", "name": random.choice(CHARACTER_NAMES["family"][3:]),
             "role": "parent", "personality": random.choice(["warm", "kind", "pragmatic"]),
             "affection": 70, "history": [], "first_met_age": 0, "status": "alive", "age": 43 + random.randint(0, 3)},
        ]
        game.normalize()
        return game

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "GameState":
        return cls(data or {})

    @staticmethod
    def default_data() -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "name": "",
            "age": 18,
            "background": "1",
            "talent": "1",
            "personality": "1",
            "difficulty": "1",
            "money": 5000,
            "health": 80,
            "happiness": 70,
            "career": 20,
            "education": 0,
            "job": None,
            "year": 1,
            "isGameOver": False,
            "isDead": False,
            "deathReason": "",
            "achievements": [],
            "events": [],
            "timeline": [{"age": 18, "event": "开启人生旅程"}],
            "spouse": None,
            "spouseType": None,
            "children": [],
            "house": False,
            "houseType": "none",
            "car": "none",
            "pet": False,
            "countries": [],
            "turningPoints": 0,
            "consecutiveTurning": 0,
            "lifeLabels": [],
            "debt": 0,
            "keyChoices": {"age18": None, "age22": None, "age25": None, "age28": None, "age35": None, "age50": None},
            "specialBuffs": {},
            "stocks": 0,
            "storyFlags": [],
            "relationships": [],
            "pendingEvent": None,
            "triggeredEvents": [],
        }

    def normalize(self) -> None:
        defaults = self.default_data()
        for key, value in defaults.items():
            if key not in self.data or self.data[key] is None and isinstance(value, (list, dict)):
                self.data[key] = copy.deepcopy(value)
        if not isinstance(self.data.get("storyFlags"), list):
            self.data["storyFlags"] = list(self.data.get("storyFlags", []))
        if not isinstance(self.data.get("relationships"), list):
            self.data["relationships"] = []
        if not isinstance(self.data.get("triggeredEvents"), list):
            self.data["triggeredEvents"] = []
        self.data["schemaVersion"] = SCHEMA_VERSION
        self.data["background"] = str(self.data.get("background", "1"))
        self.data["talent"] = str(self.data.get("talent", "1"))
        self.data["personality"] = str(self.data.get("personality", "1"))
        self.data["difficulty"] = str(self.data.get("difficulty", "1"))
        if self.data["background"] not in BACKGROUNDS:
            self.data["background"] = "1"
        if self.data["talent"] not in TALENTS:
            self.data["talent"] = "1"
        if self.data["personality"] not in PERSONALITIES:
            self.data["personality"] = "1"
        if self.data["difficulty"] not in DIFFICULTIES:
            self.data["difficulty"] = "1"
        self.data["education"] = int(self.data.get("education", 0) or 0)
        self.data["education"] = max(0, min(3, self.data["education"]))
        self.data["health"] = clamp(self.data.get("health", 80))
        self.data["happiness"] = clamp(self.data.get("happiness", 70))
        self.data["career"] = clamp(self.data.get("career", 20))

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return copy.deepcopy(self.data)

    def apply_effect(self, effect: dict[str, Any] | None) -> None:
        effect = effect or {}
        if "money" in effect:
            self.data["money"] += int(effect["money"])
        if "health" in effect:
            self.data["health"] = clamp(self.data["health"] + effect["health"])
        if "happiness" in effect:
            self.data["happiness"] = clamp(self.data["happiness"] + effect["happiness"])
        if "career" in effect:
            self.data["career"] = clamp(self.data["career"] + effect["career"])
        if effect.get("house"):
            self.data["house"] = True
        if effect.get("pet"):
            self.data["pet"] = True

    def add_timeline(self, event: str) -> None:
        self.data.setdefault("timeline", []).append({"age": self.data["age"], "event": event})

    def check_death(self) -> bool:
        if self.data["health"] > 0:
            return False
        if random.random() < 0.1:
            self.data["isDead"] = True
            self.data["deathReason"] = "因病去世"
            self.data["isGameOver"] = True
            return True
        self.trigger_turning_point()
        return False

    def check_turning_point(self) -> dict[str, Any] | None:
        diff = DIFFICULTIES[self.data["difficulty"]]
        crisis = self.data["health"] < 20 or self.data["money"] < -50000 or self.data["happiness"] < 10
        if not crisis or random.random() >= diff["turningRate"] * 0.3:
            self.data["consecutiveTurning"] = 0
            return None

        self.data["turningPoints"] += 1
        self.data["consecutiveTurning"] += 1

        if self.data["consecutiveTurning"] >= 2 and random.random() < 0.1:
            effects = {"money": 100000, "health": 50, "happiness": 50, "career": 30}
            self.apply_effect(effects)
            self.data["lifeLabels"].append("逆袭者")
            self.data["consecutiveTurning"] = 0
            self.add_timeline("🌈 人生逆袭")
            return {"type": "turning", "title": "人生逆袭！", "desc": "连续绝境触发超级转机。", "effects": effects}

        bg = self.data["background"]
        if bg in BACKGROUND_TURNING_EVENTS and random.random() < 0.8:
            event = random.choice(BACKGROUND_TURNING_EVENTS[bg])
            self.apply_effect(event["effect"])
            self.data["consecutiveTurning"] = 0
            self.add_timeline(f"🌟 {event['title']}")
            return {"type": "turning", "title": event["title"], "desc": event.get("desc", ""), "effects": event["effect"]}

        for cost_data in TURNING_COSTS.values():
            if "condition" not in cost_data or cost_data["condition"](self.data):
                if random.random() < cost_data.get("chance", 0.3):
                    self.apply_effect(cost_data["effect"])
                    self.data["consecutiveTurning"] = 0
                    self.add_timeline("🌟 转折")
                    return {"type": "turning", "title": cost_data.get("desc", "度过难关"), "effects": cost_data["effect"]}

        return self.trigger_turning_point()

    def trigger_turning_point(self) -> dict[str, Any]:
        event = random.choice(TURNING_POINT_EVENTS)
        effect = event.get("effect") or event.get("result") or {}
        self.apply_effect(effect)
        self.data["turningPoints"] += 1
        self.data["consecutiveTurning"] = 0
        self.add_timeline(f"🌟 {event['title']}")
        return {"type": "turning", "title": event["title"], "desc": event.get("desc", ""), "effects": effect}

    def _handle_special(self, special: str) -> None:
        special_buffs = self.data.setdefault("specialBuffs", {})
        talent = TALENTS[self.data["talent"]]
        study_bonus = talent["effect"].get("studyBonus", 0)
        gap_bonus = special_buffs.get("socialBonus", 0)

        if special in {"gaokao", "college_exam"}:
            if random.random() < 0.5 + study_bonus + special_buffs.get("eduSuccessBonus", 0):
                self.data["education"] = max(self.data["education"], 1)
                self.apply_effect({"happiness": 30})
                self.add_timeline("🎓 考上大学！")
            else:
                self.apply_effect({"happiness": -20})
                self.add_timeline("🎓 高考落榜...")
        elif special == "work_no_edu":
            special_buffs["eduLocked"] = True
            self.add_timeline("💼 直接工作")
            self.find_new_job()
        elif special == "kaoyan":
            if random.random() < 0.4 + study_bonus + gap_bonus:
                self.data["education"] = max(self.data["education"], 2)
                self.apply_effect({"happiness": 30})
                self.add_timeline("🎓 考上研究生！")
            else:
                self.apply_effect({"happiness": -15})
                self.add_timeline("🎓 考研落榜...")
        elif special == "kaobo":
            if random.random() < 0.3 + study_bonus + gap_bonus:
                self.data["education"] = 3
                self.apply_effect({"happiness": 30})
                self.add_timeline("🎓 考上博士！")
            else:
                self.apply_effect({"happiness": -15})
                self.add_timeline("🎓 考博落榜...")
        elif special == "find_job":
            self.find_new_job()
        elif special == "gap_year":
            special_buffs["socialBonus"] = 0.15
        elif special == "career_stay":
            special_buffs["careerGrowth"] = 0.02
        elif special == "startup":
            special_buffs["entrepreneurBonus"] = 0.10
        elif special == "early_retire":
            special_buffs["earlyRetire"] = True
        elif special == "keep_working":
            special_buffs["elderGrowth"] = 0.04
        elif special == "mentor":
            special_buffs["mentorBuff"] = 0.03

    def find_new_job(self) -> str:
        self.data["job"] = random.choice(list(JOBS.keys()))
        self.apply_effect({"happiness": 15})
        self.add_timeline(f"💼 成为{self.data['job']}")
        return self.data["job"]

    def next_year(self) -> dict[str, Any]:
        if self.data["isGameOver"]:
            return {"type": "game_over", "reason": self.data.get("deathReason", "游戏已结束"), "age": self.data["age"]}

        self.data["year"] += 1
        self.data["age"] += 1

        health_change = -random.randint(2, 8)
        happiness_change = -random.randint(2, 8)
        if self.data["personality"] == "3":
            happiness_change *= 0.7
        if self.data["talent"] == "4":
            health_change *= 0.5
        if self.data["pet"]:
            happiness_change += 5
        if self.data["house"]:
            happiness_change += 5
        if self.data.get("specialBuffs", {}).get("earlyRetire"):
            happiness_change *= 0.5
            health_change *= 0.7

        self.data["health"] = clamp(self.data["health"] + health_change)
        self.data["happiness"] = clamp(self.data["happiness"] + happiness_change)

        career_change = random.randint(-2, 5)
        if self.data["personality"] == "4":
            career_change *= 1.2
        if self.data.get("specialBuffs", {}).get("careerGrowth"):
            career_change *= 1.02
        if self.data.get("specialBuffs", {}).get("elderGrowth"):
            career_change += 4
        self.data["career"] = clamp(self.data["career"] + career_change)

        income = EDUCATIONS[self.data["education"]]["baseIncome"] * (1 + self.data["career"] / 100)
        if self.data["job"] in JOBS:
            job_data = JOBS[self.data["job"]]
            income = job_data["income"] * (1 + self.data["career"] / 100)
            if random.random() < job_data["growth"]:
                self.data["career"] = clamp(self.data["career"] + 5)
            if random.random() < job_data["risk"] * 0.1:
                self.data["job"] = None
                self.add_timeline("💸 失业")
        if self.data["talent"] == "3":
            income *= 1.3
        if self.data.get("specialBuffs", {}).get("earlyRetire"):
            income *= 0.5

        self.data["money"] += int(income)
        if self.data["spouse"]:
            self.data["money"] -= 3000
            self.apply_effect({"happiness": 5})
        self.data["money"] -= 2000 * len(self.data["children"])
        self.add_timeline(f"年收入 {format_money(int(income))}")

        if self.check_death():
            return {"type": "game_over", "reason": self.data["deathReason"], "age": self.data["age"]}

        for child in self.data["children"]:
            child["age"] = child.get("age", 0) + 1

        # 检查危机转机（保留原有逻辑，但输出统一为 event_card）
        diff = DIFFICULTIES[self.data["difficulty"]]
        crisis = self.data["health"] < 20 or self.data["money"] < -50000 or self.data["happiness"] < 10
        if crisis and random.random() < diff["turningRate"] * 0.3:
            turning_result = self.check_turning_point()
            if turning_result:
                return turning_result

        # 叙事事件引擎
        event_card = self.select_event()
        if event_card:
            card = copy.deepcopy(event_card)
            card["flavor"] = self.interpolate_flavor(card.get("flavor", ""))
            for ch in card.get("choices", []):
                if ch.get("flavor"):
                    ch["flavor"] = self.interpolate_flavor(ch["flavor"])
            return {"type": "event_card", "card": card, "is_daily": event_card.get("id", "").startswith("daily_")}

        return {"type": "normal", "message": f"年龄: {self.data['age']}"}

    # ── 叙事引擎 ──

    def match_conditions(self, conditions: dict[str, Any] | None) -> bool:
        """检查当前游戏状态是否满足事件卡的条件。"""
        if not conditions:
            return True
        data = self.data
        flags = set(data.get("storyFlags", []))
        age = data["age"]

        if "age" in conditions:
            lo, hi = conditions["age"]
            if not (lo <= age <= hi):
                return False
        if "has_job" in conditions and conditions["has_job"] is not None:
            if bool(data.get("job")) != conditions["has_job"]:
                return False
        if "has_spouse" in conditions and conditions["has_spouse"] is not None:
            if bool(data.get("spouse")) != conditions["has_spouse"]:
                return False
        if "has_children" in conditions and conditions["has_children"] is not None:
            if bool(data.get("children")) != conditions["has_children"]:
                return False
        for stat in ("health", "happiness", "career", "money", "education"):
            rng = conditions.get(stat)
            if rng is not None:
                val = data.get(stat, 0)
                if not (rng[0] <= val <= rng[1]):
                    return False
        if "flags_any" in conditions:
            if not any(f in flags for f in conditions["flags_any"]):
                return False
        if "flags_all" in conditions:
            if not all(f in flags for f in conditions["flags_all"]):
                return False
        if "flags_none" in conditions:
            if any(f in flags for f in conditions["flags_none"]):
                return False
        return True

    def interpolate_flavor(self, text: str) -> str:
        """将 flavor 文本中的模板变量替换为实际数据。"""
        data = self.data
        rels = {r["id"]: r for r in data.get("relationships", [])}
        spouse_rel = next((r for r in rels.values() if r["role"] == "spouse"), None)
        friend_rel = next((r for r in rels.values() if r["role"] in ("friend", "mentor")), None)
        vars_map = {
            "spouse_name": spouse_rel["name"] if spouse_rel else (data.get("spouse") or "伴侣"),
            "friend_name": friend_rel["name"] if friend_rel else "朋友",
            "job": data.get("job") or "待业",
            "money": format_money(data.get("money", 0)),
            "age": str(data["age"]),
            "name": data.get("name", "你"),
            "education": {0: "高中", 1: "本科", 2: "硕士", 3: "博士"}.get(data.get("education", 0), "高中"),
        }
        result = text
        for key, val in vars_map.items():
            result = result.replace("{" + key + "}", str(val))
        return result

    def select_event(self) -> dict[str, Any] | None:
        """选择本年应触发的事件卡。按优先级：pending > 关键年龄 > 高优先级 > 通用 > 日常。"""
        data = self.data
        triggered = set(data.get("triggeredEvents", []))

        # 1. pending 连锁事件
        pending_id = data.get("pendingEvent")
        if pending_id:
            card = next((c for c in EVENT_CARDS if c["id"] == pending_id), None)
            if card and self.match_conditions(card.get("conditions")) and (card.get("repeatable") or card["id"] not in triggered):
                data["pendingEvent"] = None
                data.setdefault("triggeredEvents", []).append(card["id"])
                return card
            data["pendingEvent"] = None

        # 2. 收集所有符合条件的卡片
        candidates = []
        for card in EVENT_CARDS:
            if not self.match_conditions(card.get("conditions")):
                continue
            if not card.get("repeatable") and card["id"] in triggered:
                continue
            candidates.append(card)

        # 3. 按优先级排序 + 加权随机
        if candidates:
            # 优先取最高优先级的事件
            max_pri = max(c["priority"] for c in candidates)
            top = [c for c in candidates if c["priority"] == max_pri]
            choice = random.choice(top)
            data.setdefault("triggeredEvents", []).append(choice["id"])
            return choice

        # 4. 回退到日常小事（按类别加权随机）
        DAILY_WEIGHTS = {"social": 25, "work": 20, "family": 20, "health": 15, "happy": 10, "sad": 5, "random": 5}
        daily_candidates = [d for d in DAILY_EVENTS if self.match_conditions(d.get("conditions"))]
        if not daily_candidates:
            daily_candidates = [d for d in DAILY_EVENTS if "conditions" not in d or not d["conditions"]]
        if daily_candidates:
            weights = [DAILY_WEIGHTS.get(d["category"], 10) for d in daily_candidates]
            total = sum(weights)
            r = random.uniform(0, total)
            accum = 0
            for d, w in zip(daily_candidates, weights):
                accum += w
                if r <= accum:
                    return d
            return daily_candidates[-1]

        return None

    def resolve_event_choice(self, card: dict[str, Any], choice_index: int) -> dict[str, Any]:
        """处理玩家在事件卡上的选择。返回结果描述。"""
        choices = card.get("choices", [])
        if choice_index < 0 or choice_index >= len(choices):
            raise ValueError("选择不存在")
        choice = choices[choice_index]

        # 应用数值效果
        effects = choice.get("effects", {})
        self.apply_effect(effects)

        # 应用 storyFlags
        data = self.data
        flags = set(data.get("storyFlags", []))
        for f in choice.get("flags_set", []) or []:
            flags.add(f)
        for f in choice.get("flags_clear", []) or []:
            flags.discard(f)
        data["storyFlags"] = list(flags)

        # 应用关系变化
        changes = choice.get("relationship_changes", {}) or {}
        for char_id, delta in changes.items():
            for rel in data.get("relationships", []):
                if rel["id"] == char_id:
                    rel["affection"] = max(-100, min(100, rel["affection"] + delta))
                    rel.setdefault("history", []).append({"age": data["age"], "summary": card.get("title", "")})
                    break
            else:
                # 新角色自动创建
                self._create_character_from_event(char_id, delta)

        # 处理特殊逻辑
        special = choice.get("special")
        if special:
            self._handle_special(special)

        # 处理 follow_up
        follow_up = choice.get("follow_up")
        if follow_up:
            data["pendingEvent"] = follow_up
        else:
            data["pendingEvent"] = None

        # 处理自动 dating（特殊：事件中的相亲）
        if special == "dating" and not data.get("spouse"):
            names = ["小美", "小红", "小丽", "小芳"]
            data["spouse"] = random.choice(names)
            data["spouseType"] = random.choice(list(SPOUSE_TYPES.keys()))
            self.apply_effect({"happiness": 20})
            self.add_timeline(f"💑 遇到{data['spouse']}")
            # 创建配偶关系
            spouse_name = data["spouse"]
            data.setdefault("relationships", []).append({
                "id": "spouse", "name": spouse_name, "role": "spouse",
                "personality": random.choice(list(PERSONALITY_TRAITS.keys())),
                "affection": 60, "history": [{"age": data["age"], "summary": f"初次相遇"}],
                "first_met_age": data["age"], "status": "alive", "age": data["age"]
            })

        # 自动 find_job
        if special == "find_job" or special == "work_no_edu":
            self.find_new_job()

        self.add_timeline(f"🎯 {choice['text']}")
        return {
            "type": "choice_result",
            "title": choice.get("text", ""),
            "effects": effects,
            "relationship_changes": changes,
            "flags_set": choice.get("flags_set", []),
        }

    def _create_character_from_event(self, char_id: str, affection: int) -> None:
        """根据事件需要自动创建一个关系角色。"""
        name_pool = CHARACTER_NAMES["male"] + CHARACTER_NAMES["female"]
        name = random.choice([n for n in name_pool if n not in [
            r["name"] for r in self.data.get("relationships", [])
        ]] or name_pool)
        self.data.setdefault("relationships", []).append({
            "id": char_id, "name": name, "role": "friend",
            "personality": random.choice(list(PERSONALITY_TRAITS.keys())),
            "affection": max(0, affection),
            "history": [{"age": self.data["age"], "summary": "初次相遇"}],
            "first_met_age": self.data["age"], "status": "alive", "age": self.data["age"]
        })

    def generate_ending(self) -> str:
        """根据 storyFlags 组合生成个性化人生总结。"""
        flags = set(self.data.get("storyFlags", []))
        parts = []

        if "went_to_college" in flags or "went_to_grad_school" in flags:
            parts.append("你受过良好的教育")
        elif "no_higher_edu" in flags:
            parts.append("你没有耀眼的学历，但社会是最好的大学")

        if "started_business" in flags and "took_big_risk" in flags:
            parts.append("创业的路上你赌过、输过、也赢过")
        elif "loyal_employee" in flags and "played_safe" in flags:
            parts.append("几十年如一日的踏实，为家人撑起了一片天")
        elif "changed_career" in flags:
            parts.append("你敢于在人生中途换赛道")

        if "divorced" in flags and "chose_love" in flags:
            parts.append("在爱情里受过伤，但从未因此变得冷漠")
        elif "married_early" in flags and "chose_love" in flags:
            parts.append("早早遇到了对的人，是幸运的")
        elif "never_married" in flags:
            parts.append("一个人也活出了完整的风景")

        if "has_children" in flags and "chose_love" in flags:
            parts.append("你把最好的爱给了下一代")
        elif "childfree" in flags:
            parts.append("两个人的世界也足够丰富")

        if "helped_friend" in flags or "helped_stranger" in flags:
            parts.append("有人记得你伸出的手")
        if "betrayed_friend" in flags:
            parts.append("有些遗憾，但这就是人生")

        if "won_lottery" in flags:
            parts.append("命运给过你意外的惊喜")
        if "got_scammed" in flags:
            parts.append("你也交过生活的学费")
        if "near_death" in flags:
            parts.append("走过生死边缘，更懂珍惜")

        if "comeback_king" in flags:
            parts.append("你是真正的逆袭者")

        if not parts:
            parts.append("平凡而真实的人生，也有它自己的重量")

        parts.append(f"享年{self.data['age']}岁。")
        return "。".join(parts)

    def check_achievements(self) -> list[dict[str, str]]:
        new = []
        for achievement in ACHIEVEMENTS:
            if achievement["id"] not in self.data["achievements"] and achievement["condition"](self.data):
                self.data["achievements"].append(achievement["id"])
                new.append({"id": achievement["id"], "name": achievement["name"], "icon": achievement["icon"]})
        return new

    def handle_choice(self, effect: dict[str, Any] | None = None, special: str = "") -> dict[str, Any]:
        self.apply_effect(effect)
        if special:
            self._handle_special(special)
        if self.check_death():
            return {"type": "game_over", "reason": self.data.get("deathReason", "未知"), "age": self.data["age"]}
        return self.check_turning_point() or {"type": "continue"}

    def apply_action(self, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        actions = {
            "hospital": self._action_hospital,
            "psychologist": self._action_psychologist,
            "lottery": self._action_lottery,
            "dating": self._action_dating,
            "buy_property": self._action_buy_property,
            "buy_house": lambda _: self._action_buy_property({"type": "house", "key": "small", "legacyCost": 100000}),
            "get_pet": self._action_get_pet,
            "travel": self._action_travel,
            "stock": self._action_stock,
            "find_job": self._action_find_job,
        }
        if action not in actions:
            raise ValueError("未知操作")
        return actions[action](payload)

    def _ensure_money(self, cost: int) -> None:
        if self.data.get("money", 0) < cost:
            raise ValueError("钱不够")

    def _action_hospital(self, _: dict[str, Any]) -> dict[str, Any]:
        self._ensure_money(2000)
        gain = random.randint(15, 35)
        self.data["money"] -= 2000
        self.apply_effect({"health": gain})
        self.add_timeline("🏥 去医院治疗")
        return {"type": "action", "message": f"治疗完成，健康 +{gain}"}

    def _action_psychologist(self, _: dict[str, Any]) -> dict[str, Any]:
        self._ensure_money(1000)
        gain = random.randint(10, 25)
        self.data["money"] -= 1000
        self.apply_effect({"happiness": gain})
        self.add_timeline("🧠 看心理医生")
        return {"type": "action", "message": f"咨询完成，快乐 +{gain}"}

    def _action_lottery(self, _: dict[str, Any]) -> dict[str, Any]:
        self._ensure_money(10)
        self.data["money"] -= 10
        rand = random.random()
        if rand < 0.005:
            prize, message = 100000, "恭喜中一等奖10万元！"
        elif rand < 0.015:
            prize, message = 10000, "恭喜中二等奖1万元！"
        elif rand < 0.05:
            prize, message = 1000, "恭喜中三等奖1000元！"
        else:
            prize, message = 0, "很遗憾，没有中奖..."
        self.data["money"] += prize
        self.add_timeline(f"🎰 购买彩票 {'中奖 ' + format_money(prize) if prize else '未中奖'}")
        if prize:
            self.data.setdefault("events", []).append({"type": "lottery_win", "age": self.data["age"]})
        return {"type": "action", "message": message, "prize": prize}

    def _action_dating(self, _: dict[str, Any]) -> dict[str, Any]:
        if self.data.get("spouse"):
            raise ValueError("已经结婚")
        self._ensure_money(500)
        self.data["money"] -= 500
        success_rate = 0.3 + TALENTS[self.data["talent"]]["effect"].get("socialBonus", 0)
        if random.random() >= success_rate:
            return {"type": "action", "message": "没有遇到合适的人..."}
        names = ["小美", "小红", "小丽", "小芳", "小明", "小张"]
        self.data["spouse"] = random.choice(names)
        self.data["spouseType"] = random.choice(list(SPOUSE_TYPES.keys()))
        self.apply_effect({"happiness": 20})
        self.add_timeline(f"💑 遇到{self.data['spouse']}")
        message = f"相亲成功！你认识了{self.data['spouse']}。"
        if random.random() < 0.4:
            child_names = ["小明", "小红", "小华"]
            self.data["children"].append({"name": random.choice(child_names), "age": 0})
            self.apply_effect({"happiness": 10})
            self.add_timeline("👶 有了孩子")
        return {"type": "action", "message": message}

    def _action_buy_property(self, payload: dict[str, Any]) -> dict[str, Any]:
        prop_type = payload.get("type", "house")
        prop_key = payload.get("key", "small")
        prop = PROPERTIES.get(prop_type, {}).get(prop_key)
        if not prop:
            raise ValueError("资产不存在")
        cost = int(payload.get("legacyCost") or prop.get("cost", 0))
        self._ensure_money(cost)
        if prop_type == "house" and self.data.get("house"):
            raise ValueError("已经有房")
        self.data["money"] -= cost
        self.apply_effect({"happiness": prop.get("happiness", 0)})
        if prop_type == "house":
            self.data["house"] = True
            self.data["houseType"] = prop_key
            self.add_timeline("🏠 买房")
        elif prop_type == "car":
            self.data["car"] = prop_key
            self.add_timeline("🚗 买车")
        return {"type": "action", "message": f"购买{prop['name']}成功！"}

    def _action_get_pet(self, _: dict[str, Any]) -> dict[str, Any]:
        if self.data.get("pet"):
            raise ValueError("已有宠物")
        self._ensure_money(3000)
        self.data["money"] -= 3000
        self.data["pet"] = True
        self.apply_effect({"happiness": 20})
        self.add_timeline("🐱 养宠物")
        return {"type": "action", "message": "你领养了一只可爱的宠物！"}

    def _action_travel(self, _: dict[str, Any]) -> dict[str, Any]:
        options = [
            {"name": "周边游", "cost": 3000, "happiness": 10},
            {"name": "国内游", "cost": 8000, "happiness": 20},
            {"name": "出境游", "cost": 30000, "happiness": 30},
        ]
        affordable = [trip for trip in options if self.data.get("money", 0) >= trip["cost"]]
        if not affordable:
            raise ValueError("钱不够")
        trip = random.choice(affordable)
        self.data["money"] -= trip["cost"]
        self.apply_effect({"happiness": trip["happiness"]})
        self.add_timeline(f"✈️ {trip['name']}")
        return {"type": "action", "message": f"去了{trip['name']}，心情愉快！"}

    def _action_stock(self, payload: dict[str, Any]) -> dict[str, Any]:
        percent = float(payload.get("percent", 0.2))
        percent = max(0.01, min(1, percent))
        amount = int(self.data.get("money", 0) * percent)
        if amount <= 0:
            raise ValueError("没有足够的资金")
        change = random.uniform(-0.3, 0.5)
        profit = int(amount * change)
        self.data["money"] += profit
        if profit > 0:
            self.data["stocks"] = self.data.get("stocks", 0) + profit
        self.add_timeline(f"📈 股票{'盈利' if profit > 0 else '亏损'}")
        message = f"股票赚了{format_money(profit)}！" if profit > 0 else f"股票亏了{format_money(-profit)}..."
        return {"type": "action", "message": message, "profit": profit}

    def _action_find_job(self, _: dict[str, Any]) -> dict[str, Any]:
        job = self.find_new_job()
        return {"type": "action", "message": f"找到工作：{job}", "job": job}

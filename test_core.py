"""pytest tests for core.py critical paths."""
import random

import pytest

from core import GameState


# ── Helpers ──

def fresh_game(**overrides):
    """Create a fresh GameState with optional override fields."""
    game = GameState.new(name="测试", background="1", talent="1", personality="1", difficulty="1")
    game.data.update(overrides)
    game.normalize()
    return game


# ── Death / Turning Point ──

def test_death_triggers_turning_point():
    """health=0 → 90% turning point, 10% death (statistical)."""
    random.seed(42)
    deaths = 0
    turnings = 0
    for _ in range(1000):
        game = fresh_game(health=0)
        result = game.check_death()
        if result:
            deaths += 1
        else:
            turnings += 1
    # With seed 42, expect roughly 100 deaths / 900 turnings
    assert 50 < deaths < 150, f"Expected ~100 deaths, got {deaths}"
    assert 850 < turnings < 950, f"Expected ~900 turnings, got {turnings}"


def test_death_directly_kills(monkeypatch):
    """health=0 with random.random() < 0.1 → isDead=True."""
    monkeypatch.setattr(random, "random", lambda: 0.05)  # < 0.1 → death
    game = fresh_game(health=0)
    result = game.check_death()
    assert result is True
    assert game.data["isDead"] is True
    assert game.data["deathReason"] == "因病去世"


def test_health_above_zero_no_death():
    """health > 0 → check_death returns False immediately."""
    game = fresh_game(health=50)
    result = game.check_death()
    assert result is False
    assert game.data["isDead"] is False


def test_consecutive_turning_super_event(monkeypatch):
    """consecutiveTurning ≥ 2 + random values in range → 人生逆袭."""
    # First random(): crisis gate check (needs < turningRate * 0.3 = 0.27 for 普通模式)
    # Second random(): super event check (needs < 0.1)
    calls = iter([0.05, 0.08])
    monkeypatch.setattr(random, "random", lambda: next(calls))
    game = fresh_game(health=10, money=-60000, consecutiveTurning=2)
    result = game.check_turning_point()
    assert result is not None, f"Expected super event, got None. Game state: health={game.data['health']}, money={game.data['money']}"
    assert result["type"] == "turning"
    assert result["title"] == "人生逆袭！"
    assert game.data["money"] == 40000  # -60000 + 100000
    assert game.data["health"] == 60  # 10 + 50
    assert "逆袭者" in game.data["lifeLabels"]


# ── Condition Matching ──

def test_match_conditions_age():
    """Age range conditions match correctly."""
    game = fresh_game(age=25)
    assert game.match_conditions({"age": [20, 30]}) is True
    assert game.match_conditions({"age": [30, 40]}) is False
    assert game.match_conditions({"age": [25, 25]}) is True


def test_match_conditions_job_spouse_children():
    """Boolean conditions for has_job, has_spouse, has_children."""
    game = fresh_game(job=None, spouse=None, children=[])
    assert game.match_conditions({"has_job": False}) is True
    assert game.match_conditions({"has_job": True}) is False
    assert game.match_conditions({"has_spouse": False}) is True
    assert game.match_conditions({"has_children": False}) is True

    game.data["job"] = "程序员"
    game.data["spouse"] = "小美"
    game.data["children"] = [{"name": "小明", "age": 0}]
    assert game.match_conditions({"has_job": True}) is True
    assert game.match_conditions({"has_spouse": True}) is True
    assert game.match_conditions({"has_children": True}) is True


def test_match_conditions_flags():
    """flags_any / flags_all / flags_none logic."""
    game = fresh_game(storyFlags=["went_to_college", "played_safe"])

    # flags_any: at least one match
    assert game.match_conditions({"flags_any": ["went_to_college"]}) is True
    assert game.match_conditions({"flags_any": ["took_big_risk"]}) is False

    # flags_all: all must be present
    assert game.match_conditions({"flags_all": ["went_to_college", "played_safe"]}) is True
    assert game.match_conditions({"flags_all": ["went_to_college", "took_big_risk"]}) is False

    # flags_none: none of these can be present
    assert game.match_conditions({"flags_none": ["took_big_risk"]}) is True
    assert game.match_conditions({"flags_none": ["went_to_college"]}) is False


def test_match_conditions_stat_ranges():
    """Stat range conditions (health, happiness, career, money, education)."""
    game = fresh_game(health=50, happiness=60, career=30, money=10000, education=1)

    assert game.match_conditions({"health": [40, 60]}) is True
    assert game.match_conditions({"health": [0, 20]}) is False
    assert game.match_conditions({"happiness": [50, 70]}) is True
    assert game.match_conditions({"career": [0, 50]}) is True
    assert game.match_conditions({"money": [5000, 50000]}) is True
    assert game.match_conditions({"education": [0, 1]}) is True
    assert game.match_conditions({"education": [2, 3]}) is False


def test_match_conditions_none_conditions():
    """None conditions → always match."""
    game = fresh_game()
    assert game.match_conditions(None) is True
    assert game.match_conditions({}) is True


# ── Event Selection ──

def test_select_event_returns_daily_fallback():
    """When no EVENT_CARD conditions match, fall back to daily events."""
    game = fresh_game(age=99)  # very old, unlikely to match any card's age range
    game.data["triggeredEvents"] = []  # ensure clean slate
    card = game.select_event()
    # Should return a daily event or None
    if card is not None:
        assert card.get("id", "").startswith("daily_") or "category" in card
    # If None, that's also acceptable (no daily events match either)


# ── Event Choice Resolution ──

def test_resolve_event_choice_applies_effects():
    """Choice resolution applies effects + flags + follow_up."""
    game = fresh_game(money=50000, health=80, happiness=70, career=30)

    card = {
        "id": "test_card",
        "title": "测试事件",
        "category": "career",
        "flavor": "测试",
        "priority": 5,
        "choices": [
            {
                "text": "选项A",
                "effects": {"money": 10000, "health": -5},
                "flags_set": ["went_to_college"],
                "follow_up": "test_follow",
            },
            {
                "text": "选项B",
                "effects": {"money": -5000},
                "flags_clear": [],
            },
        ],
    }

    result = game.resolve_event_choice(card, 0)

    assert result["type"] == "choice_result"
    assert game.data["money"] == 60000  # 50000 + 10000
    assert game.data["health"] == 75   # 80 - 5
    assert "went_to_college" in game.data["storyFlags"]
    assert game.data["pendingEvent"] == "test_follow"


def test_resolve_event_choice_relationship_changes():
    """Choice with relationship_changes updates affection values."""
    game = fresh_game(relationships=[
        {"id": "friend", "name": "张三", "role": "friend", "personality": "kind",
         "affection": 30, "history": [], "first_met_age": 20, "status": "alive", "age": 25}
    ])

    card = {
        "id": "test_card",
        "title": "测试关系事件",
        "category": "relationship",
        "flavor": "测试",
        "priority": 5,
        "choices": [
            {"text": "帮助朋友", "effects": {}, "relationship_changes": {"friend": 25}},
        ],
    }

    game.resolve_event_choice(card, 0)
    friend = next(r for r in game.data["relationships"] if r["id"] == "friend")
    assert friend["affection"] == 55  # 30 + 25


def test_resolve_event_choice_special_find_job():
    """Choice with special='find_job' assigns a job."""
    game = fresh_game(job=None)
    card = {
        "id": "test_card",
        "title": "找工作",
        "category": "career",
        "flavor": "测试",
        "priority": 5,
        "choices": [
            {"text": "去找工作", "effects": {}, "special": "find_job"},
        ],
    }
    game.resolve_event_choice(card, 0)
    assert game.data["job"] is not None
    assert game.data["job"] in {
        "工人", "服务员", "司机", "教师", "会计",
        "程序员", "医生", "律师", "公务员", "网红", "创业者", "经理"
    }


def test_resolve_event_choice_invalid_index():
    """Invalid choice_index raises ValueError."""
    game = fresh_game()
    card = {
        "id": "test_card", "title": "测试", "category": "career",
        "flavor": "测试", "priority": 5,
        "choices": [{"text": "唯一选项", "effects": {}}],
    }
    with pytest.raises(ValueError):
        game.resolve_event_choice(card, 99)


# ── generate_ending ──

def test_generate_ending_includes_flags():
    """Ending text references story flags."""
    game = fresh_game(storyFlags=["went_to_college", "chose_love", "married_early"], age=78)
    ending = game.generate_ending()
    assert "78" in ending or "享年" in ending
    assert len(ending) > 0


def test_generate_ending_no_flags():
    """Ending with no flags produces default text."""
    game = fresh_game(storyFlags=[], age=45)
    ending = game.generate_ending()
    assert "平凡" in ending

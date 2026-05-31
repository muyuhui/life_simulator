#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flask API for 熬过去 - 人生模拟器.

This file intentionally stays thin. Game rules live in core.py.
"""

from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS

from core import GameState, public_config


app = Flask(__name__, static_folder="web", static_url_path="/static")
app.secret_key = os.environ.get("LIFE_SIMULATOR_SECRET", "life_simulator_dev_secret")
CORS(app, supports_credentials=True)


def ok(game: GameState | dict[str, Any] | None = None, result: dict[str, Any] | None = None, **extra: Any):
    payload: dict[str, Any] = {"success": True, "newAchievements": []}
    if game is not None:
        payload["game"] = game.to_dict() if isinstance(game, GameState) else game
    if result is not None:
        payload["result"] = result
    payload.update(extra)
    return jsonify(payload)


def fail(message: str, status: int = 400, code: str = "bad_request"):
    return jsonify({"success": False, "error": {"code": code, "message": message}, "newAchievements": []}), status


def payload() -> dict[str, Any]:
    return request.get_json(silent=True) or {}


def load_session_game() -> GameState | None:
    data = session.get("game")
    if not data:
        return None
    return GameState.from_dict(data)


def save_session_game(game: GameState) -> None:
    session["game"] = game.to_dict()


def with_game() -> GameState | tuple[Any, int]:
    game = load_session_game()
    if game is None:
        return fail("没有存档", 404, "no_save")
    return game


def finish(game: GameState, result: dict[str, Any] | None = None):
    new_achievements = game.check_achievements()
    save_session_game(game)
    return ok(game, result, newAchievements=new_achievements)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify({"success": True, **public_config()})


@app.route("/api/new_game", methods=["POST"])
def new_game():
    data = payload()
    game = GameState.new(
        name=data.get("name", "玩家"),
        background=str(data.get("background", "1")),
        talent=str(data.get("talent", "1")),
        personality=str(data.get("personality", "1")),
        difficulty=str(data.get("difficulty", "1")),
    )
    save_session_game(game)
    return ok(game)


@app.route("/api/load_game", methods=["GET", "POST"])
def load_game():
    data = payload()
    if data.get("game"):
        game = GameState.from_dict(data["game"])
        save_session_game(game)
        return ok(game)
    game = load_session_game()
    if game is None:
        return fail("没有存档", 404, "no_save")
    return ok(game)


@app.route("/api/next_year", methods=["POST"])
def next_year():
    game = with_game()
    if not isinstance(game, GameState):
        return game
    result = game.next_year()
    if game.data.get("isGameOver"):
        result = {"type": "game_over", "reason": game.data.get("deathReason", "未知"), "age": game.data["age"], "ending": game.generate_ending()}
        session.pop("current_event_card_id", None)
    elif result.get("type") == "event_card":
        session["current_event_card_id"] = result["card"]["id"]
    return finish(game, result)


@app.route("/api/handle_key_choice", methods=["POST"])
def handle_key_choice():
    game = with_game()
    if not isinstance(game, GameState):
        return game
    try:
        result = game.handle_key_choice(int(payload().get("choiceIndex", 0)))
    except ValueError as exc:
        return fail(str(exc))
    return finish(game, result)


@app.route("/api/handle_event_choice", methods=["POST"])
def handle_event_choice():
    game = with_game()
    if not isinstance(game, GameState):
        return game
    card_id = session.get("current_event_card_id")
    if not card_id:
        return fail("没有待处理的事件", 400, "no_pending_event")
    from config import EVENT_CARDS, DAILY_EVENTS

    all_cards = list(EVENT_CARDS) + list(DAILY_EVENTS)
    card = next((c for c in all_cards if c["id"] == card_id), None)
    if not card:
        return fail("事件已过期", 400, "event_expired")
    try:
        result = game.resolve_event_choice(card, int(payload().get("choiceIndex", 0)))
    except ValueError as exc:
        return fail(str(exc))
    session.pop("current_event_card_id", None)
    return finish(game, result)


@app.route("/api/handle_choice", methods=["POST"])
def handle_choice():
    game = with_game()
    if not isinstance(game, GameState):
        return game
    data = payload()
    result = game.handle_choice(effect=data.get("effect", {}), special=data.get("special", ""))
    return finish(game, result)


def action_route(action: str):
    game = with_game()
    if not isinstance(game, GameState):
        return game
    try:
        result = game.apply_action(action, payload())
    except ValueError as exc:
        return fail(str(exc))
    return finish(game, result)


@app.route("/api/hospital", methods=["POST"])
def hospital():
    return action_route("hospital")


@app.route("/api/psychologist", methods=["POST"])
def psychologist():
    return action_route("psychologist")


@app.route("/api/lottery", methods=["POST"])
def lottery():
    return action_route("lottery")


@app.route("/api/dating", methods=["POST"])
def dating():
    return action_route("dating")


@app.route("/api/buy_property", methods=["POST"])
def buy_property():
    return action_route("buy_property")


@app.route("/api/buy_house", methods=["POST"])
def buy_house():
    return action_route("buy_house")


@app.route("/api/get_pet", methods=["POST"])
def get_pet():
    return action_route("get_pet")


@app.route("/api/travel", methods=["POST"])
def travel():
    return action_route("travel")


@app.route("/api/stock", methods=["POST"])
def stock():
    return action_route("stock")


@app.route("/api/find_job", methods=["POST"])
def find_job():
    return action_route("find_job")


if __name__ == "__main__":
    debug = os.environ.get("LIFE_SIMULATOR_DEBUG") == "1"
    app.run(debug=debug, port=5000, use_reloader=False)

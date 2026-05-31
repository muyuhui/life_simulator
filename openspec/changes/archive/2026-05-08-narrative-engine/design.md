# Design: Narrative Engine

## Architecture Overview

```
                    ┌──────────────────────┐
                    │     Flask API         │
                    │  (server.py)          │
                    │                       │
                    │  /api/next_year       │
                    │  /api/handle_event_   │
                    │    choice             │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   GameState           │
                    │   (core.py)           │
                    │                       │
                    │  ┌─────────────────┐  │
                    │  │ NarrativeEngine │  │
                    │  │                 │  │
                    │  │ • select_event  │  │
                    │  │ • apply_choice  │  │
                    │  │ • match_conds   │  │
                    │  │ • gen_ending    │  │
                    │  └───────┬─────────┘  │
                    │          │            │
                    │  ┌───────▼─────────┐  │
                    │  │ Event Cards     │  │
                    │  │ (config.py)     │  │
                    │  │                 │  │
                    │  │ • EVENT_CARDS   │  │
                    │  │ • DAILY_EVENTS  │  │
                    │  └─────────────────┘  │
                    │                       │
                    │  New fields:          │
                    │  • storyFlags: set    │
                    │  • relationships: list│
                    │  • pendingEvent: str  │
                    │  • triggeredEvents:set│
                    └──────────────────────┘
```

## next_year() Refactor

**Before** (current flow):
```
age++ → stat decay → income → death check → key_choice → turning_point
→ small_event → holiday_event → return
```

**After** (new flow):
```
age++ → stat decay → income → death check →
  ┌─ death triggered? → game_over
  └─ else:
      ┌─ pendingEvent exists & conditions match? → trigger pendingEvent card
      ├─ priority >= 10 event matches? → trigger key event card
      ├─ random event matches conditions? → trigger event card
      ├─ turning_point condition met? → trigger turning card (legacy compat)
      └─ none above → trigger daily event (always has 2 choices)
```

The key change: **every year returns a card with choices**. No more "normal" years where nothing happens. The `daily_event` fallback ensures this.

## Data Flow

```
1. Player clicks "下一年"
2. POST /api/next_year
3. server.next_year() → game.next_year() → returns EventCard + context
4. Response: { game, result: { type: "event_card", card: {...} } }
5. Frontend renders card in modal
6. Player selects choice (index)
7. POST /api/handle_event_choice { choiceIndex: N }
8. server.handle_event_choice() → game.resolve_event_choice(index)
   → applies effects, sets flags, updates relationships, saves pendingEvent
9. Response: { game, result: { type: "choice_result", ... }, newAchievements }
10. Frontend closes modal, updates UI (stats, relationships, timeline)
```

## New API Endpoint

```
POST /api/handle_event_choice
Body: { choiceIndex: int }

Response: {
    success: true,
    game: { ... },
    result: {
        type: "choice_result",
        title: "选择结果",
        effects: { ... },
        relationship_changes: { "liwei": 10 },
        flags_set: ["started_business"],
        message: "你选择了..."
    },
    newAchievements: [...]
}
```

## Key Design Decisions

### 1. Event cards live in config.py, not database
Rationale: 20 cards is small. A Python list of dicts is easy to edit and doesn't require migration tools. Can be moved to JSON/YAML later if needed.

### 2. Condition matching is declarative (dict-based), not code-based
Each card's `conditions` dict defines age range, stat ranges, flag requirements, etc. A single `match_conditions()` function interprets them. This keeps card authoring simple — no Python code needed to add a new card.

### 3. Template variables in flavor text
`{spouse_name}`, `{friend_name}`, `{job}`, `{money}` etc. are interpolated at render time via simple string replacement. This lets the same card read differently depending on context.

### 4. Legacy turning_point and key_choice systems are preserved in spirit but integrated
The old `trigger_turning_point()` and `check_key_age_choice()` become special event cards in the new system. The underlying random logic stays, but the presentation layer is unified.

### 5. Pending event is just a string ID
A single `pendingEvent: str | None` field is enough for MVP. If the pending event's conditions aren't met next year, it silently clears and normal event selection resumes.

### 6. Relationship panel is a new UI section, not a modal
The game screen gains a collapsible "人物网络" section alongside the existing timeline/achievements columns. This shows named characters with relationship bars, avoiding modal fatigue.

## File Changes (Detailed)

### config.py additions
- `EVENT_CARDS`: list of 20 EventCard dicts
- `DAILY_EVENTS`: list of 30-40 DailyEvent dicts
- `STORY_FLAGS`: dict mapping flag IDs to Chinese descriptions
- `CHARACTER_NAMES`: dict of name pools by gender
- `PERSONALITY_TRAITS`: dict of 8 personality labels with descriptions

### core.py additions
- `GameState.data["storyFlags"]`: `list[str]` (serialized set)
- `GameState.data["relationships"]`: `list[dict]`
- `GameState.data["pendingEvent"]`: `str | None`
- `GameState.data["triggeredEvents"]`: `list[str]`
- `GameState.match_conditions(conditions) -> bool`
- `GameState.select_event() -> EventCard | None`
- `GameState.resolve_event_choice(card, choice_index) -> dict`
- `GameState.interpolate_flavor(flavor_text) -> str`
- `GameState.generate_ending() -> str`
- Refactor `next_year()` to use `select_event()` + return event card
- Remove standalone `check_key_age_choice()`, `check_small_event()`, `check_holiday_event()`, `check_turning_point()` — integrated into event card selection

### server.py additions
- `POST /api/handle_event_choice` endpoint
- Store current event card in session for validation (or pass card ID from frontend)

### web/js/game-vue.js changes
- Enhanced `applyServerResponse()` to handle `event_card` result type
- New reactive state: `relationshipList`, `currentEventCard`
- Enhanced `showEventModal()` for immersive card rendering with flavor text, character mentions, choice outcome previews
- New `RelationshipPanel` in game screen
- `handleChoice()` split into `handleKeyChoice()` and `handleEventChoice()` paths

### web/css/style.css additions
- `.event-card` — immersive card styles
- `.event-flavor` — narrative text typography
- `.event-choice-preview` — effect preview on choices
- `.relationship-panel` — sidebar/column for character network
- `.relationship-bar` — relationship value bar
- `.relationship-change` — animated +N/-N indicator

### web/index.html additions
- Relationship panel section in game screen (alongside timeline/achievements columns)

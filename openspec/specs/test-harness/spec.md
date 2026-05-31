# test-harness Specification

## Purpose
TBD - created by archiving change dead-code-cleanup. Update Purpose after archive.
## Requirements
### Requirement: Core game rules SHALL have automated test coverage
The system SHALL include pytest tests for the following critical paths in `core.py`:
- Death check: health ≤ 0 triggers turning point (90%) or death (10%)
- Turning point: consecutiveTurning ≥ 2 with 10% probability triggers super event
- Event selection: falls back to daily events when no event card matches
- Event choice resolution: applies effects, flags, and relationship changes
- Condition matching: all condition fields (age, has_job, has_spouse, has_children, flags_any/all/none, stat ranges) are tested

#### Scenario: Death triggers turning point most of the time
- **GIVEN** a game state with health = 0
- **WHEN** `check_death()` is called 1000 times with a fixed random seed
- **THEN** approximately 900 of them trigger `trigger_turning_point()` and return False (not dead)
- **AND** approximately 100 return True (dead)

#### Scenario: Consecutive turning triggers super event
- **GIVEN** `consecutiveTurning` = 2, health < 20, and a random seed that yields < 0.1
- **WHEN** `check_turning_point()` is called
- **THEN** the result is a super event with type `"turning"`, title `"人生逆袭！"`
- **AND** money increases by 100000, health by 50, happiness by 50, career by 30

#### Scenario: Event selection falls back to daily events
- **GIVEN** a game state where no `EVENT_CARD` conditions match and no `pendingEvent` is set
- **WHEN** `select_event()` is called
- **THEN** a daily event card is returned (id starts with `"daily_"`) or None if no daily events match

#### Scenario: Event choice applies all side effects
- **GIVEN** an event card with a choice that has effects, flags_set, and relationship_changes
- **WHEN** `resolve_event_choice(card, choice_index)` is called
- **THEN** the effects are applied to the game state
- **AND** the flags in `flags_set` are added to `storyFlags`
- **AND** the relationship affection values are updated by the specified deltas
- **AND** if `follow_up` is set, `pendingEvent` is updated


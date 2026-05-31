## ADDED Requirements

### Requirement: Frontend SHALL be split into modular JavaScript files
The frontend application SHALL be split into three ES modules:
- `game-state.js`: state definitions (Vue ref/reactive), save/load localStorage, mergeReactive helper
- `game-api.js`: API call wrapper, error handling, config loading, backend online detection
- `game-ui.js`: event modal rendering, notification display, event card UI, choice handling

The entry point `game-vue.js` SHALL import from these modules and retain only the `createApp({ setup() { ... } }).mount('#app')` assembly logic.

#### Scenario: ES modules load in correct order
- **WHEN** the page loads with `<script type="module" src="js/game-vue.js"></script>`
- **THEN** all three dependent modules are resolved and loaded
- **AND** the Vue application mounts successfully

#### Scenario: Each module has a single responsibility
- **GIVEN** a function making API calls
- **WHEN** that function is located
- **THEN** it is found in `game-api.js`, not in `game-vue.js` or `game-ui.js`

### Requirement: Dead legacy choice handling SHALL be removed from frontend
The frontend SHALL no longer handle `result.type === 'key_choice'` responses from the server. The `pendingKeyChoice` state, the `/api/handle_key_choice` API call, and all associated branching SHALL be removed.

#### Scenario: Server returns key_choice type
- **GIVEN** a server response with `result.type === 'key_choice'`
- **WHEN** `applyServerResponse(response)` is called
- **THEN** the response is silently ignored (no error, no modal)

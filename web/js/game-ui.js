// game-ui.js — 事件卡/modal 渲染 + 服务器响应处理 + 快捷操作
import { mergeReactive, formatMoney } from './game-state.js';

function effectName(key) {
    return { money: '金钱', health: '健康', happiness: '快乐', career: '事业' }[key] || key;
}

function describeEffects(effects = {}) {
    return Object.entries(effects || {})
        .map(([key, value]) => `${effectName(key)} ${value > 0 ? '+' : ''}${value}`)
        .join(' / ');
}

export function createUi(stateRefs, apiHelpers) {
    const {
        gameState, config, currentScreen, hasSave, showModal, showAchievement,
        pendingAchievement, backendOnline, isBusy, busyAction, appNotice,
        modalRef, modalTitle, modalDesc, modalChoices, modalType, modalEffects,
        newGameData, canMutate, currentEventCard, isDailyEvent,
        relationshipChanges, serverEnding, SAVE_KEY
    } = stateRefs;

    const { apiCall, handleApiError, withBusy, setNotice } = apiHelpers;

    function clearNotice() {
        appNotice.value = null;
    }

    function saveGame() {
        localStorage.setItem(SAVE_KEY, JSON.stringify({ ...gameState }));
        hasSave.value = true;
    }

    function notifyAchievements(newAchievements = []) {
        if (!newAchievements.length) return;
        pendingAchievement.value = newAchievements[0];
        showAchievement.value = true;
        setTimeout(() => {
            showAchievement.value = false;
            pendingAchievement.value = null;
        }, 3000);
    }

    function showEventModal(title, desc, choices = [], type = '事件', effects = '', isEventCard = false) {
        modalTitle.value = title;
        modalDesc.value = desc || '';
        modalChoices.value = choices || [];
        modalType.value = type;
        modalEffects.value = effects || '';
        isDailyEvent.value = isEventCard;
        relationshipChanges.value = {};
        showModal.value = true;
        if (modalRef.value?.focus) modalRef.value.focus();
    }

    function showEventCardModal(card, isDaily = false) {
        currentEventCard.value = card;
        const choices = (card.choices || []).map(ch => ({
            text: ch.text,
            flavor: ch.flavor || '',
            outcome: describeEffects(ch.effects || {}),
            index: card.choices.indexOf(ch)
        }));
        showEventModal(
            card.title, card.flavor || '', choices,
            card.category === 'life_key' ? '人生关键' : card.category === 'moral' ? '道德抉择' : '事件',
            describeEffects(card.choices[0]?.effects || {}), isDaily
        );
    }

    function applyServerResponse(response, fallbackTitle = '') {
        if (response.game) {
            mergeReactive(gameState, response.game);
            saveGame();
        }

        notifyAchievements(response.newAchievements || []);
        const result = response.result;
        if (!result) return;

        if (result.type === 'event_card') {
            showEventCardModal(result.card, result.is_daily || false);
        } else if (result.type === 'choice_result') {
            relationshipChanges.value = result.relationship_changes || {};
            if (result.title) {
                setNotice(result.title, 'success');
                setTimeout(clearNotice, 2500);
            }
        } else if (result.type === 'game_over') {
            if (result.ending) serverEnding.value = result.ending;
            currentScreen.value = 'summary';
        } else if (result.type === 'turning') {
            showEventCardModal({
                id: 'turning', category: 'turning', title: result.title || '转折点',
                flavor: result.desc || '命运给了你一次转机。', choices: [], priority: 0
            });
        } else if (result.type === 'small_event') {
            showEventModal(result.event.title, describeEffects(result.event.effect), [], '日常事件');
        } else if (result.type === 'holiday') {
            showEventModal('生日', result.event.text, [], '节日事件', describeEffects(result.event.effect));
        } else if (result.message && fallbackTitle) {
            showEventModal(fallbackTitle, result.message);
        }
        // key_choice 类型不再处理（已在后端移除）
    }

    function closeModal() {
        showModal.value = false;
    }

    async function handleEventChoice(idx) {
        if (!currentEventCard.value) return;
        const card = currentEventCard.value;
        const choice = card.choices[idx];
        showModal.value = false;
        currentEventCard.value = null;

        await withBusy(isBusy, busyAction, 'event_choice', async () => {
            try {
                const response = await apiCall('/api/handle_event_choice', { choiceIndex: idx });
                applyServerResponse(response, choice.text);
            } catch (error) {
                handleApiError(error, '选择失败');
            }
        });
    }

    async function runAction(action, title, payload = {}) {
        if (!canMutate.value) {
            setNotice('后端未连接，不能执行操作。', 'error');
            return;
        }

        await withBusy(isBusy, busyAction, action, async () => {
            try {
                const response = await apiCall(`/api/${action}`, payload);
                applyServerResponse(response, title);
                if (response.result?.message) showEventModal(title, response.result.message);
            } catch (error) {
                handleApiError(error, `${title}失败`);
                showEventModal('操作失败', error.message || `${title}失败`);
            }
        });
    }

    function showAssetChoices() {
        const choices = [];
        const houses = config.properties?.house || {};
        const cars = config.properties?.car || {};

        Object.entries(houses).forEach(([key, prop]) => {
            if (key === 'none') return;
            choices.push({
                text: `购买${prop.name} - ${formatMoney(prop.cost)}`,
                outcome: `快乐 +${prop.happiness || 0}`,
                action: 'buy_property',
                payload: { type: 'house', key }
            });
        });

        Object.entries(cars).forEach(([key, prop]) => {
            if (key === 'none') return;
            choices.push({
                text: `购买${prop.name} - ${formatMoney(prop.cost)}`,
                outcome: `快乐 +${prop.happiness || 0}`,
                action: 'buy_property',
                payload: { type: 'car', key }
            });
        });

        showEventModal('购买资产', '选择一项资产。资金不足时后端会拒绝交易。', choices, '资产');
    }

    function showStockChoices() {
        showEventModal('股票投资', '选择投入当前现金的比例。收益和亏损都会立即结算。', [
            { text: '投入 20%', outcome: '稳一点', action: 'stock', payload: { percent: 0.2 } },
            { text: '投入 50%', outcome: '波动更明显', action: 'stock', payload: { percent: 0.5 } },
            { text: '投入 100%', outcome: '把命运交给市场', action: 'stock', payload: { percent: 1 } }
        ], '投资');
    }

    function showHelp() {
        showEventModal(
            '游戏帮助',
            '每次“下一年”都会由后端核心规则推进。低健康、低快乐或负债可能触发转机；快捷操作会消耗金钱并改变状态。',
            [],
            '帮助'
        );
    }

    function resetGame() {
        localStorage.removeItem(SAVE_KEY);
        mergeReactive(gameState, {});
        currentScreen.value = 'welcome';
        hasSave.value = false;
        serverEnding.value = '';
        currentEventCard.value = null;
        Object.assign(newGameData, { name: '', background: '1', talent: '1', personality: '1', difficulty: '1' });
        setNotice('本地存档已清除。', 'success');
    }

    function startNewGame() {
        currentScreen.value = 'create';
    }

    async function confirmCreate() {
        if (!newGameData.name.trim()) {
            showEventModal('提示', '请输入你的名字。');
            return;
        }
        if (!backendOnline.value) {
            setNotice('后端未连接，无法创建新人生。请先启动 Flask 服务。', 'error');
            return;
        }

        await withBusy(isBusy, busyAction, 'new_game', async () => {
            try {
                const response = await apiCall('/api/new_game', { ...newGameData });
                applyServerResponse(response);
                currentScreen.value = 'game';
                setNotice('新人生已创建。', 'success');
            } catch (error) {
                handleApiError(error, '创建失败');
            }
        });
    }

    async function continueGame() {
        const saved = localStorage.getItem(SAVE_KEY);
        if (!saved) return;

        const localGame = JSON.parse(saved);
        if (!backendOnline.value) {
            mergeReactive(gameState, localGame);
            currentScreen.value = 'game';
            setNotice('正在查看本地存档。后端未连接，操作已锁定。', 'info');
            return;
        }

        await withBusy(isBusy, busyAction, 'load_game', async () => {
            try {
                const response = await apiCall('/api/load_game', { game: localGame });
                applyServerResponse(response);
                currentScreen.value = 'game';
            } catch (error) {
                handleApiError(error, '读取存档失败');
            }
        });
    }

    async function nextYear() {
        if (!canMutate.value) {
            setNotice('后端未连接，不能推进人生。', 'error');
            return;
        }
        await withBusy(isBusy, busyAction, 'next_year', async () => {
            try {
                const response = await apiCall('/api/next_year', {});
                applyServerResponse(response);
            } catch (error) {
                handleApiError(error, '推进失败');
            }
        });
    }

    function canRunAction(action) {
        return canMutate.value && !isBusy.value && !action.blocked && gameState.money >= (action.minMoney || 0);
    }

    async function handleChoice(idx) {
        const choice = modalChoices.value[idx];

        // 事件卡选择 → 走新的事件选择流程
        if (currentEventCard.value) {
            await handleEventChoice(idx);
            return;
        }

        showModal.value = false;

        if (choice?.action) {
            await runAction(choice.action, choice.text, choice.payload || {});
        }
    }

    return {
        showEventModal, showEventCardModal, applyServerResponse,
        handleChoice, handleEventChoice, closeModal,
        notifyAchievements, describeEffects, effectName,
        showAssetChoices, showStockChoices, showHelp,
        runAction, canRunAction, resetGame,
        startNewGame, confirmCreate, continueGame,
        nextYear, saveGame, setNotice, clearNotice
    };
}

const { createApp, ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } = Vue;

const SAVE_KEY = 'lifeSimulatorSave';
const API_BASE = '';

const DEFAULT_CONFIG = {
    schemaVersion: 1,
    backgrounds: {
        '1': { name: '小镇青年', money: 5000, happiness: 70, career: 20 },
        '2': { name: '城市中产', money: 50000, happiness: 60, career: 50 },
        '3': { name: '富二代', money: 200000, happiness: 80, career: 30 },
        '4': { name: '农村出身', money: 2000, happiness: 60, career: 10 }
    },
    talents: {
        '1': { name: '学习天赋', desc: '考试成功率更高' },
        '2': { name: '社交达人', desc: '人际关系更顺利' },
        '3': { name: '财运亨通', desc: '金钱收益更高' },
        '4': { name: '健康体质', desc: '健康衰减更慢' }
    },
    personalities: {
        '1': { name: '稳健型', desc: '风险更低' },
        '2': { name: '冒险型', desc: '高风险高回报' },
        '3': { name: '佛系型', desc: '快乐衰减更慢' },
        '4': { name: '卷王', desc: '事业成长更快' }
    },
    difficulties: {
        '1': { name: '普通模式', turningRate: 0.9 },
        '2': { name: '硬核模式', turningRate: 0.7 },
        '3': { name: '休闲模式', turningRate: 1.0 }
    },
    jobs: {},
    properties: { house: {}, car: {} },
    achievements: []
};

createApp({
    setup() {
        const currentScreen = ref('welcome');
        const hasSave = ref(false);
        const showModal = ref(false);
        const showAchievement = ref(false);
        const pendingAchievement = ref(null);
        const backendOnline = ref(false);
        const pendingKeyChoice = ref(null);
        const isBusy = ref(false);
        const busyAction = ref('');
        const appNotice = ref(null);
        const modalRef = ref(null);
        const currentEventCard = ref(null);
        const isDailyEvent = ref(false);
        const relationshipChanges = ref({});
        const serverEnding = ref('');

        const modalTitle = ref('');
        const modalDesc = ref('');
        const modalChoices = ref([]);
        const modalType = ref('事件');
        const modalEffects = ref('');

        const newGameData = reactive({
            name: '',
            background: '1',
            talent: '1',
            personality: '1',
            difficulty: '1'
        });

        const gameState = reactive(defaultState());
        const config = reactive(JSON.parse(JSON.stringify(DEFAULT_CONFIG)));

        function defaultState() {
            return {
                schemaVersion: 1,
                name: '',
                age: 18,
                background: '1',
                talent: '1',
                personality: '1',
                difficulty: '1',
                money: 5000,
                health: 80,
                happiness: 70,
                career: 20,
                education: 0,
                job: null,
                year: 1,
                isGameOver: false,
                achievements: [],
                timeline: [{ age: 18, event: '开启人生旅程' }],
                spouse: null,
                spouseType: null,
                children: [],
                house: false,
                houseType: 'none',
                car: 'none',
                pet: false,
                turningPoints: 0,
                keyChoices: {},
                specialBuffs: {}
            };
        }

        const canMutate = computed(() => backendOnline.value);

        const summaryMessage = computed(() => {
            if (serverEnding.value) return serverEnding.value;
            if (gameState.age >= 100) return '百岁人生，已经很了不起。';
            if (gameState.turningPoints >= 5) return '你一次次从绝境里撑了过来。';
            if (gameState.money >= 1000000) return '财富自由，人生赢家。';
            if (gameState.age < 30 && gameState.isGameOver) return '英年早逝，令人惋惜。';
            return '平凡而真实的人生，也有它自己的重量。';
        });

        const achievementCards = computed(() => {
            return (config.achievements || []).map((achievement) => ({
                ...achievement,
                unlocked: gameState.achievements.includes(achievement.id)
            }));
        });

        const relationshipList = computed(() => {
            return (gameState.relationships || []).map(r => ({
                ...r,
                affectionLabel: r.affection >= 60 ? '亲密' : r.affection >= 20 ? '友好' : r.affection >= -20 ? '普通' : r.affection >= -60 ? '疏远' : '破裂',
                affectionColor: r.affection >= 60 ? 'var(--happiness)' : r.affection >= 20 ? 'var(--career)' : r.affection >= -20 ? 'var(--muted)' : r.affection >= -60 ? 'var(--money)' : 'var(--health)'
            }));
        });

        const quickActions = computed(() => [
            { key: 'hospital', icon: '🏥', label: '医院', hint: '花费 2,000，恢复健康', minMoney: 2000, run: () => runAction('hospital', '医院') },
            { key: 'psychologist', icon: '🧠', label: '心理医生', hint: '花费 1,000，恢复快乐', minMoney: 1000, run: () => runAction('psychologist', '心理医生') },
            { key: 'lottery', icon: '🎰', label: '彩票', hint: '花费 10，碰碰运气', minMoney: 10, run: () => runAction('lottery', '彩票') },
            { key: 'dating', icon: '💕', label: '相亲', hint: gameState.spouse ? '已有伴侣' : '花费 500，寻找伴侣', minMoney: 500, blocked: !!gameState.spouse, run: () => runAction('dating', '相亲') },
            { key: 'asset', icon: '🏠', label: '买资产', hint: '房产和车辆', minMoney: 1, run: showAssetChoices },
            { key: 'pet', icon: '🐱', label: '养宠物', hint: gameState.pet ? '已有宠物' : '花费 3,000，提升快乐', minMoney: 3000, blocked: !!gameState.pet, run: () => runAction('get_pet', '养宠物') },
            { key: 'travel', icon: '✈️', label: '旅行', hint: '至少 3,000，随机行程', minMoney: 3000, run: () => runAction('travel', '旅行') },
            { key: 'stock', icon: '📈', label: '股票', hint: '投入一定比例资产', minMoney: 1, run: showStockChoices },
            { key: 'job', icon: '💼', label: '求职', hint: '寻找或更换工作', minMoney: 0, run: () => runAction('find_job', '求职') }
        ]);

        function formatMoney(amount) {
            const value = Number(amount || 0);
            if (value < 0) return '-' + formatMoney(-value);
            if (value >= 100000000) return (value / 100000000).toFixed(1) + '亿';
            if (value >= 10000) return (value / 10000).toFixed(1) + '万';
            return String(Math.floor(value));
        }

        const getBgIcon = (key) => ({ '1': '🏘️', '2': '🏙️', '3': '💎', '4': '🌾' }[key] || '🏠');
        const getTalentIcon = (key) => ({ '1': '📚', '2': '🤝', '3': '💰', '4': '💪', '5': '⭐' }[key] || '✨');
        const getPersIcon = (key) => ({ '1': '🛡️', '2': '⚔️', '3': '🧘', '4': '📚' }[key] || '🧑');
        const getDiffIcon = (key) => ({ '1': '🌟', '2': '🔥', '3': '☀️' }[key] || '🎯');
        const getEducationName = (edu) => ({ 0: '高中', 1: '本科', 2: '硕士', 3: '博士' }[Number(edu)] || '高中');

        function mergeReactive(target, source) {
            Object.keys(target).forEach((key) => delete target[key]);
            Object.assign(target, defaultState(), source || {});
            if (!Array.isArray(target.timeline)) target.timeline = [];
            if (!Array.isArray(target.achievements)) target.achievements = [];
            if (!Array.isArray(target.children)) target.children = [];
        }

        function setNotice(message, type = 'info') {
            appNotice.value = { message, type };
        }

        function clearNotice() {
            appNotice.value = null;
        }

        function saveGame() {
            localStorage.setItem(SAVE_KEY, JSON.stringify({ ...gameState }));
            hasSave.value = true;
        }

        function handleApiError(error, fallback = '操作失败') {
            backendOnline.value = false;
            setNotice(error?.message || fallback, 'error');
        }

        async function apiCall(endpoint, data = null, method = 'POST') {
            const options = {
                method,
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            };
            if (data !== null) options.body = JSON.stringify(data);
            const response = await fetch(API_BASE + endpoint, options);
            const json = await response.json();
            if (!response.ok || json.success === false) {
                const message = typeof json.error === 'string' ? json.error : (json.error?.message || '请求失败');
                throw new Error(message);
            }
            backendOnline.value = true;
            return json;
        }

        async function withBusy(action, task) {
            if (isBusy.value) return null;
            isBusy.value = true;
            busyAction.value = action;
            try {
                return await task();
            } finally {
                isBusy.value = false;
                busyAction.value = '';
            }
        }

        async function loadConfig() {
            try {
                const response = await fetch(API_BASE + '/api/config', { credentials: 'include' });
                if (!response.ok) throw new Error('后端配置不可用');
                Object.assign(config, await response.json());
                backendOnline.value = true;
                clearNotice();
            } catch (error) {
                backendOnline.value = false;
                Object.assign(config, JSON.parse(JSON.stringify(DEFAULT_CONFIG)));
                setNotice('后端未连接：可以查看本地存档，但不能推进人生或执行操作。', 'info');
            }
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
            nextTick(() => modalRef.value?.focus());
        }

        function showEventCardModal(card, isDaily = false) {
            currentEventCard.value = card;
            const choices = (card.choices || []).map(ch => ({
                text: ch.text,
                flavor: ch.flavor || '',
                outcome: describeEffects(ch.effects || {}),
                index: card.choices.indexOf(ch)
            }));
            showEventModal(card.title, card.flavor || '', choices, card.category === 'life_key' ? '人生关键' : card.category === 'moral' ? '道德抉择' : '事件', describeEffects(card.choices[0]?.effects || {}), isDaily);
        }

        async function handleEventChoice(idx) {
            if (!currentEventCard.value) return;
            const card = currentEventCard.value;
            const choice = card.choices[idx];
            showModal.value = false;
            currentEventCard.value = null;

            await withBusy('event_choice', async () => {
                try {
                    const response = await apiCall('/api/handle_event_choice', { choiceIndex: idx });
                    applyServerResponse(response, choice.text);
                } catch (error) {
                    handleApiError(error, '选择失败');
                }
            });
        }

        function closeModal() {
            showModal.value = false;
            pendingKeyChoice.value = null;
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

        function describeEffects(effects = {}) {
            return Object.entries(effects || {})
                .map(([key, value]) => `${effectName(key)} ${value > 0 ? '+' : ''}${value}`)
                .join(' / ');
        }

        function effectName(key) {
            return { money: '金钱', health: '健康', happiness: '快乐', career: '事业' }[key] || key;
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
            } else if (result.type === 'key_choice') {
                pendingKeyChoice.value = result;
                showEventModal(`${result.age}岁 - 人生选择`, '这一年需要你做一个关键决定。', result.choices, '关键选择');
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

            await withBusy('new_game', async () => {
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

            await withBusy('load_game', async () => {
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
            await withBusy('next_year', async () => {
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

        async function runAction(action, title, payload = {}) {
            if (!canMutate.value) {
                setNotice('后端未连接，不能执行操作。', 'error');
                return;
            }

            await withBusy(action, async () => {
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

        async function handleChoice(idx) {
            const choice = modalChoices.value[idx];

            // 事件卡选择 → 走新的事件选择流程
            if (currentEventCard.value) {
                await handleEventChoice(idx);
                return;
            }

            showModal.value = false;

            if (pendingKeyChoice.value) {
                const choiceIndex = idx;
                pendingKeyChoice.value = null;
                await withBusy('key_choice', async () => {
                    try {
                        const response = await apiCall('/api/handle_key_choice', { choiceIndex });
                        applyServerResponse(response, '选择结果');
                    } catch (error) {
                        handleApiError(error, '选择失败');
                    }
                });
                return;
            }

            if (choice?.action) {
                await runAction(choice.action, choice.text, choice.payload || {});
            }
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
            mergeReactive(gameState, defaultState());
            currentScreen.value = 'welcome';
            hasSave.value = false;
            serverEnding.value = '';
            currentEventCard.value = null;
            Object.assign(newGameData, { name: '', background: '1', talent: '1', personality: '1', difficulty: '1' });
            setNotice('本地存档已清除。', 'success');
        }

        function onKeyDown(event) {
            if (event.key === 'Escape' && showModal.value) closeModal();
        }

        onMounted(async () => {
            await loadConfig();
            hasSave.value = !!localStorage.getItem(SAVE_KEY);
            window.addEventListener('keydown', onKeyDown);
        });

        onBeforeUnmount(() => {
            window.removeEventListener('keydown', onKeyDown);
        });

        return {
            currentScreen,
            hasSave,
            showModal,
            showAchievement,
            pendingAchievement,
            backendOnline,
            isBusy,
            busyAction,
            appNotice,
            modalRef,
            modalTitle,
            modalDesc,
            modalChoices,
            modalType,
            modalEffects,
            newGameData,
            gameState,
            config,
            canMutate,
            summaryMessage,
            achievementCards,
            quickActions,
            relationshipList,
            isDailyEvent,
            relationshipChanges,
            formatMoney,
            getBgIcon,
            getTalentIcon,
            getPersIcon,
            getDiffIcon,
            getEducationName,
            clearNotice,
            startNewGame,
            confirmCreate,
            continueGame,
            nextYear,
            canRunAction,
            handleChoice,
            handleEventChoice,
            closeModal,
            showHelp,
            resetGame
        };
    }
}).mount('#app');

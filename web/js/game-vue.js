// game-vue.js — Vue 3 应用入口，组装 state / api / ui 三个模块
import { createApp, ref, reactive, computed, onMounted, onBeforeUnmount } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js';
import {
    defaultState, mergeReactive, formatMoney, SAVE_KEY,
    getBgIcon, getTalentIcon, getPersIcon, getDiffIcon, getEducationName,
    DEFAULT_CONFIG
} from './game-state.js';
import { createApi } from './game-api.js';
import { createUi } from './game-ui.js';

createApp({
    setup() {
        // ── 响应式状态（所有权在入口文件） ──
        const currentScreen = ref('welcome');
        const hasSave = ref(false);
        const showModal = ref(false);
        const showAchievement = ref(false);
        const pendingAchievement = ref(null);
        const backendOnline = ref(false);
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

        const newGameData = reactive({ name: '', background: '1', talent: '1', personality: '1', difficulty: '1' });
        const gameState = reactive(defaultState());
        const config = reactive(JSON.parse(JSON.stringify(DEFAULT_CONFIG)));

        const canMutate = computed(() => backendOnline.value);

        // ── 装配 API 层 ──
        const apiRefs = { backendOnline, config, appNotice };
        const api = createApi(apiRefs);

        // ── 装配 UI 层 ──
        const stateRefs = {
            gameState, config, currentScreen, hasSave, showModal, showAchievement,
            pendingAchievement, backendOnline, isBusy, busyAction, appNotice,
            modalRef, modalTitle, modalDesc, modalChoices, modalType, modalEffects,
            newGameData, canMutate, currentEventCard, isDailyEvent,
            relationshipChanges, serverEnding, SAVE_KEY
        };
        const ui = createUi(stateRefs, api);

        // ── 计算属性 ──
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
            { key: 'hospital', icon: '🏥', label: '医院', hint: '花费 2,000，恢复健康', minMoney: 2000, run: () => ui.runAction('hospital', '医院') },
            { key: 'psychologist', icon: '🧠', label: '心理医生', hint: '花费 1,000，恢复快乐', minMoney: 1000, run: () => ui.runAction('psychologist', '心理医生') },
            { key: 'lottery', icon: '🎰', label: '彩票', hint: '花费 10，碰碰运气', minMoney: 10, run: () => ui.runAction('lottery', '彩票') },
            { key: 'dating', icon: '💕', label: '相亲', hint: gameState.spouse ? '已有伴侣' : '花费 500，寻找伴侣', minMoney: 500, blocked: !!gameState.spouse, run: () => ui.runAction('dating', '相亲') },
            { key: 'asset', icon: '🏠', label: '买资产', hint: '房产和车辆', minMoney: 1, run: ui.showAssetChoices },
            { key: 'pet', icon: '🐱', label: '养宠物', hint: gameState.pet ? '已有宠物' : '花费 3,000，提升快乐', minMoney: 3000, blocked: !!gameState.pet, run: () => ui.runAction('get_pet', '养宠物') },
            { key: 'travel', icon: '✈️', label: '旅行', hint: '至少 3,000，随机行程', minMoney: 3000, run: () => ui.runAction('travel', '旅行') },
            { key: 'stock', icon: '📈', label: '股票', hint: '投入一定比例资产', minMoney: 1, run: ui.showStockChoices },
            { key: 'job', icon: '💼', label: '求职', hint: '寻找或更换工作', minMoney: 0, run: () => ui.runAction('find_job', '求职') }
        ]);

        // ── 生命周期 ──
        function onKeyDown(event) {
            if (event.key === 'Escape' && showModal.value) ui.closeModal();
        }

        onMounted(async () => {
            await api.loadConfig();
            hasSave.value = !!localStorage.getItem(SAVE_KEY);
            window.addEventListener('keydown', onKeyDown);
        });

        onBeforeUnmount(() => {
            window.removeEventListener('keydown', onKeyDown);
        });

        // ── 返回模板绑定 ──
        return {
            currentScreen, hasSave, showModal, showAchievement,
            pendingAchievement, backendOnline, isBusy, busyAction,
            appNotice, modalRef, modalTitle, modalDesc, modalChoices,
            modalType, modalEffects, newGameData, gameState, config,
            canMutate, summaryMessage, achievementCards, quickActions,
            relationshipList, isDailyEvent, relationshipChanges,
            formatMoney, getBgIcon, getTalentIcon, getPersIcon, getDiffIcon,
            getEducationName,
            clearNotice: ui.clearNotice,
            startNewGame: ui.startNewGame,
            confirmCreate: ui.confirmCreate,
            continueGame: ui.continueGame,
            nextYear: ui.nextYear,
            canRunAction: ui.canRunAction,
            handleChoice: ui.handleChoice,
            handleEventChoice: ui.handleEventChoice,
            closeModal: ui.closeModal,
            showHelp: ui.showHelp,
            resetGame: ui.resetGame
        };
    }
}).mount('#app');

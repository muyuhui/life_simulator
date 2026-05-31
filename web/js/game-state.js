// game-state.js — 状态管理 + 存档 + 纯工具函数
// 所有响应式状态集中定义，通过 createState() 返回

export const SAVE_KEY = 'lifeSimulatorSave';
export const API_BASE = '';

export const DEFAULT_CONFIG = {
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

export function defaultState() {
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

export function formatMoney(amount) {
    const value = Number(amount || 0);
    if (value < 0) return '-' + formatMoney(-value);
    if (value >= 100000000) return (value / 100000000).toFixed(1) + '亿';
    if (value >= 10000) return (value / 10000).toFixed(1) + '万';
    return String(Math.floor(value));
}

export const getBgIcon = (key) => ({ '1': '🏘️', '2': '🏙️', '3': '💎', '4': '🌾' }[key] || '🏠');
export const getTalentIcon = (key) => ({ '1': '📚', '2': '🤝', '3': '💰', '4': '💪', '5': '⭐' }[key] || '✨');
export const getPersIcon = (key) => ({ '1': '🛡️', '2': '⚔️', '3': '🧘', '4': '📚' }[key] || '🧑');
export const getDiffIcon = (key) => ({ '1': '🌟', '2': '🔥', '3': '☀️' }[key] || '🎯');
export const getEducationName = (edu) => ({ 0: '高中', 1: '本科', 2: '硕士', 3: '博士' }[Number(edu)] || '高中');

export function mergeReactive(target, source) {
    Object.keys(target).forEach((key) => delete target[key]);
    Object.assign(target, defaultState(), source || {});
    if (!Array.isArray(target.timeline)) target.timeline = [];
    if (!Array.isArray(target.achievements)) target.achievements = [];
    if (!Array.isArray(target.children)) target.children = [];
}

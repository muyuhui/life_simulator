// ====== 熬过去 - Vue.js 版 ======

const { createApp, ref, reactive, computed, onMounted } = Vue;

createApp({
    setup() {
        // API 地址
        const API_BASE = '';

        // 响应式状态
        const currentScreen = ref('welcome');
        const hasSave = ref(false);
        const showModal = ref(false);
        
        const modalTitle = ref('');
        const modalDesc = ref('');
        const modalChoices = ref([]);
        const modalType = ref('事件');
        
        const newGameData = reactive({
            name: '',
            background: '1',
            talent: '1',
            personality: '1',
            difficulty: '1'
        });

        const gameState = reactive({
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
            events: [],
            timeline: [],
            spouse: null,
            spouseType: null,
            children: [],
            house: false,
            houseType: 'none',
            car: 'none',
            pet: false,
            turningPoints: 0,
            keyEvents: [],
            lifeLabels: [],
            specialBuffs: {}
        });

        const config = reactive({
            backgrounds: {},
            talents: {},
            personalities: {},
            difficulties: {},
            achievements: []
        });

        // 计算属性
        const unlockedAchievements = computed(() => gameState.achievements?.length || 0);
        const totalAchievements = computed(() => config.achievements?.length || 0);

        const summaryMessage = computed(() => {
            if (gameState.age >= 100) return '百岁老人，功德圆满！';
            if (gameState.age >= 80) return '安享晚年，福寿双全！';
            if (gameState.money >= 1000000) return '富甲一方，人生赢家！';
            if (gameState.age < 30) return '英年早逝，令人惋惜...';
            return '平凡而真实的人生。';
        });

        // 工具函数
        const formatMoney = (amount) => {
            if (amount >= 10000) return (amount / 10000).toFixed(1) + '万';
            return amount.toString();
        };

        const random = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
        const clamp = (value, min = 0, max = 100) => Math.max(min, Math.min(max, value));

        const getBgIcon = (key) => ({ '1': '🏘️', '2': '🏙️', '3': '💎', '4': '🌾' }[key] || '🏠');
        const getPersIcon = (key) => ({ '1': '🛡️', '2': '⚔️', '3': '🧘', '4': '📚' }[key] || '🧑');
        const getDiffIcon = (key) => ({ '1': '🌟', '2': '🔥', '3': '☀️' }[key] || '🎯');
        const getEducationName = (edu) => ['高中', '本科', '硕士', '博士'][edu] || '高中';

        // API 调用
        const apiCall = async (endpoint, data = {}) => {
            try {
                const response = await fetch(API_BASE + endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (e) {
                console.error('API调用失败:', e);
                return { success: false, error: e.message };
            }
        };

        // 加载配置
        const loadConfig = async () => {
            try {
                const response = await fetch(API_BASE + '/api/config');
                if (response.ok) {
                    const data = await response.json();
                    Object.assign(config, data);
                }
            } catch (e) {
                console.log('使用默认配置');
            }
            
            // 默认配置
            if (Object.keys(config.backgrounds).length === 0) {
                Object.assign(config, {
                    backgrounds: {
                        '1': { name: '小镇青年', money: 5000, happiness: 70, career: 20 },
                        '2': { name: '城市中产', money: 50000, happiness: 60, career: 50 },
                        '3': { name: '富二代', money: 200000, happiness: 80, career: 30 },
                        '4': { name: '农村出身', money: 2000, happiness: 60, career: 10 }
                    },
                    talents: {
                        '1': { name: '学习天赋', desc: '考试成功率+30%' },
                        '2': { name: '社交达人', desc: '人际关系+20%' },
                        '3': { name: '财运亨通', desc: '金钱收益+30%' },
                        '4': { name: '健康体质', desc: '健康衰减-50%' },
                        '5': { name: '天选之人', desc: '所有属性+10%' }
                    },
                    personalities: {
                        '1': { name: '稳健型', desc: '风险-20%' },
                        '2': { name: '冒险型', desc: '高风险高回报+30%' },
                        '3': { name: '佛系型', desc: '快乐衰减-30%' },
                        '4': { name: '卷王', desc: '事业+20%, 快乐-10%' }
                    },
                    difficulties: {
                        '1': { name: '普通模式', turningRate: 0.9 },
                        '2': { name: '硬核模式', turningRate: 0.7 },
                        '3': { name: '休闲模式', turningRate: 1.0 }
                    },
                    achievements: [
                        { id: 'millionaire', name: '百万富翁', icon: '💰' },
                        { id: 'centenarian', name: '百岁老人', icon: '🎂' },
                        { id: 'winner', name: '人生赢家', icon: '🏆' },
                        { id: 'survivor', name: '绝境逢生', icon: '🌟' },
                        { id: 'married', name: '结婚', icon: '💑' },
                        { id: 'family', name: '儿女成群', icon: '👨‍👩‍👧‍👦' },
                        { id: 'homeowner', name: '有房一族', icon: '🏠' },
                        { id: 'petOwner', name: '铲屎官', icon: '🐱' },
                    ]
                });
            }
        };

        // 游戏操作
        const startNewGame = () => {
            currentScreen.value = 'create';
        };

        const confirmCreate = async () => {
            if (!newGameData.name.trim()) {
                alert('请输入名字！');
                return;
            }

            const result = await apiCall('/api/new_game', newGameData);
            
            if (result.success) {
                Object.assign(gameState, result.game);
                currentScreen.value = 'game';
                saveGame();
            } else {
                // 本地模式
                initLocalGame();
            }
        };

        const initLocalGame = () => {
            const bg = config.backgrounds[newGameData.background];
            gameState.name = newGameData.name;
            gameState.background = newGameData.background;
            gameState.talent = newGameData.talent;
            gameState.personality = newGameData.personality;
            gameState.difficulty = newGameData.difficulty;
            gameState.money = bg.money;
            gameState.happiness = bg.happiness;
            gameState.career = bg.career;
            gameState.age = 18;
            gameState.education = 0;
            gameState.year = 1;
            gameState.isGameOver = false;
            gameState.achievements = [];
            gameState.timeline = [{ age: 18, event: '开启人生旅程' }];
            gameState.spouse = null;
            gameState.children = [];
            gameState.house = false;
            gameState.car = 'none';
            gameState.pet = false;
            gameState.keyEvents = [];
            
            currentScreen.value = 'game';
            saveGame();
        };

        const continueGame = () => {
            const saved = localStorage.getItem('lifeSimulatorSave');
            if (saved) {
                Object.assign(gameState, JSON.parse(saved));
                currentScreen.value = 'game';
            }
        };

        const nextYear = async () => {
            if (gameState.isGameOver) return;

            const result = await apiCall('/api/next_year', {});

            if (result.success) {
                Object.assign(gameState, result.game);
                
                if (result.result.type === 'turning') {
                    showEventModal('🌟 转折点', result.result.desc || result.result.title, [
                        { text: '感谢命运', effect: {} }
                    ]);
                } else if (result.result.type === 'key_choice') {
                    showKeyChoiceModal(result.result);
                } else if (result.result.type === 'game_over') {
                    showSummary(result.result);
                    return;
                }
                
                if (result.newAchievements?.length) {
                    result.newAchievements.forEach(a => showAchievementNotification(a));
                }
            } else {
                nextYearLocal();
            }

            saveGame();
        };

        const nextYearLocal = () => {
            gameState.year++;
            gameState.age++;

            let healthChange = -random(2, 8);
            let happinessChange = -random(2, 8);

            if (gameState.personality === '3') happinessChange *= 0.7;
            if (gameState.talent === '4') healthChange *= 0.5;
            if (gameState.pet) happinessChange += 5;
            if (gameState.house) happinessChange += 5;

            gameState.health = clamp(gameState.health + healthChange);
            gameState.happiness = clamp(gameState.happiness + happinessChange);
            gameState.career = clamp(gameState.career + random(-2, 5));

            const baseIncome = [100, 200, 350, 500][gameState.education] || 100;
            let income = baseIncome * (1 + gameState.career / 100);
            if (gameState.job) income *= 1.5;
            if (gameState.talent === '3') income *= 1.3;

            gameState.money += Math.floor(income);
            gameState.timeline.push({ age: gameState.age, event: `年收入 ${formatMoney(Math.floor(income))}` });

            // 关键年龄事件
            checkKeyAgeEventsLocal();

            // 检测死亡
            if (gameState.health <= 0) {
                if (Math.random() < 0.9) {
                    gameState.health = 30;
                    gameState.turningPoints++;
                    showEventModal('🌟 绝境逢生', '你生命力顽强，从死亡线上挺了过来！', [
                        { text: '感谢命运', effect: {} }
                    ]);
                } else {
                    gameState.isGameOver = true;
                    showSummary({ age: gameState.age, reason: '因病去世' });
                    return;
                }
            }

            // 检查成就
            checkLocalAchievements();
        };

        const checkKeyAgeEventsLocal = () => {
            // 高考
            if (gameState.age === 18 && gameState.education === 0 && !gameState.keyEvents.includes('gaokao')) {
                showEventModal('🎓 高考', '你高中毕业了，面临人生第一次大考！', [
                    { text: '📚 努力备考', effect: { money: -5000 }, special: 'gaokao' },
                    { text: '💰 直接打工', effect: { money: 5000 } }
                ]);
                gameState.keyEvents.push('gaokao');
                return;
            }
            
            // 考研
            if (gameState.age === 22 && gameState.education === 1 && !gameState.keyEvents.includes('kaoyan')) {
                showEventModal('🎓 大学毕业', '本科毕业了！', [
                    { text: '📚 考研深造', effect: { money: -20000 }, special: 'kaoyan' },
                    { text: '💼 直接工作', effect: { happiness: 10 }, special: 'find_job' }
                ]);
                gameState.keyEvents.push('kaoyan');
                return;
            }
            
            // 考博
            if (gameState.age === 28 && gameState.education === 2 && !gameState.keyEvents.includes('kaobo')) {
                showEventModal('🎓 硕士毕业', '硕士毕业了！', [
                    { text: '📚 考博深造', effect: { money: -30000 }, special: 'kaobo' },
                    { text: '💼 直接工作', effect: { happiness: 10 }, special: 'find_job' }
                ]);
                gameState.keyEvents.push('kaobo');
                return;
            }
        };

        // 事件处理
        const showEventModal = (title, desc, choices) => {
            modalTitle.value = title;
            modalDesc.value = desc;
            modalChoices.value = choices;
            modalType.value = '事件';
            showModal.value = true;
        };

        const showKeyChoiceModal = (keyChoiceData) => {
            const age = keyChoiceData.age;
            let title = `🎯 ${age}岁 - 人生选择`;
            let desc = '';
            
            if (age === 18) desc = '高考结束，你面临人生第一个重大选择！';
            else if (age === 22) desc = '本科毕业，面临人生选择！';
            else if (age === 25) desc = '职业定型前，需要做出选择...';
            else if (age === 35) desc = '中年危机来临...';
            else if (age === 50) desc = '人生下半场...';

            modalTitle.value = title;
            modalDesc.value = desc;
            modalChoices.value = keyChoiceData.choices.map(c => ({
                text: c.text,
                effect: c.effect || {},
                special: c.special || ''
            }));
            modalType.value = '🎯 选择';
            showModal.value = true;
        };

        const handleChoice = async (idx) => {
            const choice = modalChoices.value[idx];
            showModal.value = false;

            // 执行效果
            if (choice.effect) {
                if (choice.effect.money) gameState.money += choice.effect.money;
                if (choice.effect.health) gameState.health = clamp(gameState.health + choice.effect.health);
                if (choice.effect.happiness) gameState.happiness = clamp(gameState.happiness + choice.effect.happiness);
                if (choice.effect.career) gameState.career = clamp(gameState.career + choice.effect.career);
            }

            // 处理特殊事件
            if (choice.special === 'gaokao') {
                const talentBonus = gameState.talent === '1' ? 0.3 : 0;
                if (Math.random() < 0.5 + talentBonus) {
                    gameState.education = 1;
                    gameState.happiness = clamp(gameState.happiness + 30);
                    gameState.timeline.push({ age: gameState.age, event: '🎓 考上大学！' });
                    showEventModal('🎓 高考录取', '恭喜你被大学录取了！', [{ text: '太棒了', effect: {} }]);
                } else {
                    gameState.happiness = clamp(gameState.happiness - 20);
                    gameState.timeline.push({ age: gameState.age, event: '🎓 高考落榜...' });
                    showEventModal('🎓 高考落榜', '很遗憾，你没有考上大学...', [{ text: '再接再厉', effect: {} }]);
                }
                saveGame();
                return;
            }

            if (choice.special === 'kaoyan') {
                const talentBonus = gameState.talent === '1' ? 0.3 : 0;
                if (Math.random() < 0.4 + talentBonus) {
                    gameState.education = 2;
                    gameState.happiness = clamp(gameState.happiness + 30);
                    gameState.timeline.push({ age: gameState.age, event: '🎓 考上研究生！' });
                    showEventModal('🎓 考研录取', '恭喜你被研究生录取了！', [{ text: '太棒了', effect: {} }]);
                } else {
                    gameState.happiness = clamp(gameState.happiness - 15);
                    gameState.timeline.push({ age: gameState.age, event: '🎓 考研落榜...' });
                    showEventModal('🎓 考研落榜', '很遗憾，你没有考上研究生...', [{ text: '再接再厉', effect: {} }]);
                }
                saveGame();
                return;
            }

            if (choice.special === 'kaobo') {
                const talentBonus = gameState.talent === '1' ? 0.3 : 0;
                if (Math.random() < 0.3 + talentBonus) {
                    gameState.education = 3;
                    gameState.happiness = clamp(gameState.happiness + 30);
                    gameState.timeline.push({ age: gameState.age, event: '🎓 考上博士！' });
                    showEventModal('🎓 考博录取', '恭喜你被博士录取了！', [{ text: '太棒了', effect: {} }]);
                } else {
                    gameState.happiness = clamp(gameState.happiness - 15);
                    gameState.timeline.push({ age: gameState.age, event: '🎓 考博落榜...' });
                    showEventModal('🎓 考博落榜', '很遗憾，你没有考上博士...', [{ text: '再接再厉', effect: {} }]);
                }
                saveGame();
                return;
            }

            if (choice.special === 'find_job') {
                findNewJob();
                return;
            }

            saveGame();
        };

        const closeModal = () => {
            showModal.value = false;
        };

        const showSummary = (result) => {
            currentScreen.value = 'summary';
        };

        // 快速操作
        const hospital = async () => {
            if (gameState.money < 2000) {
                showEventModal('💰 钱不够', '去医院需要2000元！', [{ text: '好吧', effect: {} }]);
                return;
            }
            gameState.money -= 2000;
            const gain = random(15, 35);
            gameState.health = clamp(gameState.health + gain);
            showEventModal('🏥 医院', `治疗完成，健康+${gain}`, [{ text: '谢谢医生', effect: {} }]);
            saveGame();
        };

        const psychologist = async () => {
            if (gameState.money < 1000) {
                showEventModal('💰 钱不够', '看心理医生需要1000元！', [{ text: '好吧', effect: {} }]);
                return;
            }
            gameState.money -= 1000;
            const gain = random(10, 25);
            gameState.happiness = clamp(gameState.happiness + gain);
            showEventModal('🧠 心理医生', `咨询完成，快乐+${gain}`, [{ text: '舒服多了', effect: {} }]);
            saveGame();
        };

        const lottery = async () => {
            if (gameState.money < 10) {
                showEventModal('💰 钱不够', '买彩票需要10元！', [{ text: '好吧', effect: {} }]);
                return;
            }
            gameState.money -= 10;
            const rand = Math.random();
            let prize = 0, msg = '';
            if (rand < 0.005) { prize = 100000; msg = '恭喜中一等奖10万元！'; gameState.happiness = clamp(gameState.happiness + 80); }
            else if (rand < 0.015) { prize = 10000; msg = '恭喜中二等奖1万元！'; gameState.happiness = clamp(gameState.happiness + 40); }
            else if (rand < 0.05) { prize = 1000; msg = '恭喜中三等奖1000元！'; gameState.happiness = clamp(gameState.happiness + 20); }
            else msg = '很遗憾，没有中奖...';
            gameState.money += prize;
            showEventModal('🎰 彩票', msg, [{ text: prize > 0 ? '太棒了！' : '继续努力', effect: {} }]);
            saveGame();
        };

        const showDating = () => {
            if (gameState.spouse) {
                showEventModal('💕 已婚', '你已经结婚了！', [{ text: '知道啦', effect: {} }]);
                return;
            }
            if (gameState.money < 500) {
                showEventModal('💰 钱不够', '相亲需要500元！', [{ text: '好吧', effect: {} }]);
                return;
            }
            gameState.money -= 500;
            const talentBonus = gameState.talent === '2' ? 0.2 : 0;
            if (Math.random() < 0.3 + talentBonus) {
                const names = ['小美', '小红', '小丽', '小芳', '小明', '小张'];
                gameState.spouse = names[random(0, names.length - 1)];
                gameState.happiness = clamp(gameState.happiness + 20);
                gameState.timeline.push({ age: gameState.age, event: `💑 遇到${gameState.spouse}` });
                
                if (Math.random() < 0.4) {
                    gameState.children.push({ name: ['小明', '小红', '小华'][random(0, 2)], age: 0 });
                    gameState.happiness = clamp(gameState.happiness + 10);
                    gameState.timeline.push({ age: gameState.age, event: '👶 有了孩子' });
                }
                showEventModal('💕 相亲成功', `你们互相产生了好感，决定交往！`, [{ text: '太好了', effect: {} }]);
            } else {
                showEventModal('💕 相亲', '没有遇到合适的人...', [{ text: '再接再厉', effect: {} }]);
            }
            saveGame();
        };

        const buyHouse = () => {
            if (gameState.house) {
                showEventModal('🏠 已有房', '你已经有房子了！', [{ text: '知道啦', effect: {} }]);
                return;
            }
            if (gameState.money < 100000) {
                showEventModal('💰 钱不够', '买房需要10万元！', [{ text: '好吧', effect: {} }]);
                return;
            }
            gameState.money -= 100000;
            gameState.house = true;
            gameState.happiness = clamp(gameState.happiness + 30);
            gameState.timeline.push({ age: gameState.age, event: '🏠 买房' });
            showEventModal('🏠 买房', '恭喜你买了新房子！', [{ text: '开心', effect: {} }]);
            saveGame();
        };

        const getPet = () => {
            if (gameState.pet) {
                showEventModal('🐱 已有宠物', '你已经有宠物了！', [{ text: '知道啦', effect: {} }]);
                return;
            }
            if (gameState.money < 3000) {
                showEventModal('💰 钱不够', '养宠物需要3000元！', [{ text: '好吧', effect: {} }]);
                return;
            }
            gameState.money -= 3000;
            gameState.pet = true;
            gameState.happiness = clamp(gameState.happiness + 20);
            gameState.timeline.push({ age: gameState.age, event: '🐱 养宠物' });
            showEventModal('🐱 养宠物', '你领养了一只可爱的小猫！', [{ text: '喵~', effect: {} }]);
            saveGame();
        };

        const travel = () => {
            const trips = [
                { name: '周边游', cost: 3000, happiness: 10 },
                { name: '国内游', cost: 8000, happiness: 20 },
                { name: '出境游', cost: 30000, happiness: 30 }
            ];
            const trip = trips[random(0, 2)];
            if (gameState.money < trip.cost) {
                showEventModal('💰 钱不够', `去${trip.name}需要${trip.cost}元！`, [{ text: '好吧', effect: {} }]);
                return;
            }
            gameState.money -= trip.cost;
            gameState.happiness = clamp(gameState.happiness + trip.happiness);
            gameState.timeline.push({ age: gameState.age, event: `✈️ ${trip.name}` });
            showEventModal('✈️ 旅行', `去${trip.name}玩了一圈，心情愉快！`, [{ text: '开心', effect: {} }]);
            saveGame();
        };

        const showStock = () => {
            showEventModal('📈 股票投资', '请选择投资金额', [
                { text: '10% 💵', action: () => investStock(0.1) },
                { text: '20% 💵', action: () => investStock(0.2) },
                { text: '50% 💰', action: () => investStock(0.5) },
                { text: '全部梭哈！🎲', action: () => investStock(1.0) },
                { text: '不投了', effect: {} }
            ]);
        };

        const investStock = (percent) => {
            const amount = Math.floor(gameState.money * percent);
            if (amount <= 0) {
                showEventModal('📈 股票', '没有足够的资金投资！', [{ text: '好吧', effect: {} }]);
                return;
            }
            const change = random(-30, 50) / 100;
            const profit = Math.floor(amount * change);
            gameState.money += profit;
            showEventModal('📈 股票', profit >= 0 ? `股票赚了${formatMoney(profit)}！` : `股票赔了${formatMoney(-profit)}...`, [{ text: '知道了', effect: {} }]);
            saveGame();
        };

        const showJobSearch = () => {
            if (gameState.job) {
                showEventModal('💼 换工作', `你目前的工作是：${gameState.job}，要换一份工作吗？`, [
                    { text: '换工作 🔄', action: () => findNewJob() },
                    { text: '不换了', effect: {} }
                ]);
            } else {
                findNewJob();
            }
        };

        const findNewJob = () => {
            const career = gameState.career;
            let jobPool = [];
            
            if (career < 30) jobPool = ['工人', '服务员', '司机', '快递员', '保安'];
            else if (career < 60) jobPool = ['教师', '会计', '程序员', '公务员', '销售', '设计师'];
            else jobPool = ['医生', '律师', '经理', '高管', '创业者', '网红'];
            
            if (gameState.education >= 1) jobPool = jobPool.concat(['工程师', '研究员']);
            if (gameState.education >= 2) jobPool = jobPool.concat(['教授', '专家', '顾问']);

            gameState.job = jobPool[random(0, jobPool.length - 1)];
            const careerBonus = Math.floor(career * 0.5);
            gameState.happiness = clamp(gameState.happiness + 15 + careerBonus);
            gameState.timeline.push({ age: gameState.age, event: `💼 成为${gameState.job}` });
            showEventModal('💼 找到工作', `你找到了 ${gameState.job} 的工作！事业值越高，收入加成越多！`, [{ text: '太好了', effect: {} }]);
            saveGame();
        };

        // 成就系统
        const checkLocalAchievements = () => {
            const achievements = [
                { id: 'millionaire', condition: () => gameState.money >= 1000000 },
                { id: 'centenarian', condition: () => gameState.age >= 100 },
                { id: 'winner', condition: () => gameState.money >= 100000 && gameState.happiness >= 80 && gameState.career >= 80 },
                { id: 'survivor', condition: () => gameState.turningPoints >= 5 },
                { id: 'married', condition: () => gameState.spouse != null },
                { id: 'family', condition: () => gameState.children.length >= 3 },
                { id: 'homeowner', condition: () => gameState.house === true },
                { id: 'petOwner', condition: () => gameState.pet === true },
            ];
            
            achievements.forEach(ach => {
                if (!gameState.achievements) gameState.achievements = [];
                if (!gameState.achievements.includes(ach.id) && ach.condition()) {
                    gameState.achievements.push(ach.id);
                    const configAch = config.achievements.find(a => a.id === ach.id);
                    if (configAch) showAchievementNotification(configAch);
                }
            });
        };

        const showAchievementNotification = (achievement) => {
            const notification = document.createElement('div');
            notification.className = 'achievement-notification';
            notification.innerHTML = `<span class="achievement-icon">${achievement.icon}</span><span class="achievement-text">解锁成就: ${achievement.name}</span>`;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 3000);
        };

        // 存档
        const saveGame = () => {
            localStorage.setItem('lifeSimulatorSave', JSON.stringify(gameState));
        };

        const resetGame = () => {
            localStorage.removeItem('lifeSimulatorSave');
            currentScreen.value = 'welcome';
            hasSave.value = false;
            Object.assign(newGameData, {
                name: '',
                background: '1',
                talent: '1',
                personality: '1',
                difficulty: '1'
            });
        };

        // 初始化
        onMounted(async () => {
            await loadConfig();
            const saved = localStorage.getItem('lifeSimulatorSave');
            if (saved) hasSave.value = true;
        });

        return {
            // 状态
            currentScreen,
            hasSave,
            showModal,
            modalTitle,
            modalDesc,
            modalChoices,
            modalType,
            newGameData,
            gameState,
            config,
            
            // 计算属性
            unlockedAchievements,
            totalAchievements,
            summaryMessage,
            
            // 方法
            formatMoney,
            getBgIcon,
            getPersIcon,
            getDiffIcon,
            getEducationName,
            startNewGame,
            confirmCreate,
            continueGame,
            nextYear,
            handleChoice,
            closeModal,
            showSummary,
            hospital,
            psychologist,
            lottery,
            showDating,
            buyHouse,
            getPet,
            travel,
            showStock,
            showJobSearch,
            resetGame,
            Math
        };
    }
}).mount('#app');

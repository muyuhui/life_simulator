// ====== 熬过去 - 人生模拟器 Web版 ======
// 整合后端API服务

const API_BASE = ''; // 如果后端分离可修改

// 游戏状态
let gameState = {
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
    timeline: [{ age: 18, event: '开启人生旅程' }],
    spouse: null,
    children: [],
    house: false,
    pet: false,
    countries: [],
    turningPoints: 0,
    lifeLabels: []
};

// 配置数据
let config = {
    backgrounds: {},
    talents: {},
    personalities: {},
    difficulties: {},
    jobs: {},
    educations: {},
    achievements: []
};

// ====== 工具函数 ======
function $(id) { return document.getElementById(id); }

function random(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function formatMoney(amount) {
    if (amount >= 10000) return (amount / 10000).toFixed(1) + '万';
    return amount.toString();
}

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    $(screenId).classList.add('active');
}

// ====== API调用 ======
async function apiCall(endpoint, data = {}) {
    try {
        const response = await fetch(API_BASE + endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await response.json();
    } catch (e) {
        console.error('API调用失败:', e);
        // 降级到本地模式
        return { success: false, error: e.message };
    }
}

async function loadConfig() {
    const response = await fetch(API_BASE + '/api/config');
    if (response.ok) {
        config = await response.json();
    }
}

// ====== 界面函数 ======
function showCreateCharacter() {
    // 填充配置选项
    const bgContainer = $('background-select');
    bgContainer.innerHTML = Object.entries(config.backgrounds).map(([k, v]) => 
        `<div class="option-card" data-value="${k}" onclick="selectOption(this, 'background')">
            <div class="option-icon">${k === '1' ? '🏘️' : k === '2' ? '🏙️' : k === '3' ? '💎' : '🌾'}</div>
            <div class="option-name">${v.name}</div>
            <div class="option-stats">💰${formatMoney(v.money)} | 😊${v.happiness} | 💼${v.career}</div>
        </div>`
    ).join('');

    const talentContainer = $('talent-select');
    talentContainer.innerHTML = Object.entries(config.talents).map(([k, v]) => 
        `<div class="option-card" data-value="${k}" onclick="selectOption(this, 'talent')">
            <div class="option-icon">📚</div>
            <div class="option-name">${v.name}</div>
            <div class="option-desc">${v.desc}</div>
        </div>`
    ).join('');

    const persContainer = $('personality-select');
    persContainer.innerHTML = Object.entries(config.personalities).map(([k, v]) => 
        `<div class="option-card" data-value="${k}" onclick="selectOption(this, 'personality')">
            <div class="option-icon">${k === '1' ? '🛡️' : k === '2' ? '⚔️' : k === '3' ? '🧘' : '📚'}</div>
            <div class="option-name">${v.name}</div>
            <div class="option-desc">${v.desc}</div>
        </div>`
    ).join('');

    const diffContainer = $('difficulty-select');
    if (diffContainer) {
        diffContainer.innerHTML = Object.entries(config.difficulties).map(([k, v]) => 
            `<div class="option-card ${k === '1' ? 'selected' : ''}" data-value="${k}" onclick="selectOption(this, 'difficulty')">
                <div class="option-icon">${k === '1' ? '🌟' : k === '2' ? '🔥' : '☀️'}</div>
                <div class="option-name">${v.name}</div>
                <div class="option-desc">转机率${v.turningRate * 100}%</div>
            </div>`
        ).join('');
    }

    showScreen('create-screen');
}

function selectOption(element, type) {
    const container = element.parentElement;
    container.querySelectorAll('.option-card').forEach(card => card.classList.remove('selected'));
    element.classList.add('selected');

    if (type === 'background') gameState.background = element.dataset.value;
    if (type === 'talent') gameState.talent = element.dataset.value;
    if (type === 'personality') gameState.personality = element.dataset.value;
    if (type === 'difficulty') gameState.difficulty = element.dataset.value;
}

async function startGame() {
    const name = $('player-name').value.trim();
    if (!name) { alert('请输入名字！'); return; }

    const bg = $('background-select').querySelector('.selected');
    const talent = $('talent-select').querySelector('.selected');
    const pers = $('personality-select').querySelector('.selected');
    const diff = $('difficulty-select')?.querySelector('.selected');

    if (!bg || !talent || !pers) { alert('请完成选择！'); return; }

    const result = await apiCall('/api/new_game', {
        name: name,
        background: bg.dataset.value,
        talent: talent.dataset.value,
        personality: pers.dataset.value,
        difficulty: diff ? diff.dataset.value : '1'
    });

    if (result.success) {
        gameState = result.game;
        updateDisplay();
        showScreen('game-screen');
        checkAchievements();
    } else {
        // 本地模式降级
        initLocalGame(name, bg.dataset.value, talent.dataset.value, pers.dataset.value, diff?.dataset.value || '1');
    }
}

function initLocalGame(name, bg, talent, pers, diff) {
    gameState = {
        name: name,
        age: 18,
        background: bg,
        talent: talent,
        personality: pers,
        difficulty: diff,
        money: parseInt(config.backgrounds[bg]?.money || 5000),
        health: 80,
        happiness: parseInt(config.backgrounds[bg]?.happiness || 70),
        career: parseInt(config.backgrounds[bg]?.career || 20),
        education: 0,
        job: null,
        year: 1,
        isGameOver: false,
        achievements: [],
        events: [],
        timeline: [{ age: 18, event: '开启人生旅程' }],
        spouse: null,
        children: [],
        house: false,
        pet: false,
        countries: [],
        turningPoints: 0,
        lifeLabels: []
    };
    updateDisplay();
    showScreen('game-screen');
    saveGame();
}

function updateDisplay() {
    $('player-name-display').textContent = gameState.name;
    $('age-display').textContent = gameState.age + '岁';

    const eduNames = ['高中', '本科', '硕士', '博士'];
    $('education-display').textContent = eduNames[gameState.education] || '高中';
    $('job-display').textContent = gameState.job || '待业';

    $('money-display').textContent = formatMoney(gameState.money);
    $('health-display').textContent = gameState.health;
    $('happiness-display').textContent = gameState.happiness;
    $('career-display').textContent = gameState.career;

    $('money-bar').style.width = Math.min(100, gameState.money / 10000) + '%';
    $('health-bar').style.width = gameState.health + '%';
    $('happiness-bar').style.width = gameState.happiness + '%';
    $('career-bar').style.width = gameState.career + '%';

    // 更新状态指示器
    const spouseEl = $('status-spouse');
    const childrenEl = $('status-children');
    const houseEl = $('status-house');
    const petEl = $('status-pet');
    const carEl = $('status-car');
    
    if (gameState.spouse) {
        spouseEl.style.display = 'flex';
        const spouseType = gameState.spouseType ? `(${gameState.spouseType})` : '';
        spouseEl.textContent = `💑 ${gameState.spouse}${spouseType}`;
    } else {
        spouseEl.style.display = 'none';
    }
    
    if (gameState.children?.length > 0) {
        childrenEl.style.display = 'flex';
        childrenEl.textContent = `👶 ${gameState.children.length}个孩子`;
    } else {
        childrenEl.style.display = 'none';
    }
    
    if (gameState.house) {
        houseEl.style.display = 'flex';
        const houseTypes = { 'small': '小户型', 'large': '大户型', 'villa': '别墅' };
        houseEl.textContent = `🏠 ${houseTypes[gameState.houseType] || '有房'}`;
    } else {
        houseEl.style.display = 'none';
    }
    
    if (gameState.car && gameState.car !== 'none') {
        carEl.style.display = 'flex';
        const carTypes = { 'economy': '代步车', 'luxury': '豪车' };
        carEl.textContent = `🚗 ${carTypes[gameState.car] || '有车'}`;
    } else {
        carEl.style.display = 'none';
    }
    
    if (gameState.pet) {
        petEl.style.display = 'flex';
        petEl.textContent = '🐱 有宠';
    } else {
        petEl.style.display = 'none';
    }

    updateTimeline();
    updateAchievementsDisplay();
}

function updateTimeline() {
    const timeline = $('timeline');
    timeline.innerHTML = gameState.timeline.slice(-10).map(item => 
        `<div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
                <span class="timeline-age">${item.age}岁</span>
                <span class="timeline-event">${item.event}</span>
            </div>
        </div>`
    ).join('');
}

function updateAchievementsDisplay() {
    const container = $('achievements');
    const unlocked = gameState.achievements;
    
    container.innerHTML = config.achievements.map(a => 
        `<div class="achievement ${unlocked.includes(a.id) ? 'unlocked' : 'locked'}">
            <span class="achievement-icon">${a.icon}</span>
            <span class="achievement-name">${a.name}</span>
        </div>`
    ).join('');
}

async function nextYear() {
    if (gameState.isGameOver) return;

    const result = await apiCall('/api/next_year', {});

    if (result.success) {
        gameState = result.game;
        
        if (result.result.type === 'turning') {
            showTurningPoint(result.result);
        } else if (result.result.type === 'game_over') {
            showGameOver(result.result);
            return;
        } else if (result.result.type === 'key_choice') {
            showKeyChoiceModal(result.result);
        } else if (result.result.type === 'small_event') {
            showSmallEvent(result.result.event);
        } else if (result.result.type === 'holiday') {
            showHolidayEvent(result.result.event);
        } else if (result.result.type === 'normal_event') {
            showEventModal(result.result.event);
        }
        
        if (result.newAchievements?.length) {
            result.newAchievements.forEach(a => showAchievementNotification(a));
        }
    } else {
        // 本地模式
        nextYearLocal();
    }

    updateDisplay();
    saveGame();
}

function nextYearLocal() {
    gameState.year++;
    gameState.age++;

    let healthChange = -random(2, 8);
    let happinessChange = -random(2, 8);

    if (gameState.pet) happinessChange += 5;
    if (gameState.house) happinessChange += 5;

    gameState.health = Math.max(0, Math.min(100, gameState.health + healthChange));
    gameState.happiness = Math.max(0, Math.min(100, gameState.happiness + happinessChange));
    gameState.career = Math.max(0, Math.min(100, gameState.career + random(-2, 5)));

    const baseIncome = [100, 200, 350, 500][gameState.education] || 100;
    let income = baseIncome * (1 + gameState.career / 100);
    
    if (gameState.job) income *= 1.5;
    if (gameState.talent === '3') income *= 1.3;

    gameState.money += Math.floor(income);
    gameState.timeline.push({ age: gameState.age, event: `年收入 ${formatMoney(Math.floor(income))}` });

    // 30%概率随机事件
    if (Math.random() < 0.3) {
        const events = [
            { title: '工作表现好', effect: { career: 5, money: 1000 } },
            { title: '朋友聚会', effect: { money: -500, happiness: 15 } },
            { title: '身体检查', effect: { health: random(-5, 10) } },
        ];
        const event = events[random(0, events.length - 1)];
        if (event.effect.money) gameState.money += event.effect.money;
        if (event.effect.health) gameState.health = Math.max(0, Math.min(100, gameState.health + event.effect.health));
        if (event.effect.happiness) gameState.happiness = Math.max(0, Math.min(100, gameState.happiness + event.effect.happiness));
        if (event.effect.career) gameState.career = Math.max(0, Math.min(100, gameState.career + event.effect.career));
        gameState.timeline.push({ age: gameState.age, event: event.title });
    }

    // 检测死亡
    if (gameState.health <= 0) {
        if (Math.random() < 0.9) {
            gameState.health = 30;
            showTurningPoint({ title: '绝境逢生', desc: '你生命力顽强，从死亡线上挺了过来！', effects: { health: 30 } });
        } else {
            gameState.isGameOver = true;
            showGameOver({ reason: '因病去世', age: gameState.age });
            return;
        }
    }

    // 检测关键年龄事件 - 高考/考研/考博
    if (gameState.age === 18 && gameState.education === 0 && !gameState.keyEvents?.includes('gaokao')) {
        showEventModal({
            title: '🎓 高考',
            desc: '你高中毕业了，面临人生第一次大考！选择备考需要花费5000元，但有50%概率考上大学',
            choices: [
                { text: '📚 努力备考 - 高考', effect: { money: -5000 }, special: 'gaokao' },
                { text: '💰 直接打工', effect: { money: 5000 } }
            ]
        });
        gameState.keyEvents = gameState.keyEvents || [];
        gameState.keyEvents.push('gaokao');
    } else if (gameState.age === 22 && gameState.education === 1 && !gameState.keyEvents?.includes('kaoyan')) {
        // 本科毕业
        showEventModal({
            title: '🎓 大学毕业',
            desc: '本科毕业了！选择考研需要花费20000元，有40%概率考上研究生',
            choices: [
                { text: '📚 考研深造', effect: { money: -20000 }, special: 'kaoyan' },
                { text: '💼 直接工作', effect: { happiness: 10 } }
            ]
        });
        gameState.keyEvents = gameState.keyEvents || [];
        gameState.keyEvents.push('kaoyan');
    } else if (gameState.age === 28 && gameState.education === 2 && !gameState.keyEvents?.includes('kaobo')) {
        // 硕士毕业
        showEventModal({
            title: '🎓 硕士毕业',
            desc: '硕士毕业了！选择考博需要花费30000元，有30%概率考上博士',
            choices: [
                { text: '📚 考博深造', effect: { money: -30000 }, special: 'kaobo' },
                { text: '💼 直接工作', effect: { happiness: 10 } }
            ]
        });
        gameState.keyEvents = gameState.keyEvents || [];
        gameState.keyEvents.push('kaobo');
    }
    
    // 检查成就（本地模式）
    checkLocalAchievements();
}

// 本地模式成就检查
function checkLocalAchievements() {
    const achievements = [
        { id: 'millionaire', name: '百万富翁', icon: '💰', condition: () => gameState.money >= 1000000 },
        { id: 'centenarian', name: '百岁老人', icon: '🎂', condition: () => gameState.age >= 100 },
        { id: 'winner', name: '人生赢家', icon: '🏆', condition: () => gameState.money >= 100000 && gameState.happiness >= 80 && gameState.career >= 80 },
        { id: 'survivor', name: '绝境逢生', icon: '🌟', condition: () => (gameState.turningPoints || 0) >= 5 },
        { id: 'married', name: '结婚', icon: '💑', condition: () => gameState.spouse != null },
        { id: 'family', name: '儿女成群', icon: '👨‍👩‍👧‍👦', condition: () => (gameState.children?.length || 0) >= 3 },
        { id: 'homeowner', name: '有房一族', icon: '🏠', condition: () => gameState.house === true },
        { id: 'petOwner', name: '铲屎官', icon: '🐱', condition: () => gameState.pet === true },
        { id: 'carOwner', name: '有车一族', icon: '🚗', condition: () => gameState.car && gameState.car !== 'none' },
    ];
    
    achievements.forEach(ach => {
        if (!gameState.achievements) gameState.achievements = [];
        if (!gameState.achievements.includes(ach.id) && ach.condition()) {
            gameState.achievements.push(ach.id);
            showAchievementNotification(ach);
        }
    });
}

function showTurningPoint(result) {
    showEvent(result.title, result.desc, [{ text: '感谢命运', effect: {} }]);
    $('event-header').querySelector('.event-type').textContent = '🌟 转折点';
    $('event-header').style.borderColor = '#f59e0b';
}

function showEventModal(event) {
    $('event-title').textContent = event.title;
    $('event-desc').textContent = event.desc;
    
    const choicesContainer = $('event-choices');
    choicesContainer.innerHTML = event.choices.map((choice, idx) => 
        `<button class="event-choice-btn" onclick="handleChoice(${idx})">${choice.text}</button>`
    ).join('');
    
    window.currentEvent = event;
    $('event-modal').style.display = 'flex';
    $('event-header').style.borderColor = '';
}

async function handleChoice(idx) {
    const choice = window.currentEvent.choices[idx];
    $('event-modal').style.display = 'none';

    const result = await apiCall('/api/handle_choice', {
        effect: choice.effect || {},
        special: choice.special || ''
    });

    if (result.success) {
        gameState = result.game;
        if (result.result.type === 'turning') showTurningPoint(result.result);
        if (result.result.type === 'game_over') { showGameOver(result.result); return; }
    } else {
        // 本地处理
        if (choice.effect) {
            if (choice.effect.money) gameState.money += choice.effect.money;
            if (choice.effect.health) gameState.health = Math.max(0, Math.min(100, gameState.health + choice.effect.health));
            if (choice.effect.happiness) gameState.happiness = Math.max(0, Math.min(100, gameState.happiness + choice.effect.happiness));
            if (choice.effect.career) gameState.career = Math.max(0, Math.min(100, gameState.career + choice.effect.career));
        }
        
        // 处理特殊事件
        if (choice.special === 'gaokao') {
            // 高考
            const talentBonus = gameState.talent === '1' ? 0.3 : 0; // 学习天赋+30%
            const success = Math.random() < (0.5 + talentBonus);
            if (success) {
                gameState.education = 1;
                gameState.happiness = Math.min(100, gameState.happiness + 30);
                gameState.timeline.push({ age: gameState.age, event: '🎓 考上大学！' });
                showEvent('🎓 高考录取', '恭喜你被大学录取了！', [{ text: '太棒了', effect: {} }]);
            } else {
                gameState.happiness = Math.max(0, gameState.happiness - 20);
                gameState.timeline.push({ age: gameState.age, event: '🎓 高考落榜...' });
                showEvent('🎓 高考落榜', '很遗憾，你没有考上大学...', [{ text: '再接再厉', effect: {} }]);
            }
            updateDisplay();
            saveGame();
            return;
        }
        
        if (choice.special === 'kaoyan') {
            // 考研
            const talentBonus = gameState.talent === '1' ? 0.3 : 0;
            const success = Math.random() < (0.4 + talentBonus);
            if (success) {
                gameState.education = 2;
                gameState.happiness = Math.min(100, gameState.happiness + 30);
                gameState.timeline.push({ age: gameState.age, event: '🎓 考上研究生！' });
                showEvent('🎓 考研录取', '恭喜你被研究生录取了！', [{ text: '太棒了', effect: {} }]);
            } else {
                gameState.happiness = Math.max(0, gameState.happiness - 15);
                gameState.timeline.push({ age: gameState.age, event: '🎓 考研落榜...' });
                showEvent('🎓 考研落榜', '很遗憾，你没有考上研究生...', [{ text: '再接再厉', effect: {} }]);
            }
            updateDisplay();
            saveGame();
            return;
        }
        
        if (choice.special === 'kaobo') {
            // 考博
            const talentBonus = gameState.talent === '1' ? 0.3 : 0;
            const success = Math.random() < (0.3 + talentBonus);
            if (success) {
                gameState.education = 3;
                gameState.happiness = Math.min(100, gameState.happiness + 30);
                gameState.timeline.push({ age: gameState.age, event: '🎓 考上博士！' });
                showEvent('🎓 考博录取', '恭喜你被博士录取了！', [{ text: '太棒了', effect: {} }]);
            } else {
                gameState.happiness = Math.max(0, gameState.happiness - 15);
                gameState.timeline.push({ age: gameState.age, event: '🎓 考博落榜...' });
                showEvent('🎓 考博落榜', '很遗憾，你没有考上博士...', [{ text: '再接再厉', effect: {} }]);
            }
            updateDisplay();
            saveGame();
            return;
        }
        
        if (choice.special === 'find_job') {
            findNewJob();
            return;
        }
            if (success) {
                gameState.education = 2;
                gameState.happiness = Math.min(100, gameState.happiness + 30);
                gameState.timeline.push({ age: gameState.age, event: '🎓 考上研究生' });
                showEvent('🎓 考研录取', '恭喜你被研究生录取了！', [{ text: '太棒了', effect: {} }]);
            } else {
                gameState.happiness = Math.max(0, gameState.happiness - 15);
                gameState.timeline.push({ age: gameState.age, event: '🎓 考研落榜' });
                showEvent('🎓 考研落榜', '很遗憾，你没有考上研究生...', [{ text: '再接再厉', effect: {} }]);
            }
            updateDisplay();
            saveGame();
            return;
        }
    }

    updateDisplay();
    saveGame();
}

function showEvent(title, desc, choices) {
    $('event-title').textContent = title;
    $('event-desc').textContent = desc;
    
    $('event-choices').innerHTML = choices.map((c, i) => 
        `<button class="event-choice-btn" onclick="handleEventChoice(${i})">${c.text}</button>`
    ).join('');
    
    window.currentChoices = choices;
    $('event-modal').style.display = 'flex';
}

function handleEventChoice(idx) {
    const choice = window.currentChoices[idx];
    $('event-modal').style.display = 'none';
    
    if (choice.action) {
        // 有自定义 action，执行它
        choice.action();
    } else if (choice.effect) {
        // 执行效果并更新
        if (choice.effect.money) gameState.money += choice.effect.money;
        if (choice.effect.health) gameState.health = Math.max(0, Math.min(100, gameState.health + choice.effect.health));
        if (choice.effect.happiness) gameState.happiness = Math.max(0, Math.min(100, gameState.happiness + choice.effect.happiness));
        if (choice.effect.career) gameState.career = Math.max(0, Math.min(100, gameState.career + choice.effect.career));
        
        // 立即更新并保存
        updateDisplay();
        saveGame();
    }
}

function closeModal() {
    $('event-modal').style.display = 'none';
}

function showGameOver(result) {
    gameState.isGameOver = true;
    showScreen('summary-screen');
    
    $('summary-name').textContent = gameState.name;
    $('summary-age').textContent = result.age + '岁';
    $('summary-money').textContent = formatMoney(gameState.money);
    $('summary-happiness').textContent = gameState.happiness;

    let message = '';
    if (result.age >= 100) message = '百岁老人，功德圆满！';
    else if (result.age >= 80) message = '安享晚年，福寿双全！';
    else if (gameState.money >= 1000000) message = '富甲一方，人生赢家！';
    else if (result.age < 30) message = '英年早逝，令人惋惜...';
    else message = '平凡而真实的人生。';
    
    $('summary-message').textContent = message;
}

// ====== 快速操作 ======
async function hospital() {
    const result = await apiCall('/api/hospital', {});
    if (result.success) {
        gameState = result.game;
        showEvent('🏥 医院', result.message, [{ text: '谢谢医生', effect: {} }]);
    } else {
        if (gameState.money < 2000) { showEvent('💰 钱不够', '去医院需要2000元！', [{ text: '好吧', effect: {} }]); return; }
        gameState.money -= 2000;
        const gain = random(15, 35);
        gameState.health = Math.min(100, gameState.health + gain);
        showEvent('🏥 医院', `治疗完成，健康+${gain}`, [{ text: '谢谢医生', effect: {} }]);
    }
    updateDisplay();
    saveGame();
}

async function psychologist() {
    const result = await apiCall('/api/psychologist', {});
    if (result.success) {
        gameState = result.game;
        showEvent('🧠 心理医生', result.message, [{ text: '舒服多了', effect: {} }]);
    } else {
        if (gameState.money < 1000) { showEvent('💰 钱不够', '看心理医生需要1000元！', [{ text: '好吧', effect: {} }]); return; }
        gameState.money -= 1000;
        const gain = random(10, 25);
        gameState.happiness = Math.min(100, gameState.happiness + gain);
        showEvent('🧠 心理医生', `咨询完成，快乐+${gain}`, [{ text: '舒服多了', effect: {} }]);
    }
    updateDisplay();
    saveGame();
}

async function lottery() {
    const result = await apiCall('/api/lottery', {});
    if (result.success) {
        gameState = result.game;
        showEvent('🎰 彩票', result.message, [{ text: result.prize > 0 ? '太棒了！' : '继续努力', effect: {} }]);
    } else {
        if (gameState.money < 10) { showEvent('💰 钱不够', '买彩票需要10元！', [{ text: '好吧', effect: {} }]); return; }
        gameState.money -= 10;
        const rand = Math.random();
        let prize = 0, msg = '';
        if (rand < 0.005) { prize = 100000; msg = '恭喜中一等奖10万元！'; gameState.happiness = Math.min(100, gameState.happiness + 80); }
        else if (rand < 0.015) { prize = 10000; msg = '恭喜中二等奖1万元！'; gameState.happiness = Math.min(100, gameState.happiness + 40); }
        else if (rand < 0.05) { prize = 1000; msg = '恭喜中三等奖1000元！'; gameState.happiness = Math.min(100, gameState.happiness + 20); }
        else msg = '很遗憾，没有中奖...';
        gameState.money += prize;
        showEvent('🎰 彩票', msg, [{ text: prize > 0 ? '太棒了！' : '继续努力', effect: {} }]);
    }
    updateDisplay();
    saveGame();
}

async function showDating() {
    if (gameState.spouse) { showEvent('💕 已婚', '你已经结婚了！', [{ text: '知道啦', effect: {} }]); return; }
    const result = await apiCall('/api/dating', {});
    if (result.success) {
        gameState = result.game;
        showEvent('💕 相亲', result.message, [{ text: '太好了', effect: {} }]);
    } else {
        if (gameState.money < 500) { showEvent('💰 钱不够', '相亲需要500元！', [{ text: '好吧', effect: {} }]); return; }
        gameState.money -= 500;
        if (Math.random() < 0.3) {
            const names = ['小美', '小红', '小丽', '小明'];
            gameState.spouse = names[random(0, names.length - 1)];
            gameState.happiness = Math.min(100, gameState.happiness + 20);
            gameState.timeline.push({ age: gameState.age, event: `💑 遇到${gameState.spouse}` });
            if (Math.random() < 0.4) {
                gameState.children.push({ name: '孩子', age: 0 });
                gameState.happiness = Math.min(100, gameState.happiness + 10);
                gameState.timeline.push({ age: gameState.age, event: '👶 有了孩子' });
            }
            showEvent('💕 相亲成功', `你们互相产生了好感，决定交往！`, [{ text: '太好了', effect: {} }]);
        } else {
            showEvent('💕 相亲', '没有遇到合适的人...', [{ text: '再接再厉', effect: {} }]);
        }
    }
    updateDisplay();
    saveGame();
}

async function buyHouse() {
    const result = await apiCall('/api/buy_house', {});
    if (result.success) {
        gameState = result.game;
        showEvent('🏠 买房', result.message, [{ text: '开心', effect: {} }]);
    } else {
        if (gameState.house) { showEvent('🏠 已有房', '你已经有房子了！', [{ text: '知道啦', effect: {} }]); return; }
        if (gameState.money < 100000) { showEvent('💰 钱不够', '买房需要10万元！', [{ text: '好吧', effect: {} }]); return; }
        gameState.money -= 100000;
        gameState.house = true;
        gameState.happiness = Math.min(100, gameState.happiness + 30);
        gameState.timeline.push({ age: gameState.age, event: '🏠 买房' });
        showEvent('🏠 买房', '恭喜你买了新房子！', [{ text: '开心', effect: {} }]);
    }
    updateDisplay();
    saveGame();
}

async function getPet() {
    const result = await apiCall('/api/get_pet', {});
    if (result.success) {
        gameState = result.game;
        showEvent('🐱 养宠物', result.message, [{ text: '喵~', effect: {} }]);
    } else {
        if (gameState.pet) { showEvent('🐱 已有宠物', '你已经有宠物了！', [{ text: '知道啦', effect: {} }]); return; }
        if (gameState.money < 3000) { showEvent('💰 钱不够', '养宠物需要3000元！', [{ text: '好吧', effect: {} }]); return; }
        gameState.money -= 3000;
        gameState.pet = true;
        gameState.happiness = Math.min(100, gameState.happiness + 20);
        gameState.timeline.push({ age: gameState.age, event: '🐱 养宠物' });
        showEvent('🐱 养宠物', '你领养了一只可爱的小猫！', [{ text: '喵~', effect: {} }]);
    }
    updateDisplay();
    saveGame();
}

async function travel() {
    const result = await apiCall('/api/travel', {});
    if (result.success) {
        gameState = result.game;
        showEvent('✈️ 旅行', result.message, [{ text: '开心', effect: {} }]);
    } else {
        const trips = [{ name: '周边游', cost: 3000, happiness: 10 }, { name: '国内游', cost: 8000, happiness: 20 }, { name: '出境游', cost: 30000, happiness: 30 }];
        const trip = trips[random(0, 2)];
        if (gameState.money < trip.cost) { showEvent('💰 钱不够', `去${trip.name}需要${trip.cost}元！`, [{ text: '好吧', effect: {} }]); return; }
        gameState.money -= trip.cost;
        gameState.happiness = Math.min(100, gameState.happiness + trip.happiness);
        gameState.timeline.push({ age: gameState.age, event: `✈️ ${trip.name}` });
        showEvent('✈️ 旅行', `去${trip.name}玩了一圈，心情愉快！`, [{ text: '开心', effect: {} }]);
    }
    updateDisplay();
    saveGame();
}

async function stock() {
    showEvent('📈 股票投资', '请选择投资金额', [
        { text: '10% 💵', action: () => investStock(0.1) },
        { text: '20% 💵', action: () => investStock(0.2) },
        { text: '50% 💰', action: () => investStock(0.5) },
        { text: '全部梭哈！🎲', action: () => investStock(1.0) },
        { text: '不投了', effect: {} }
    ]);
}

async function investStock(percent) {
    const result = await apiCall('/api/stock', { percent: percent });
    if (result.success) {
        gameState = result.game;
        showEvent('📈 股票', result.message, [{ text: '知道了', effect: {} }]);
    } else {
        const amount = Math.floor(gameState.money * percent);
        if (amount <= 0) { showEvent('📈 股票', '没有足够的资金投资！', [{ text: '好吧', effect: {} }]); return; }
        const change = random(-30, 50) / 100;
        const profit = Math.floor(amount * change);
        gameState.money += profit;
        showEvent('📈 股票', profit >= 0 ? `股票赚了${formatMoney(profit)}！` : `股票赔了${formatMoney(-profit)}...`, [{ text: '知道了', effect: {} }]);
    }
    updateDisplay();
    saveGame();
}

function showJobSearch() {
    if (gameState.job) {
        // 已有工作，询问是否换工作
        showEvent('💼 换工作', `你目前的工作是：${gameState.job}，要换一份工作吗？`, [
            { text: '换工作 🔄', action: () => changeJob() },
            { text: '不换了', effect: {} }
        ]);
    } else {
        // 没有工作，直接找工作
        findNewJob();
    }
}

function findNewJob() {
    // 职业由事业值决定，学历加成概率
    const career = gameState.career;
    const edu = gameState.education;
    
    // 基础工作池（按事业值划分）
    let jobPool = [];
    
    if (career < 30) {
        jobPool = ['工人', '服务员', '司机', '快递员', '保安'];
    } else if (career < 60) {
        jobPool = ['教师', '会计', '程序员', '公务员', '销售', '设计师'];
    } else {
        jobPool = ['医生', '律师', '经理', '高管', '创业者', '网红'];
    }
    
    // 高学历可以解锁更多好工作
    if (edu >= 1) jobPool = jobPool.concat(['工程师', '研究员']);
    if (edu >= 2) jobPool = jobPool.concat(['教授', '专家', '顾问']);
    
    // 随机选择，但事业值高更容易选中好工作
    const idx = Math.floor(Math.random() * jobPool.length);
    gameState.job = jobPool[idx];
    
    // 事业值影响初始收入加成
    const careerBonus = Math.floor(career * 0.5);
    gameState.happiness = Math.min(100, gameState.happiness + 15 + careerBonus);
    gameState.timeline.push({ age: gameState.age, event: `💼 成为${gameState.job}` });
    showEvent('💼 找到工作', `你找到了 ${gameState.job} 的工作！事业值越高，收入加成越多！`, [{ text: '太好了', effect: {} }]);
    updateDisplay();
    saveGame();
}

function changeJob() {
    const oldJob = gameState.job;
    findNewJob();
    // 换工作可能影响心情
    if (gameState.job !== oldJob) {
        gameState.timeline.push({ age: gameState.age, event: `💼 从${oldJob}跳槽到${gameState.job}` });
    }
}

// ====== 菜单功能 ======
function showMenu() {
    $('menu-panel').classList.add('active');
    $('overlay').classList.add('active');
}

function hideMenu() {
    $('menu-panel').classList.remove('active');
    $('overlay').classList.remove('active');
}

function saveGame() {
    localStorage.setItem('lifeSimulatorSave', JSON.stringify(gameState));
}

async function loadSavegame() {
    const saved = localStorage.getItem('lifeSimulatorSave');
    if (saved) {
        gameState = JSON.parse(saved);
        try {
            const result = await apiCall('/api/load_game', {});
            if (result.success) {
                gameState = result.game;
            }
        } catch (e) {
            console.log('使用本地存档');
        }
        updateDisplay();
        showScreen('game-screen');
    }
}

function resetGame() {
    if (confirm('确定要重新开始吗？')) {
        localStorage.removeItem('lifeSimulatorSave');
        gameState = { name: '', age: 18 };
        showScreen('welcome-screen');
    }
}

function checkAchievements() {
    if (!config.achievements) return;
    config.achievements.forEach(a => {
        if (!gameState.achievements.includes(a.id) && a.condition(gameState)) {
            gameState.achievements.push(a.id);
            showAchievementNotification(a);
        }
    });
}

function showAchievementNotification(achievement) {
    const notification = document.createElement('div');
    notification.className = 'achievement-notification';
    notification.innerHTML = `<span class="achievement-icon">${achievement.icon}</span><span class="achievement-text">解锁成就: ${achievement.name}</span>`;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function showAchievements() {
    hideMenu();
    const unlocked = gameState.achievements.length;
    const total = config.achievements?.length || 0;
    alert(`成就系统: ${unlocked}/${total} 已解锁\n\n${gameState.achievements.map(id => config.achievements?.find(a => a.id === id)?.name).join('、') || '暂无'}`);
}

function showHelp() {
    hideMenu();
    alert('🎮 熬过去 - 人生模拟器\n\n' +
        '目标: 活得更久、更有钱、更快乐！\n\n' +
        '📌 启动方式:\n' +
        '  • 完整版: 先运行 python server.py，再访问 http://localhost:5000\n' +
        '  • 简易版: 直接打开 web/index.html（功能可能不全）\n\n' +
        '操作:\n' +
        '  • 点击"下一年"推进时间\n' +
        '  • 使用快速操作恢复状态\n' +
        '  • 抓住机会，做出选择\n\n' +
        '提示: 健康归零时，90%概率会触发转机！');
}

// ====== 新增功能：关键年龄选择 ======
function showKeyChoiceModal(keyChoiceData) {
    const age = keyChoiceData.age;
    const choices = keyChoiceData.choices;
    
    let desc = '';
    if (age === 18) desc = '高考结束，你面临人生第一个重大选择！';
    else if (age === 25) desc = '工作几年后，你开始思考职业发展方向...';
    else if (age === 35) desc = '中年危机来临，你需要做出选择...';
    else if (age === 50) desc = '人生下半场的选择...';
    
    $('event-title').textContent = `🎯 ${age}岁 - 人生选择`;
    $('event-desc').textContent = desc;
    
    const choicesContainer = $('event-choices');
    choicesContainer.innerHTML = choices.map((choice, idx) => 
        `<button class="event-choice-btn" onclick="handleKeyChoice(${idx})">${choice.text}<br><small>${choice.outcome}</small></button>`
    ).join('');
    
    window.currentKeyChoice = keyChoiceData;
    $('event-modal').style.display = 'flex';
    $('event-header').style.borderColor = '#8b5cf6';
}

async function handleKeyChoice(idx) {
    $('event-modal').style.display = 'none';
    
    const result = await apiCall('/api/handle_key_choice', { choiceIndex: idx });
    if (result.success) {
        gameState = result.game;
        if (result.result?.result) {
            showEvent('🎯 选择结果', result.result.result, [{ text: '知道了', effect: {} }]);
        }
        if (result.newAchievements?.length) {
            result.newAchievements.forEach(a => showAchievementNotification(a));
        }
    }
    
    updateDisplay();
    saveGame();
}

// ====== 小确幸/小确丧事件 ======
function showSmallEvent(event) {
    // 小事件自动显示并消失，不阻塞流程
    const isHappy = event.effect && (event.effect.happiness > 0 || event.effect.money > 0);
    const icon = isHappy ? '😊' : '😢';
    // 可以选择显示通知或者静默处理
    console.log(`${icon} ${event.title}`);
}

// ====== 节日事件 ======
function showHolidayEvent(event) {
    const icon = event.effect?.happiness > 0 ? '🎉' : '🎂';
    console.log(`${icon} ${event.text || '节日快乐'}`);
}

// ====== 资产购买 ======
async function buyProperty(type, key) {
    const result = await apiCall('/api/buy_property', { type: type, key: key });
    if (result.success) {
        gameState = result.game;
        showEvent('🏠 购买成功', result.message, [{ text: '开心', effect: {} }]);
        updateDisplay();
        saveGame();
    } else {
        showEvent('💰 购买失败', result.error || '钱不够！', [{ text: '好吧', effect: {} }]);
    }
}

// ====== 初始化 ======
window.onload = async function() {
    await loadConfig();
    
    const saved = localStorage.getItem('lifeSimulatorSave');
    if (saved) {
        $('continue-btn').style.display = 'inline-block';
    }
    
    // 如果配置加载失败，使用默认
    if (!config.backgrounds || Object.keys(config.backgrounds).length === 0) {
        config = {
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
                { id: 'petOwner', name: '铲屎官', icon: '🐱' }
            ]
        };
    }
};

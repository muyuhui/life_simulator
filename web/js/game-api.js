// game-api.js — API 调用封装 + 后端连通性检测
import { API_BASE, DEFAULT_CONFIG } from './game-state.js';

export function createApi(stateRefs) {
    const { backendOnline, config, appNotice } = stateRefs;

    function setNotice(message, type = 'info') {
        appNotice.value = { message, type };
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

    async function withBusy(isBusy, busyAction, action, task) {
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
            appNotice.value = null;
        } catch (error) {
            backendOnline.value = false;
            Object.assign(config, JSON.parse(JSON.stringify(DEFAULT_CONFIG)));
            setNotice('后端未连接：可以查看本地存档，但不能推进人生或执行操作。', 'info');
        }
    }

    return { apiCall, handleApiError, loadConfig, withBusy, setNotice };
}

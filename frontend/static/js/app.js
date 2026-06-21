/* ═══════════════════════════════════════════════════════════
   FINPILOT СППР — app.js v3.0
   Multi-page aware, no-reload operations, clean architecture
   ═══════════════════════════════════════════════════════════ */

// ── Helpers ──────────────────────────────────────────────────
const fmt = {
    num(v)  { return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 2 }).format(v); },
    cur(v)  { return `${this.num(v)} ₽`; },
    pct(v)  { return `${(v * 100).toFixed(1)}%`; },
    date(v) {
        if (!v) return '—';
        const d = new Date(v);
        return isNaN(d.getTime()) ? '—' : d.toLocaleDateString('ru-RU');
    },
    today() { return new Date().toISOString().slice(0, 10); },
};

function pn(v) { const n = Number(v); return isNaN(n) ? 0 : n; }
function clamp(v, lo = 0, hi = 100) { return Math.max(lo, Math.min(hi, v)); }

const $ = (s, p) => (p || document).querySelector(s);
const $$ = (s, p) => (p || document).querySelectorAll(s);

function on(el, ev, fn) { if (el) el.addEventListener(ev, fn); }

// BUG-01: защита форм создания от двойной отправки (двойной клик / холодный старт).
// Блокирует submit-кнопку и игнорирует повторный submit, пока запрос в полёте.
function bindSubmit(formSel, handler) {
    const form = $(formSel);
    if (!form) return;
    let inFlight = false;
    form.addEventListener('submit', async e => {
        e.preventDefault();
        if (inFlight) return;
        inFlight = true;
        const btn = form.querySelector('button[type="submit"]');
        if (btn) btn.disabled = true;
        try {
            await handler(e);
        } finally {
            inFlight = false;
            if (btn) btn.disabled = false;
        }
    });
}

async function api(url, opts = {}) {
    const r = await fetch(url, opts);
    let d = {};
    if (r.status !== 204) {
        const text = await r.text();
        if (text) {
            try { d = JSON.parse(text); } catch { d = {}; }
        }
    }
    if (!r.ok) throw new Error(d.detail || 'Ошибка сервера');
    return d;
}

function openModal(m)  { if (m) { m.setAttribute('aria-hidden', 'false'); } }
function closeModal(m) { if (m) { m.setAttribute('aria-hidden', 'true'); } }

// ── State ────────────────────────────────────────────────────
const state = {
    limit: 10,
    page: 1,
    dateFrom: null,
    dateTo: null,
    transactions: [],
    obligations: [],
    goals: [],
    liquid_assets: [],
};

// ── Theme (светлая / тёмная) ─────────────────────────────────
const SUN_SVG  = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;
const MOON_SVG = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;

function initTheme() {
    const btn = document.getElementById('theme-toggle');
    const stored = () => { try { return localStorage.getItem('finpilot-theme'); } catch (e) { return null; } };
    const apply = t => {
        document.documentElement.setAttribute('data-theme', t);
        try { localStorage.setItem('finpilot-theme', t); } catch (e) {}
        if (btn) btn.innerHTML = t === 'light' ? MOON_SVG : SUN_SVG;
    };
    apply(stored() || 'dark');
    on(btn, 'click', () => {
        const next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        apply(next);
    });
}

// ── FR-14: разрез расходов «куда уходят деньги» ──
function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s == null ? '' : String(s);
    return div.innerHTML;
}

async function loadSpendingBreakdown(days = 30) {
    const catBox = $('#spending-categories');
    const merchBox = $('#spending-merchants');
    if (!catBox) return;
    try {
        const res = await api(`/api/analysis/spending?days=${days}`);
        const cats = res.categories || [];
        const total = res.total_expense || 0;
        if (!cats.length) {
            catBox.innerHTML = '<div style="font-size:.8rem; color:var(--c-text3);">Нет расходов за период.</div>';
            if (merchBox) merchBox.innerHTML = '<div style="font-size:.8rem; color:var(--c-text3);">—</div>';
            return;
        }
        const max = Math.max(...cats.map(c => c.total));
        catBox.innerHTML = cats.map(c => {
            const pct = max > 0 ? Math.round(c.total / max * 100) : 0;
            const share = total > 0 ? Math.round(c.total / total * 100) : 0;
            return `<div style="margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; font-size:.8rem; margin-bottom:4px;">
                    <span>${escapeHtml(c.category)} <span style="color:var(--c-text3);">· ${c.count}</span></span>
                    <span style="font-weight:600;">${fmt.cur(c.total)} <span style="color:var(--c-text3); font-weight:400;">${share}%</span></span>
                </div>
                <div class="indicator-track"><div class="indicator-track-fill resource-fill" style="width:${pct}%;"></div></div>
            </div>`;
        }).join('');
        const merchants = res.top_merchants || [];
        if (merchBox) {
            merchBox.innerHTML = merchants.length
                ? merchants.map((m, i) => `<div style="display:flex; justify-content:space-between; font-size:.8rem; padding:7px 0; border-bottom:1px solid var(--c-border);">
                    <span><span style="color:var(--c-text3);">${i + 1}.</span> ${escapeHtml(m.merchant)}</span>
                    <span style="font-weight:600;">${fmt.cur(m.total)}</span>
                </div>`).join('')
                : '<div style="font-size:.8rem; color:var(--c-text3);">—</div>';
        }
    } catch (e) { console.error('Spending breakdown error:', e); }
}

// ── FR-22: категорийные бюджеты на дашборде ──
async function loadBudgets() {
    const box = $('#budgets-list');
    if (!box) return;
    try {
        const items = await api('/api/budgets/status');
        if (!items.length) {
            box.innerHTML = '<div style="font-size:.8rem; color:var(--c-text3);">Бюджеты не заданы. Добавьте лимит на категорию ниже.</div>';
            return;
        }
        box.innerHTML = items.map(b => {
            const pct = Math.min(b.pct, 100);
            const color = b.over ? 'var(--c-red)' : b.pct > 80 ? 'var(--c-amber)' : 'var(--c-green)';
            return `<div style="margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between; font-size:.82rem; margin-bottom:4px;">
                    <span>${escapeHtml(b.category)}${b.over ? ' <span style="color:var(--c-red); font-size:.72rem;">превышен</span>' : ''}</span>
                    <span><strong>${fmt.cur(b.spent)}</strong> <span style="color:var(--c-text3);">/ ${fmt.cur(b.limit_amount)} · ${b.pct}%</span>
                        <button class="budget-del" data-budget-id="${b.id}" title="Удалить" style="background:none; border:none; color:var(--c-text3); cursor:pointer; padding:0 4px; font-size:.9rem;">✕</button>
                    </span>
                </div>
                <div class="indicator-track"><div class="indicator-track-fill" style="width:${pct}%; background:${color};"></div></div>
            </div>`;
        }).join('');
    } catch (e) { console.error('Budgets error:', e); }
}

// ── FR-09: совет распределить поступивший доход ──
function showIncomeAdvice(amount) {
    document.querySelectorAll('.income-advice-toast').forEach(t => t.remove());
    const toast = document.createElement('div');
    toast.className = 'income-advice-toast';
    toast.innerHTML = `
        <div style="flex:1; min-width:0;">
            <strong>Поступил доход ${fmt.cur(amount)}</strong>
            <div style="font-size:.76rem; color:var(--c-text3); margin-top:2px;">Распределить между долгом, резервом и целями?</div>
        </div>
        <button type="button" class="income-advice-btn">Построить план</button>`;
    document.body.appendChild(toast);
    const timer = setTimeout(() => toast.remove(), 10000);
    toast.querySelector('.income-advice-btn').addEventListener('click', () => {
        clearTimeout(timer);
        toast.remove();
        window.location.href = '/planning';
    });
}

// ── Undo-уведомление для восстановления удалённой транзакции (BUG-03) ──
function showUndoToast(transactionId) {
    document.querySelectorAll('.undo-toast').forEach(t => t.remove());
    const toast = document.createElement('div');
    toast.className = 'undo-toast';
    toast.innerHTML = `<span>Операция удалена</span><button type="button" class="undo-toast-btn">Вернуть</button>`;
    document.body.appendChild(toast);
    const timer = setTimeout(() => toast.remove(), 7000);
    toast.querySelector('.undo-toast-btn').addEventListener('click', async () => {
        clearTimeout(timer);
        try {
            await api(`/api/transactions/${transactionId}/restore`, { method: 'POST' });
            await loadPage();
        } catch (e) { window.showToast(e.message, {error:true}); }
        toast.remove();
    });
}


// ── Undo для целей/обязательств/активов: пересоздание из снапшота ──
function showRestoreToast(message, snapshot, postUrl) {
    document.querySelectorAll('.undo-toast').forEach(t => t.remove());
    const toast = document.createElement('div');
    toast.className = 'undo-toast';
    toast.innerHTML = `<span>${message}</span><button type="button" class="undo-toast-btn">Вернуть</button>`;
    document.body.appendChild(toast);
    const timer = setTimeout(() => toast.remove(), 7000);
    toast.querySelector('.undo-toast-btn').addEventListener('click', async () => {
        clearTimeout(timer);
        try {
            await api(postUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(snapshot),
            });
            await loadPage();
        } catch (e) { window.showToast(e.message, {error:true}); }
        toast.remove();
    });
}

// ── Boot ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    bindGlobalUI();
    bindPlanningUI();
    loadPage();
});

// ── Активный тест-кейс: помним, какой портрет загружен ───────
const ACTIVE_CASE_KEY = 'finpilot-active-case';

function showActiveCase(label) {
    const ind = $('#active-case-indicator');
    const nameEl = $('#active-case-name');
    if (ind && nameEl && label) { nameEl.textContent = label; ind.style.display = 'block'; }
}

function setActiveCase(value, label) {
    try { localStorage.setItem(ACTIVE_CASE_KEY, JSON.stringify({ value, label })); } catch (e) {}
    showActiveCase(label);
}

function clearActiveCase() {
    try { localStorage.removeItem(ACTIVE_CASE_KEY); } catch (e) {}
    const ind = $('#active-case-indicator');
    if (ind) ind.style.display = 'none';
    const sel = $('#demo-case-select');
    if (sel) sel.selectedIndex = 0;
}

function restoreActiveCase() {
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(ACTIVE_CASE_KEY) || 'null'); } catch (e) {}
    if (!saved || !saved.value) return;
    const sel = $('#demo-case-select');
    if (sel) {
        const opt = Array.from(sel.options).find(o => o.value === saved.value);
        if (opt) sel.value = saved.value;
    }
    showActiveCase(saved.label || saved.value);
}

// ── Global UI Bindings ───────────────────────────────────────
function bindGlobalUI() {
    restoreActiveCase();
    // Close modals
    $$('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            closeModal(document.getElementById(btn.getAttribute('data-close-modal')));
        });
    });

    // Click outside modal card → close
    $$('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', e => {
            if (e.target === backdrop) closeModal(backdrop);
        });
    });

    // Escape key closes modals
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            $$('.modal-backdrop:not([aria-hidden="true"])').forEach(closeModal);
        }
    });

    // Demo buttons — load selected case from dropdown
    on($('#load-demo-button'), 'click', async () => {
        const btn = $('#load-demo-button');
        const sel = $('#demo-case-select');
        const caseName = sel ? sel.value : 'anna';
        if (!caseName) { window.showToast('Сначала выберите тест-кейс из списка.'); return; }
        btn.disabled = true; btn.textContent = 'Загрузка…';
        try {
            await api(`/api/demo/load?case=${encodeURIComponent(caseName)}`, { method: 'POST' });
            const label = sel && sel.selectedIndex >= 0 ? sel.options[sel.selectedIndex].text : caseName;
            setActiveCase(caseName, label);
            await loadPage();
        }
        catch(e) { console.error(e); }
        finally { btn.disabled = false; btn.innerHTML = svgIcon('download', 16) + ' Загрузить кейс'; }
    });

    on($('#clear-demo-button'), 'click', async () => {
        const btn = $('#clear-demo-button');
        btn.disabled = true; btn.textContent = 'Очистка…';
        try { await api('/api/demo/clear', { method: 'POST' }); clearActiveCase(); await loadPage(); }
        catch(e) { console.error(e); }
        finally { btn.disabled = false; btn.innerHTML = svgIcon('trash', 16) + ' Очистить'; }
    });

    // Transaction modals
    on($('#open-income-modal'), 'click', () => {
        $('#transaction-type').value = 'income';
        $('#transaction-modal-title').textContent = 'Новый доход';
        $('#transaction-date').value = fmt.today();
        openModal($('#transaction-modal'));
    });
    on($('#open-expense-modal'), 'click', () => {
        $('#transaction-type').value = 'expense';
        $('#transaction-modal-title').textContent = 'Новый расход';
        $('#transaction-date').value = fmt.today();
        openModal($('#transaction-modal'));
    });

    // Transaction form
    bindSubmit('#transaction-form', async () => {
        const txType = $('#transaction-type').value;
        const txAmount = pn($('#transaction-amount').value);
        try {
            await api('/api/transactions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    amount: pn($('#transaction-amount').value),
                    category: $('#transaction-category').value.trim(),
                    type: $('#transaction-type').value,
                    date: new Date($('#transaction-date').value).toISOString(),
                }),
            });
            closeModal($('#transaction-modal'));
            $('#transaction-form').reset();
            await loadPage();
            if (txType === 'income' && txAmount > 0) showIncomeAdvice(txAmount);
        } catch (e) { window.showToast(e.message, {error:true}); }
    });

    bindSubmit('#budget-form', async () => {
        const category = $('#budget-category').value.trim();
        const limit = pn($('#budget-limit').value);
        if (!category || !(limit > 0)) return;
        try {
            await api('/api/budgets', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category, limit_amount: limit }),
            });
            $('#budget-form').reset();
            loadBudgets();
        } catch (e) { window.showToast(e.message, {error:true}); }
    });

    on($('#budgets-list'), 'click', async e => {
        const btn = e.target.closest('.budget-del');
        if (!btn) return;
        try {
            await api(`/api/budgets/${btn.dataset.budgetId}`, { method: 'DELETE' });
            loadBudgets();
        } catch (e) { window.showToast(e.message, {error:true}); }
    });

    // Obligation modal
    on($('#open-obligation-modal'), 'click', () => {
        openModal($('#obligation-modal'));
    });

    bindSubmit('#obligation-form', async () => {
        try {
            await api('/api/obligations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: $('#obligation-name').value.trim(),
                    amount: pn($('#obligation-amount').value),
                    interest_rate: pn($('#obligation-interest-rate').value),
                    term: pn($('#obligation-term').value),
                    monthly_payment: pn($('#obligation-monthly-payment').value),
                    payment_day: pn($('#obligation-payment-day').value) || 1,
                    start_date: $('#obligation-start-date').value || null,
                    comment: $('#obligation-comment').value.trim() || null,
                }),
            });
            closeModal($('#obligation-modal'));
            $('#obligation-form').reset();
            await loadPage();
        } catch (e) { window.showToast(e.message, {error:true}); }
    });

    // Goal modal
    on($('#open-goal-modal'), 'click', () => {
        $('#goal-deadline').value = fmt.today();
        populateGoalAssetSelect();
        openModal($('#goal-modal'));
    });

    bindSubmit('#goal-form', async () => {
        const linkedRaw = $('#goal-linked-asset')?.value || '';
        try {
            await api('/api/goals', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: $('#goal-name').value.trim(),
                    target_amount: pn($('#goal-target-amount').value),
                    current_amount: pn($('#goal-current-amount').value),
                    deadline: new Date($('#goal-deadline').value).toISOString(),
                    category: $('#goal-category')?.value || 'material',
                    savings_rate: pn($('#goal-savings-rate')?.value || 0) / 100,
                    linked_asset_id: linkedRaw ? Number(linkedRaw) : null,
                    comment: $('#goal-comment').value.trim() || null,
                }),
            });
            closeModal($('#goal-modal'));
            $('#goal-form').reset();
            await loadPage();
        } catch (e) { window.showToast(e.message, {error:true}); }
    });

    // Liquid assets — модал и форма
    on($('#open-asset-modal'), 'click', () => openModal($('#asset-modal')));

    bindSubmit('#asset-form', async () => {
        try {
            await api('/api/liquid-assets', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: $('#asset-name').value.trim() || 'Депозит',
                    amount: pn($('#asset-amount').value),
                    interest_rate: pn($('#asset-rate').value) / 100,
                    type: $('#asset-type').value,
                    comment: $('#asset-comment').value.trim() || null,
                }),
            });
            closeModal($('#asset-modal'));
            $('#asset-form').reset();
            await loadPage();
        } catch (e) { window.showToast(e.message, {error:true}); }
    });

    on($('#liquid-assets-list'), 'click', async e => {
        const btn = e.target.closest('.delete-asset-button');
        if (!btn) return;
        btn.disabled = true;
        const snap = state.liquid_assets.find(a => String(a.id) === String(btn.dataset.assetId));
        try {
            await api(`/api/liquid-assets/${btn.dataset.assetId}`, { method: 'DELETE' });
            await loadPage();
            if (snap) showRestoreToast('Актив удалён', snap, '/api/liquid-assets');
        } catch(e) { window.showToast(e.message, {error:true}); btn.disabled = false; }
    });

    // Delete handlers (delegated)
    on($('#transactions-list'), 'click', async e => {
        const btn = e.target.closest('.delete-button');
        if (!btn) return;
        const txId = btn.dataset.transactionId;
        btn.disabled = true;
        try {
            await api(`/api/transactions/${txId}`, { method: 'DELETE' });
            await loadPage();
            showUndoToast(txId);
        } catch(e) { window.showToast(e.message, {error:true}); btn.disabled = false; }
    });

    on($('#obligations-list'), 'click', async e => {
        const btn = e.target.closest('.delete-button');
        if (!btn) return;
        btn.disabled = true;
        const snap = state.obligations.find(o => String(o.id) === String(btn.dataset.obligationId));
        try {
            await api(`/api/obligations/${btn.dataset.obligationId}`, { method: 'DELETE' });
            await loadPage();
            if (snap) showRestoreToast('Обязательство удалено', snap, '/api/obligations');
        } catch(e) { window.showToast(e.message, {error:true}); btn.disabled = false; }
    });

    on($('#goals-list'), 'click', async e => {
        const btn = e.target.closest('.delete-button');
        if (!btn) return;
        btn.disabled = true;
        const snap = state.goals.find(g => String(g.id) === String(btn.dataset.goalId));
        try {
            await api(`/api/goals/${btn.dataset.goalId}`, { method: 'DELETE' });
            await loadPage();
            if (snap) showRestoreToast('Цель удалена', snap, '/api/goals');
        } catch(e) { window.showToast(e.message, {error:true}); btn.disabled = false; }
    });

    // Limit switcher
    on($('#transactions-limit-switcher'), 'click', e => {
        const btn = e.target.closest('[data-limit]');
        if (!btn) return;
        state.limit = Number(btn.dataset.limit);
        state.page = 1;
        $$('.limit-button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderTransactions();
    });

    // Simulator form
    on($('#analysis-form'), 'submit', async e => {
        e.preventDefault();
        const incInput = pn($('#income').value);
        const expInput = pn($('#expense').value);
        // Если юзер не ввёл — берём фактические из БД (placeholder показывает их)
        const factInc = state.transactions.filter(t => t.type === 'income').reduce((s, t) => s + pn(t.amount), 0);
        const factExp = state.transactions.filter(t => t.type === 'expense').reduce((s, t) => s + pn(t.amount), 0);
        const inc = incInput > 0 ? incInput : factInc;
        const exp = expInput > 0 ? expInput : factExp;
        const txns = [];
        if (inc > 0) txns.push({ amount: inc, type: 'income', category: 'Симуляция', date: new Date().toISOString() });
        if (exp > 0) txns.push({ amount: exp, type: 'expense', category: 'Симуляция', date: new Date().toISOString() });
        try {
            const res = await api('/api/recommendation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ transactions: txns, obligations: state.obligations, goals: state.goals }),
            });
            renderDashboardCards(res, true);  // флаг симуляции
        } catch(e) { console.error(e); }
    });

    on($('#restore-summary-button'), 'click', async () => {
        await loadPage();
    });

    // Bank sync — individual bank cards
    $$('[data-bank-id]').forEach(card => {
        card.addEventListener('click', async () => {
            const bankId = card.dataset.bankId;
            const statusEl = $(`.bank-sync-status[data-bank="${bankId}"]`);
            if (statusEl) statusEl.textContent = 'Синхронизация…';
            card.style.opacity = '.6';
            try {
                const res = await api(`/api/banks/sync/${bankId}`, { method: 'POST' });
                if (statusEl) statusEl.textContent = `✓ ${res.added_count} операций загружено`;
                showSyncMsg(`✓ ${res.message}`);
            } catch(e) {
                if (statusEl) statusEl.textContent = '✗ Ошибка';
                showSyncMsg('✗ ' + e.message);
            } finally { card.style.opacity = '1'; }
        });
    });

    // Sync all banks
    on($('#sync-all-btn'), 'click', async () => {
        const btn = $('#sync-all-btn');
        btn.disabled = true; btn.textContent = 'Синхронизация…';
        try {
            const res = await api('/api/banks/sync', { method: 'POST' });
            showSyncMsg(`✓ ${res.message}`);
            // Update each bank status
            if (res.banks) {
                res.banks.forEach(b => {
                    const s = $(`.bank-sync-status[data-bank="${b.bank_id}"]`);
                    if (s) s.textContent = `✓ ${b.added_count} операций`;
                });
            }
        } catch(e) { showSyncMsg('✗ ' + e.message); }
        finally { btn.disabled = false; btn.textContent = 'Симулировать все банки'; }
    });

    // File upload — real bank statement
    const dropZone = $('#drop-zone');
    const fileInput = $('#file-input');
    const uploadBtn = $('#upload-btn');
    const uploadForm = $('#upload-form');

    if (dropZone && fileInput) {
        // Click to select
        dropZone.addEventListener('click', () => fileInput.click());

        // Drag & drop
        dropZone.addEventListener('dragover', e => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--c-accent)';
            dropZone.style.background = 'var(--c-accent-bg)';
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = 'var(--c-border)';
            dropZone.style.background = 'transparent';
        });
        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--c-border)';
            dropZone.style.background = 'transparent';
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                onFileSelected(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) onFileSelected(fileInput.files[0]);
        });

        function onFileSelected(file) {
            $('#drop-label').textContent = `Файл: ${file.name} (${(file.size / 1024).toFixed(1)} КБ)`;
            uploadBtn.disabled = false;
        }
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', async e => {
            e.preventDefault();
            if (!fileInput.files.length) return;

            uploadBtn.disabled = true;
            uploadBtn.textContent = 'Импорт…';
            const resultDiv = $('#upload-result');

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('bank_id', $('#bank-select').value);

            try {
                const res = await fetch('/api/banks/upload', { method: 'POST', body: formData });
                const data = await res.json();

                if (data.status === 'success') {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <div style="background:var(--c-green-bg); border:1px solid rgba(34,197,94,.25); border-radius:var(--r-md); padding:20px;">
                            <div style="font-weight:700; color:var(--c-green); margin-bottom:8px;">✓ ${esc(data.message)}</div>
                            <div style="font-size:.85rem; color:var(--c-text2); display:flex; gap:24px;">
                                <span>Доходов: <strong style="color:var(--c-green)">+${fmt.cur(data.total_income)}</strong></span>
                                <span>Расходов: <strong style="color:var(--c-red)">−${fmt.cur(data.total_expense)}</strong></span>
                            </div>
                        </div>`;
                } else {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <div style="background:var(--c-red-bg); border:1px solid rgba(244,63,94,.25); border-radius:var(--r-md); padding:20px;">
                            <div style="font-weight:700; color:var(--c-red);">✗ ${esc(data.message)}</div>
                        </div>`;
                }
            } catch(err) {
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = `<div style="color:var(--c-red);">Ошибка: ${esc(err.message)}</div>`;
            } finally {
                uploadBtn.disabled = false;
                uploadBtn.textContent = 'Импортировать операции';
            }
        });
    }
}

// ── Sync Message Helper ──────────────────────────────────────
function showSyncMsg(text) {
    const msg = $('#sync-status-message');
    if (msg) {
        msg.textContent = text;
        msg.className = text.startsWith('✓') ? 'sync-message success' : 'sync-message';
    }
}

// ── Page Data Loader ─────────────────────────────────────────
async function loadPage() {
    const isDash = !!$('#summary-income');
    const tList  = $('#transactions-list');
    const oList  = $('#obligations-list');
    const gList  = $('#goals-list');
    const aList  = $('#liquid-assets-list');

    try {
        const promises = [];
        const needs = {
            t: isDash || !!tList,
            o: isDash || !!oList,
            g: isDash || !!gList,
            a: isDash || !!aList,
        };

        if (needs.t) promises.push(api('/api/transactions'));      else promises.push(Promise.resolve(null));
        if (needs.o) promises.push(api('/api/obligations'));       else promises.push(Promise.resolve(null));
        if (needs.g) promises.push(api('/api/goals'));             else promises.push(Promise.resolve(null));
        if (needs.a) promises.push(api('/api/liquid-assets'));     else promises.push(Promise.resolve(null));

        const [trans, obs, goals, assets] = await Promise.all(promises);

        if (trans !== null)  state.transactions = trans;
        if (obs !== null)    state.obligations  = obs;
        if (goals !== null)  state.goals        = goals;
        if (assets !== null) state.liquid_assets = assets;

        if (isDash) {
            const inc = state.transactions.filter(t => t.type === 'income').reduce((s, t) => s + pn(t.amount), 0);
            const exp = state.transactions.filter(t => t.type === 'expense').reduce((s, t) => s + pn(t.amount), 0);
            const obl = state.obligations.reduce((s, o) => s + pn(o.monthly_payment), 0);

            setText('#summary-income', fmt.cur(inc));
            setText('#summary-expense', fmt.cur(exp));
            setText('#summary-obligations', fmt.cur(obl));

            if ($('#income') && !$('#income').value) $('#income').placeholder = `${fmt.num(inc)} ₽ (факт)`;
            if ($('#expense') && !$('#expense').value) $('#expense').placeholder = `${fmt.num(exp)} ₽ (факт)`;

            try {
                const res = await api('/api/recommendation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                });
                renderDashboardCards(res);
            } catch(e) { console.error('Recommendation error:', e); }
            const periodSel = $('#spending-period');
            loadSpendingBreakdown(periodSel ? Number(periodSel.value) : 30);
            loadBudgets();
        }

        if (tList) renderTransactions();
        if (oList) renderObligations();
        if (gList) renderGoals();
        if (aList) renderLiquidAssets();

    } catch (e) {
        console.error('loadPage error:', e);
    }
}

// ── Renderers ────────────────────────────────────────────────
function setText(sel, text) {
    const el = $(sel);
    if (el) el.textContent = text;
}

const BANK_LABELS = {
    tinkoff: 'Тинькофф', sber: 'Сбер', alfa: 'Альфа-Банк',
    vtb: 'ВТБ', raiffeisen: 'Райффайзен',
};

function filteredTransactions() {
    let list = state.transactions;
    if (state.dateFrom) list = list.filter(t => t.date.slice(0, 10) >= state.dateFrom);
    if (state.dateTo)   list = list.filter(t => t.date.slice(0, 10) <= state.dateTo);
    return list;
}

function renderTransactions() {
    const list = $('#transactions-list');
    if (!list) return;

    const all = filteredTransactions();
    const pages = Math.max(1, Math.ceil(all.length / state.limit));
    if (state.page > pages) state.page = pages;
    const start = (state.page - 1) * state.limit;
    const visible = all.slice(start, start + state.limit);

    if (visible.length === 0) {
        list.innerHTML = `<div class="empty-row">Нет записей — добавьте операцию, измените период или синхронизируйте банк</div>`;
    } else {
        list.innerHTML = visible.map(t => {
            const isIncome = t.type === 'income';
            const color = isIncome ? 'var(--c-green)' : 'var(--c-red)';
            const sign = isIncome ? '+' : '−';
            const typePill = isIncome
                ? '<span class="action-pill success-pill" style="pointer-events:none;font-size:.72rem;padding:4px 10px;">Доход</span>'
                : '<span class="action-pill danger-pill" style="pointer-events:none;font-size:.72rem;padding:4px 10px;">Расход</span>';
            const source = t.is_synced
                ? `<span style="color:var(--c-cyan);font-size:.78rem;font-weight:600;">● ${BANK_LABELS[t.bank] || 'Банк'}</span>`
                : '<span style="color:var(--c-text3);font-size:.78rem;">○ Ручной</span>';

            return `<div class="table-row">
                <span>${source}</span>
                <span>${fmt.date(t.date)}</span>
                <span style="font-weight:500;">${esc(t.category)}</span>
                <span>${typePill}</span>
                <span class="text-right" style="color:${color};font-weight:600;">${sign}${fmt.cur(t.amount)}</span>
                <span class="text-right">
                    <button class="ghost-button delete-button" data-transaction-id="${t.id}" style="padding:4px 8px;color:var(--c-red);font-size:.85rem;" title="Удалить">✕</button>
                </span>
            </div>`;
        }).join('');
    }

    renderTransactionsPagination(all.length, pages);
    renderOperationsStats(all);
}

function renderTransactionsPagination(total, pages) {
    const pg = $('#transactions-pagination');
    if (!pg) return;
    if (total === 0) { pg.innerHTML = ''; return; }
    const from = (state.page - 1) * state.limit + 1;
    const to = Math.min(state.page * state.limit, total);

    // компактный ряд страниц: 1 … p-1 p p+1 … N
    const nums = new Set([1, pages, state.page - 1, state.page, state.page + 1]);
    const seq = [...nums].filter(n => n >= 1 && n <= pages).sort((a, b) => a - b);
    let btns = '', prev = 0;
    for (const n of seq) {
        if (n - prev > 1) btns += `<span style="color:var(--c-text3); padding:0 2px;">…</span>`;
        btns += `<button class="limit-button${n === state.page ? ' active' : ''}" type="button" data-page="${n}">${n}</button>`;
        prev = n;
    }
    pg.innerHTML = `
        <span style="color:var(--c-text3);">Показано ${from}–${to} из ${total}</span>
        <div style="display:flex; gap:6px; align-items:center;">
            <button class="limit-button" type="button" data-page="${state.page - 1}" ${state.page <= 1 ? 'disabled style="opacity:.4;"' : ''}>‹</button>
            ${btns}
            <button class="limit-button" type="button" data-page="${state.page + 1}" ${state.page >= pages ? 'disabled style="opacity:.4;"' : ''}>›</button>
        </div>`;
}


// ── Визуальный дашборд операций: donut + месячные бары ───────
const CHART_COLORS = ['#6366F1', '#22C55E', '#F59E0B', '#EF4444', '#06B6D4', '#A855F7', '#EC4899', '#94A3B8'];

function renderDonutChart(all) {
    const el = $('#chart-donut');
    if (!el) return;
    const expenses = all.filter(t => t.type === 'expense');
    const total = expenses.reduce((s, t) => s + pn(t.amount), 0);
    if (!total) { el.innerHTML = '<div class="empty-row">Нет расходов за период</div>'; return; }

    const byCat = {};
    for (const t of expenses) {
        const k = t.category || 'Прочее';
        byCat[k] = (byCat[k] || 0) + pn(t.amount);
    }
    let entries = Object.entries(byCat).sort((a, b) => b[1] - a[1]);
    if (entries.length > 7) {
        const head = entries.slice(0, 7);
        const restSum = entries.slice(7).reduce((s, e) => s + e[1], 0);
        entries = [...head, ['Остальное', restSum]];
    }

    // сегменты через stroke-dasharray
    const R = 70, C = 2 * Math.PI * R;
    let offset = 0;
    const segs = entries.map(([name, sum], i) => {
        const frac = sum / total;
        const seg = `<circle r="${R}" cx="90" cy="90" fill="none"
            stroke="${CHART_COLORS[i % CHART_COLORS.length]}" stroke-width="26"
            stroke-dasharray="${(frac * C).toFixed(2)} ${C.toFixed(2)}"
            stroke-dashoffset="${(-offset * C).toFixed(2)}"
            transform="rotate(-90 90 90)"><title>${esc(name)}: ${fmt.cur(sum)} (${(frac * 100).toFixed(0)}%)</title></circle>`;
        offset += frac;
        return seg;
    }).join('');

    const legend = entries.map(([name, sum], i) => `
        <div style="display:flex; align-items:center; gap:8px; font-size:.78rem; margin-bottom:6px; min-width:0;">
            <span style="width:10px; height:10px; border-radius:3px; background:${CHART_COLORS[i % CHART_COLORS.length]}; flex-shrink:0;"></span>
            <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1;">${esc(name)}</span>
            <span style="color:var(--c-text3); white-space:nowrap;">${(sum / total * 100).toFixed(0)}%</span>
        </div>`).join('');

    el.innerHTML = `
        <div style="display:flex; gap:20px; align-items:center; flex-wrap:wrap;">
            <svg width="180" height="180" viewBox="0 0 180 180" style="flex-shrink:0;">
                ${segs}
                <text x="90" y="84" text-anchor="middle" style="font-size:11px; fill:var(--c-text3);">расходы</text>
                <text x="90" y="102" text-anchor="middle" style="font-size:13px; font-weight:700; fill:var(--c-text);">${fmt.num(total)} ₽</text>
            </svg>
            <div style="flex:1; min-width:160px;">${legend}</div>
        </div>`;
}

function renderMonthsChart(all) {
    const el = $('#chart-months');
    if (!el) return;
    if (!all.length) { el.innerHTML = '<div class="empty-row">Нет данных</div>'; return; }

    const byMonth = {};
    for (const t of all) {
        const k = t.date.slice(0, 7); // YYYY-MM
        (byMonth[k] ||= { inc: 0, exp: 0 });
        if (t.type === 'income') byMonth[k].inc += pn(t.amount);
        else byMonth[k].exp += pn(t.amount);
    }
    const months = Object.keys(byMonth).sort().slice(-8); // последние 8 месяцев периода
    const max = Math.max(...months.flatMap(m => [byMonth[m].inc, byMonth[m].exp]), 1);

    const W = 420, H = 190, padB = 26, barArea = H - padB - 8;
    const groupW = W / months.length;
    const barW = Math.min(22, groupW / 3);
    const MN = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];

    const bars = months.map((m, i) => {
        const x0 = i * groupW + groupW / 2;
        const hI = byMonth[m].inc / max * barArea;
        const hE = byMonth[m].exp / max * barArea;
        const [y, mo] = m.split('-');
        return `
            <rect x="${(x0 - barW - 2).toFixed(1)}" y="${(8 + barArea - hI).toFixed(1)}" width="${barW}" height="${hI.toFixed(1)}" rx="3" fill="var(--c-green)" opacity=".85"><title>${MN[+mo-1]} ${y}: доход ${fmt.cur(byMonth[m].inc)}</title></rect>
            <rect x="${(x0 + 2).toFixed(1)}" y="${(8 + barArea - hE).toFixed(1)}" width="${barW}" height="${hE.toFixed(1)}" rx="3" fill="var(--c-red)" opacity=".85"><title>${MN[+mo-1]} ${y}: расход ${fmt.cur(byMonth[m].exp)}</title></rect>
            <text x="${x0.toFixed(1)}" y="${H - 8}" text-anchor="middle" style="font-size:10px; fill:var(--c-text3);">${MN[+mo-1]} ${y.slice(2)}</text>`;
    }).join('');

    el.innerHTML = `<svg width="100%" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet">
        <line x1="0" y1="${8 + barArea}" x2="${W}" y2="${8 + barArea}" stroke="var(--c-border)" stroke-width="1"/>
        ${bars}
    </svg>`;
}

function renderOperationsStats(all) {
    renderDonutChart(all);
    renderMonthsChart(all);
    const catEl = $('#stats-by-category');
    const merEl = $('#stats-by-merchant');
    if (!catEl && !merEl) return;

    const expenses = all.filter(t => t.type === 'expense');
    const totalExp = expenses.reduce((s, t) => s + pn(t.amount), 0);

    const barList = (groups, el) => {
        if (!el) return;
        const top = Object.entries(groups).sort((a, b) => b[1].sum - a[1].sum).slice(0, 8);
        if (!top.length || totalExp === 0) { el.innerHTML = '<div class="empty-row">Нет расходов за период</div>'; return; }
        const max = top[0][1].sum;
        el.innerHTML = top.map(([name, g]) => `
            <div style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; font-size:.8rem; margin-bottom:3px;">
                    <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:60%;">${esc(name)} <span style="color:var(--c-text3);">· ${g.count}</span></span>
                    <span style="white-space:nowrap;"><b>${fmt.cur(g.sum)}</b> <span style="color:var(--c-text3);">${(g.sum / totalExp * 100).toFixed(0)}%</span></span>
                </div>
                <div style="height:6px; background:var(--c-surface2); border-radius:3px; overflow:hidden;">
                    <div style="height:100%; width:${(g.sum / max * 100).toFixed(1)}%; background:var(--c-accent); border-radius:3px;"></div>
                </div>
            </div>`).join('');
    };

    const byCat = {};
    for (const t of expenses) {
        const k = t.category || 'Прочее';
        (byCat[k] ||= { sum: 0, count: 0 });
        byCat[k].sum += pn(t.amount); byCat[k].count++;
    }
    barList(byCat, catEl);

    const byMer = {};
    for (const t of expenses) {
        const k = (t.description || '').trim();
        if (!k) continue;
        (byMer[k] ||= { sum: 0, count: 0 });
        byMer[k].sum += pn(t.amount); byMer[k].count++;
    }
    barList(byMer, merEl);
}

function renderObligations() {
    const list = $('#obligations-list');
    if (!list) return;

    if (state.obligations.length === 0) {
        list.innerHTML = `<article class="stack-item empty-stack-item"><div class="stack-item-title" style="color:var(--c-text3)">Обязательств пока нет</div></article>`;
        return;
    }

    list.innerHTML = state.obligations.map(o => {
        const rate = pn(o.interest_rate);
        // В интерфейсе ставка может прийти долей (0.085) или процентом (8.5) — нормализуем к %.
        const ratePct = rate > 0 && rate < 1 ? rate * 100 : rate;
        const payment = pn(o.monthly_payment);

        // term — ОБЩИЙ срок кредита; «выплачено»/«осталось» приходят посчитанными с сервера.
        const elapsed = pn(o.months_elapsed);
        const remaining = pn(o.months_remaining);
        const totalTerm = pn(o.term);
        const hasProgress = o.start_date && totalTerm > 0 && payment > 0;
        const paidSum = elapsed * payment;       // сколько уже отдано банку
        const totalPay = totalTerm * payment;    // всего платежей по графику
        const remainPay = remaining * payment;   // осталось выплатить
        const pct = totalTerm > 0 ? Math.min(100, elapsed / totalTerm * 100) : 0;

        const takenLine = o.start_date ? ` · взят ${fmt.date(o.start_date)}` : '';

        const progressBlock = hasProgress ? `
            <div class="indicator-track" style="height:5px; margin-top:10px;">
                <div class="indicator-track-fill debt-fill" style="width:${pct}%"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:.78rem; color:var(--c-text3); margin-top:4px;">
                <span>Выплачено ${fmt.cur(paidSum)} из ${fmt.cur(totalPay)} · ${pct.toFixed(0)}%</span>
                <span>Осталось ${fmt.cur(remainPay)}</span>
            </div>` : `
            <div style="font-size:.78rem; color:var(--c-text3); margin-top:8px;">
                Остаток долга: <strong style="color:var(--c-text2);">${fmt.cur(o.amount)}</strong>
            </div>`;

        // Раскрываемые детали
        const details = `
            <div style="margin-top:12px; padding-top:12px; border-top:1px solid var(--c-border); display:grid; grid-template-columns:1fr 1fr; gap:8px 18px; font-size:.8rem;">
                <div>Платёж в месяц: <strong>${fmt.cur(payment)}</strong></div>
                <div>Процентная ставка: <strong>${ratePct.toFixed(ratePct % 1 ? 1 : 0)}%</strong></div>
                <div>Остаток долга: <strong>${fmt.cur(o.amount)}</strong></div>
                <div>Осталось платежей: <strong>${remaining} мес</strong></div>
                ${o.start_date ? `<div>Когда взят: <strong>${fmt.date(o.start_date)}</strong></div><div>Платите уже: <strong>${elapsed} мес</strong></div>` : ''}
                ${hasProgress ? `<div style="grid-column:1 / -1; color:var(--c-text3);">Всего по графику: ${fmt.cur(totalPay)} (${totalTerm} платежей по ${fmt.cur(payment)}). Сумма включает проценты.</div>` : ''}
                ${o.comment ? `<div style="grid-column:1 / -1; color:var(--c-text2);">${esc(o.comment)}</div>` : ''}
            </div>`;

        return `
        <details class="stack-item" style="flex-direction:column; align-items:stretch; gap:0; cursor:pointer;">
            <summary style="list-style:none; display:block;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div class="stack-item-title">${esc(o.name)}</div>
                    <button class="ghost-button delete-button" data-obligation-id="${o.id}" style="color:var(--c-red);font-size:.85rem;padding:6px 10px;" title="Удалить" onclick="event.preventDefault()">✕</button>
                </div>
                <div class="stack-item-text">
                    ${fmt.cur(payment)} / мес · Ставка ${ratePct.toFixed(ratePct % 1 ? 1 : 0)}% · Осталось ${remaining} мес${takenLine}
                </div>
                ${progressBlock}
            </summary>
            ${details}
        </details>`;
    }).join('');
}

function populateGoalAssetSelect() {
    const sel = $('#goal-linked-asset');
    if (!sel) return;
    const assets = state.liquid_assets || [];
    sel.innerHTML = '<option value="">— не привязан (деньги вне счетов) —</option>' +
        assets.map(a => `<option value="${a.id}">${esc(a.name)} — ${fmt.cur(pn(a.amount))}${pn(a.interest_rate) > 0 ? ` (${(pn(a.interest_rate) * 100).toFixed(1)}%)` : ''}</option>`).join('');
}

// Эффективные значения цели с учётом привязки к активу (конверты).
function effectiveGoal(g) {
    let current = pn(g.current_amount), rate = pn(g.savings_rate), linkedName = null;
    if (g.linked_asset_id) {
        const a = (state.liquid_assets || []).find(x => x.id === g.linked_asset_id);
        if (a) { current = pn(a.amount); rate = pn(a.interest_rate); linkedName = a.name; }
    }
    return { current, rate, linkedName };
}

function renderGoals() {
    const list = $('#goals-list');
    if (!list) return;

    if (state.goals.length === 0) {
        list.innerHTML = `<article class="stack-item empty-stack-item"><div class="stack-item-title" style="color:var(--c-text3)">Целей пока нет</div></article>`;
        return;
    }

    const CAT_LABELS = {
        income_growth: 'рост дохода',
        safety: 'безопасность',
        material: 'материальная',
        emotional: 'эмоциональная',
    };

    const totalAccum = state.goals.reduce((x, g) => x + effectiveGoal(g).current, 0);
    const accumLine = totalAccum > 0 ? `
        <div style="font-size:.78rem; color:var(--c-text3); padding:8px 0; margin-bottom:8px; border-bottom:1px solid var(--c-border);">
            Всего накоплено по целям: <strong style="color:var(--c-green);">${fmt.cur(totalAccum)}</strong> — учитывается в плане распределения
        </div>` : '';
    list.innerHTML = accumLine + state.goals.map(g => {
        const { current, rate, linkedName } = effectiveGoal(g);
        const pct = g.target_amount > 0 ? Math.min(100, (current / g.target_amount * 100)) : 0;
        const cat = g.category || 'material';
        const catLabel = CAT_LABELS[cat] || cat;
        const rateLine = rate > 0 ? ` · ставка ${(rate * 100).toFixed(1)}%` : '';
        const linkLine = linkedName ? `<div style="font-size:.72rem; color:var(--c-accent-hl); margin-top:2px;">Копится на счёте: ${esc(linkedName)}</div>` : '';
        return `
        <article class="stack-item" style="flex-direction:column; align-items:stretch; gap:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class="stack-item-title">${esc(g.name)}
                        <span class="goal-category-badge goal-category-${esc(cat)}" style="margin-left:8px;">${catLabel}</span>
                    </div>
                    <div class="stack-item-text">${fmt.cur(current)} из ${fmt.cur(g.target_amount)} · до ${fmt.date(g.deadline)}${rateLine}</div>
                    ${linkLine}
                </div>
                <button class="ghost-button delete-button" data-goal-id="${g.id}" style="color:var(--c-red);font-size:.85rem;padding:6px 10px;" title="Удалить">✕</button>
            </div>
            <div class="indicator-track" style="height:5px;">
                <div class="indicator-track-fill resource-fill" style="width:${pct}%"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:.78rem; color:var(--c-text3);">
                <span>${pct.toFixed(0)}% выполнено</span>
                <span>Осталось ${fmt.cur(Math.max(0, g.target_amount - current))}</span>
            </div>
        </article>`;
    }).join('');
}

function renderLiquidAssets() {
    const list = $('#liquid-assets-list');
    if (!list) return;

    if (!state.liquid_assets.length) {
        list.innerHTML = `<article class="stack-item empty-stack-item"><div class="stack-item-title" style="color:var(--c-text3)">Ликвидных активов пока нет</div><div class="stack-item-text" style="color:var(--c-text3);font-size:.78rem;">Добавьте депозиты, накопительные счета или кэш — алгоритм будет учитывать их в BLR и сможет использовать для разового закрытия близких целей.</div></article>`;
        return;
    }

    const total = state.liquid_assets.reduce((s, a) => s + pn(a.amount), 0);
    const TYPE_LABELS = {
        deposit: 'депозит',
        savings_account: 'накопит. счёт',
        cash: 'кэш',
    };

    list.innerHTML = `
        <div style="font-size:.78rem; color:var(--c-text3); padding:8px 0; margin-bottom:8px; border-bottom:1px solid var(--c-border);">
            B<sub>liq</sub> = <strong style="color:#60A5FA;">${fmt.cur(total)}</strong> (всего ${state.liquid_assets.length} активов)
        </div>
        ${state.liquid_assets.map(a => `
            <article class="stack-item">
                <div style="flex:1;">
                    <div class="stack-item-title">${esc(a.name)}
                        <span style="background:rgba(96,165,250,.15); color:#60A5FA; padding:2px 8px; border-radius:10px; font-size:.68rem; margin-left:8px;">${TYPE_LABELS[a.type] || a.type}</span>
                    </div>
                    <div class="stack-item-text">
                        ${fmt.cur(a.amount)} ₽ · ставка ${(pn(a.interest_rate)*100).toFixed(1)}%
                        ${a.comment ? `· ${esc(a.comment)}` : ''}
                    </div>
                </div>
                <button class="ghost-button delete-asset-button" data-asset-id="${a.id}" style="color:var(--c-red);font-size:.85rem;padding:6px 10px;" title="Удалить">✕</button>
            </article>
        `).join('')}`;
}


// ── Детальные пояснения метрик дашборда (по клику на карточку) ──
function metricExplainHTML(key, ind) {
    const m = v => fmt.cur(v);
    const It = ind.It || 0, Et = ind.Et || 0, SigmaP = ind.SigmaP || 0;
    const Rt = ind.Rt || 0, Lt = ind.Lt || 0, Dt = ind.Dt || 0;
    const Bt = ind.Bt || 0, Bliq = ind.Bliq || 0, BLR = ind.BLR || 0;
    const oblig = Et + SigmaP;

    const block = (title, rows, note) => `
        <section class="glass-panel" style="padding:18px 22px; position:relative;">
            <button id="metric-explain-close" style="position:absolute; top:12px; right:14px; background:none; border:none; color:var(--c-text3); cursor:pointer; font-size:1rem;">✕</button>
            <h3 style="font-size:.95rem; margin:0 0 12px;">${title}</h3>
            <div style="display:flex; flex-direction:column; gap:8px; font-size:.82rem;">${rows}</div>
            ${note ? `<div style="margin-top:12px; padding-top:10px; border-top:1px solid var(--c-border); font-size:.78rem; color:var(--c-text3);">${note}</div>` : ''}
        </section>`;
    const row = (label, val) => `<div style="display:flex; justify-content:space-between; gap:16px;"><span style="color:var(--c-text2);">${label}</span><span style="text-align:right;">${val}</span></div>`;

    if (key === 'rt') {
        const verdict = Rt > 0
            ? `Эти <b>${m(Rt)}</b> каждый месяц можно направлять на досрочное погашение, в резерв или на цели — именно эту сумму система распределяет в плане.`
            : `Свободных денег нет: траты и платежи превышают доход на <b>${m(Math.abs(Rt))}</b>. Сначала нужно сократить расходы или увеличить доход — распределять пока нечего.`;
        return block('Свободные деньги (Rt) — как посчитано',
            row('Доходы за месяц', `<b style="color:var(--c-green);">+${m(It)}</b>`) +
            row('− Обычные расходы', `<b style="color:var(--c-red);">−${m(Et)}</b>`) +
            row('− Платежи по кредитам', `<b style="color:var(--c-red);">−${m(SigmaP)}</b>`) +
            row('= Свободные деньги', `<b style="color:${Rt >= 0 ? 'var(--c-green)' : 'var(--c-red)'};">${m(Rt)}</b>`),
            verdict);
    }
    if (key === 'lt') {
        const verdict = Lt >= 2.5
            ? `Значение <b>${Lt.toFixed(1)} мес.</b> — в норме (2.5–6 месяцев по Greninger): на случай потери дохода есть запас.`
            : Lt >= 1
                ? `Значение <b>${Lt.toFixed(1)} мес.</b> — подушка ниже нормы (2.5–6 мес.), стоит её наращивать.`
                : `Значение <b>${Lt.toFixed(1)} мес.</b> — выделенного резерва почти нет, имеет смысл в первую очередь его пополнять.`;
        return block('Запас прочности (L<sub>t</sub>) — как посчитано',
            row('Ликвидная подушка (резерв)', `<b>${m(Bliq)}</b>`) +
            row('÷ Месячные расходы', `<b>${m(Et)}</b>`) +
            row('= Запас прочности', `<b>${Lt.toFixed(1)} мес.</b>`),
            `Сколько месяцев вы проживёте на свободной ликвидной подушке без дохода (накопления на целях сюда не входят — они учтены в «Подушке безопасности»). Норма — 2.5–6 месяцев (Greninger, 1996). ${verdict}`);
    }
    if (key === 'dt') {
        const verdict = Dt <= 0.36
            ? `Ваши <b>${fmt.pct(Dt)}</b> — в зелёной зоне.`
            : Dt <= 0.5 ? `Ваши <b>${fmt.pct(Dt)}</b> — повышенная нагрузка, банки могут отказывать в новых кредитах.`
            : `Ваши <b>${fmt.pct(Dt)}</b> — опасная зона, выше половины дохода уходит на долги.`;
        return block('Долговая нагрузка (Dt / ПДН) — как посчитано',
            row('Платежи по кредитам в месяц', `<b>${m(SigmaP)}</b>`) +
            row('÷ Доходы за месяц', `<b>${m(It)}</b>`) +
            row('= Долговая нагрузка', `<b>${fmt.pct(Dt)}</b>`),
            `Это «показатель долговой нагрузки» (ПДН) — его же считает Банк России при выдаче кредитов. Порог регулятора — 40%. ${verdict}`);
    }
    if (key === 'blr') {
        const verdict = BLR < 1 ? 'Это критично: без дохода деньги закончатся почти сразу.'
            : BLR < 2.5 ? 'Это ниже нормы: подушку стоит наращивать.'
            : BLR <= 6 ? 'Это норма: запас от 2.5 до 6 месяцев считается здоровым.'
            : 'Это избыток: часть денег можно перевести в доходные инструменты — лежащие без дела деньги съедает инфляция.';
        return block('Подушка безопасности (BLR) — как посчитано',
            row('Накоплено на целях (B<sub>t</sub>)', `<b>${m(Bt)}</b>`) +
            row('+ Накопления и депозиты (B<sub>liq</sub>)', `<b>${m(Bliq)}</b>`) +
            row('÷ Обычные расходы в месяц', `<b>${m(Et)}</b>`) +
            row('= Хватит на', `<b>${BLR.toFixed(1)} мес</b>`),
            `Показывает, сколько месяцев вы проживёте при полной потере дохода, тратя как сейчас. ${verdict}`);
    }
    return '';
}

function renderDashboardCards(res, isSimulation = false) {
    if (!res || !res.indicators) return;

    state.lastIndicators = res.indicators;
    const { Rt, Lt, Dt, Bt, BLR, Bliq, BLR_status } = res.indicators;
    const blr = BLR ?? 0;
    const bliq = Bliq ?? 0;
    const bt = Bt ?? 0;

    // Indicator — симуляция или факт
    const headerEl = $('#summary-header');
    if (headerEl) {
        if (isSimulation) {
            headerEl.innerHTML = `<div style="background:rgba(251,191,36,.12); border:1px solid var(--c-amber); padding:8px 14px; border-radius:var(--r-sm); margin-bottom:14px; font-size:.78rem; color:var(--c-amber); display:flex; justify-content:space-between; align-items:center;">
                <span><strong>Гипотетический режим симулятора</strong> — БД не изменена, показаны симулированные значения</span>
                <button onclick="document.getElementById('restore-summary-button').click()" style="background:var(--c-amber); color:#000; border:none; padding:4px 12px; border-radius:var(--r-sm); cursor:pointer; font-weight:600; font-size:.74rem;">Вернуть факт</button>
            </div>`;
        } else {
            headerEl.innerHTML = '';
        }
    }

    // ─── Metric values ───────────────────────────────────────────
    setText('#rt-value', fmt.num(Rt));
    const heroRt = $('#hero-rt-value');
    if (heroRt) {
        heroRt.textContent = fmt.cur(Rt);
        heroRt.style.color = Rt >= 0 ? 'var(--c-green)' : 'var(--c-red)';
    }
    setText('#lt-value', `${Number(Lt).toFixed(1)} мес`);
    setText('#dt-value', fmt.pct(Dt));
    setText('#blr-value', `${blr.toFixed(1)} мес`);

    const rtEl = $('#rt-value');
    const ltEl = $('#lt-value');
    const dtEl = $('#dt-value');
    const blrEl = $('#blr-value');
    const blrBadge = $('#blr-status-badge');

    // Rt: цвет по знаку
    if (rtEl) rtEl.style.color = Rt >= 0 ? 'var(--c-green)' : 'var(--c-red)';
    // Lt: ликвидность — месяцы автономии, норма 2.5–6 (Greninger)
    if (ltEl) ltEl.style.color = Lt >= 2.5 ? 'var(--c-green)' : Lt >= 1 ? 'var(--c-amber)' : 'var(--c-red)';
    // Dt: ПДН Банка России — ≤36% норма, 36–50% повышенный, >50% опасный
    if (dtEl) dtEl.style.color = Dt <= 0.36 ? 'var(--c-green)' : Dt <= 0.5 ? 'var(--c-amber)' : 'var(--c-red)';
    // BLR: Greninger — <1 критично, 1–2.5 слабо, 2.5–6 норма, >6 избыток
    const blrLevel = BLR_status?.level || (blr < 1 ? 'critical' : blr < 2.5 ? 'weak' : blr < 6 ? 'normal' : 'surplus');
    const blrLabel = BLR_status?.label || (blr < 1 ? 'критично' : blr < 2.5 ? 'слабо' : blr < 6 ? 'норма' : 'избыток');
    const blrColors = { critical: 'var(--c-red)', weak: 'var(--c-amber)', normal: 'var(--c-green)', surplus: 'var(--c-violet)' };
    if (blrEl) blrEl.style.color = blrColors[blrLevel] || 'var(--c-text)';
    if (blrBadge) {
        blrBadge.textContent = blrLabel;
        blrBadge.dataset.level = blrLevel;
    }

    // Status badge
    const statusEl = $('#rec-status');
    if (statusEl) {
        if (Dt > 0.5 || Rt < 0) {
            statusEl.textContent = '● Внимание';
            statusEl.className = 'rec-status status-danger';
        } else if (Dt > 0.36 || blr < 1) {
            statusEl.textContent = '● Пограничный';
            statusEl.className = 'rec-status status-warn';
        } else {
            statusEl.textContent = '● Стабильно';
            statusEl.className = 'rec-status status-ok';
        }
    }

    // Render recommendation
    const recText = $('#recommendation-text');
    if (recText && res.recommendation) {
        recText.innerHTML = `<div style="font-size:.84rem; line-height:1.6; color:var(--c-text);">${esc(res.recommendation)}</div>`;
    }

    // Render breakdown — формулы ВКР + бенчмарки
    const explEl = $('#explanation-text');
    if (explEl) {
        const ltGround = Lt >= 2.5
            ? "Подушки хватит на несколько месяцев жизни без дохода — здоровый уровень."
            : Lt >= 1
                ? "Подушка ниже нормы (2.5–6 мес.) — её стоит наращивать."
                : "Выделенного резерва почти нет — в первую очередь стоит его пополнять.";
        const dtGround = Dt <= 0.36
            ? "Это в пределах нормы (безопасная граница — 40% дохода)."
            : Dt <= 0.5
                ? "Нагрузка повышенная — новые кредиты сейчас брать не стоит."
                : "Нагрузка высокая — снижать долг стоит в первую очередь.";
        const blrGround = blr < 2.5
            ? "Маловато — комфортный запас это 3–6 месяцев расходов."
            : blr <= 6
                ? "Здоровый запас на случай потери дохода."
                : "Запас даже с избытком — лишнее можно направить в цели или накопления.";

        let html = `<div class="rec-grounding" style="margin-top:0;">
            <div style="font-size:.72rem; color:var(--c-text3); margin-bottom:8px; text-transform:uppercase; letter-spacing:.5px;">Что значат эти числа</div>
            <div style="display:flex; flex-direction:column; gap:8px; font-size:.78rem; line-height:1.5;">
                <div><strong>Запас прочности — ${Number(Lt).toFixed(1)} мес.</strong> ${ltGround}</div>
                <div><strong>Долговая нагрузка — ${fmt.pct(Dt)}.</strong> ${dtGround}</div>
                <div><strong>Подушка безопасности — ${blr.toFixed(1)} мес.</strong> ${blrGround}</div>
            </div>
        </div>`;

        const summary = res.input_summary || {};
        if (summary.transactions_count) {
            html += `<div style="margin-top:8px; font-size:.72rem; color:var(--c-text3);">
                ${summary.transactions_count} операций · ${summary.obligations_count || 0} обяз. · ${summary.active_goals_count || 0} целей · ${summary.liquid_assets_count || 0} активов
            </div>`;
        }
        explEl.innerHTML = html;
    }

    // Progress bars
    const maxR = 500000;
    setBar('#resource-scale-bar', '#resource-scale-text', clamp(Math.abs(Rt) / maxR * 100), fmt.cur(Rt));
    // Lt прогресс: 100% = 6 месяцев (верх нормы Greninger)
    setBar('#liquidity-scale-bar', '#liquidity-scale-text', clamp((Lt / 6) * 100), Lt.toFixed(1) + ' мес');
    setBar('#debt-scale-bar', '#debt-scale-text', clamp(Dt * 100), fmt.pct(Dt));
}


function setBar(barSel, textSel, pct, text) {
    const bar = $(barSel);
    const txt = $(textSel);
    if (bar) bar.style.width = `${pct}%`;
    if (txt) txt.textContent = text;
}

function esc(s) {
    if (!s) return '';
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

function svgIcon(name, size = 16) {
    const icons = {
        download: `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="vertical-align:-2px;margin-right:6px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
        trash: `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="vertical-align:-2px;margin-right:6px;"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>`,
    };
    return icons[name] || '';
}

// ── Planning Page (ВКР: Генерация и ранжирование альтернатив) ──
let planRisk = 3;
let planLmin = 0.0;
let planRbench = 0.14;
const RISK_LABELS = {1:'Консервативный',2:'Умеренно-консервативный',3:'Сбалансированный',4:'Умеренно-агрессивный',5:'Агрессивный'};

function bindPlanningUI() {
    const form = $('#planning-form');
    if (!form) return;

    // Экспорт рекомендации: CSV — серверный эндпоинт (гарантированное скачивание),
    // PDF — печать браузера.
    on($('#export-csv'), 'click', () => {
        const params = new URLSearchParams();
        if (typeof planRisk === 'number') params.set('risk_tolerance', planRisk);
        if (typeof planLmin === 'number') params.set('l_min', planLmin);
        if (typeof planRbench === 'number') params.set('r_bench', planRbench);
        window.location.href = `/api/planning/export.csv?${params.toString()}`;
    });
    on($('#export-pdf'), 'click', () => window.print());

    // L_min slider
    const lminSlider = $('#lmin-slider');
    const lminVal    = $('#lmin-value');
    if (lminSlider) {
        lminSlider.addEventListener('input', () => {
            planLmin = parseFloat(lminSlider.value);
            if (lminVal) lminVal.textContent = planLmin.toFixed(1);
        });
    }

    // Ставка по накоплениям (r_bench) + подстановка ключевой ставки ЦБ
    const rbenchSlider = $('#rbench-slider');
    const rbenchVal = $('#rbench-value');
    const setRbench = (pct) => {
        planRbench = pct / 100;
        if (rbenchSlider) rbenchSlider.value = pct;
        if (rbenchVal) rbenchVal.textContent = pct.toFixed(1) + '%';
    };
    if (rbenchSlider) {
        rbenchSlider.addEventListener('input', () => setRbench(parseFloat(rbenchSlider.value)));
    }
    on($('#rbench-cbr'), 'click', async () => {
        const hint = $('#rbench-hint');
        try {
            const r = await api('/api/planning/key-rate');
            const pct = Math.round(r.key_rate * 1000) / 10;
            setRbench(pct);
            if (hint) hint.textContent = r.source === 'cbr'
                ? `Ставка ЦБ на ${r.as_of}: ${pct.toFixed(1)}% — подставлена.`
                : `ЦБ недоступен${r.detail ? ': ' + r.detail : ''} Подставлено резервное значение ${pct.toFixed(1)}%.`;
        } catch (e) { window.showToast('Не удалось получить ставку ЦБ', {error:true}); }
    });

    on($('#rbench-from-asset'), 'click', () => {
        const hint = $('#rbench-hint');
        const assets = state.liquid_assets || [];
        const best = assets.reduce((mx, a) => Math.max(mx, pn(a.interest_rate)), 0);
        if (best <= 0) {
            if (hint) hint.textContent = 'У вас пока нет вкладов со ставкой. Добавьте их в разделе «Ликвидные активы».';
            return;
        }
        const pct = best > 0 && best < 1 ? best * 100 : best;
        setRbench(Math.round(pct * 10) / 10);
        if (hint) hint.textContent = `Подставлена лучшая ставка среди ваших вкладов: ${pct.toFixed(1)}%.`;
    });

    // Risk selector
    $$('.risk-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            planRisk = Number(btn.dataset.risk);
            $$('.risk-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const lbl = $('#risk-label');
            if (lbl) lbl.textContent = RISK_LABELS[planRisk] || '';
        });
    });

    // Form submit
    form.addEventListener('submit', async e => {
        e.preventDefault();
        const btn = form.querySelector('button[type=submit]');
        btn.disabled = true; btn.textContent = 'Расчёт…';
        try {
            const res = await api('/api/planning/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ risk_tolerance: planRisk, l_min: planLmin, r_bench: planRbench }),
            });
            renderPlanning(res);
        } catch(e) { console.error(e); }
        finally { btn.disabled = false; btn.textContent = 'Рассчитать альтернативы'; }
    });

    // FR-07: пересчёт и сохранение сценария «что если»
    let lastScenario = null;
    on($('#scenario-calc-btn'), 'click', async () => {
        const inc = $('#scenario-income').value.trim();
        const exp = $('#scenario-expense').value.trim();
        const params = { risk_tolerance: planRisk, l_min: planLmin, r_bench: planRbench };
        if (inc !== '') params.income_override = pn(inc);
        if (exp !== '') params.expense_override = pn(exp);
        const sbtn = $('#scenario-calc-btn');
        sbtn.disabled = true; sbtn.textContent = 'Пересчёт…';
        try {
            const res = await api('/api/planning/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params),
            });
            renderPlanning(res);
            lastScenario = { parameters: params, result: { Rt: res.indicators ? res.indicators.Rt : null } };
            $('#scenario-save-btn').style.display = '';
            $('#scenario-hint').textContent = 'План пересчитан под сценарий — можно сохранить.';
        } catch (e) { window.showToast(e.message, {error:true}); }
        finally { sbtn.disabled = false; sbtn.textContent = 'Пересчитать сценарий'; }
    });
    on($('#scenario-save-btn'), 'click', async () => {
        if (!lastScenario) return;
        const name = prompt('Название сценария:', 'Мой сценарий');
        if (!name) return;
        try {
            await api('/api/planning/scenarios', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, parameters: lastScenario.parameters, result: lastScenario.result }),
            });
            $('#scenario-hint').textContent = 'Сценарий сохранён ✓';
        } catch (e) { window.showToast(e.message, {error:true}); }
    });

    // Horizon selector → reload forecast
    const horizonSel = $('#forecast-horizon');
    if (horizonSel) {
        horizonSel.addEventListener('change', () => loadForecast(Number(horizonSel.value)));
    }

    // Auto-load
    form.dispatchEvent(new Event('submit'));
    loadForecast(6);
    loadSpendingAdvice();
}

async function loadForecast(horizon = 6) {
    try {
        const data = await api('/api/planning/forecast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ horizon }),
        });
        renderForecast(data);
    } catch(e) { console.error('forecast error', e); }
}

// ── Советы по тратам (мат-модель v3) ─────────────────────────
async function loadSpendingAdvice() {
    try {
        const data = await api('/api/planning/spending-advice?months=6');
        renderSpendingAdvice(data);
    } catch (e) { console.error('spending-advice error', e); }
}

function renderSpendingAdvice(data) {
    const container = $('#spending-advice-container');
    const body = $('#spending-advice-body');
    if (!container || !body) return;
    container.style.display = 'block';

    const advice = (data && data.advice) || [];
    const monthsData = data ? data.months_with_data : 0;

    if (!advice.length) {
        const msg = monthsData < 3
            ? 'Нужно больше истории операций — минимум 3 месяца, чтобы построить вашу персональную норму трат и сравнить с ней.'
            : 'Аномальных или явно сокращаемых трат не нашли — ваши расходы в пределах обычной нормы.';
        body.innerHTML = `<div style="font-size:.82rem; color:var(--c-text3); line-height:1.5;">${msg}</div>`;
        return;
    }

    const cards = advice.map(a => `
        <div style="padding:12px 14px; border:1px solid var(--c-border); border-radius:var(--r-md); margin-bottom:10px; font-size:.82rem; line-height:1.5;">
            ${esc(a.message)}
        </div>`).join('');

    const total = data.total_potential_saving || 0;
    const summary = total > 0
        ? `<div style="font-size:.78rem; color:var(--c-text2); margin-top:8px; padding:10px 14px; background:var(--c-surface-up); border-radius:var(--r-sm); line-height:1.5;">
               Если постепенно привести эти траты к норме, в перспективе можно высвобождать <strong style="color:var(--c-green);">до ${fmt.cur(total)}</strong> в месяц — на досрочку, подушку или цели.
               <br><span style="color:var(--c-text3);">Это ориентир на будущее, а не мгновенный эффект: план выше посчитан по вашим текущим тратам. Привычки меняются постепенно — начните с одной категории.</span>
           </div>`
        : '';

    body.innerHTML = cards + summary;
}

// ── SVG fan-chart прогноза Rt с 80% доверительным интервалом ──
function forecastChartSVG(data) {
    const pts = (data && data.forecast) || [];
    if (!pts.length) return '';

    const compact = (v) => {
        const a = Math.abs(v);
        if (a >= 1e6) return (v / 1e6).toFixed(a >= 1e7 ? 0 : 1).replace('.0', '') + 'M';
        if (a >= 1e3) return Math.round(v / 1e3) + 'k';
        return String(Math.round(v));
    };

    const W = 1160, H = 360, padL = 96, padR = 32, padT = 24, padB = 48;
    const innerW = W - padL - padR, innerH = H - padT - padB;
    const n = pts.length;
    const hasCI = pts.every(p => p.Rt_p10 != null && p.Rt_p90 != null);

    const vals = [0];
    pts.forEach(p => { vals.push(p.Rt); if (hasCI) { vals.push(p.Rt_p10, p.Rt_p90); } });
    let minV = Math.min(...vals), maxV = Math.max(...vals);
    if (minV === maxV) { maxV += 1; minV -= 1; }
    const span = (maxV - minV) * 0.10; minV -= span; maxV += span;

    const xOf = i => padL + (n === 1 ? innerW / 2 : innerW * i / (n - 1));
    const yOf = v => padT + innerH * (1 - (v - minV) / (maxV - minV));

    // Горизонтальная сетка + подписи оси Y (5 уровней)
    let grid = '', yTicks = '';
    const LEVELS = 4;
    for (let g = 0; g <= LEVELS; g++) {
        const v = minV + (maxV - minV) * g / LEVELS;
        const y = yOf(v).toFixed(1);
        grid += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="var(--c-border)" stroke-width="1"/>`;
        yTicks += `<text x="${padL - 10}" y="${(yOf(v) + 4).toFixed(1)}" text-anchor="end" font-size="11" fill="var(--c-text3)" font-family="var(--font-mono),monospace">${compact(v)}</text>`;
    }

    // Нулевая линия
    let zero = '';
    if (minV < 0 && maxV > 0) {
        const zy = yOf(0).toFixed(1);
        zero = `<line x1="${padL}" y1="${zy}" x2="${W - padR}" y2="${zy}" stroke="var(--c-text2)" stroke-width="1.5" stroke-dasharray="5 4" opacity="0.6"/>`;
    }

    // CI-полоса (80%) + её границы
    let band = '';
    if (hasCI) {
        const top = pts.map((p, i) => `${xOf(i).toFixed(1)},${yOf(p.Rt_p90).toFixed(1)}`);
        const bot = pts.map((p, i) => `${xOf(i).toFixed(1)},${yOf(p.Rt_p10).toFixed(1)}`).reverse();
        band = `<polygon points="${top.concat(bot).join(' ')}" fill="var(--c-amber)" opacity="0.16"/>`
             + `<polyline points="${top.join(' ')}" fill="none" stroke="var(--c-amber)" stroke-width="1.5" opacity="0.65"/>`
             + `<polyline points="${pts.map((p, i) => `${xOf(i).toFixed(1)},${yOf(p.Rt_p10).toFixed(1)}`).join(' ')}" fill="none" stroke="var(--c-amber)" stroke-width="1.5" opacity="0.65"/>`;
    }

    // Линия точечного прогноза Rt + точки
    const line = pts.map((p, i) => `${xOf(i).toFixed(1)},${yOf(p.Rt).toFixed(1)}`).join(' ');
    const linePoly = `<polyline points="${line}" fill="none" stroke="var(--c-accent)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>`;
    const dots = pts.map((p, i) => {
        const col = p.Rt >= 0 ? 'var(--c-green)' : 'var(--c-red)';
        return `<circle cx="${xOf(i).toFixed(1)}" cy="${yOf(p.Rt).toFixed(1)}" r="3.5" fill="${col}" stroke="var(--c-bg)" stroke-width="1.5"/>`;
    }).join('');

    // Подписи оси X (прореживаем, если периодов много)
    const stepX = n <= 12 ? 1 : Math.ceil(n / 12);
    let xTicks = '';
    pts.forEach((p, i) => {
        if (i % stepX !== 0 && i !== n - 1) return;
        xTicks += `<text x="${xOf(i).toFixed(1)}" y="${H - padB + 20}" text-anchor="middle" font-size="11" fill="var(--c-text3)">+${p.period}м</text>`;
    });

    const legend = `
        <div style="display:flex; gap:18px; justify-content:flex-end; font-size:.72rem; color:var(--c-text2); margin-bottom:6px;">
            <span style="display:inline-flex; align-items:center; gap:6px;"><span style="width:14px; height:3px; background:var(--c-accent); border-radius:2px;"></span>Свободные деньги R<sub>t</sub> (прогноз)</span>
            ${hasCI ? `<span style="display:inline-flex; align-items:center; gap:6px;"><span style="width:14px; height:10px; background:var(--c-amber); opacity:.3; border-radius:2px;"></span>Вероятный диапазон (80%)</span>` : ''}
        </div>`;

    return `
        <div style="margin-bottom:16px;">
            <div style="font-size:.82rem; font-weight:600; margin-bottom:8px;">График прогноза свободных денег R<sub>t</sub></div>
            ${legend}
            <svg viewBox="0 0 ${W} ${H}" width="100%" preserveAspectRatio="xMidYMid meet" style="display:block; max-width:100%;">
                ${grid}${zero}${band}${linePoly}${dots}${yTicks}${xTicks}
            </svg>
        </div>`;
}

function renderForecast(data) {
    const container = $('#forecast-container');
    const body = $('#forecast-body');
    if (!container || !body || !data) return;

    container.style.display = '';

    const TREND_LABEL = { stable: 'Стабильный', improving: 'Улучшение', deteriorating: 'Ухудшение' };
    const TREND_COLOR = { stable: 'var(--c-text3)', improving: 'var(--c-green)', deteriorating: 'var(--c-red)' };
    const trend = data.trend || 'stable';
    const method = data.method || {};

    const rows = (data.forecast || []).map(p => {
        const ci = (p.Rt_p10 !== undefined && p.Rt_p90 !== undefined)
            ? `<span style="color:var(--c-amber); font-family:var(--font-mono);">${fmt.num(p.Rt_p10)} … ${fmt.num(p.Rt_p90)}</span>`
            : '—';
        return `
        <tr>
            <td style="padding:6px 10px; color:var(--c-text3);">+${p.period} мес.</td>
            <td style="padding:6px 10px; text-align:right; color:var(--c-text2);">${fmt.cur(p.Bt)}</td>
            <td style="padding:6px 10px; text-align:right; font-weight:600; color:${p.Rt >= 0 ? 'var(--c-green)' : 'var(--c-red)'};">${fmt.cur(p.Rt)}</td>
            <td style="padding:6px 10px; text-align:right; font-size:.76rem; background:rgba(251,191,36,.05);">${ci}</td>
            <td style="padding:6px 10px; text-align:right; color:${p.Lt >= 2.5 ? 'var(--c-green)' : p.Lt >= 1.0 ? 'var(--c-amber)' : 'var(--c-red)'};">${p.Lt.toFixed(3)}</td>
            <td style="padding:6px 10px; text-align:right; color:${p.Dt <= 0.36 ? 'var(--c-green)' : p.Dt <= 0.5 ? 'var(--c-amber)' : 'var(--c-red)'};">${(p.Dt * 100).toFixed(1)}%</td>
        </tr>`;
    }).join('');

    const alert = data.deficit_alert;
    const alertHtml = alert ? `
        <div style="margin-bottom:14px; padding:12px 16px; border-radius:10px; background:rgba(239,68,68,.08); border:1px solid rgba(239,68,68,.3); font-size:.84rem; line-height:1.5;">
            <strong style="color:var(--c-red);">${alert.pessimistic ? 'Риск нехватки денег' : 'Прогноз: денег может не хватить'}</strong><br/>
            Через <strong>${alert.period} мес.</strong> ${alert.pessimistic ? 'при неблагоприятном сценарии ' : ''}свободных денег может не хватить — разрыв около <strong>${fmt.cur(alert.gap)}</strong>. Стоит заранее снизить расходы или отложить крупные траты.
        </div>` : '';

    body.innerHTML = `
        ${alertHtml}
        ${(() => {
            const pts = data.forecast || [];
            if (!pts.length) return '';
            const last = pts[pts.length - 1];
            const cur = data.current || {};
            const h = data.horizon || pts.length;
            const curBt = cur.Bt != null ? cur.Bt : (pts[0] ? pts[0].Bt - pts[0].cash_flow : 0);
            const deltaBt = last.Bt - curBt;
            const hasCI = last.Rt_p10 != null && last.Rt_p90 != null;
            const card = (label, value, sub, color) => `
                <div style="flex:1; min-width:150px; padding:14px 16px; background:rgba(255,255,255,.03);
                            border:1px solid var(--c-border); border-radius:var(--r-md);">
                    <div style="font-size:.72rem; color:var(--c-text3); text-transform:uppercase; letter-spacing:.4px;">${label}</div>
                    <div style="font-size:1.25rem; font-weight:700; margin-top:4px; color:${color || 'var(--c-text)'};">${value}</div>
                    <div style="font-size:.72rem; color:var(--c-text3); margin-top:2px;">${sub}</div>
                </div>`;
            return `<div style="display:flex; flex-wrap:wrap; gap:12px; margin-bottom:18px;">
                ${card('Баланс через ' + h + ' мес', fmt.cur(last.Bt) + ' ₽',
                    (deltaBt >= 0 ? '▲ +' : '▼ ') + fmt.cur(Math.abs(deltaBt)) + ' ₽ к текущему',
                    deltaBt >= 0 ? 'var(--c-green)' : 'var(--c-red)')}
                ${card('Свободные деньги/мес', fmt.cur(last.Rt) + ' ₽', 'прогноз Rt на горизонте', 'var(--c-accent)')}
                ${hasCI ? card('Диапазон (80%)', fmt.num(last.Rt_p10) + '…' + fmt.num(last.Rt_p90),
                    'где окажется Rt с вероятностью 80%', 'var(--c-amber)') : ''}
                ${card('Тренд', TREND_LABEL[trend], 'динамика свободных денег', TREND_COLOR[trend])}
            </div>`;
        })()}
        ${forecastChartSVG(data)}
        ${(() => {
            const sb = data.stable_baseline;
            if (!sb || (sb.recurring_income <= 0 && sb.recurring_expense <= 0)) return '';
            return `<div style="margin-bottom:10px; font-size:.78rem; color:var(--c-text2); line-height:1.5;
                        padding:10px 14px; background:rgba(34,197,94,.06); border-radius:var(--r-sm);
                        border-left:3px solid var(--c-green);">
                <strong>Стабильная база прогноза:</strong> из дохода регулярны
                <strong>${fmt.cur(sb.recurring_income)}</strong> (${(sb.income_share*100).toFixed(0)}%),
                из расходов — <strong>${fmt.cur(sb.recurring_expense)}</strong> (${(sb.expense_share*100).toFixed(0)}%).
                Чем выше доля регулярных операций, тем надёжнее прогноз.
            </div>`;
        })()}
        <div style="margin-bottom:10px; font-size:.78rem; color:var(--c-text3); line-height:1.5;">
            Тренд Rt: <strong style="color:${TREND_COLOR[trend]};">${TREND_LABEL[trend]}</strong>
            <details style="margin-top:6px;">
                <summary style="cursor:pointer; font-size:.82rem; color:var(--c-accent); font-weight:600;
                    display:inline-flex; align-items:center; gap:6px; padding:8px 14px;
                    border:1px solid var(--c-accent); border-radius:var(--r-sm); list-style:none; width:fit-content;">
                    Как построен прогноз и можно ли ему доверять</summary>
                <div style="margin-top:8px; font-size:.74rem; line-height:1.55;">
                    <p style="margin:0 0 6px;"><b>Что показывает.</b> Синяя линия — сколько свободных денег у вас будет оставаться месяц за месяцем, если доходы и расходы сохранятся примерно как в вашей истории. Жёлтый коридор — диапазон, в который значение попадёт примерно в 80 случаях из 100.</p>
                    <p style="margin:0 0 4px;"><b>Как строится — по шагам:</b></p>
                    <ol style="margin:0 0 6px; padding-left:18px; display:flex; flex-direction:column; gap:3px;">
                        <li>Берём вашу историю доходов и расходов по месяцам.</li>
                        <li>Считаем устойчивый средний уровень — недавние месяцы весят больше старых, потому что свежие данные лучше описывают вашу текущую ситуацию.</li>
                        <li>Проецируем этот уровень вперёд и накапливаем остаток месяц к месяцу — так получается синяя линия.</li>
                        <li>Прогоняем 1000 случайных сценариев вокруг прогноза (с учётом того, насколько «скачут» ваши данные) — из них складывается жёлтый коридор 80%.</li>
                    </ol>
                    <p style="margin:0 0 6px;"><b>Почему этому можно доверять.</b> Чем больше у вас истории и чем стабильнее операции, тем уже коридор и точнее прогноз. Если данных мало или они сильно скачут — коридор становится широким, и это честный сигнал «пока многое неопределённо», а не ложная точность.</p>
                    <p style="margin:0 0 6px;"><b>Почему линия часто прямая.</b> Прогноз идёт по среднему: каждый месяц прибавляется примерно одинаковая сумма, поэтому накопление ложится прямой. При стабильных данных так и должно быть.</p>
                    <p style="margin:0;"><b>Как проверить самому.</b> Введите другой доход или расход в «Сценарий "что если"» — наклон линии изменится сразу. Или добавьте крупный расход в операции: прогноз пересчитается, и линия уйдёт вниз.</p>
                </div>
            </details>
        </div>
        <table style="width:100%; border-collapse:collapse; font-size:.82rem;">
            <thead>
                <tr style="border-bottom:1px solid var(--c-border); color:var(--c-text3); font-size:.72rem; text-transform:uppercase;">
                    <th style="padding:6px 10px; text-align:left; font-weight:600;">Период</th>
                    <th style="padding:6px 10px; text-align:right; font-weight:600;">Баланс B<sub>t</sub></th>
                    <th style="padding:6px 10px; text-align:right; font-weight:600;">Свободные R<sub>t</sub></th>
                    <th style="padding:6px 10px; text-align:right; font-weight:600; color:var(--c-amber);">Вероятный диапазон (80%)</th>
                    <th style="padding:6px 10px; text-align:right; font-weight:600;">Запас прочности L<sub>t</sub></th>
                    <th style="padding:6px 10px; text-align:right; font-weight:600;">Долговая нагрузка D<sub>t</sub></th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>`;
}

// ── Цвет дельты ──────────────────────────────────────────────
function deltaColor(val, invert = false) {
    if (val === 0) return 'var(--c-text3)';
    const positive = invert ? val < 0 : val > 0;
    return positive ? 'var(--c-green)' : 'var(--c-red)';
}
function deltaSign(val) { return val > 0 ? '+' : ''; }

// ── Визуальные полоски распределения ─────────────────────────
function renderAllocationBar(xObl, xRes, xGoals, rt) {
    if (!rt) return '';
    const pObl  = Math.round(xObl  / rt * 100);
    const pRes  = Math.round(xRes  / rt * 100);
    const pGoal = Math.round(xGoals / rt * 100);
    const segments = [];
    if (pObl  > 0) segments.push(`<div style="flex:${pObl};  background:var(--c-red);   border-radius:2px;" title="Долг ${pObl}%"></div>`);
    if (pRes  > 0) segments.push(`<div style="flex:${pRes};  background:var(--c-amber); border-radius:2px;" title="Резерв ${pRes}%"></div>`);
    if (pGoal > 0) segments.push(`<div style="flex:${pGoal}; background:var(--c-green); border-radius:2px;" title="Цели ${pGoal}%"></div>`);
    if (!segments.length) return '';
    return `
        <div style="display:flex; gap:3px; height:8px; margin:10px 0 4px;">
            ${segments.join('')}
        </div>
        <div style="display:flex; gap:12px; font-size:.70rem; color:var(--c-text3);">
            ${pObl  > 0 ? `<span style="color:var(--c-red);">Долг ${pObl}%</span>` : ''}
            ${pRes  > 0 ? `<span style="color:var(--c-amber);">Резерв ${pRes}%</span>` : ''}
            ${pGoal > 0 ? `<span style="color:var(--c-green);">Цели ${pGoal}%</span>` : ''}
        </div>`;
}

// ── Карточка ТОП-3 ────────────────────────────────────────────
// ── Детализация распределения для наилучшей альтернативы ─────
function renderAllocationDetails(a) {
    const obl = a.obligation_allocation || [];
    const goal = a.goal_allocation || {};

    const oblBlock = (() => {
        const changed = obl.filter(o => Math.abs(parseFloat(o.new_payment || 0) - 0) >= 0)
            .filter(o => parseFloat(a.x_obl_effective || 0) > 0);
        // Покажу только кредиты, которые ЗАТРОНУТЫ досрочкой (новый_платёж < исходного)
        // У нас в obligation_allocation все obls, поэтому фильтруем по тому, что есть xобязательства
        if (parseFloat(a.x_obl_effective || 0) <= 0 || !obl.length) return '';
        return `
        <div class="alt-detail-block">
            <div class="alt-detail-title" style="color:#F472B6;">Куда идёт досрочное погашение</div>
            ${obl.map(o => {
                const rate = (parseFloat(o.interest_rate || 0) * 100).toFixed(1);
                return `
                <div class="alt-detail-item">
                    <span class="alt-arrow">→</span>
                    <span>
                        <strong>${esc(o.name)}</strong>
                        <span style="color:var(--c-text3); font-size:.74rem;">  · ставка ${rate}%</span><br/>
                        <span class="alt-meta">остаток ${fmt.cur(o.new_amount)} ₽ · платёж ${fmt.cur(o.new_payment)} ₽/мес</span>
                    </span>
                </div>`;
            }).join('')}
        </div>`;
    })();

    const goalIds = Object.keys(goal).filter(k => parseFloat(goal[k]) > 0);
    const goalBlock = goalIds.length ? `
        <div class="alt-detail-block">
            <div class="alt-detail-title" style="color:#4ADE80;">Как делятся деньги между целями</div>
            ${goalIds.map(id => `
                <div class="alt-detail-item">
                    <span class="alt-arrow">→</span>
                    <span>Цель #${id}: <strong>${fmt.cur(goal[id])} ₽</strong></span>
                </div>
            `).join('')}
        </div>` : '';

    return oblBlock + goalBlock;
}

function renderTop3Card(a, rank, indicators, weights, rival) {
    const e = a.explanation || {};
    const d = e.delta || {};
    const gains = (e.gains || []);
    const costs = (e.costs || []);
    const { Rt, Lt, Dt } = indicators;

    const rankColors = ['var(--c-green)', 'var(--c-accent-hl)', 'var(--c-text2)'];
    const rankLabels = ['Наилучшая', 'Альтернатива #2', 'Альтернатива #3'];
    const borderColors = [
        'rgba(34,197,94,.3)', 'rgba(99,102,241,.25)', 'rgba(255,255,255,.08)'
    ];
    const rc = rankColors[rank] || 'var(--c-text2)';
    const bc = borderColors[rank] || borderColors[2];

    const afterRt  = a.Rt_new  !== undefined ? fmt.cur(a.Rt_new)          : '—';
    const afterLt  = a.Lt_new  !== undefined ? a.Lt_new.toFixed(3)         : '—';
    const afterDt  = a.Dt_new  !== undefined ? (a.Dt_new*100).toFixed(1)+'%' : '—';

    const dRtStr   = d.Rt  !== undefined ? `${deltaSign(d.Rt)}${fmt.cur(d.Rt)}`       : '';
    const dLtStr   = d.Lt  !== undefined ? `${deltaSign(d.Lt)}${d.Lt.toFixed(3)}`     : '';
    const dDtStr   = d.Dt  !== undefined ? `${deltaSign(d.Dt*100)}${(d.Dt*100).toFixed(1)}%` : '';

    return `
    <article class="glass-panel alt-card" style="border:1px solid ${bc}; padding:20px 22px; margin-bottom:16px; cursor:pointer;" title="Нажмите, чтобы раскрыть разбор">
        <!-- Заголовок -->
        <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="min-width:28px; height:28px; background:${rc}22; border-radius:var(--r-sm);
                            display:grid; place-items:center; font-size:.85rem; font-weight:800; color:${rc};">
                    ${rank + 1}
                </div>
                <div>
                    <div style="font-weight:700; font-size:.95rem;">${esc(a.name)}</div>
                    <div style="font-size:.72rem; color:${rc}; margin-top:2px;">${rankLabels[rank]} · оценка <strong>${a.utility}</strong></div>
                </div>
            </div>
        </div>

        <!-- Insight -->
        <div style="font-size:.83rem; color:var(--c-text2); line-height:1.6; margin-bottom:12px;
                    padding:10px 14px; background:rgba(255,255,255,.04); border-radius:var(--r-sm);
                    border-left:3px solid ${rc};">
            ${esc(e.insight || '')}
        </div>

        <!-- Полоска распределения -->
        ${renderAllocationBar(a.x_obligations, a.x_reserve, a.x_goals, a.x_obligations + a.x_reserve + a.x_goals)}

        <!-- Что выигрываем -->
        ${gains.length ? `
        <div style="margin-top:12px;">
            <div style="font-size:.72rem; text-transform:uppercase; letter-spacing:.5px;
                        color:var(--c-green); font-weight:700; margin-bottom:6px;">Что улучшается</div>
            ${gains.map(g => `
            <div style="display:flex; gap:8px; font-size:.81rem; color:var(--c-text1); margin-bottom:4px; line-height:1.5;">
                <span style="color:var(--c-green); flex-shrink:0;">↑</span>
                <span>${esc(g)}</span>
            </div>`).join('')}
        </div>` : ''}

        <!-- Компромисс -->
        ${costs.length ? `
        <div style="margin-top:10px;">
            <div style="font-size:.72rem; text-transform:uppercase; letter-spacing:.5px;
                        color:var(--c-amber); font-weight:700; margin-bottom:6px;">Компромисс</div>
            ${costs.map(c => `
            <div style="display:flex; gap:8px; font-size:.81rem; color:var(--c-text3); margin-bottom:4px; line-height:1.5;">
                <span style="color:var(--c-amber); flex-shrink:0;">~</span>
                <span>${esc(c)}</span>
            </div>`).join('')}
        </div>` : ''}

        ${renderAllocationDetails(a)}

        <!-- Показатели до / после -->
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-top:14px;
                    padding-top:12px; border-top:1px solid var(--c-border); font-size:.78rem;">
            <div style="background:rgba(255,255,255,.03); border-radius:var(--r-sm); padding:8px 10px;">
                <div style="color:var(--c-text3); margin-bottom:2px;">Свободные R<sub>t</sub></div>
                <div style="font-weight:700;">${afterRt}</div>
                ${dRtStr ? `<div style="font-size:.70rem; color:${deltaColor(d.Rt)};">${dRtStr} к текущему</div>` : ''}
            </div>
            <div style="background:rgba(255,255,255,.03); border-radius:var(--r-sm); padding:8px 10px;">
                <div style="color:var(--c-text3); margin-bottom:2px;">Lt'</div>
                <div style="font-weight:700;">${afterLt}</div>
                ${dLtStr ? `<div style="font-size:.70rem; color:${deltaColor(d.Lt)};">${dLtStr}</div>` : ''}
            </div>
            <div style="background:rgba(255,255,255,.03); border-radius:var(--r-sm); padding:8px 10px;">
                <div style="color:var(--c-text3); margin-bottom:2px;">Dt'</div>
                <div style="font-weight:700;">${afterDt}</div>
                ${dDtStr ? `<div style="font-size:.70rem; color:${deltaColor(d.Dt, true)};">${dDtStr}</div>` : ''}
            </div>
        </div>
        ${renderCalcDetails(a, indicators, weights, rival)}
    </article>`;
}

// ── Раскрываемый расчёт альтернативы (детали формул) ──────────
function renderCalcDetails(a, ind, weights, rival) {
    const It = ind.It || 0, Et = ind.Et || 0, SigmaP = ind.SigmaP || 0, Rt = ind.Rt || 0;
    const m = v => fmt.cur(v);
    const step = (n, title, body) => `
        <div class="calc-row">
            <span class="calc-label">Шаг ${n} · ${title}</span>
            <div style="margin-top:4px;">${body}</div>
        </div>`;

    // ── Шаг 1: свободные деньги ──
    const s1 = `${m(It)} доход − ${m(Et)} расходы − ${m(SigmaP)} платежи по кредитам = <b>${m(Rt)}</b>`;

    // ── Шаг 2: перебор вариантов ──
    const s2 = `Алгоритм перебрал все варианты распределения этой суммы (доли с шагом 10%: долг / резерв / цели), отбросил нарушающие ограничения по долговой нагрузке и ликвидности, остальные оценил и отранжировал. Этот план: на досрочку <b>${m(a.x_obligations)}</b> · в резерв <b>${m(a.x_reserve)}</b> · на цели <b>${m(a.x_goals)}</b>.`;

    // ── Шаг 3: Avalanche (досрочка) ──
    let s3 = '';
    const av = a.avalanche_detail;
    if (av && (a.x_obligations > 0 || (av.skipped || []).length)) {
        const rb = (av.r_bench * 100).toFixed(1);
        let parts = [];
        if ((av.passed || []).length) {
            parts.push(`Досрочно гасим только кредиты со ставкой ≥ ${rb}% (ниже — деньгам выгоднее работать на накопительном счёте), в порядке убывания ставки:`);
            parts.push((av.passed || []).map(o => `
                <div class="alt-detail-item"><span class="alt-arrow">→</span>
                <span><strong>${esc(o.name)}</strong> (${(o.interest_rate * 100).toFixed(1)}%): влито ${m(o.paid_in)}${o.closed ? ' — <b style="color:var(--c-green);">кредит закрыт</b>' : ''}${o.payment_saved > 0 ? `, платёж ↓ на ${m(o.payment_saved)}/мес` : ''}</span></div>`).join(''));
        }
        if ((av.skipped || []).length) {
            parts.push(`<div style="margin-top:4px;">Не гасим досрочно: ${(av.skipped || []).map(o => `<strong>${esc(o.name)}</strong> (${(o.interest_rate * 100).toFixed(1)}% &lt; ${rb}%)`).join(', ')} — дешевле бенчмарка.</div>`);
        }
        if (av.x_unused_to_goals > 0) {
            parts.push(`<div style="margin-top:4px;">Высвобожденные <b>${m(av.x_unused_to_goals)}</b> перенаправлены на цели.</div>`);
        }
        if (av.delta_payment > 0) {
            parts.push(`<div style="margin-top:4px;">Итог: ежемесячные платежи снизятся на <b style="color:var(--c-green);">${m(av.delta_payment)}</b>.</div>`);
        }
        if (parts.length) s3 = step(3, 'Какие кредиты гасим (стратегия Avalanche)', parts.join(''));
    }

    // ── Шаг 4: распределение по целям ──
    let s4 = '';
    const gb = a.goal_breakdown || [];
    if (gb.length && a.x_goals > 0) {
        const CAT_RU = { income_growth: 'рост дохода', safety: 'безопасность', material: 'материальная', emotional: 'эмоциональная' };
        const rows = gb.map(g => `
            <div style="display:grid; grid-template-columns:minmax(0,1.4fr) auto auto auto auto; gap:6px 10px; font-size:.76rem; padding:3px 0; align-items:center;">
                <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${esc(g.name)}</span>
                <span style="color:var(--c-text3);">вес ${g.weight} (${CAT_RU[g.category] || g.category})</span>
                <span style="color:var(--c-text3);">срочн. ×${g.urgency}</span>
                <span style="color:var(--c-text3);">${(g.share * 100).toFixed(0)}%</span>
                <span style="text-align:right;"><b>${m(g.amount)}</b></span>
            </div>`).join('');
        s4 = step(s3 ? 4 : 3, 'Как поделили деньги между целями', `
            <div style="font-size:.76rem; color:var(--c-text3); margin-bottom:6px;">Каждая цель получает долю по формуле: вес категории × срочность (12 ÷ месяцев до срока). Важные и близкие цели получают больше.</div>
            <div style="padding:8px 12px; background:rgba(255,255,255,.03); border-radius:8px;">${rows}</div>`);
    }

    // ── Шаг 5: оценка U с сырыми значениями ──
    let s5 = '';
    if (a.scores && weights) {
        const crit = [
            { label: 'Свободные деньги', raw: a.Rt_new !== undefined ? m(a.Rt_new) : '—', w: weights.w_rt, n: a.scores.Rt_norm },
            { label: 'Ликвидность', raw: a.Lt_new !== undefined ? a.Lt_new.toFixed(3) : '—', w: weights.w_lt, n: a.scores.Lt_norm },
            { label: 'Снижение долга', raw: a.Dt_new !== undefined ? (a.Dt_new * 100).toFixed(1) + '%' : '—', w: weights.w_dt, n: a.scores.Dt_norm },
            { label: 'Цели', raw: a.Si !== undefined ? (a.Si * 100).toFixed(1) + '%' : '—', w: weights.w_goals, n: a.scores.Si_norm },
        ];
        const rows = crit.map(c => `
            <div style="display:grid; grid-template-columns:minmax(0,1fr) auto auto; gap:6px 12px; font-size:.76rem; padding:3px 0;">
                <span style="color:var(--c-text2);">${c.label} <span style="color:var(--c-text3);">(${c.raw})</span></span>
                <span style="color:var(--c-text3); white-space:nowrap;">${c.n.toFixed(2)} × вес ${c.w.toFixed(2)}</span>
                <span style="text-align:right;"><b>${(c.w * c.n).toFixed(3)}</b></span>
            </div>`).join('');
        const dominant = crit.reduce((x, y) => (y.w * y.n > x.w * x.n ? y : x));
        let rivalLine = '';
        if (rival && rival.utility !== undefined) {
            const diff = a.utility - rival.utility;
            rivalLine = diff > 0.0005
                ? `<div style="margin-top:6px; font-size:.76rem;">Ближайший конкурент «${esc(rival.name || 'Альтернатива #2')}» набрал <b>${rival.utility}</b> — этот план впереди на <b>${diff.toFixed(3)}</b>.</div>`
                : `<div style="margin-top:6px; font-size:.76rem;">План «${esc(rival.name || 'Альтернатива #2')}» набрал столько же (<b>${rival.utility}</b>) — по вашему профилю они равноценны, можно выбрать любой.</div>`;
        }
        s5 = step(s3 && s4 ? 5 : (s3 || s4 ? 4 : 3), `Итоговая оценка U = ${a.utility}`, `
            <div style="font-size:.76rem; color:var(--c-text3); margin-bottom:6px;">Каждый критерий сравнивается со всеми допустимыми планами и приводится к шкале 0–1 (1.00 = лучший среди всех по этому критерию), затем умножается на вес вашего профиля риска.</div>
            <div style="padding:8px 12px; background:rgba(255,255,255,.03); border-radius:8px;">
                ${rows}
                <div style="display:flex; justify-content:space-between; font-size:.76rem; padding-top:6px; margin-top:4px; border-top:1px solid var(--c-border);">
                    <span style="color:var(--c-text2);">Итог</span><span><b>${a.utility}</b> из 1.00</span>
                </div>
            </div>
            <div style="margin-top:6px; font-size:.76rem; color:var(--c-text3);">Наибольший вклад дал критерий «${dominant.label}» — по нему этот план обходит остальные.</div>
            ${rivalLine}`);
    }

    return `
    <details class="calc-details">
        <summary>Как алгоритм пришёл к этому — полный разбор</summary>
        <div class="calc-body">
            ${step(1, 'Свободные деньги (Rt)', s1)}
            ${step(2, 'Перебор и отбор вариантов', s2)}
            ${s3}
            ${s4}
            ${s5}
        </div>
    </details>`;
}

// ── Компактная строка для полного списка ──────────────────────
// ── Мини-разбор оценки альтернативы (для строк полного списка) ─
function altBreakdownHTML(a, weights, best) {
    if (!a.scores || !weights) return '';
    const m = v => fmt.cur(v);
    const crit = [
        { key: 'Rt', label: 'Свободные деньги', raw: a.Rt_new != null ? m(a.Rt_new) : '—', w: weights.w_rt, n: a.scores.Rt_norm },
        { key: 'Lt', label: 'Ликвидность', raw: a.Lt_new != null ? a.Lt_new.toFixed(3) : '—', w: weights.w_lt, n: a.scores.Lt_norm },
        { key: 'Dt', label: 'Снижение долга', raw: a.Dt_new != null ? (a.Dt_new * 100).toFixed(1) + '%' : '—', w: weights.w_dt, n: a.scores.Dt_norm },
        { key: 'Si', label: 'Цели', raw: a.Si != null ? (a.Si * 100).toFixed(1) + '%' : '—', w: weights.w_goals, n: a.scores.Si_norm },
    ];
    const rows = crit.map(c => `
        <div style="display:grid; grid-template-columns:minmax(0,1fr) auto auto; gap:6px 12px; font-size:.74rem; padding:2px 0;">
            <span style="color:var(--c-text2);">${c.label} <span style="color:var(--c-text3);">(${c.raw})</span></span>
            <span style="color:var(--c-text3); white-space:nowrap;">${c.n.toFixed(2)} × ${c.w.toFixed(2)}</span>
            <span style="text-align:right;"><b>${(c.w * c.n).toFixed(3)}</b></span>
        </div>`).join('');

    const isBest = a === best;
    let cmp = '';
    if (isBest) {
        cmp = `<div style="margin-top:8px; font-size:.74rem; color:var(--c-green); line-height:1.5;">Это рекомендованный план — лучшая суммарная оценка по вашему профилю риска.</div>`;
    } else if (best && best.scores && best.utility !== undefined) {
        let worst = null, worstLoss = -1;
        crit.forEach(c => {
            const bn = best.scores[c.key + '_norm'];
            if (bn === undefined) return;
            const loss = c.w * bn - c.w * c.n;
            if (loss > worstLoss) { worstLoss = loss; worst = c; }
        });
        const diff = best.utility - a.utility;
        cmp = `<div style="margin-top:8px; font-size:.74rem; color:var(--c-text2); line-height:1.5;">
            Уступает рекомендованному плану на <b style="color:var(--c-amber);">${diff.toFixed(3)}</b> балла${worst ? ` — главным образом по критерию «${worst.label}»` : ''}.
        </div>`;
    }

    return `
        <div style="padding:10px 14px 12px 50px; background:rgba(255,255,255,.02);">
            <div style="font-size:.72rem; color:var(--c-text3); margin-bottom:6px;">Из чего сложилась оценка (норм. значение × вес профиля):</div>
            <div style="padding:8px 12px; background:rgba(255,255,255,.03); border-radius:8px;">
                ${rows}
                <div style="display:flex; justify-content:space-between; font-size:.74rem; padding-top:5px; margin-top:4px; border-top:1px solid var(--c-border);">
                    <span style="color:var(--c-text2);">Итог</span><span><b>${a.utility}</b> из 1.00</span>
                </div>
            </div>
            ${cmp}
        </div>`;
}

// ── Компактная кликабельная строка для полного списка ─────────
function renderAltRow(a, idx, weights, best) {
    const isBest = a === best;
    return `
    <details class="alt-row" style="border-bottom:1px solid var(--c-border);">
        <summary style="display:grid; grid-template-columns:28px 1fr auto auto auto auto 16px; align-items:center;
                    gap:10px; padding:8px 12px; font-size:.8rem; cursor:pointer;${isBest ? ' background:rgba(34,197,94,.05);' : ''}">
            <span style="color:var(--c-text3); font-size:.72rem; text-align:center;">${idx + 1}</span>
            <span>${esc(a.name)}${isBest ? ' <span style="color:var(--c-green); font-size:.68rem; font-weight:600;">рекомендованный</span>' : ''}</span>
            <span style="color:var(--c-red);   text-align:right;">${a.x_obligations > 0 ? fmt.cur(a.x_obligations) : '—'}</span>
            <span style="color:var(--c-amber); text-align:right;">${a.x_reserve    > 0 ? fmt.cur(a.x_reserve)    : '—'}</span>
            <span style="color:var(--c-green); text-align:right;">${a.x_goals      > 0 ? fmt.cur(a.x_goals)      : '—'}</span>
            <span style="color:var(--c-accent-hl); font-weight:700; text-align:right;">${a.utility}</span>
            <span class="alt-row-chevron" style="color:var(--c-text3); font-size:.7rem; text-align:center;">▸</span>
        </summary>
        ${altBreakdownHTML(a, weights, best)}
    </details>`;
}

// ── Кликабельная строка отклонённой альтернативы (почему отсеяли) ─
function rejectedRowHTML(a) {
    const viol = a.violations || [];
    const vals = [
        { label: 'Свободные деньги после плана (Rt)', val: a.Rt_new != null ? fmt.cur(a.Rt_new) + ' ₽' : '—' },
        { label: 'Запас прочности (Lt)', val: a.Lt_new != null ? a.Lt_new.toFixed(3) : '—' },
        { label: 'Долговая нагрузка (Dt)', val: a.Dt_new != null ? (a.Dt_new * 100).toFixed(1) + '%' : '—' },
    ];
    const rows = vals.map(c => `
        <div style="display:grid; grid-template-columns:1fr auto; gap:6px 12px; font-size:.74rem; padding:2px 0;">
            <span style="color:var(--c-text2);">${c.label}</span>
            <span style="color:var(--c-text1); font-weight:600;">${c.val}</span>
        </div>`).join('');
    const why = viol.length
        ? viol.map(v => `<div style="display:flex; gap:8px; font-size:.76rem; color:var(--c-text2); margin-top:4px; line-height:1.5;"><span style="color:var(--c-red); flex-shrink:0;">•</span><span>${esc(v)}</span></div>`).join('')
        : '<div style="font-size:.76rem; color:var(--c-text3);">Не прошёл по ограничениям модели.</div>';
    return `
    <details class="alt-row" style="border-bottom:1px solid var(--c-border);">
        <summary style="display:grid; grid-template-columns:1fr auto 16px; align-items:center; gap:10px;
                    padding:7px 12px; font-size:.8rem; cursor:pointer; opacity:.78;">
            <span>${esc(a.name)}</span>
            <span style="font-size:.72rem; color:var(--c-red); text-align:right; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${viol.length ? esc(viol[0]) : 'не прошёл ограничения'}</span>
            <span class="alt-row-chevron" style="color:var(--c-text3); font-size:.7rem; text-align:center;">▸</span>
        </summary>
        <div style="padding:10px 14px 12px; background:rgba(244,63,94,.03);">
            <div style="font-size:.72rem; color:var(--c-text3); margin-bottom:8px;">Распределение: долг ${fmt.cur(a.x_obligations || 0)} · резерв ${fmt.cur(a.x_reserve || 0)} · цели ${fmt.cur(a.x_goals || 0)}</div>
            <div style="font-size:.72rem; color:var(--c-red); font-weight:600; margin-bottom:2px;">Почему отклонён:</div>
            ${why}
            <div style="margin-top:8px; padding:8px 12px; background:rgba(255,255,255,.03); border-radius:8px;">${rows}</div>
        </div>
    </details>`;
}

function exportPlanCSV(res) {
    if (!res || !res.top3 || !res.top3.length) return;
    const ind = res.indicators || {};
    const best = res.top3[0];
    const rows = [];
    const push = (a, b) => rows.push([a, b]);

    push('FINPILOT — план распределения', '');
    push('Профиль риска', res.risk_profile || '');
    push('', '');
    push('ПОКАЗАТЕЛЬ', 'ЗНАЧЕНИЕ');
    push('Свободные деньги (Rt), ₽', ind.Rt ?? '');
    push('Ликвидность (Lt)', ind.Lt ?? '');
    push('Долговая нагрузка (Dt), %', ((ind.Dt ?? 0) * 100).toFixed(1));
    push('Подушка (BLR), мес', (ind.BLR ?? 0).toFixed(2));
    push('', '');
    push('РЕКОМЕНДОВАННОЕ РАСПРЕДЕЛЕНИЕ', best.name || '');
    push('На досрочное погашение, ₽', best.x_obligations ?? 0);
    push('В подушку безопасности, ₽', best.x_reserve ?? 0);
    push('На цели, ₽', best.x_goals ?? 0);
    push('Оценка полезности U', best.utility ?? '');
    push('', '');
    push('ВСЕ АЛЬТЕРНАТИВЫ (топ-3)', '');
    push('#', 'Название;Долг;Резерв;Цели;Оценка');
    res.top3.forEach((a, i) => {
        push(i + 1, `${a.name};${a.x_obligations || 0};${a.x_reserve || 0};${a.x_goals || 0};${a.utility}`);
    });

    const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(';')).join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `finpilot-plan-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function renderPlanning(res) {
    if (!res) return;
    state.lastPlan = res;  // для экспорта (CSV / печать)
    const exportBar = $('#export-bar');
    if (exportBar) exportBar.style.display = (res.top3 && res.top3.length) ? 'flex' : 'none';
    const ind = res.indicators || {};
    const { Rt, Lt, Dt, Bt = 0, Bliq = 0, BLR = 0, SigmaP = 0, It = 0, Et = 0 } = ind;

    // Показатели
    const rtEl = $('#plan-rt');
    const ltEl = $('#plan-lt');
    const dtEl = $('#plan-dt');
    if (rtEl) { rtEl.textContent = fmt.cur(Rt); rtEl.style.color = Rt >= 0 ? 'var(--c-green)' : 'var(--c-red)'; }
    if (ltEl) { ltEl.textContent = `${Number(Lt).toFixed(1)} мес`; ltEl.style.color = Lt >= 2.5 ? 'var(--c-green)' : Lt >= 1 ? 'var(--c-amber)' : 'var(--c-red)'; }
    if (dtEl) { dtEl.textContent = fmt.pct(Dt); dtEl.style.color = Dt <= 0.36 ? 'var(--c-green)' : Dt <= 0.5 ? 'var(--c-amber)' : 'var(--c-red)'; }

    // Человекочитаемая расшифровка показателей (без формульной нотации)
    const rtForm = $('#plan-rt-formula');
    const ltForm = $('#plan-lt-formula');
    const dtForm = $('#plan-dt-formula');
    if (rtForm) rtForm.innerHTML = `${fmt.num(It)} доход − ${fmt.num(Et)} траты − ${fmt.num(SigmaP)} кредиты`;
    if (ltForm) ltForm.innerHTML = `месяцев жизни на свободной подушке`;
    if (dtForm) dtForm.innerHTML = `${fmt.num(SigmaP)} платежей из ${fmt.num(It)} дохода`;

    // Веса
    const wd = $('#weights-display');
    if (wd && res.weights) {
        const w = res.weights;
        wd.innerHTML = `
            <div style="font-size:.78rem; color:var(--c-text3); margin-bottom:8px;">Профиль:
                <strong style="color:var(--c-accent-hl);">${esc(res.risk_profile)}</strong>
            </div>
            <div class="rec-formula" style="margin:0;">
                <div style="display:grid; grid-template-columns:auto 1fr auto; gap:2px 10px; font-size:.78rem;">
                    <span style="opacity:.6;">w₁ (Rt)</span><span>Ресурс</span><strong>${w.w_rt}</strong>
                    <span style="opacity:.6;">w₂ (Lt)</span><span>Ликвидность</span><strong>${w.w_lt}</strong>
                    <span style="opacity:.6;">w₃ (Dt)</span><span>Долговая нагрузка</span><strong>${w.w_dt}</strong>
                    <span style="opacity:.6;">w₄ (Si)</span><span>Обеспеченность целей</span><strong>${w.w_goals}</strong>
                </div>
            </div>`;
    }

    // Входные данные
    const inp = $('#input-display');
    if (inp) {
        const s = res.input_summary || {};
        const rowI = (label, val) => `<div style="display:flex; justify-content:space-between; gap:8px; padding:4px 0; flex-wrap:wrap;"><span style="color:var(--c-text3); min-width:0;">${label}</span><strong style="color:var(--c-green); text-align:right; margin-left:auto;">${val}</strong></div>`;
        const rowE = (label, val) => `<div style="display:flex; justify-content:space-between; gap:8px; padding:4px 0; flex-wrap:wrap;"><span style="color:var(--c-text3); min-width:0;">${label}</span><strong style="color:var(--c-red); text-align:right; margin-left:auto;">${val}</strong></div>`;
        inp.innerHTML = `
            <div style="font-size:.68rem; color:var(--c-text3); margin-bottom:10px; padding:6px 10px; background:var(--c-surface2); border-radius:var(--r-sm); text-align:center;">
                Источник данных: <strong style="color:var(--c-text2);">база данных пользователя</strong>
            </div>
            <div style="display:grid; grid-template-columns:1fr; gap:12px; font-size:.8rem;">
                <div style="min-width:0; border:1px solid rgba(74,222,128,.35); border-radius:var(--r-sm); padding:10px 12px; background:rgba(74,222,128,.05);">
                    <div style="font-size:.68rem; font-weight:700; letter-spacing:.06em; color:var(--c-green); margin-bottom:6px;">ПРИХОДИТ / ЕСТЬ</div>
                    ${rowI('Доходы в месяц', fmt.cur(s.income))}
                    ${rowI('Накоплено на целях (Bt)', fmt.cur(Bt))}
                    ${rowI('Накопления (Bliq)', fmt.cur(Bliq))}
                </div>
                <div style="min-width:0; border:1px solid rgba(248,113,113,.35); border-radius:var(--r-sm); padding:10px 12px; background:rgba(248,113,113,.05);">
                    <div style="font-size:.68rem; font-weight:700; letter-spacing:.06em; color:var(--c-red); margin-bottom:6px;">УХОДИТ</div>
                    ${rowE('Расходы в месяц', fmt.cur(s.expense))}
                    ${rowE('Платежи по кредитам', fmt.cur(SigmaP))}
                </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr auto; gap:4px 12px; font-size:.78rem; margin-top:10px; padding-top:10px; border-top:1px solid var(--c-border);">
                <span style="color:var(--c-text3);">Подушка (BLR)</span><strong>${BLR.toFixed(2)} мес</strong>
                <span style="color:var(--c-text3);">Ставка-ориентир (r_bench)</span><strong>${((s.r_bench||0.14)*100).toFixed(1)}%${s.r_bench_source === 'best_asset_rate' ? ' <span style="font-weight:400; color:var(--c-text3); font-size:.7rem;">— из вашего накопит. счёта</span>' : ''}</strong>
            </div>
            <div style="margin-top:10px; font-size:.72rem; color:var(--c-text3);">
                ${s.transactions_count || 0} операций · ${s.obligations_count || 0} обяз. · ${s.goals_count || 0} целей · ${s.liquid_assets_count || 0} ликв. активов
            </div>`;
    }

    // Bliq preallocation block (если сработала предобработка)
    const bp = res.bliq_preallocation;
    if (bp && bp.closed_goals && bp.closed_goals.length) {
        const banner = `
            <div class="alt-detail-block" style="border-color:#60A5FA; margin-bottom:12px;">
                <div class="alt-detail-title" style="color:#60A5FA;">Близкие цели можно закрыть из накоплений</div>
                <div style="font-size:.82rem; color:var(--c-text); margin-bottom:8px;">
                    У вас есть накопления, которыми можно разом закрыть цели с близким сроком (до 3 месяцев) — на это уйдёт <strong>${fmt.cur(bp.bliq_used)}</strong>:
                </div>
                ${bp.closed_goals.map(g => `
                    <div class="alt-detail-item">
                        <span class="alt-arrow">→</span>
                        <span><strong>${esc(g.name)}</strong>: ${fmt.cur(g.amount)}</span>
                    </div>
                `).join('')}
                <div class="alt-meta" style="margin-top:6px;">Останется накоплений: ${fmt.cur(bp.bliq_remaining)}</div>
            </div>`;
        const bpEl = $('#bliq-preallocation');
        if (bpEl) bpEl.innerHTML = banner;
    } else {
        const bpEl = $('#bliq-preallocation');
        if (bpEl) bpEl.innerHTML = '';
    }

    // Топ-3
    const optC = $('#best-container');
    if (optC) {
        if (res.top3 && res.top3.length) {
            optC.innerHTML = `
                <div style="font-size:.78rem; color:var(--c-text3); margin-bottom:12px;">
                    Сгенерировано <strong>${res.alternatives_total}</strong> альтернатив ·
                    Допустимых: <strong>${res.admissible_count}</strong> ·
                    Отклонено: <strong>${res.rejected_count}</strong>
                </div>
                ${res.top3.map((a, i) => renderTop3Card(a, i, res.indicators, res.weights, res.top3[i + 1] || null)).join('')}`;
        } else {
            optC.innerHTML = `
                <div class="glass-panel" style="border:1px solid rgba(244,63,94,.2); padding:20px 24px; text-align:center;">
                    <div style="font-weight:700; color:var(--c-red); margin-bottom:6px;">Все альтернативы отклонены (структурный диагноз)</div>
                    <div style="font-size:.84rem; color:var(--c-text3);">
                        A_доп = ∅. Свободный поток Rt = ${fmt.cur(Rt)} ₽. Распределять нечего —
                        требуется пересмотр расходов или рефинансирование дорогих кредитов.
                    </div>
                </div>`;
        }
    }

    // Полный список — схлопнут
    const altC = $('#alternatives-container');
    if (altC && res.ranked && res.ranked.length > 3) {
        altC.innerHTML = `
            <details style="margin-top:4px;">
                <summary style="font-size:.82rem; color:var(--c-text3); cursor:pointer; padding:8px 0;
                                display:flex; align-items:center; gap:6px;">
                    Все ${res.ranked.length} допустимых альтернатив (нажмите на любую — разбор оценки)
                </summary>
                <div style="margin-top:10px; border:1px solid var(--c-border); border-radius:var(--r-sm); overflow:hidden;">
                    <div style="display:grid; grid-template-columns:28px 1fr auto auto auto auto 16px; gap:10px;
                                padding:6px 12px; font-size:.68rem; text-transform:uppercase; letter-spacing:.4px;
                                color:var(--c-text3); border-bottom:1px solid var(--c-border); font-weight:600;">
                        <span>#</span><span>Название</span>
                        <span style="color:var(--c-red);">Долг</span>
                        <span style="color:var(--c-amber);">Резерв</span>
                        <span style="color:var(--c-green);">Цели</span>
                        <span>Оценка</span>
                        <span></span>
                    </div>
                    ${res.ranked.map((a, i) => renderAltRow(a, i, res.weights, res.ranked[0])).join('')}
                </div>
            </details>`;
    } else if (altC) {
        altC.innerHTML = '';
    }

    // Отклонённые
    const rejC = $('#rejected-container');
    if (rejC && res.rejected && res.rejected.length) {
        rejC.innerHTML = `
            <details style="margin-top:4px;">
                <summary style="font-size:.82rem; color:var(--c-text3); cursor:pointer; padding:8px 0;">
                    Отклонено по ограничениям: ${res.rejected.length} (нажмите на любую — почему отсеяли)
                </summary>
                <div style="margin-top:8px; border:1px solid var(--c-border); border-radius:var(--r-sm); overflow:hidden;">
                    ${res.rejected.map(a => rejectedRowHTML(a)).join('')}
                </div>
            </details>`;
    } else if (rejC) {
        rejC.innerHTML = '';
    }
}

// ── Клик по метрик-картам дашборда → детальное пояснение ─────
document.addEventListener('click', e => {
    const closeBtn = e.target.closest('#metric-explain-close');
    if (closeBtn) {
        const panel = $('#metric-explain');
        if (panel) { panel.style.display = 'none'; panel.innerHTML = ''; }
        document.querySelectorAll('.metric-clickable.metric-active').forEach(c => c.classList.remove('metric-active'));
        return;
    }
    const card = e.target.closest('.metric-clickable');
    if (!card) return;
    const panel = $('#metric-explain');
    if (!panel || !state.lastIndicators) return;
    const key = card.dataset.metric;
    const wasActive = card.classList.contains('metric-active');
    document.querySelectorAll('.metric-clickable.metric-active').forEach(c => c.classList.remove('metric-active'));
    if (wasActive) {
        panel.style.display = 'none'; panel.innerHTML = '';
        return;
    }
    card.classList.add('metric-active');
    panel.innerHTML = metricExplainHTML(key, state.lastIndicators);
    panel.style.display = 'block';
});

// ── Клик по карточке альтернативы → раскрыть/свернуть разбор ──
document.addEventListener('click', e => {
    const card = e.target.closest('.alt-card');
    if (!card) return;
    // клики по самим details/summary обрабатывает браузер — не дублируем
    if (e.target.closest('.calc-details')) return;
    const det = card.querySelector('.calc-details');
    if (det) det.open = !det.open;
});

// ── Пагинация журнала операций ────────────────────────────────
document.addEventListener('click', e => {
    const btn = e.target.closest('#transactions-pagination [data-page]');
    if (!btn || btn.disabled) return;
    const p = Number(btn.dataset.page);
    if (!p || p === state.page) return;
    state.page = p;
    renderTransactions();
});

// ── Период трат на дашборде ───────────────────────────────────
document.addEventListener('change', e => {
    if (e.target.id === 'spending-period') {
        loadSpendingBreakdown(Number(e.target.value) || 30);
    }
});

// ── Фильтр по датам в журнале ─────────────────────────────────
// Слушаем и change, и input: WebKit/DuckDuckGo шлёт change для type=date
// только при потере фокуса, а input — сразу при выборе даты.
function applyTxDateFilter(e) {
    if (e.target.id === 'tx-date-from') { state.dateFrom = e.target.value || null; state.page = 1; renderTransactions(); }
    if (e.target.id === 'tx-date-to')   { state.dateTo   = e.target.value || null; state.page = 1; renderTransactions(); }
}
document.addEventListener('change', applyTxDateFilter);
document.addEventListener('input', applyTxDateFilter);
document.addEventListener('click', e => {
    if (e.target.id !== 'tx-export-csv') return;
    const params = new URLSearchParams();
    if (state.dateFrom) params.set('date_from', state.dateFrom);
    if (state.dateTo) params.set('date_to', state.dateTo);
    window.location.href = `/api/transactions/export.csv?${params.toString()}`;
});
document.addEventListener('click', e => {
    if (e.target.id !== 'tx-date-reset') return;
    state.dateFrom = state.dateTo = null;
    state.page = 1;
    const f = $('#tx-date-from'), t = $('#tx-date-to');
    if (f) f.value = ''; if (t) t.value = '';
    renderTransactions();
});

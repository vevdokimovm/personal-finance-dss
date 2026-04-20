/* ═══════════════════════════════════════════════════════════
   PersFin СППР — app.js v3.0
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

async function api(url, opts = {}) {
    const r = await fetch(url, opts);
    const ct = r.headers.get('content-type') || '';
    const d = ct.includes('json') ? await r.json() : {};
    if (!r.ok) throw new Error(d.detail || 'Ошибка сервера');
    return d;
}

function openModal(m)  { if (m) { m.setAttribute('aria-hidden', 'false'); } }
function closeModal(m) { if (m) { m.setAttribute('aria-hidden', 'true'); } }

// ── State ────────────────────────────────────────────────────
const state = {
    limit: 10,
    transactions: [],
    obligations: [],
    goals: [],
};

// ── Boot ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    bindGlobalUI();
    bindPlanningUI();
    loadPage();
});

// ── Global UI Bindings ───────────────────────────────────────
function bindGlobalUI() {
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

    // Demo buttons
    on($('#load-demo-button'), 'click', async () => {
        const btn = $('#load-demo-button');
        btn.disabled = true; btn.textContent = 'Загрузка…';
        try { await api('/api/demo/load', { method: 'POST' }); await loadPage(); }
        catch(e) { console.error(e); }
        finally { btn.disabled = false; btn.innerHTML = svgIcon('download', 16) + ' Загрузить демо'; }
    });

    on($('#clear-demo-button'), 'click', async () => {
        const btn = $('#clear-demo-button');
        btn.disabled = true; btn.textContent = 'Очистка…';
        try { await api('/api/demo/clear', { method: 'POST' }); await loadPage(); }
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
    on($('#transaction-form'), 'submit', async e => {
        e.preventDefault();
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
        } catch (e) { alert(e.message); }
    });

    // Obligation modal
    on($('#open-obligation-modal'), 'click', () => {
        openModal($('#obligation-modal'));
    });

    on($('#obligation-form'), 'submit', async e => {
        e.preventDefault();
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
                    comment: $('#obligation-comment').value.trim() || null,
                }),
            });
            closeModal($('#obligation-modal'));
            $('#obligation-form').reset();
            await loadPage();
        } catch (e) { alert(e.message); }
    });

    // Goal modal
    on($('#open-goal-modal'), 'click', () => {
        $('#goal-deadline').value = fmt.today();
        openModal($('#goal-modal'));
    });

    on($('#goal-form'), 'submit', async e => {
        e.preventDefault();
        try {
            await api('/api/goals', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: $('#goal-name').value.trim(),
                    target_amount: pn($('#goal-target-amount').value),
                    current_amount: pn($('#goal-current-amount').value),
                    deadline: new Date($('#goal-deadline').value).toISOString(),
                    comment: $('#goal-comment').value.trim() || null,
                }),
            });
            closeModal($('#goal-modal'));
            $('#goal-form').reset();
            await loadPage();
        } catch (e) { alert(e.message); }
    });

    // Delete handlers (delegated)
    on($('#transactions-list'), 'click', async e => {
        const btn = e.target.closest('.delete-button');
        if (!btn) return;
        btn.disabled = true;
        try {
            await api(`/api/transactions/${btn.dataset.transactionId}`, { method: 'DELETE' });
            await loadPage();
        } catch(e) { alert(e.message); btn.disabled = false; }
    });

    on($('#obligations-list'), 'click', async e => {
        const btn = e.target.closest('.delete-button');
        if (!btn) return;
        btn.disabled = true;
        try {
            await api(`/api/obligations/${btn.dataset.obligationId}`, { method: 'DELETE' });
            await loadPage();
        } catch(e) { alert(e.message); btn.disabled = false; }
    });

    on($('#goals-list'), 'click', async e => {
        const btn = e.target.closest('.delete-button');
        if (!btn) return;
        btn.disabled = true;
        try {
            await api(`/api/goals/${btn.dataset.goalId}`, { method: 'DELETE' });
            await loadPage();
        } catch(e) { alert(e.message); btn.disabled = false; }
    });

    // Limit switcher
    on($('#transactions-limit-switcher'), 'click', e => {
        const btn = e.target.closest('[data-limit]');
        if (!btn) return;
        state.limit = Number(btn.dataset.limit);
        $$('.limit-button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderTransactions();
    });

    // Simulator form
    on($('#analysis-form'), 'submit', async e => {
        e.preventDefault();
        const inc = pn($('#income').value);
        const exp = pn($('#expense').value);
        const txns = [];
        if (inc > 0) txns.push({ amount: inc, type: 'income', category: 'Симуляция', date: new Date().toISOString() });
        if (exp > 0) txns.push({ amount: exp, type: 'expense', category: 'Симуляция', date: new Date().toISOString() });
        try {
            const res = await api('/api/recommendation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ transactions: txns, obligations: state.obligations, goals: state.goals }),
            });
            renderDashboardCards(res);
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
            $('#drop-label').textContent = `📎 ${file.name} (${(file.size / 1024).toFixed(1)} КБ)`;
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

    try {
        // Fetch data in parallel where needed
        const promises = [];
        const needs = { t: isDash || !!tList, o: isDash || !!oList, g: !!gList };
        
        if (needs.t) promises.push(api('/api/transactions'));
        else promises.push(Promise.resolve(null));
        
        if (needs.o) promises.push(api('/api/obligations'));
        else promises.push(Promise.resolve(null));
        
        if (needs.g) promises.push(api('/api/goals'));
        else promises.push(Promise.resolve(null));
        
        const [trans, obs, goals] = await Promise.all(promises);

        if (trans !== null) state.transactions = trans;
        if (obs !== null)   state.obligations = obs;
        if (goals !== null) state.goals = goals;

        // Dashboard summary
        if (isDash) {
            const inc = state.transactions.filter(t => t.type === 'income').reduce((s, t) => s + pn(t.amount), 0);
            const exp = state.transactions.filter(t => t.type === 'expense').reduce((s, t) => s + pn(t.amount), 0);
            const obl = state.obligations.reduce((s, o) => s + pn(o.monthly_payment), 0);

            setText('#summary-income', fmt.cur(inc));
            setText('#summary-expense', fmt.cur(exp));
            setText('#summary-obligations', fmt.cur(obl));

            if ($('#income')) $('#income').value = inc || '';
            if ($('#expense')) $('#expense').value = exp || '';

            // Load recommendation
            try {
                const res = await api('/api/recommendation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                });
                renderDashboardCards(res);
            } catch(e) { console.error('Recommendation error:', e); }
        }

        // Render lists
        if (tList)  renderTransactions();
        if (oList)  renderObligations();
        if (gList)  renderGoals();

    } catch (e) {
        console.error('loadPage error:', e);
    }
}

// ── Renderers ────────────────────────────────────────────────
function setText(sel, text) {
    const el = $(sel);
    if (el) el.textContent = text;
}

function renderTransactions() {
    const list = $('#transactions-list');
    if (!list) return;

    const visible = state.transactions.slice(0, state.limit);
    
    if (visible.length === 0) {
        list.innerHTML = `<div class="empty-row">Нет записей — добавьте операцию или синхронизируйте банк</div>`;
        return;
    }

    list.innerHTML = visible.map(t => {
        const isIncome = t.type === 'income';
        const color = isIncome ? 'var(--c-green)' : 'var(--c-red)';
        const sign = isIncome ? '+' : '−';
        const typePill = isIncome
            ? '<span class="action-pill success-pill" style="pointer-events:none;font-size:.72rem;padding:4px 10px;">Доход</span>'
            : '<span class="action-pill danger-pill" style="pointer-events:none;font-size:.72rem;padding:4px 10px;">Расход</span>';
        const source = t.is_synced
            ? '<span style="color:var(--c-cyan);font-size:.78rem;font-weight:600;">● Банк</span>'
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

function renderObligations() {
    const list = $('#obligations-list');
    if (!list) return;

    if (state.obligations.length === 0) {
        list.innerHTML = `<article class="stack-item empty-stack-item"><div class="stack-item-title" style="color:var(--c-text3)">Обязательств пока нет</div></article>`;
        return;
    }

    list.innerHTML = state.obligations.map(o => `
        <article class="stack-item">
            <div>
                <div class="stack-item-title">${esc(o.name)}</div>
                <div class="stack-item-text">
                    ${fmt.cur(o.monthly_payment)} / мес · Ставка ${o.interest_rate}% · Срок ${o.term} мес
                    ${o.comment ? ' · ' + esc(o.comment) : ''}
                </div>
            </div>
            <button class="ghost-button delete-button" data-obligation-id="${o.id}" style="color:var(--c-red);font-size:.85rem;padding:6px 10px;" title="Удалить">✕</button>
        </article>
    `).join('');
}

function renderGoals() {
    const list = $('#goals-list');
    if (!list) return;

    if (state.goals.length === 0) {
        list.innerHTML = `<article class="stack-item empty-stack-item"><div class="stack-item-title" style="color:var(--c-text3)">Целей пока нет</div></article>`;
        return;
    }

    list.innerHTML = state.goals.map(g => {
        const pct = g.target_amount > 0 ? Math.min(100, (g.current_amount / g.target_amount * 100)) : 0;
        return `
        <article class="stack-item" style="flex-direction:column; align-items:stretch; gap:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class="stack-item-title">${esc(g.name)}</div>
                    <div class="stack-item-text">${fmt.cur(g.current_amount)} из ${fmt.cur(g.target_amount)} · до ${fmt.date(g.deadline)}</div>
                </div>
                <button class="ghost-button delete-button" data-goal-id="${g.id}" style="color:var(--c-red);font-size:.85rem;padding:6px 10px;" title="Удалить">✕</button>
            </div>
            <div class="indicator-track" style="height:5px;">
                <div class="indicator-track-fill resource-fill" style="width:${pct}%"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:.78rem; color:var(--c-text3);">
                <span>${pct.toFixed(0)}% выполнено</span>
                <span>Осталось ${fmt.cur(Math.max(0, g.target_amount - g.current_amount))}</span>
            </div>
        </article>`;
    }).join('');
}

function renderDashboardCards(res) {
    if (!res || !res.indicators) return;

    const { Rt, Lt, Dt } = res.indicators;

    // Metric values
    setText('#rt-value', fmt.num(Rt));
    setText('#lt-value', fmt.num(Lt));
    setText('#dt-value', fmt.pct(Dt));

    // Color metrics dynamically
    const rtEl = $('#rt-value');
    const ltEl = $('#lt-value');
    const dtEl = $('#dt-value');
    if (rtEl) rtEl.style.color = Rt >= 0 ? 'var(--c-green)' : 'var(--c-red)';
    if (ltEl) ltEl.style.color = Lt >= 1.5 ? 'var(--c-green)' : Lt >= 1 ? 'var(--c-amber)' : 'var(--c-red)';
    if (dtEl) dtEl.style.color = Dt <= 0.2 ? 'var(--c-green)' : Dt <= 0.4 ? 'var(--c-amber)' : 'var(--c-red)';

    // Status badge
    const statusEl = $('#rec-status');
    if (statusEl) {
        if (Dt > 0.4 || Lt < 1 || Rt < 0) {
            statusEl.textContent = '● Внимание';
            statusEl.className = 'rec-status status-danger';
        } else if (Dt > 0.2 || Lt < 1.5) {
            statusEl.textContent = '● Пограничный';
            statusEl.className = 'rec-status status-warn';
        } else {
            statusEl.textContent = '● Стабильно';
            statusEl.className = 'rec-status status-ok';
        }
    }

    // Render recommendation — compact version
    const recText = $('#recommendation-text');
    if (recText && res.recommendation) {
        recText.innerHTML = `<div style="font-size:.84rem; line-height:1.6; color:var(--c-text);">${esc(res.recommendation)}</div>`;
    }

    // Render breakdown — mini table + formula
    const explEl = $('#explanation-text');
    if (explEl) {
        const summary = res.input_summary || {};
        let html = `<div class="rec-formula" style="margin-top:0;">
            <div style="display:grid; grid-template-columns:auto 1fr; gap:2px 12px; font-size:.78rem;">
                <span style="opacity:.6;">Rt</span><span>= ${fmt.num(Rt)} ₽</span>
                <span style="opacity:.6;">Lt</span><span>= ${Lt.toFixed(2)}</span>
                <span style="opacity:.6;">Dt</span><span>= ${fmt.pct(Dt)}</span>
            </div>
        </div>`;

        if (summary.transactions_count) {
            html += `<div style="margin-top:8px; font-size:.72rem; color:var(--c-text3);">
                ${summary.transactions_count} операций · ${summary.obligations_count || 0} обяз. · ${summary.active_goals_count || 0} целей
            </div>`;
        }
        explEl.innerHTML = html;
    }

    // Progress bars
    const maxR = 500000;
    setBar('#resource-scale-bar', '#resource-scale-text', clamp(Math.abs(Rt) / maxR * 100), fmt.cur(Rt));
    setBar('#liquidity-scale-bar', '#liquidity-scale-text', clamp((Lt / 3) * 100), Lt.toFixed(2));
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
const RISK_LABELS = {1:'Консервативный',2:'Умеренно-консервативный',3:'Сбалансированный',4:'Умеренно-агрессивный',5:'Агрессивный'};

function bindPlanningUI() {
    const form = $('#planning-form');
    if (!form) return;

    // L_min slider
    const lminSlider = $('#lmin-slider');
    const lminVal    = $('#lmin-value');
    if (lminSlider) {
        lminSlider.addEventListener('input', () => {
            planLmin = parseFloat(lminSlider.value);
            if (lminVal) lminVal.textContent = planLmin.toFixed(2);
        });
    }

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
                body: JSON.stringify({ risk_tolerance: planRisk, l_min: planLmin }),
            });
            renderPlanning(res);
        } catch(e) { console.error(e); }
        finally { btn.disabled = false; btn.textContent = 'Рассчитать альтернативы'; }
    });

    // Horizon selector → reload forecast
    const horizonSel = $('#forecast-horizon');
    if (horizonSel) {
        horizonSel.addEventListener('change', () => loadForecast(Number(horizonSel.value)));
    }

    // Auto-load
    form.dispatchEvent(new Event('submit'));
    loadForecast(6);
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

function renderForecast(data) {
    const container = $('#forecast-container');
    const body = $('#forecast-body');
    if (!container || !body || !data) return;

    container.style.display = '';

    const TREND_LABEL = { stable: 'Стабильный', improving: 'Улучшение', deteriorating: 'Ухудшение' };
    const TREND_COLOR = { stable: 'var(--c-text3)', improving: 'var(--c-green)', deteriorating: 'var(--c-red)' };
    const trend = data.trend || 'stable';

    const rows = (data.forecast || []).map(p => `
        <tr>
            <td style="padding:6px 10px; color:var(--c-text3);">+${p.period} мес.</td>
            <td style="padding:6px 10px; text-align:right; font-weight:600; color:${p.Rt >= 0 ? 'var(--c-green)' : 'var(--c-red)'};">${fmt.cur(p.Rt)}</td>
            <td style="padding:6px 10px; text-align:right; color:${p.Lt >= 0.3 ? 'var(--c-green)' : p.Lt >= 0.1 ? 'var(--c-amber)' : 'var(--c-red)'};">${p.Lt.toFixed(3)}</td>
            <td style="padding:6px 10px; text-align:right; color:${p.Dt <= 0.2 ? 'var(--c-green)' : p.Dt <= 0.4 ? 'var(--c-amber)' : 'var(--c-red)'};">${(p.Dt * 100).toFixed(1)}%</td>
            <td style="padding:6px 10px; text-align:right; color:var(--c-text3);">${fmt.cur(p.cash_flow)}</td>
        </tr>`).join('');

    body.innerHTML = `
        <div style="margin-bottom:10px; font-size:.78rem; color:var(--c-text3);">
            Тренд Rt: <strong style="color:${TREND_COLOR[trend]};">${TREND_LABEL[trend]}</strong>
            &nbsp;·&nbsp; Baseline-прогноз (постоянные доходы/расходы, форм. 35 ВКР)
        </div>
        <table style="width:100%; border-collapse:collapse; font-size:.82rem;">
            <thead>
                <tr style="border-bottom:1px solid var(--c-border); color:var(--c-text3); font-size:.72rem; text-transform:uppercase;">
                    <th style="padding:6px 10px; text-align:left; font-weight:600;">Период</th>
                    <th style="padding:6px 10px; text-align:right; font-weight:600;">Rt</th>
                    <th style="padding:6px 10px; text-align:right; font-weight:600;">Lt</th>
                    <th style="padding:6px 10px; text-align:right; font-weight:600;">Dt</th>
                    <th style="padding:6px 10px; text-align:right; font-weight:600;">CFt</th>
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
function renderTop3Card(a, rank, indicators) {
    const e = a.explanation || {};
    const d = e.delta || {};
    const gains = (e.gains || []);
    const costs = (e.costs || []);
    const { Rt, Lt, Dt } = indicators;

    const rankColors = ['var(--c-green)', 'var(--c-accent-hl)', 'var(--c-text2)'];
    const rankLabels = ['Оптимальная', 'Альтернатива #2', 'Альтернатива #3'];
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
    <article class="glass-panel" style="border:1px solid ${bc}; padding:20px 22px; margin-bottom:16px;">
        <!-- Заголовок -->
        <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="min-width:28px; height:28px; background:${rc}22; border-radius:var(--r-sm);
                            display:grid; place-items:center; font-size:.85rem; font-weight:800; color:${rc};">
                    ${rank + 1}
                </div>
                <div>
                    <div style="font-weight:700; font-size:.95rem;">${esc(a.name)}</div>
                    <div style="font-size:.72rem; color:${rc}; margin-top:2px;">${rankLabels[rank]} · U(a) = <strong>${a.utility}</strong></div>
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

        <!-- Показатели до / после -->
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-top:14px;
                    padding-top:12px; border-top:1px solid var(--c-border); font-size:.78rem;">
            <div style="background:rgba(255,255,255,.03); border-radius:var(--r-sm); padding:8px 10px;">
                <div style="color:var(--c-text3); margin-bottom:2px;">Rt</div>
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
    </article>`;
}

// ── Компактная строка для полного списка ──────────────────────
function renderAltRow(a, idx) {
    return `
    <div style="display:grid; grid-template-columns:28px 1fr auto auto auto auto; align-items:center;
                gap:10px; padding:8px 12px; border-bottom:1px solid var(--c-border); font-size:.8rem;">
        <span style="color:var(--c-text3); font-size:.72rem; text-align:center;">${idx+1}</span>
        <span>${esc(a.name)}</span>
        <span style="color:var(--c-red);   text-align:right;">${a.x_obligations > 0 ? fmt.cur(a.x_obligations) : '—'}</span>
        <span style="color:var(--c-amber); text-align:right;">${a.x_reserve    > 0 ? fmt.cur(a.x_reserve)    : '—'}</span>
        <span style="color:var(--c-green); text-align:right;">${a.x_goals      > 0 ? fmt.cur(a.x_goals)      : '—'}</span>
        <span style="color:var(--c-accent-hl); font-weight:700; text-align:right;">${a.utility}</span>
    </div>`;
}

function renderPlanning(res) {
    if (!res) return;
    const { Rt, Lt, Dt } = res.indicators || {};

    // Показатели
    const rtEl = $('#plan-rt');
    const ltEl = $('#plan-lt');
    const dtEl = $('#plan-dt');
    if (rtEl) { rtEl.textContent = fmt.cur(Rt); rtEl.style.color = Rt >= 0 ? 'var(--c-green)' : 'var(--c-red)'; }
    if (ltEl) { ltEl.textContent = Lt.toFixed(3); ltEl.style.color = Lt >= 0.5 ? 'var(--c-green)' : Lt >= 0.2 ? 'var(--c-amber)' : 'var(--c-red)'; }
    if (dtEl) { dtEl.textContent = fmt.pct(Dt); dtEl.style.color = Dt <= 0.2 ? 'var(--c-green)' : Dt <= 0.4 ? 'var(--c-amber)' : 'var(--c-red)'; }

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
                    <span style="opacity:.6;">w₁ (Rt)</span><span>Финансовая гибкость</span><strong>${w.w_rt}</strong>
                    <span style="opacity:.6;">w₂ (Lt)</span><span>Устойчивость</span><strong>${w.w_lt}</strong>
                    <span style="opacity:.6;">w₃ (Dt)</span><span>Риск</span><strong>${w.w_dt}</strong>
                    <span style="opacity:.6;">w₄ (Goals)</span><span>Достижение целей</span><strong>${w.w_goals}</strong>
                </div>
            </div>`;
    }

    // Входные данные
    const inp = $('#input-display');
    if (inp && res.input_summary) {
        const s = res.input_summary;
        inp.innerHTML = `
            <div style="display:grid; grid-template-columns:1fr auto; gap:4px 12px; font-size:.8rem;">
                <span style="color:var(--c-text3);">Доходы</span><strong style="color:var(--c-green);">${fmt.cur(s.income)}</strong>
                <span style="color:var(--c-text3);">Расходы</span><strong style="color:var(--c-red);">${fmt.cur(s.expense)}</strong>
                <span style="color:var(--c-text3);">Обязательства</span><strong>${fmt.cur(s.obligations)}</strong>
                <span style="color:var(--c-text3);">Цели (остаток)</span><strong>${fmt.cur(s.goals_total)}</strong>
            </div>
            <div style="margin-top:10px; font-size:.72rem; color:var(--c-text3);">
                ${s.transactions_count} операций · ${s.obligations_count} обяз. · ${s.goals_count} целей
            </div>`;
    }

    // Блок топ-3 (заменяет optimal-container)
    const optC = $('#optimal-container');
    if (optC) {
        if (res.top3 && res.top3.length) {
            optC.innerHTML = `
                <div style="font-size:.78rem; color:var(--c-text3); margin-bottom:12px;">
                    Сгенерировано <strong>${res.alternatives_total}</strong> альтернатив ·
                    Допустимых: <strong>${res.admissible_count}</strong> ·
                    Отклонено: <strong>${res.rejected_count}</strong>
                </div>
                ${res.top3.map((a, i) => renderTop3Card(a, i, res.indicators)).join('')}`;
        } else {
            optC.innerHTML = `
                <div class="glass-panel" style="border:1px solid rgba(244,63,94,.2); padding:20px 24px; text-align:center;">
                    <div style="font-weight:700; color:var(--c-red); margin-bottom:6px;">Все альтернативы отклонены</div>
                    <div style="font-size:.84rem; color:var(--c-text3);">
                        A_доп = ∅. Попробуйте снизить L<sub>min</sub> или пересмотреть бюджет.
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
                    Все ${res.ranked.length} допустимых альтернатив (развернуть)
                </summary>
                <div style="margin-top:10px; border:1px solid var(--c-border); border-radius:var(--r-sm); overflow:hidden;">
                    <div style="display:grid; grid-template-columns:28px 1fr auto auto auto auto; gap:10px;
                                padding:6px 12px; font-size:.68rem; text-transform:uppercase; letter-spacing:.4px;
                                color:var(--c-text3); border-bottom:1px solid var(--c-border); font-weight:600;">
                        <span>#</span><span>Название</span>
                        <span style="color:var(--c-red);">Долг</span>
                        <span style="color:var(--c-amber);">Резерв</span>
                        <span style="color:var(--c-green);">Цели</span>
                        <span>U(a)</span>
                    </div>
                    ${res.ranked.map((a, i) => renderAltRow(a, i)).join('')}
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
                    Отклонено по ограничениям: ${res.rejected.length}
                </summary>
                <div style="margin-top:8px; border:1px solid var(--c-border); border-radius:var(--r-sm); overflow:hidden;">
                    ${res.rejected.map((a, i) => `
                    <div style="display:flex; justify-content:space-between; align-items:center;
                                padding:7px 12px; border-bottom:1px solid var(--c-border); font-size:.8rem; opacity:.6;">
                        <span>${esc(a.name)}</span>
                        <span style="font-size:.72rem; color:var(--c-red);">
                            ${(a.violations || []).join(' · ')}
                        </span>
                    </div>`).join('')}
                </div>
            </details>`;
    } else if (rejC) {
        rejC.innerHTML = '';
    }
}


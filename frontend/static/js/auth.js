// FINPILOT auth (v3.0.0) — вход/регистрация, JWT через Bearer на каждый запрос.
// Изоляция: токен хранится в localStorage; перехватываем fetch и подставляем
// Authorization: Bearer. Cookie тоже ставится сервером (httpOnly), но Bearer
// делает многопользовательский режим явным и независимым от cookie.
(function () {
    'use strict';

    const TOKEN_KEY = 'finpilot-token';
    const getToken = () => { try { return localStorage.getItem(TOKEN_KEY); } catch { return null; } };
    const setToken = (t) => { try { localStorage.setItem(TOKEN_KEY, t); } catch {} };
    const clearToken = () => { try { localStorage.removeItem(TOKEN_KEY); } catch {} };

    // ── Перехват fetch: добавляем Bearer ко всем /api и /v1 запросам ──
    const originalFetch = window.fetch.bind(window);
    window.fetch = function (input, init = {}) {
        const url = typeof input === 'string' ? input : (input && input.url) || '';
        const token = getToken();
        if (token && (url.startsWith('/api') || url.startsWith('/v1'))) {
            init = { ...init };
            const headers = new Headers(init.headers || (typeof input !== 'string' && input.headers) || {});
            if (!headers.has('Authorization')) headers.set('Authorization', 'Bearer ' + token);
            init.headers = headers;
        }
        return originalFetch(input, init);
    };

    // ── DOM ──
    const modal = document.getElementById('auth-modal');
    const statusEl = document.getElementById('auth-status');
    const loginBtn = document.getElementById('auth-login-btn');
    const logoutBtn = document.getElementById('auth-logout-btn');
    const errorEl = document.getElementById('auth-error');
    const emailEl = document.getElementById('auth-email');
    const passwordEl = document.getElementById('auth-password');
    const nameRow = document.getElementById('auth-name-row');
    const nameEl = document.getElementById('auth-name');
    const consentRow = document.getElementById('auth-consent-row');
    const consentEl = document.getElementById('auth-consent');
    const newsletterEl = document.getElementById('auth-newsletter');
    const submitBtn = document.getElementById('auth-submit');
    const tabs = document.querySelectorAll('[data-auth-tab]');

    if (!modal) return; // base.html без auth-разметки — выходим

    let mode = 'login';

    const openModal = () => { modal.setAttribute('aria-hidden', 'false'); errorEl.style.display = 'none'; };
    const closeModal = () => { modal.setAttribute('aria-hidden', 'true'); };
    const showError = (msg) => { errorEl.textContent = msg; errorEl.style.display = 'block'; };
    function setMode(next) {
        mode = next;
        tabs.forEach((t) => t.classList.toggle('active', t.dataset.authTab === next));
        nameRow.style.display = next === 'register' ? 'block' : 'none';
        if (consentRow) consentRow.style.display = next === 'register' ? 'block' : 'none';
        submitBtn.textContent = next === 'register' ? 'Зарегистрироваться' : 'Войти';
        document.getElementById('auth-modal-title').textContent =
            next === 'register' ? 'Регистрация в FINPILOT' : 'Вход в FINPILOT';
        // В режиме регистрации просим браузер предложить сгенерированный пароль.
        if (passwordEl) {
            passwordEl.setAttribute('autocomplete', next === 'register' ? 'new-password' : 'current-password');
        }
        errorEl.style.display = 'none';
    }

    async function fetchMe() {
        const token = getToken();
        if (!token) { renderLoggedOut(); return; }
        try {
            const r = await originalFetch('/api/auth/me', { headers: { Authorization: 'Bearer ' + token } });
            if (r.ok) { renderLoggedIn(await r.json()); }
            else { clearToken(); renderLoggedOut(); }
        } catch { renderLoggedOut(); }
    }

    function renderLoggedIn(user) {
        statusEl.textContent = user.display_name || user.email;
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
    }

    function renderLoggedOut() {
        statusEl.textContent = 'Гость';
        loginBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
    }

    async function submit() {
        const email = (emailEl.value || '').trim();
        const password = passwordEl.value || '';
        if (!email || !password) { showError('Заполните email и пароль.'); return; }

        const endpoint = mode === 'register' ? '/api/auth/register' : '/api/auth/login';
        const payload = { email, password };
        if (mode === 'register') {
            if (consentEl && !consentEl.checked) {
                showError('Подтвердите согласие на обработку персональных данных.');
                return;
            }
            if (nameEl.value.trim()) payload.display_name = nameEl.value.trim();
            payload.consent = consentEl ? consentEl.checked : true;
            payload.newsletter_opt_in = newsletterEl ? newsletterEl.checked : false;
        }

        submitBtn.disabled = true;
        try {
            const r = await originalFetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await r.json().catch(() => ({}));
            if (!r.ok) { showError(data.detail || 'Ошибка. Проверьте данные.'); return; }
            setToken(data.access_token);
            renderLoggedIn(data.user);
            closeModal();
            // SMTP не настроен: показываем ссылку подтверждения email кнопкой в тосте
            if (mode === 'register' && data.verification_url && window.showToast) {
                window.showToast('Аккаунт создан. Подтвердите email по ссылке:', {
                    linkUrl: data.verification_url, linkLabel: 'Подтвердить email',
                });
                return; // не перезагружаем — иначе тост исчезнет; шапка уже обновлена
            }
            // Перезагрузка — данные на странице принадлежат новому пользователю
            window.location.reload();
        } catch {
            showError('Сеть недоступна. Повторите позже.');
        } finally {
            submitBtn.disabled = false;
        }
    }

    async function logout() {
        try { await originalFetch('/api/auth/logout', { method: 'POST' }); } catch {}
        clearToken();
        renderLoggedOut();
        window.location.reload();
    }

    // ── События ──
    loginBtn && loginBtn.addEventListener('click', () => { setMode('login'); openModal(); });
    logoutBtn && logoutBtn.addEventListener('click', logout);
    const authForm = document.getElementById('auth-form');
    authForm && authForm.addEventListener('submit', (e) => { e.preventDefault(); submit(); });
    tabs.forEach((t) => t.addEventListener('click', () => setMode(t.dataset.authTab)));
    document.querySelectorAll('[data-close-modal="auth-modal"]').forEach((el) =>
        el.addEventListener('click', closeModal)
    );
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.getAttribute('aria-hidden') === 'false') closeModal();
    });
    [emailEl, passwordEl, nameEl].forEach((el) => el && el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') submit();
    }));

    fetchMe();
})();

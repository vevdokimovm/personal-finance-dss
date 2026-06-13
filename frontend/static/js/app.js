const form = document.getElementById("analysis-form");
const status = document.getElementById("status");
const submitButton = document.getElementById("submit-button");
const restoreSummaryButton = document.getElementById("restore-summary-button");
const loadDemoButton = document.getElementById("load-demo-button");
const clearDemoButton = document.getElementById("clear-demo-button");
const incomeInput = document.getElementById("income");
const expenseInput = document.getElementById("expense");

const rtValue = document.getElementById("rt-value");
const ltValue = document.getElementById("lt-value");
const dtValue = document.getElementById("dt-value");
const recommendationText = document.getElementById("recommendation-text");
const explanationText = document.getElementById("explanation-text");

const summaryIncome = document.getElementById("summary-income");
const summaryExpense = document.getElementById("summary-expense");
const summaryObligations = document.getElementById("summary-obligations");

const transactionsList = document.getElementById("transactions-list");
const transactionsLimitSwitcher = document.getElementById("transactions-limit-switcher");
const obligationsList = document.getElementById("obligations-list");
const goalsList = document.getElementById("goals-list");

const openIncomeModalButton = document.getElementById("open-income-modal");
const openExpenseModalButton = document.getElementById("open-expense-modal");
const openObligationModalButton = document.getElementById("open-obligation-modal");
const openGoalModalButton = document.getElementById("open-goal-modal");

const transactionModal = document.getElementById("transaction-modal");
const obligationModal = document.getElementById("obligation-modal");
const goalModal = document.getElementById("goal-modal");

const transactionForm = document.getElementById("transaction-form");
const obligationForm = document.getElementById("obligation-form");
const goalForm = document.getElementById("goal-form");

const transactionModalTitle = document.getElementById("transaction-modal-title");
const transactionTypeInput = document.getElementById("transaction-type");
const transactionCategoryInput = document.getElementById("transaction-category");
const transactionAmountInput = document.getElementById("transaction-amount");
const transactionDateInput = document.getElementById("transaction-date");

const obligationNameInput = document.getElementById("obligation-name");
const obligationAmountInput = document.getElementById("obligation-amount");
const obligationMonthlyPaymentInput = document.getElementById("obligation-monthly-payment");
const obligationPaymentDayInput = document.getElementById("obligation-payment-day");
const obligationInterestRateInput = document.getElementById("obligation-interest-rate");
const obligationTermInput = document.getElementById("obligation-term");
const obligationCommentInput = document.getElementById("obligation-comment");

const goalNameInput = document.getElementById("goal-name");
const goalTargetAmountInput = document.getElementById("goal-target-amount");
const goalCurrentAmountInput = document.getElementById("goal-current-amount");
const goalDeadlineInput = document.getElementById("goal-deadline");
const goalCommentInput = document.getElementById("goal-comment");

const appState = {
    transactions: [],
    obligations: [],
    goals: [],
    transactionsVisibleLimit: 10,
};

function formatNumber(value) {
    return new Intl.NumberFormat("ru-RU", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
    }).format(value);
}

function formatCurrency(value) {
    return `${formatNumber(value)} ₽`;
}

function formatPercent(value) {
    return `${(value * 100).toFixed(1)}%`;
}

function clampPercent(value) {
    return Math.max(0, Math.min(100, value));
}

function updateIndicatorsVisual(indicators) {
    const resourceScaleBar = document.getElementById("resource-scale-bar");
    const liquidityScaleBar = document.getElementById("liquidity-scale-bar");
    const debtScaleBar = document.getElementById("debt-scale-bar");
    const resourceScaleText = document.getElementById("resource-scale-text");
    const liquidityScaleText = document.getElementById("liquidity-scale-text");
    const debtScaleText = document.getElementById("debt-scale-text");

    const rt = parseNumber(indicators.Rt);
    const lt = parseNumber(indicators.Lt);
    const dt = parseNumber(indicators.Dt);

    const resourcePercent = clampPercent(Math.abs(rt) / 500000 * 100);
    const liquidityPercent = clampPercent((lt / 3) * 100);
    const debtPercent = clampPercent(dt * 100);

    if (resourceScaleBar) {
        resourceScaleBar.style.width = `${resourcePercent}%`;
    }

    if (liquidityScaleBar) {
        liquidityScaleBar.style.width = `${liquidityPercent}%`;
    }

    if (debtScaleBar) {
        debtScaleBar.style.width = `${debtPercent}%`;
    }

    if (resourceScaleText) {
        resourceScaleText.textContent = formatNumber(rt);
    }

    if (liquidityScaleText) {
        liquidityScaleText.textContent = `${lt.toFixed(2)} / 3.00`;
    }

    if (debtScaleText) {
        debtScaleText.textContent = formatPercent(dt);
    }
}

function formatDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    return new Intl.DateTimeFormat("ru-RU").format(date);
}

function parseNumber(value) {
    const num = Number(value);
    return Number.isNaN(num) ? 0 : num;
}

function getTodayDate() {
    return new Date().toISOString().slice(0, 10);
}

function setIdleState() {
    status.classList.remove("loading");
    status.textContent = "Система готова к работе с показателями.";
    restoreSummaryButton.disabled = false;
}

function setLoadingState(message = "Загрузка...") {
    status.classList.add("loading");
    status.textContent = message;
    submitButton.disabled = true;
    restoreSummaryButton.disabled = true;
    loadDemoButton.disabled = true;
    clearDemoButton.disabled = true;
    openIncomeModalButton.disabled = true;
    openExpenseModalButton.disabled = true;
    openObligationModalButton.disabled = true;
    openGoalModalButton.disabled = true;
}

function unlockControls() {
    submitButton.disabled = false;
    restoreSummaryButton.disabled = false;
    loadDemoButton.disabled = false;
    clearDemoButton.disabled = false;
    openIncomeModalButton.disabled = false;
    openExpenseModalButton.disabled = false;
    openObligationModalButton.disabled = false;
    openGoalModalButton.disabled = false;
}

function applyRiskClass(element, value, type) {
    element.classList.remove("good", "warning", "bad");

    if (type === "Dt") {
        if (value > 0.4) {
            element.classList.add("bad");
        } else if (value > 0.2) {
            element.classList.add("warning");
        } else {
            element.classList.add("good");
        }
        return;
    }

    if (type === "Lt") {
        if (value < 1) {
            element.classList.add("bad");
        } else if (value < 1.5) {
            element.classList.add("warning");
        } else {
            element.classList.add("good");
        }
        return;
    }

    if (type === "Rt") {
        if (value < 0) {
            element.classList.add("bad");
        } else {
            element.classList.add("good");
        }
    }
}

function openModal(modal) {
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
}

function closeModal(modal) {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
}

function resetTransactionForm(type) {
    transactionForm.reset();
    transactionTypeInput.value = type;
    transactionDateInput.value = getTodayDate();
    transactionModalTitle.textContent =
        type === "income" ? "Новый доход" : "Новый расход";
}

function resetObligationForm() {
    obligationForm.reset();
    obligationPaymentDayInput.value = "1";
    obligationInterestRateInput.value = "0";
    obligationTermInput.value = "0";
}

function resetGoalForm() {
    goalForm.reset();
    goalCurrentAmountInput.value = "0";
    goalDeadlineInput.value = getTodayDate();
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : {};

    if (!response.ok) {
        throw new Error(data.detail || "Ошибка сервера.");
    }

    return data;
}

function updateSummary(transactions, obligations) {
    const incomeTotal = transactions
        .filter((item) => item.type === "income")
        .reduce((sum, item) => sum + parseNumber(item.amount), 0);

    const expenseTotal = transactions
        .filter((item) => item.type === "expense")
        .reduce((sum, item) => sum + parseNumber(item.amount), 0);

    const obligationsTotal = obligations.reduce(
        (sum, item) => sum + parseNumber(item.monthly_payment),
        0,
    );

    summaryIncome.textContent = formatCurrency(incomeTotal);
    summaryExpense.textContent = formatCurrency(expenseTotal);
    summaryObligations.textContent = formatCurrency(obligationsTotal);
}

function renderTransactions(transactions) {
    if (!transactions.length) {
        transactionsList.innerHTML = `
            <div class="table-row empty-row">
                <span>Нет записей</span>
                <span>Добавьте доход или расход</span>
                <span>—</span>
                <span>0</span>
            </div>
        `;
        return;
    }

    const visibleTransactions = transactions.slice(0, appState.transactionsVisibleLimit);

    transactionsList.innerHTML = visibleTransactions
        .map((transaction) => {
            const isIncome = transaction.type === "income";
            const typeLabel = transaction.type === "income" ? "Доход" : "Расход";
            const typeClass = isIncome ? "transaction-type income-type" : "transaction-type expense-type";
            const amountClass = isIncome ? "transaction-amount income-amount" : "transaction-amount expense-amount";
            const amountPrefix = isIncome ? "+" : "-";
            return `
                <div class="table-row">
                    <span>${formatDate(transaction.date)}</span>
                    <span>${transaction.category}</span>
                    <span><span class="${typeClass}">${typeLabel}</span></span>
                    <span>
                        <span class="${amountClass}">${amountPrefix}${formatCurrency(parseNumber(transaction.amount))}</span>
                        <button class="delete-button" type="button" data-transaction-id="${transaction.id}">Удалить</button>
                    </span>
                </div>
            `;
        })
        .join("");
}

function updateTransactionsLimitButtons() {
    if (!transactionsLimitSwitcher) {
        return;
    }

    const buttons = transactionsLimitSwitcher.querySelectorAll("[data-limit]");
    buttons.forEach((button) => {
        const limit = Number(button.getAttribute("data-limit"));
        button.classList.toggle("active", limit === appState.transactionsVisibleLimit);
    });
}

function renderObligations(obligations) {
    if (!obligations.length) {
        obligationsList.innerHTML = `
            <article class="stack-item empty-stack-item">
                <div class="stack-item-title">Список обязательств пока пуст</div>
                <div class="stack-item-text">Добавьте обязательство, чтобы учитывать его в расчёте показателей.</div>
            </article>
        `;
        return;
    }

    obligationsList.innerHTML = obligations
        .map((obligation) => `
            <article class="stack-item">
                <div class="stack-item-title">${obligation.name}</div>
                <div class="stack-item-text">Ежемесячный платёж: ${formatCurrency(parseNumber(obligation.monthly_payment))}</div>
                <div class="stack-item-text">День платежа: ${obligation.payment_day}</div>
                <div class="stack-item-text">${obligation.comment || "Комментарий отсутствует."}</div>
                <button class="delete-button" type="button" data-obligation-id="${obligation.id}">Удалить</button>
            </article>
        `)
        .join("");
}

function renderGoals(goals) {
    if (!goals.length) {
        goalsList.innerHTML = `
            <article class="stack-item empty-stack-item">
                <div class="stack-item-title">Активных целей пока нет</div>
                <div class="stack-item-text">Добавьте цель, чтобы видеть её в dashboard и учитывать в рекомендациях.</div>
            </article>
        `;
        return;
    }

    goalsList.innerHTML = goals
        .map((goal) => `
            <article class="stack-item">
                <div class="stack-item-title">${goal.name}</div>
                <div class="stack-item-text">Целевая сумма: ${formatCurrency(parseNumber(goal.target_amount))}</div>
                <div class="stack-item-text">Уже накоплено: ${formatCurrency(parseNumber(goal.current_amount))}</div>
                <div class="stack-item-text">Срок: ${formatDate(goal.deadline)}</div>
                <div class="stack-item-text">${goal.comment || "Комментарий отсутствует."}</div>
                <button class="delete-button" type="button" data-goal-id="${goal.id}">Удалить</button>
            </article>
        `)
        .join("");
}

function renderIndicators(indicators, recommendation, explanation) {
    const rt = parseNumber(indicators.Rt);
    const lt = parseNumber(indicators.Lt);
    const dt = parseNumber(indicators.Dt);

    rtValue.textContent = formatNumber(rt);
    ltValue.textContent = formatNumber(lt);
    dtValue.textContent = formatPercent(dt);
    recommendationText.textContent = recommendation || "Рекомендация недоступна.";
    explanationText.textContent = explanation || "Пояснение к рекомендации недоступно.";

    applyRiskClass(rtValue, rt, "Rt");
    applyRiskClass(ltValue, lt, "Lt");
    applyRiskClass(dtValue, dt, "Dt");
    updateIndicatorsVisual(indicators);
}

async function loadTransactions() {
    return requestJson("/api/transactions");
}

async function loadObligations() {
    return requestJson("/api/obligations");
}

async function loadGoals() {
    return requestJson("/api/goals");
}

async function loadRecommendation(payload = null) {
    return requestJson("/api/recommendation", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(
            payload || {
                transactions: [],
                obligations: [],
                goals: [],
            },
        ),
    });
}

async function refreshDashboard() {
    const [transactions, obligations, goals, analysis] = await Promise.all([
        loadTransactions(),
        loadObligations(),
        loadGoals(),
        loadRecommendation(),
    ]);

    appState.transactions = transactions;
    appState.obligations = obligations;
    appState.goals = goals;

    updateTransactionsLimitButtons();
    renderTransactions(transactions);
    renderObligations(obligations);
    renderGoals(goals);
    updateSummary(transactions, obligations);
    renderIndicators(analysis.indicators, analysis.recommendation, analysis.explanation);

    return { transactions, obligations, goals };
}

async function calculateFromCurrentForm() {
    const income = parseNumber(incomeInput.value);
    const expense = parseNumber(expenseInput.value);

    const formTransactions = [];
    if (income > 0) {
        formTransactions.push({
            amount: income,
            category: "Доход",
            type: "income",
            date: new Date().toISOString(),
        });
    }
    if (expense > 0) {
        formTransactions.push({
            amount: expense,
            category: "Расход",
            type: "expense",
            date: new Date().toISOString(),
        });
    }

    const analysis = await loadRecommendation({
        transactions: formTransactions,
        obligations: appState.obligations,
        goals: appState.goals,
    });

    updateSummary(formTransactions, appState.obligations);
    renderIndicators(analysis.indicators, analysis.recommendation, analysis.explanation);
}

async function createTransaction(payload) {
    await requestJson("/api/transactions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });
}

async function createObligation(payload) {
    await requestJson("/api/obligations", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });
}

async function createGoal(payload) {
    await requestJson("/api/goals", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });
}

async function deleteTransactionById(transactionId) {
    await requestJson(`/api/transactions/${transactionId}`, { method: "DELETE" });
}

async function deleteObligationById(obligationId) {
    await requestJson(`/api/obligations/${obligationId}`, { method: "DELETE" });
}

async function deleteGoalById(goalId) {
    await requestJson(`/api/goals/${goalId}`, { method: "DELETE" });
}

function fillFormFromTransactions(transactions) {
    const incomeTotal = transactions
        .filter((item) => item.type === "income")
        .reduce((sum, item) => sum + parseNumber(item.amount), 0);

    const expenseTotal = transactions
        .filter((item) => item.type === "expense")
        .reduce((sum, item) => sum + parseNumber(item.amount), 0);

    incomeInput.value = incomeTotal ? String(incomeTotal) : "";
    expenseInput.value = expenseTotal ? String(expenseTotal) : "";
}

async function restoreSummaryFromJournal() {
    setLoadingState("Возврат значений из журнала...");

    try {
        const transactions = await requestJson("/api/transactions");
        fillFormFromTransactions(transactions);
        await calculateFromCurrentForm();
        status.classList.remove("loading");
        status.textContent = "Значения доходов и расходов возвращены к данным журнала.";
    } catch (error) {
        setErrorState(error instanceof Error ? error.message : "Не удалось вернуть значения из журнала.");
    } finally {
        unlockControls();
    }
}

async function handleAction(action, loadingMessage, successMessage) {
    setLoadingState(loadingMessage);

    try {
        await action();
        const state = await refreshDashboard();
        fillFormFromTransactions(state.transactions);
        status.textContent = successMessage;
    } catch (error) {
        status.textContent = error.message || "Произошла ошибка при обновлении данных.";
    } finally {
        unlockControls();
        setTimeout(setIdleState, 1800);
    }
}

function bindModalCloseEvents() {
    document.querySelectorAll("[data-close-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            const modalId = button.getAttribute("data-close-modal");
            const modal = document.getElementById(modalId);
            if (modal) {
                closeModal(modal);
            }
        });
    });

    [transactionModal, obligationModal, goalModal].forEach((modal) => {
        modal.addEventListener("click", (event) => {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    setLoadingState("Выполняется расчёт показателей...");

    try {
        await calculateFromCurrentForm();
        status.textContent = "Показатели обновлены.";
    } catch (error) {
        status.textContent = error.message || "Не удалось рассчитать показатели.";
    } finally {
        unlockControls();
        setTimeout(setIdleState, 1800);
    }
});

openIncomeModalButton.addEventListener("click", () => {
    resetTransactionForm("income");
    openModal(transactionModal);
});

openExpenseModalButton.addEventListener("click", () => {
    resetTransactionForm("expense");
    openModal(transactionModal);
});

openObligationModalButton.addEventListener("click", () => {
    resetObligationForm();
    openModal(obligationModal);
});

openGoalModalButton.addEventListener("click", () => {
    resetGoalForm();
    openModal(goalModal);
});

restoreSummaryButton.addEventListener("click", async () => {
    await restoreSummaryFromJournal();
});

transactionForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    await handleAction(
        async () => {
            await createTransaction({
                amount: parseNumber(transactionAmountInput.value),
                category: transactionCategoryInput.value.trim(),
                type: transactionTypeInput.value,
                date: new Date(transactionDateInput.value).toISOString(),
            });
            closeModal(transactionModal);
        },
        transactionTypeInput.value === "income" ? "Добавление дохода..." : "Добавление расхода...",
        transactionTypeInput.value === "income" ? "Доход добавлен." : "Расход добавлен.",
    );
});

obligationForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    await handleAction(
        async () => {
            await createObligation({
                name: obligationNameInput.value.trim(),
                amount: parseNumber(obligationAmountInput.value),
                interest_rate: parseNumber(obligationInterestRateInput.value),
                term: parseNumber(obligationTermInput.value),
                monthly_payment: parseNumber(obligationMonthlyPaymentInput.value),
                payment_day: parseNumber(obligationPaymentDayInput.value) || 1,
                comment: obligationCommentInput.value.trim() || null,
            });
            closeModal(obligationModal);
        },
        "Добавление обязательства...",
        "Обязательство добавлено.",
    );
});

goalForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    await handleAction(
        async () => {
            await createGoal({
                name: goalNameInput.value.trim(),
                target_amount: parseNumber(goalTargetAmountInput.value),
                current_amount: parseNumber(goalCurrentAmountInput.value),
                deadline: new Date(goalDeadlineInput.value).toISOString(),
                comment: goalCommentInput.value.trim() || null,
            });
            closeModal(goalModal);
        },
        "Добавление цели...",
        "Цель добавлена.",
    );
});

loadDemoButton.addEventListener("click", async () => {
    await handleAction(
        () => requestJson("/api/demo/load", { method: "POST" }),
        "Загрузка демо-данных...",
        "Демо-данные загружены, показатели обновлены.",
    );
});

clearDemoButton.addEventListener("click", async () => {
    await handleAction(
        async () => {
            await requestJson("/api/demo/clear", { method: "POST" });
            incomeInput.value = "";
            expenseInput.value = "";
        },
        "Очистка данных...",
        "Данные очищены.",
    );
});

transactionsList.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
        return;
    }

    const transactionId = target.dataset.transactionId;
    if (!transactionId) {
        return;
    }

    await handleAction(
        () => deleteTransactionById(Number(transactionId)),
        "Удаление транзакции...",
        "Транзакция удалена.",
    );
});

obligationsList.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
        return;
    }

    const obligationId = target.dataset.obligationId;
    if (!obligationId) {
        return;
    }

    await handleAction(
        () => deleteObligationById(Number(obligationId)),
        "Удаление обязательства...",
        "Обязательство удалено.",
    );
});

goalsList.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
        return;
    }

    const goalId = target.dataset.goalId;
    if (!goalId) {
        return;
    }

    await handleAction(
        () => deleteGoalById(Number(goalId)),
        "Удаление цели...",
        "Цель удалена.",
    );
});

transactionsLimitSwitcher.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
        return;
    }

    const limit = Number(target.dataset.limit);
    if (!limit) {
        return;
    }

    appState.transactionsVisibleLimit = limit;
    updateTransactionsLimitButtons();
    renderTransactions(appState.transactions);
});

(async function initDashboard() {
    transactionDateInput.value = getTodayDate();
    goalDeadlineInput.value = getTodayDate();
    bindModalCloseEvents();
    setLoadingState("Загрузка данных dashboard...");

    try {
        const state = await refreshDashboard();
        fillFormFromTransactions(state.transactions);
        status.textContent = "Данные успешно загружены.";
    } catch (error) {
        status.textContent = error.message || "Не удалось загрузить показатели и данные интерфейса.";
    } finally {
        unlockControls();
        setTimeout(setIdleState, 1800);
    }
})();

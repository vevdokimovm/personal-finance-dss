/**
 * FINPILOT — English survey form builder (Google Apps Script)
 * ============================================================
 * Programmatically rebuilds the RU questionnaire (62 items, 7 sections) in ENGLISH
 * as a real Google Form. You don't create anything by hand — the script does it.
 *
 * HOW TO RUN (2 minutes):
 *   1. Go to https://script.google.com  →  New project.
 *   2. Delete the sample code, paste THIS whole file.
 *   3. Press Run  →  select function `buildSurveyForm`.
 *   4. Google asks for authorization (it creates a Form on your Drive) → Allow.
 *   5. When it finishes, open View → Logs (or Execution log): it prints
 *      the EDIT url and the public RESPONDER url of the created form.
 *
 * NOTES / LIMITATIONS (honest):
 *   - RANKING question (Q14) is built as a 1–5 grid. The Apps Script API cannot
 *     toggle "Limit to one response per column", so open the form once and enable
 *     it manually for Q14 if you want a strict ranking (one number per column).
 *   - Currency is USD ($): amounts are re-anchored for a foreign audience while
 *     preserving the scenario's ratios (income:mandatory:loan:goal:free). To use €
 *     instead, the same numbers work 1:1 (just replace the $ sign).
 *   - "Required" flags mirror the ones marked in the original where visible.
 *   - Junk/troll answer options from the response data (e.g. in marital status)
 *     are NOT included — only the real options are used.
 */

function buildSurveyForm() {
  var form = FormApp.create('How do you decide where to direct your money? — research survey');
  form.setDescription(
    'Hello! I\'m building a smart, algorithm-based personal-finance assistant and I want to ' +
    'understand what\'s wrong with current apps — how people really manage money, what they ' +
    'lack, and what frustrates them.\n\n' +
    'The survey is fully anonymous, 7 short sections, ~7–9 minutes. Results are used only in ' +
    'aggregate, to build a more useful personal-finance tool. Thank you for your time!'
  );
  form.setProgressBar(true);
  form.setCollectEmail(false);

  QUESTIONS.forEach(function (q) { addItem(form, q); });

  Logger.log('DONE.');
  Logger.log('EDIT form:      ' + form.getEditUrl());
  Logger.log('SHARE (fill in): ' + form.getPublishedUrl());
}

/** Dispatch one question spec to the right FormApp item. */
function addItem(form, q) {
  switch (q.type) {
    case 'section': {
      var pb = form.addPageBreakItem().setTitle(q.title);
      if (q.help) pb.setHelpText(q.help);
      break;
    }
    case 'single': {
      var mc = form.addMultipleChoiceItem().setTitle(q.title);
      if (q.help) mc.setHelpText(q.help);
      var choices = q.options.map(function (o) { return mc.createChoice(o); });
      mc.setChoices(choices);
      if (q.other) mc.showOtherOption(true);
      mc.setRequired(!!q.required);
      break;
    }
    case 'multi': {
      var cb = form.addCheckboxItem().setTitle(q.title);
      if (q.help) cb.setHelpText(q.help);
      cb.setChoiceValues(q.options);
      if (q.other) cb.showOtherOption(true);
      cb.setRequired(!!q.required);
      break;
    }
    case 'scale': {
      var sc = form.addScaleItem().setTitle(q.title);
      if (q.help) sc.setHelpText(q.help);
      sc.setBounds(q.lo, q.hi).setLabels(q.left || '', q.right || '');
      sc.setRequired(!!q.required);
      break;
    }
    case 'grid': {
      var gr = form.addGridItem().setTitle(q.title);
      if (q.help) gr.setHelpText(q.help);
      gr.setRows(q.rows).setColumns(q.cols);
      gr.setRequired(!!q.required);
      break;
    }
    case 'text': {
      var ti = form.addTextItem().setTitle(q.title);
      if (q.help) ti.setHelpText(q.help);
      ti.setRequired(!!q.required);
      break;
    }
    case 'paragraph': {
      var pi = form.addParagraphTextItem().setTitle(q.title);
      if (q.help) pi.setHelpText(q.help);
      pi.setRequired(!!q.required);
      break;
    }
  }
}

/** ---- Full questionnaire spec (English), in original order ---- */
var SCALE_1_5 = { lo: 1, hi: 5 };

var QUESTIONS = [
  // ===== Section 1 =====
  { type: 'section', title: 'Section 1. How you currently manage your finances',
    help: 'Tell us how you work with your money today — which tools you use and what you like / dislike about them.' },

  { type: 'multi', required: true, other: true,
    title: 'What do you use to track your finances? (select all that apply)',
    options: ['Bank\'s built-in statistics (Tinkoff, Sber, etc.)', 'A separate app (Zen-Money, Coinkeeper, Money Manager)',
      'AI assistants (ChatGPT, GigaChat)', 'Google Sheets / Excel', 'Notes on my phone', 'I don\'t use anything'] },

  { type: 'single',
    title: 'How many banks do you use in daily life?',
    help: 'Count everywhere you have a card, account, loan, mortgage or deposit — even if you use it rarely.',
    options: ['1 bank', '2 banks', '3 banks', '4 banks', '5 or more'] },

  { type: 'multi', required: true,
    title: 'What exactly do you have in these banks? (select all that apply)',
    options: ['Salary card', 'Debit card for purchases', 'Credit card', 'Cash loan', 'Mortgage',
      'Installment / BNPL (Dolyami, Split, etc.)', 'Deposit / savings account', 'Investment / brokerage account',
      'Card for subscriptions and online services', 'Hard to say / prefer not to say'] },

  { type: 'single', required: true,
    title: 'How often do you check your finances?',
    options: ['Every day', 'Once a week', 'Several times a month', 'When something happens (payment, salary)', 'Almost never'] },

  { type: 'single',
    title: 'Have you used an AI assistant (ChatGPT, GigaChat, Claude, DeepSeek, etc.) specifically for financial questions — calculations, advice, planning?',
    options: ['Yes, I use it regularly', 'Yes, tried it a few times', 'No, but I\'ve heard it\'s possible',
      'No, I didn\'t know that was possible', 'On principle I don\'t use AI for money'] },

  { type: 'multi',
    title: 'What stops you from trusting an AI assistant (ChatGPT, Gemini, Claude, etc.) with financial questions? (select all)',
    options: ['Not sure it calculates correctly — it could get the numbers wrong', 'I don\'t understand how it decides — a "black box"',
      'I\'m afraid my financial data will leak', 'It doesn\'t know my specific situation — gives generic advice',
      'It gives different answers to the same question each time', 'Financial matters are too serious — I need a human / specialist',
      'I don\'t understand where and how my financial data is stored', 'AI takes no responsibility for its advice',
      'I trust it, nothing stops me', 'Haven\'t tried it, hard to say'] },

  { type: 'single', required: true,
    title: 'How long have you used this tool?',
    options: ['Less than 3 months', '3–12 months', 'More than a year', 'I don\'t use anything'] },

  { type: 'multi', required: true, other: true,
    title: 'How does your current tool actually help you? (select all)',
    options: ['I see where my money goes', 'I keep category limits under control', 'It helps me plan what to do next',
      'I track my balance', 'It helps me decide where to direct money', 'Nothing really helps'] },

  { type: 'multi', required: true, other: true,
    title: 'What annoys you about the interface of finance apps? (select all)',
    options: ['Entering data manually is slow and tedious', 'Too many charts and numbers — unclear what to look at',
      'Notifications and reminders are annoying', 'Unclear where to start on first launch',
      'The interface is overloaded — too many features', 'Everything suits me', 'I don\'t use one'] },

  { type: 'multi', other: true,
    title: 'What can your current tool NOT do that you\'d want? (select all)',
    options: ['Doesn\'t tell me where to direct free money', 'Doesn\'t account for debts and goals together',
      'Doesn\'t warn me in advance that money will run short', 'Doesn\'t explain the logic of its advice',
      'There is advice, but I don\'t trust it — unclear where it comes from', 'Everything suits me'] },

  { type: 'single',
    title: 'Why did you stop using a finance app, or never start?',
    options: ['Got tired of entering data manually', 'It shows statistics — but then what? Unclear',
      'I don\'t see real benefit', 'I don\'t trust the app with my data', 'I still use it', 'Never tried'] },

  // ===== Section 2 =====
  { type: 'section', title: 'Section 2. How you make financial decisions',
    help: 'A few questions about how you choose where to direct money.' },

  { type: 'single', required: true,
    title: 'When you have several options for where to direct money — how do you choose?',
    options: ['By feeling', 'I calculate manually what\'s more beneficial', 'I ask someone', 'I postpone the decision and the money just sits'] },

  { type: 'multi', other: true,
    title: 'Do you use any rule for allocating money? (select all)',
    options: ['The 50/30/20 rule (50% needs, 30% wants, 20% savings)',
      '"Pay yourself first" — set aside a fixed % of income immediately (e.g. 10%)',
      'Envelope method — split across accounts / categories in advance',
      'Pay off debts first — while I have loans, everything else at the minimum',
      'Build a cushion first — until I have a reserve, goals can wait',
      'Set aside a fixed amount (a specific sum, not a %, e.g. $500/mo)',
      'Set aside a % of unexpected income (bonuses, refunds)'] },

  { type: 'grid',
    title: 'When you have free money left at the end of the month, in what priority do you usually use it? (rank 1 = highest … 5 = lowest)',
    help: 'Tip: for a strict ranking, enable "Limit to one response per column" for this question in the form editor.',
    rows: ['Pay off debts / loans early', 'Top up the financial cushion (reserve)',
      'Save for a specific goal (vacation, purchase, etc.)', 'Invest (deposit, stocks — something income-generating)',
      'Spend on myself — whatever I want'],
    cols: ['1', '2', '3', '4', '5'] },

  { type: 'multi',
    title: 'What has happened to you because you didn\'t have a proper tool? (select all)',
    options: ['Money seemed to be there — but fell short for a payment', 'I was saving for a goal but spent it elsewhere',
      'I didn\'t know in what order to pay off debts — paid at random',
      'I borrowed even though the money was actually there, just not in the right place', 'Nothing critical happened'] },

  { type: 'multi', other: true,
    title: 'When you need financial advice — what / whom do you turn to? (select all)',
    options: ['I Google / read articles', 'I ask relatives or friends', 'Financial bloggers, Telegram channels',
      'YouTube videos', 'A bank manager / financial consultant', 'Finance apps / bank advice',
      'AI assistants (ChatGPT, GigaChat, etc.)', 'I don\'t ask anyone, I decide myself'] },

  { type: 'single',
    title: 'If a bank or app gave you advice (how to allocate funds optimally) — did you follow it?',
    options: ['Yes, if it was clear why', 'No — unclear what the advice is based on',
      'I haven\'t received such advice', 'I never pay attention to advice'] },

  { type: 'multi', other: true,
    title: 'In what format is it more convenient for you to receive financial advice? (select all)',
    options: ['A short message with a specific action ("do this")', 'An explanation with numbers and calculation',
      'A visualization — chart, comparison of options', 'Just a notification when something goes wrong'] },

  // ===== Section 3 =====
  { type: 'section', title: 'Section 3. A specific case — your last choice situation',
    help: 'Recall a real situation when you had some free money and had to decide where to direct it.' },

  { type: 'single',
    title: 'Recall the last time you had a free sum (a bonus, month-end leftover, a refund, etc.) and had to decide where to direct it — pay off a loan/debt, save for a goal, keep it in reserve, or spend it. How long did that decision take you, from "need to think" to "decided"?',
    options: ['Decided at once, didn\'t think (< 1 minute)', '1–5 minutes', '5–15 minutes', '15–30 minutes',
      '30–60 minutes', '1–2 hours', 'Postponed the decision for days / weeks'] },

  { type: 'scale', required: true, lo: 1, hi: 5, left: 'Completely unsure', right: 'Completely sure',
    title: 'How confident are you that this decision was optimal?' },

  { type: 'single',
    title: 'How often do such choice situations arise for you — where to direct money?',
    options: ['Several times a month', 'About once a month', 'Once every 2–3 months', 'Less often / almost never'] },

  { type: 'single',
    title: 'When choosing where to direct free money — how many options do you usually compare?',
    options: ['I decide without comparing', '2 options', '3–4 options', '5 or more'] },

  { type: 'scale', lo: 1, hi: 5, left: 'Much worse than expected', right: 'Much better than expected',
    title: 'Recall that same decision about free money. Time has passed — how do you rate its result now?' },

  { type: 'multi', other: true,
    title: 'If the result differed from your expectations — what influenced it? (select all)',
    options: ['Unexpected expenses came up', 'My income changed', 'I didn\'t account for some payments',
      'The decision itself was a bad one', 'External circumstances (market, exchange rate, inflation)', 'Everything went as planned'] },

  { type: 'paragraph',
    title: '(Optional) If you\'d like — tell this story in a bit more detail, in one or two sentences. For example: what you were choosing between, how it ended, what you\'d do differently.' },

  { type: 'single',
    title: 'Imagine a specific situation: your income is $4,000/mo — mandatory payments (rent, utilities, transport, food) are $2,500 — you have a loan of $3,000 at 20%/yr (minimum payment $200/mo) — your goal is to save $5,000 for a vacation by summer — you currently have $750 in reserve. At the end of the month you have $1,500 free. Where do you direct it?',
    options: ['All $1,500 to early loan repayment', 'All $1,500 to the goal — the vacation matters more',
      'All $1,500 to reserve — just in case', 'Split roughly evenly among debt, goal and reserve',
      'Split, but in different proportions', 'Spend it — I\'ve earned it', 'I don\'t know, I\'d need to calculate'] },

  { type: 'single', required: true,
    title: 'What did you base the answer above on?',
    options: ['I worked out in my head what\'s more beneficial money-wise (interest, savings)',
      'I went by comfort — what worries me less', 'I thought about the worst case — what if I\'m fired or get sick',
      'I applied a rule I use in life (e.g. "debts first")', 'Not sure I chose right — at random'] },

  // ===== Section 4 =====
  { type: 'section', title: 'Section 4. Your financial situation',
    help: 'Tell us a bit about your current financial situation. All answers are anonymous.' },

  { type: 'single',
    title: 'Which best describes your usual financial behavior after all mandatory payments?',
    help: 'Mandatory = what you pay every month: rent, utilities, loans, installments, insurance.',
    options: ['I almost always have leftover money that I save',
      'I plan in advance how much to set aside at the start of the month and stick strictly to the plan',
      'I almost never have leftover money — it all goes to current needs',
      'I have no clear system: sometimes I save, sometimes I spend to the last penny',
      'I have regular mandatory payments (loan, mortgage, insurance) that I pay, and I spend the rest'] },

  { type: 'single', required: true, other: true,
    title: 'On what principle do you set money aside?',
    options: ['I set aside whatever is left after all spending',
      'I set aside a strictly defined amount every month (e.g. 10% of income)',
      'I set aside when there\'s free money, with no system', 'I don\'t set aside'] },

  { type: 'single',
    title: 'Do you split your money into different "envelopes" / accounts / wallets for different purposes?',
    help: 'For example: separate bank accounts — one for daily spending, one for a vacation, one as an "untouchable reserve".',
    options: ['Yes, always — I have a clear separation system', 'Sometimes — for big goals or important expenses',
      'No, all my money is in one place'] },

  { type: 'single',
    title: 'How far ahead can you realistically plan your finances?',
    help: 'Meaning: you roughly know how much money you\'ll have and where it will go.',
    options: ['I can\'t plan', 'A few days', 'A week or two', 'A month', '2–3 months', 'Half a year', 'A year', 'Several years', 'Hard to say'] },

  { type: 'single',
    title: 'Do you have a financial goal for the coming year — to save for something specific?',
    options: ['Yes, a clear goal and amount', 'There\'s something, but it\'s vague', 'No'] },

  { type: 'multi',
    title: 'Which saving motives are most important to you? (choose up to 3 — the most important ones)',
    options: ['For a rainy day', 'For a big purchase', 'For rest / travel', 'For education', 'For buying property',
      'For retirement', 'For financial independence', 'Just because', 'To protect against inflation', 'To grow my capital'] },

  { type: 'single', required: true,
    title: 'How would you rate your level of financial literacy?',
    options: ['Very low — I get confused even in basic terms', 'Low — I know the basics but get lost in complex decisions',
      'Medium — I handle typical tasks', 'High — I confidently make financial decisions', 'Very high — I could advise others'] },

  { type: 'single',
    title: 'Do you currently have a loan, installment plan or debt?',
    options: ['Yes, several', 'Yes, one', 'No', 'Prefer not to say'] },

  { type: 'single',
    title: 'Have you ever been unsure whether it\'s better to pay off debt early or save for a goal?',
    options: ['Yes, that happened and I didn\'t know what to choose', 'Yes, but I just chose at random',
      'No, I have no debts', 'No, I always understand what\'s better'] },

  { type: 'multi', other: true,
    title: 'What feelings do you most often have when you think about your finances? (select all)',
    options: ['Calm — everything under control', 'Anxiety that something won\'t be enough', 'Irritation at having to calculate',
      'Confusion — I don\'t know where to start', 'Guilt over past financial decisions', 'Boredom — not interested in this',
      'Curiosity — I want to understand it better'] },

  { type: 'scale', lo: 1, hi: 5, left: 'Completely absent', right: 'So strong it\'s hard to think clearly',
    title: 'How strong is your anxiety related to finances?' },

  { type: 'single', required: true,
    title: 'How often do you have free money left at the end of the month?',
    options: ['Almost always', 'Sometimes', 'Rarely', 'Never — it all goes to zero or into the red'] },

  { type: 'single',
    title: 'How often do you worry about forgetting a regular mandatory payment? (loan, installment, debt, mortgage, taxes)',
    options: ['1 – almost never', '2 – rarely', '3 – sometimes', '4 – often', '5 – very often'] },

  { type: 'single',
    title: 'If you lost your main source of income (your job), how long would your current savings last?',
    options: ['Less than 1 month', '1–3 months', '4–6 months', '7–11 months', 'A year or more'] },

  // ===== Section 5 =====
  { type: 'section', title: 'Section 5. The tool idea',
    help: 'Thanks for your time — two short sections left. A couple of questions about the tool I\'m building.' },

  { type: 'grid',
    title: 'When you have free money and decide where to direct it — how important is each of these criteria to you? (1 = not important at all, 5 = critically important)',
    rows: ['Yield — earn or save as much money as possible', 'Liquidity — keep a reserve of cash on hand for the unexpected',
      'Debt reduction — reduce debts and interest', 'Safety — don\'t take risks, choose reliable options'],
    cols: ['1', '2', '3', '4', '5'] },

  { type: 'single',
    title: 'Ordinary apps show statistics: "you spent $750 on food." Would a tool be useful that instead calculates for you and says specifically: "You have $400 free this month. Given your $2,500 debt at 18%, your goal to save $5,000 for a vacation, and the risk that next month\'s income may dip — it\'s optimal to put $250 toward early repayment, $100 into reserve, $50 toward the goal. That way you save about $60 in interest and don\'t go into the red." (i.e. it accounts for all your debts, goals, mortgages, taxes, mandatory payments and reserve at once, not separately)',
    options: ['Yes — that\'s exactly what\'s missing', 'Interesting, but it depends on how transparent it is', 'No, I prefer to decide myself'] },

  { type: 'multi', other: true,
    title: 'What should such a tool have for you to use it? (select all)',
    options: ['Sees all my debts, goals and balance in one place',
      'Tells me how much free money I really have, accounting for all payments',
      'Warns me in advance that money will run short', 'Gives specific advice with an explanation of why',
      'Shows what happens if I do it one way or another'] },

  { type: 'multi',
    title: 'What would make you trust a financial assistant\'s advice? (select all)',
    options: ['An explanation with numbers — why this action is more beneficial', 'The ability to see alternatives and compare',
      'Recommendations from other users / reviews', 'A transparent algorithm — I understand how it\'s calculated',
      'Nothing would — I decide myself'] },

  { type: 'multi',
    title: 'On what device / in what format would it be more convenient to use such an assistant? (select all)',
    options: ['Mobile app (iOS/Android)', 'Website via browser', 'Telegram bot', 'Desktop / web app', 'Doesn\'t matter, as long as it works'] },

  { type: 'scale', required: true, lo: 1, hi: 7, left: '', right: '',
    title: 'Please select 7 stars to confirm that you are reading the statements.' },

  { type: 'single',
    title: 'How much would you be willing to pay per month for such a tool, if it really helps?',
    options: ['Up to $2/mo', '$2–5/mo', '$5–10/mo', 'Willing to pay once (e.g. $15–30)',
      'Willing to pay a % of what\'s saved / earned'] },

  { type: 'single',
    title: 'Imagine two equally convenient systems, both giving financial advice. Which would you trust more?',
    options: ['System A — AI-based (ChatGPT/Gemini/Claude). Understands free text, replies in a human way, but you don\'t see how it calculates',
      'System B — based on mathematical formulas. You see concrete calculations, criteria weights, an explanation with numbers. But the interface is forms and buttons, with no free dialogue',
      'I\'d trust both equally, as long as the recommendations are sound', 'I wouldn\'t trust either'] },

  { type: 'single',
    title: 'What\'s more important to you in a financial advisor?',
    options: ['That it can understand complex questions in natural language',
      'That I can see the exact calculation logic and verify it', 'Both are equally important', 'Neither — the result is what matters'] },

  { type: 'grid', required: true,
    title: 'Would you trust an AI assistant with the following financial tasks?',
    rows: ['Explain an unclear financial term', 'Calculate the benefit of early loan repayment',
      'Suggest how to split a bonus between debt and savings', 'Forecast how much money you\'ll have in 3 months',
      'Decide for you and automatically transfer the money'],
    cols: ['Yes', 'No', 'Not sure'] },

  { type: 'paragraph',
    title: '(Optional) If you had an ideal financial assistant — describe in one or two sentences what it does. What feature would matter most to you? (you can skip this)' },

  // ===== Section 6 =====
  { type: 'section', title: 'Section 6. About you',
    help: 'A final short block. All answers are anonymous and used only for analysis.' },

  { type: 'single', required: true, title: 'Please specify your gender', options: ['Male', 'Female'] },

  { type: 'single', required: true, title: 'Please specify your age',
    options: ['Under 18', '18–22', '23–27', '28–35', '36–45', '46–60', '61+'] },

  { type: 'single', required: true, other: true,
    title: 'What is your education?',
    options: ['Didn\'t finish school', 'General secondary education', 'Vocational secondary education',
      'Incomplete higher education', 'Higher education', 'Academic degree'] },

  { type: 'single', required: true, other: true,
    title: 'Your marital status',
    options: ['Married', 'In a relationship', 'Not in a relationship'] },

  { type: 'multi', required: true,
    title: 'What is your status? (select all that apply)',
    options: ['Student', 'Employed', 'Entrepreneur', 'On parental leave / not working',
      'Parent with dependent children', 'Freelancer / self-employed'] },

  { type: 'single',
    title: 'Where do you live?',
    options: ['Moscow / St. Petersburg', 'A city of 1M+', 'A city under 1M', 'A small town / village'] },

  { type: 'single',
    title: 'What is your approximate monthly income?',
    options: ['Under $1,000', '$1,000–2,000', '$2,000–4,000', '$4,000–7,000', '$7,000–12,000', 'Over $12,000'] },

  { type: 'single',
    title: 'Rate your material situation',
    options: ['Not enough even for food', 'Enough only for food', 'Enough for clothes and food, but not for buying electronics',
      'Enough for electronics, but not for big purchases', 'Can afford big purchases (apartment, car, vacation)'] },

  // ===== Section 7 =====
  { type: 'section', title: 'Section 7. Finally',
    help: 'Thank you for completing the survey!' },

  { type: 'text',
    title: 'If you want to be the first to know when the app launches — leave your email. I\'ll personally write when the prototype is live.',
    help: 'The email is used only for a single launch notification. It is not shared with third parties.' },

  { type: 'paragraph',
    title: '(Optional) What important thing did I, as a researcher, not ask about, but you want to say on this topic? You can share your experience with financial assistants, comments / ideas, or your personal vision of an ideal financial advisor. (you can skip this)' }
];

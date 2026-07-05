/**
 * FINPILOT — English version of the audience survey.
 * Google Apps Script: recreates the original 62-question, 7-section Russian form
 * in English. Data-driven — the SURVEY object holds the translated content, the
 * builder loop applies the correct Google Forms item type per question.
 *
 * HOW TO RUN:
 *   1. Open https://script.google.com → New project.
 *   2. Paste this file, save.
 *   3. Run createFinpilotSurveyEN() once, authorize when prompted.
 *   4. The published + edit URLs are printed to the execution log (View → Logs).
 *
 * Note: monetary amounts kept in ₽ to preserve the research context 1:1.
 * Item types: radio = single choice, checkbox = multi, scale = 1..N slider,
 * grid = matrix (rows × columns), text = short answer, paragraph = long answer.
 */

var SURVEY = {
  title: "Survey: How do you decide where to put your money?",
  description:
    "Anonymous, 7 minutes.\n\n" +
    "Hi! I'm Vasilii. I'm building a smart, algorithm-based personal finance " +
    "assistant and I want to understand what's wrong with today's apps — which " +
    "tools people actually use, what frustrates them, and what's missing.\n\n" +
    "The survey is fully anonymous, 7 short sections, ~7–9 minutes. Results are " +
    "used only in aggregated form for research purposes.\n\n" +
    "Thank you for your time and cooperation!\n* Required question",
  sections: [
    {
      title: "Section 1. How you currently manage your finances",
      help: "Tell us how you work with your money today — which tools you use and what does/doesn't work.",
      items: [
        { type: "checkbox", required: true, other: true,
          title: "What do you use to track your finances? (select all that apply)",
          help: "Check all that apply.",
          choices: ["Built-in bank statistics (Tinkoff, Sber, etc.)",
                    "A dedicated app (Zen-money, CoinKeeper, Money Manager)",
                    "AI assistants (ChatGPT, GigaChat)", "Google Sheets / Excel",
                    "Notes on my phone", "I don't use anything"] },
        { type: "radio",
          title: "How many banks do you use in everyday life?",
          help: "Count every bank where you have a card, account, loan, mortgage or deposit — even if you use it rarely.",
          choices: ["1 bank", "2 banks", "3 banks", "4 banks", "5 or more"] },
        { type: "checkbox", required: true,
          title: "What exactly do you have in these banks? (select all that apply)",
          choices: ["Salary card", "Debit card for purchases", "Credit card", "Cash loan",
                    "Mortgage", "Installment / BNPL (Dolyame, Split, etc.)",
                    "Deposit / savings account", "Investment / brokerage account",
                    "Card for subscriptions and online services", "Prefer not to say"] },
        { type: "radio", required: true,
          title: "How often do you check your finances?",
          choices: ["Every day", "Once a week", "Several times a month",
                    "When something happens (a payment, salary)", "Almost never"] },
        { type: "radio",
          title: "Have you used an AI assistant (ChatGPT, GigaChat, Claude, DeepSeek, etc.) specifically for financial questions — calculations, advice, planning?",
          choices: ["Yes, I use it regularly", "Yes, I've tried it a few times",
                    "No, but I've heard it's possible", "No, I didn't know you could",
                    "I deliberately don't use AI for money matters"] },
        { type: "checkbox",
          title: "What stops you from trusting an AI assistant (ChatGPT, Gemini, Claude, etc.) with financial questions? (select all that apply)",
          choices: ["I'm not sure it calculates correctly — it might get numbers wrong",
                    "I don't understand how it decides — it's a black box",
                    "I'm afraid my financial data could leak",
                    "It doesn't know my specific situation — gives generic advice",
                    "It gives different answers to the same question each time",
                    "Financial questions are too serious — I need a human/specialist",
                    "I don't understand where and how my financial data is stored",
                    "The AI isn't accountable for its advice",
                    "I trust it, nothing stops me", "I haven't tried it, hard to say"] },
        { type: "radio", required: true,
          title: "How long have you been using this tool?",
          choices: ["Less than 3 months", "3–12 months", "More than a year", "I don't use anything"] },
        { type: "checkbox", required: true, other: true,
          title: "How does your current tool actually help you? (select all that apply)",
          choices: ["I see where my money goes", "I control category limits",
                    "It helps me plan what to do next", "I track my balance",
                    "It helps me decide where to put my money", "Nothing really helps"] },
        { type: "checkbox", required: true, other: true,
          title: "What annoys you about the interface of finance apps? (select all that apply)",
          choices: ["Entering data manually is slow and tedious",
                    "Too many charts and numbers — unclear what to look at",
                    "Notifications and reminders are annoying",
                    "Unclear where to start on first launch",
                    "The interface is overloaded — too many features",
                    "Everything is fine", "I don't use any"] },
        { type: "checkbox", required: true, other: true,
          title: "What can't your current tool do that you'd want? (select all that apply)",
          choices: ["Doesn't tell me where to put my free money",
                    "Doesn't account for debts and goals at the same time",
                    "Doesn't warn me in advance that money will run short",
                    "Doesn't explain the logic behind its advice",
                    "It gives advice, but I don't trust it — unclear where it comes from",
                    "Everything is fine"] },
        { type: "radio",
          title: "Why did you stop using a finance app, or never started?",
          choices: ["Tired of entering data manually",
                    "It shows statistics — but then what? Unclear",
                    "I don't see real value", "I don't trust the app with my data",
                    "I still use one", "I've never tried"] }
      ]
    },
    {
      title: "Section 2. How you make financial decisions",
      help: "A few questions about how you choose where to put your money.",
      items: [
        { type: "radio", required: true,
          title: "When you have several options for where to put your money — how do you choose?",
          choices: ["By feeling", "I calculate by hand what's more profitable",
                    "I ask someone", "I postpone the decision and the money just sits there"] },
        { type: "checkbox", other: true,
          title: "Do you use any rule to allocate money? (select all that apply)",
          choices: ["The 50/30/20 rule (50% needs, 30% wants, 20% savings)",
                    "\"Pay yourself first\" — set aside a fixed % of income immediately (e.g. 10%)",
                    "The envelope method — split across accounts/categories in advance",
                    "Debts first — while I have loans, everything else is minimal",
                    "Emergency fund first — until I build a reserve, goals wait",
                    "I set aside a fixed amount (a specific sum, e.g. 10,000 ₽/mo)",
                    "I set aside a % of unexpected income (bonuses, refunds)"] },
        { type: "grid",
          title: "If money is left over at the end of the month — in what priority do you usually use it?",
          help: "Rank from most important (1) to least (5).",
          rows: ["Pay off debts/loans early", "Top up the emergency fund (reserve)",
                 "Save toward a specific goal (vacation, purchase, etc.)",
                 "Invest (deposit, stocks, something income-generating)",
                 "Spend on myself — what I want"],
          columns: ["1", "2", "3", "4", "5"] },
        { type: "checkbox",
          title: "What happened because you didn't have a proper tool? (select all that apply)",
          choices: ["I had money on paper — but came up short for a payment",
                    "I was saving for a goal but spent it elsewhere",
                    "I didn't know the order to pay off debts — I paid at random",
                    "I borrowed even though I had the money, just not in the right place",
                    "Nothing critical happened"] },
        { type: "checkbox", other: true,
          title: "When you need financial advice — what/whom do you turn to? (select all that apply)",
          choices: ["I Google / read articles", "I ask family or friends",
                    "Finance bloggers, Telegram channels", "YouTube videos",
                    "A bank manager / financial advisor", "Finance apps / bank tips",
                    "AI assistants (ChatGPT, GigaChat, etc.)", "I don't ask anyone, I decide myself"] },
        { type: "radio",
          title: "If a bank or app gave you advice (how to optimally allocate funds) — did you follow it?",
          choices: ["Yes, if it was clear why", "No, unclear what it's based on",
                    "I haven't received such advice", "I never pay attention to advice"] },
        { type: "checkbox", other: true,
          title: "In what format is it more convenient to receive financial advice? (select all that apply)",
          choices: ["A short message with a specific action (\"do this\")",
                    "An explanation with numbers and calculation",
                    "Visualization — a chart, comparison of options",
                    "Just a notification when something goes wrong"] }
      ]
    },
    {
      title: "Section 3. A specific case — your last decision",
      help: "Recall a specific situation when you had a free sum and had to decide where to put it.",
      items: [
        { type: "radio",
          title: "Recall the last time you had a free sum (a bonus, month-end leftover, refund, etc.) and had to decide where to put it — pay off a loan/debt, save toward a goal, keep it in reserve, or spend it. How long did that decision take — from \"I need to think\" to \"decided\"?",
          choices: ["Decided instantly, didn't think (< 1 minute)", "1–5 minutes", "5–15 minutes",
                    "15–30 minutes", "30–60 minutes", "1–2 hours",
                    "I postponed the decision for days/weeks"] },
        { type: "scale", required: true, low: 1, high: 5,
          leftLabel: "Completely unsure", rightLabel: "Completely confident",
          title: "How confident are you that this decision was optimal?" },
        { type: "radio",
          title: "How often do such choices come up — where to put your money?",
          choices: ["Several times a month", "About once a month",
                    "Once every 2–3 months", "Rarely / almost never"] },
        { type: "radio",
          title: "When choosing where to put free money — how many options do you usually compare?",
          choices: ["I decide without comparing", "2 options", "3–4 options", "5 or more"] },
        { type: "scale", required: true, low: 1, high: 5,
          leftLabel: "Much worse than expected", rightLabel: "Much better than expected",
          title: "Recall that same decision about free money. Time has passed — how do you rate its outcome now?" },
        { type: "checkbox", other: true,
          title: "If the outcome differed from expectations — what influenced it? (select all that apply)",
          choices: ["Unexpected expenses came up", "My income changed",
                    "I didn't account for some payments", "The decision itself was poor",
                    "External circumstances (market, exchange rate, inflation)",
                    "Everything went as planned"] },
        { type: "paragraph",
          title: "(Optional) If you'd like — tell this story in a sentence or two. E.g.: what you chose, how it ended, what you'd do differently." },
        { type: "radio",
          title: "Imagine a specific situation. Your income is 80,000 ₽/mo. Mandatory payments (rent, utilities, transport, food): 50,000 ₽. You have a loan: 60,000 ₽ at 20% annual (minimum payment 4,000 ₽/mo). Goal: save 100,000 ₽ for a vacation by summer. Your reserve now: 15,000 ₽. At the end of the month you have 30,000 ₽ left over. Where do you put it?",
          choices: ["All 30,000 ₽ to early loan repayment",
                    "All 30,000 ₽ to the goal — the vacation matters more",
                    "All 30,000 ₽ to reserve — just in case",
                    "Split roughly equally between debt, goal and reserve",
                    "Split, but in different proportions", "Spend it — I've earned it",
                    "I don't know, need to calculate"] },
        { type: "radio", required: true,
          title: "What did you rely on when choosing your answer above?",
          choices: ["I calculated in my head what's better money-wise (interest, savings)",
                    "I went by comfort — what worries me less",
                    "I thought about the worst case — what if I'm laid off, get sick",
                    "I applied a rule I use in life (e.g. \"debts first\")",
                    "I'm not sure what I chose — at random"] }
      ]
    },
    {
      title: "Section 4. Your financial situation",
      help: "Tell us a bit about your current financial situation. All answers are anonymous.",
      items: [
        { type: "radio",
          title: "Which of the following best describes your usual financial behavior after all mandatory payments?",
          help: "This means monthly payments: rent, utilities, loans, installments, insurance.",
          choices: ["I almost always have unspent money left, which I save",
                    "I plan in advance how much to save and stick strictly to the plan",
                    "I almost never have money left — everything goes to current needs",
                    "I have no clear system: sometimes I save, sometimes I spend it all",
                    "I have regular mandatory payments (loan, mortgage, insurance) that I pay, and I spend the rest"] },
        { type: "radio", required: true, other: true,
          title: "By what principle do you save money?",
          choices: ["I save whatever is left after all spending",
                    "I save a strictly fixed amount every month (e.g. 10% of income)",
                    "I save when I have free money, without a system", "I don't save"] },
        { type: "radio",
          title: "Do you split your money across different \"envelopes\" / accounts / wallets for different goals?",
          help: "E.g. different bank accounts — one for everyday spending, another for vacation, a third for the \"untouchable reserve\".",
          choices: ["Yes, always — I have a clear separation system",
                    "Sometimes — for big goals or important expenses",
                    "No, all money in one place"] },
        { type: "radio",
          title: "How far ahead can you realistically plan your finances?",
          help: "Meaning: you roughly know how much money you'll have and where it will go.",
          choices: ["I can't plan", "A few days", "A week or two", "A month",
                    "2–3 months", "Half a year", "A year", "Several years", "Hard to say"] },
        { type: "radio",
          title: "Do you have a financial goal for the coming year — to save for something specific?",
          choices: ["Yes, a clear goal and amount", "Something, but vague", "No"] },
        { type: "checkbox",
          title: "Which savings motives are most important to you?",
          help: "You can select several, but no more than 3 — pick the most important.",
          choices: ["For a rainy day", "For a big purchase", "For rest / travel", "For education",
                    "For buying real estate", "For retirement", "For financial independence",
                    "Just because", "To protect from inflation", "To grow capital"] },
        { type: "radio", required: true,
          title: "How would you rate your level of financial literacy?",
          choices: ["Very low — I get confused even by basic terms",
                    "Low — I know the basics, but get lost in complex decisions",
                    "Medium — I handle typical tasks",
                    "High — I make financial decisions confidently",
                    "Very high — I can advise others"] },
        { type: "radio", required: true,
          title: "Do you currently have a loan, installment plan or debt?",
          choices: ["Yes, several", "Yes, one", "No", "Prefer not to say"] },
        { type: "radio",
          title: "Has it ever happened that you didn't know — whether to pay off debt early or save toward a goal?",
          choices: ["Yes, that happened and I didn't know what to choose",
                    "Yes, but I just chose at random", "No, I have no debts",
                    "No, I always understand what's better"] },
        { type: "checkbox", other: true,
          title: "What feelings do you most often have when thinking about your finances? (select all that apply)",
          choices: ["Calm, everything's under control", "Anxiety that something won't be enough",
                    "Irritation at having to calculate", "Confusion, don't know where to start",
                    "Guilt over past financial decisions", "Boredom, not interested in this",
                    "Curiosity, want to understand better"] },
        { type: "scale", low: 1, high: 5,
          leftLabel: "Completely absent", rightLabel: "So strong it's hard to think clearly",
          title: "How strong is your feeling of anxiety about finances?" },
        { type: "radio", required: true,
          title: "How often is money left over at the end of the month?",
          choices: ["Almost always", "Sometimes", "Rarely", "Never, everything goes to zero or negative"] },
        { type: "radio",
          title: "How often do you worry you might forget a regular mandatory payment? (loan, installment, debt, mortgage, taxes)",
          choices: ["1 – almost never", "2 – rarely", "3 – sometimes", "4 – often", "5 – very often"] },
        { type: "radio",
          title: "If you lost your main source of income (your job), how long would your current savings last?",
          choices: ["Less than 1 month", "1–3 months", "4–6 months", "7–11 months", "A year or more"] }
      ]
    },
    {
      title: "Section 5. The tool idea",
      help: "Thanks for your time, two short sections left. A couple of questions about the tool I'm building.",
      items: [
        { type: "grid",
          title: "When you have free money and decide where to put it — how important is each of these criteria?",
          help: "1 — not important at all, 5 — critically important. One oval per row.",
          rows: ["Profitability — earn or save the maximum money",
                 "Liquidity — keep cash on hand for the unexpected",
                 "Reducing debt burden — cut debts and interest",
                 "Safety — don't take risks, choose reliable options"],
          columns: ["1", "2", "3", "4", "5"] },
        { type: "radio",
          title: "Regular apps show statistics: \"you spent 15,000 on food.\" Would you find useful a tool that instead calculates for you and says: \"You have 8,000 free this month. Given your 50,000 debt at 18%, your goal of 100,000 for a vacation, and the risk your income drops next month — optimally put 5,000 to early repayment, 2,000 to reserve, 1,000 to the goal. You save 1,200 ₽ in interest and don't go negative.\" I.e. it accounts for all your debts, goals, mortgages, taxes, payments and reserve at once, not separately.",
          choices: ["Yes, this is exactly what's missing",
                    "Interesting, but depends on how transparent it is",
                    "No, I prefer to decide myself"] },
        { type: "checkbox", other: true,
          title: "What should such a tool have for you to use it? (select all that apply)",
          choices: ["Sees all my debts, goals and balance in one place",
                    "Tells me how much free money I really have given all payments",
                    "Warns me in advance that money will run short",
                    "Gives specific advice with an explanation of why",
                    "Shows what happens if I do it one way or another"] },
        { type: "checkbox",
          title: "What would make you trust a financial assistant's advice? (select all that apply)",
          choices: ["An explanation with numbers — why this action is more profitable",
                    "The ability to see alternatives and compare",
                    "Recommendations from other users / reviews",
                    "A transparent algorithm — I understand how it's calculated",
                    "Nothing would, I decide myself"] },
        { type: "checkbox",
          title: "On what device / in what format would it be more convenient to use such an assistant? (select all that apply)",
          choices: ["Mobile app (iOS/Android)", "Website via browser", "Telegram bot",
                    "Desktop / Web-app", "Doesn't matter, as long as it works"] },
        { type: "scale", low: 1, high: 7, leftLabel: "", rightLabel: "",
          title: "Please select 7 stars to confirm you're reading the statements." },
        { type: "radio",
          title: "How much would you be willing to pay per month for such a tool if it really helps?",
          choices: ["Up to 200 ₽/mo", "200–500 ₽/mo", "500–1000 ₽/mo",
                    "Willing to pay a one-time fee (e.g. 1500–3000 ₽)",
                    "Willing to pay a percentage of what I save/earn"] },
        { type: "radio",
          title: "Imagine two equally convenient systems, both giving financial advice. Which would you trust more?",
          choices: ["System A — AI-based (ChatGPT/Gemini/Claude). Understands free text, replies in a human way, but you don't see exactly how it calculates",
                    "System B — based on mathematical formulas. You see the calculations, criteria weights, explanations with numbers. But the interface is forms and buttons, no free dialogue",
                    "I'd trust both equally, as long as recommendations are sound",
                    "I wouldn't trust either"] },
        { type: "radio", required: true,
          title: "What matters more to you in a financial advisor?",
          choices: ["That it can understand complex questions in natural language",
                    "That I see the exact calculation logic and can verify it",
                    "Both are equally important", "Neither — what matters is the result"] },
        { type: "grid",
          title: "Would you trust an AI assistant with the following financial tasks?",
          help: "One oval per row.",
          rows: ["Explain an unclear financial term",
                 "Calculate the benefit of early loan repayment",
                 "Suggest how to split a bonus between debt and savings",
                 "Forecast how much money you'll have in 3 months",
                 "Decide for you and automatically transfer money"],
          columns: ["Yes", "No", "Not sure"] },
        { type: "paragraph",
          title: "(Optional) If you had a perfect financial assistant — describe in a sentence or two what it does. Which feature would be most important? (can skip)" }
      ]
    },
    {
      title: "Section 6. About you",
      help: "A final short block. All answers are anonymous and used only for analysis.",
      items: [
        { type: "radio", required: true, title: "Your gender, please",
          choices: ["Male", "Female"] },
        { type: "radio", required: true, title: "Your age, please",
          choices: ["Under 18", "18–22", "23–27", "28–35", "36–45", "46–60", "61+"] },
        { type: "radio", required: true, other: true, title: "Your education?",
          choices: ["Didn't finish school", "Secondary general education",
                    "Vocational / technical education", "Incomplete higher education",
                    "Higher education", "Academic degree"] },
        { type: "radio", required: true, other: true, title: "Your marital status?",
          choices: ["Married", "In a relationship", "Not in a relationship"] },
        { type: "checkbox", required: true, title: "Your status? (select all that apply)",
          choices: ["Student", "Employed", "Entrepreneur", "On parental leave / not working",
                    "Parent with dependent children", "Freelancer / self-employed"] },
        { type: "radio", required: true, title: "Where do you live?",
          choices: ["Moscow / St. Petersburg", "A million-plus city", "A city under 1 million",
                    "A small town / village"] },
        { type: "radio", required: true, title: "What is your approximate monthly income?",
          choices: ["Up to 30,000 ₽", "30,000–60,000 ₽", "60,000–100,000 ₽",
                    "100,000–200,000 ₽", "200,000–300,000 ₽", "More than 300,000 ₽"] },
        { type: "radio", required: true, title: "Rate your material situation",
          choices: ["Not enough money even for food", "Enough only for food",
                    "Enough for clothes and food, but not electronics",
                    "Enough for electronics, but not major purchases",
                    "I can afford major purchases (apartment, car, vacation)"] }
      ]
    },
    {
      title: "Section 7. Finally",
      help: "Thank you for completing the survey!",
      items: [
        { type: "text",
          title: "If you'd like to be first to know when the app launches — leave your email. I'll personally write when I launch the prototype.",
          help: "Email is used only for a single launch notification. Not shared with third parties." },
        { type: "paragraph",
          title: "(Optional) What important thing did I not ask, but you'd like to say about this topic? (can skip)",
          help: "Share your experience with financial assistants, comments/ideas, or your vision of the ideal advisor. Anything you think is worth writing." }
      ]
    }
  ]
};

function createFinpilotSurveyEN() {
  var form = FormApp.create(SURVEY.title);
  form.setDescription(SURVEY.description);
  form.setProgressBar(true);
  form.setCollectEmail(false);

  SURVEY.sections.forEach(function (section) {
    var page = form.addPageBreakItem().setTitle(section.title);
    if (section.help) page.setHelpText(section.help);
    section.items.forEach(function (q) { addItem(form, q); });
  });

  Logger.log("Published URL: " + form.getPublishedUrl());
  Logger.log("Edit URL: " + form.getEditUrl());
}

function addItem(form, q) {
  var it;
  switch (q.type) {
    case "radio":
      it = form.addMultipleChoiceItem().setTitle(q.title).setChoiceValues(q.choices);
      if (q.other) it.showOtherOption(true);
      break;
    case "checkbox":
      it = form.addCheckboxItem().setTitle(q.title).setChoiceValues(q.choices);
      if (q.other) it.showOtherOption(true);
      break;
    case "scale":
      it = form.addScaleItem().setTitle(q.title).setBounds(q.low, q.high);
      if (q.leftLabel || q.rightLabel) it.setLabels(q.leftLabel || "", q.rightLabel || "");
      break;
    case "grid":
      it = form.addGridItem().setTitle(q.title).setRows(q.rows).setColumns(q.columns);
      break;
    case "text":
      it = form.addTextItem().setTitle(q.title);
      break;
    case "paragraph":
      it = form.addParagraphTextItem().setTitle(q.title);
      break;
    default:
      return;
  }
  if (q.help) it.setHelpText(q.help);
  if (q.required) it.setRequired(true);
}

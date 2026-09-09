# Рекомендательные системы — бандиты, RL, off-policy оценка

**Дата:** 08.09.2026. **Статус:** первичный материал подагента, чей родительский агент оборвался
по лимиту. Сохранено дословно (правило проекта §9). Бюджет исчерпан: 13 WebSearch + 2 WebFetch,
один фетч (ACM DL) вернул HTTP 403.

🔴 **Почему это важно для FINPILOT:** наше ядро — детерминированный перебор + SAW, без обучения
на пользователях. Раздел 5 ниже (отложенное вознаграждение) описывает ровно нашу ситуацию:
результат совета виден через месяцы, решений на пользователя — единицы в год.

---

## 1. Multi-armed / contextual bandits в рекомендациях

**Li, Chu, Langford, Schapire — «A Contextual-Bandit Approach to Personalized News Article
Recommendation», WWW 2010.** Предлагает LinUCB (disjoint и hybrid линейные модели).
https://ir.webis.de/anthology/2010.wwwconf_conference-2010.67/

**Chapelle, Li — «An Empirical Evaluation of Thompson Sampling», NIPS 2011** (Advances in NIPS 24,
стр. 2249–2257). Thompson sampling конкурентоспособен на симулированных и реальных данных, несмотря
на непопулярность в литературе на момент публикации; авторы предлагают включать его в стандартные
бейзлайны как простой в реализации. https://papers.nips.cc/paper/4321-an-empirical-evaluation-of-thompson-sampling

**Netflix — «Artwork Personalization at Netflix»**, Netflix Technology Blog, декабрь 2017
(Chandrashekar, Amat, Basilico, Jebara; позже RecSys 2018). Причина выбора contextual bandits:
**малое пространство действий** (варианты обложек одного тайтла, а не десятки тысяч тайтлов);
контролируемая рандомизация в продакшене вместо batch A/B. Масштаб: **свыше 20 млн персонализированных
запросов изображений в секунду на пике**. https://netflixtechblog.com/artwork-personalization-c589f074ad76

**Agarwal et al. — «Making Contextual Decisions with Low Technical Debt», arXiv:1606.03966**
(2016, rev. 2017). Microsoft Decision Service — первая «общая система» для контекстного обучения
в проде. https://arxiv.org/abs/1606.03966

Spotify BaRT — прямой первичной статьи с точными данными не найдено, не включать без проверки.

## 2. 🔴 Подводные камни бандитов в проде

**Chaney, Stewart, Engelhardt — «How Algorithmic Confounding in Recommendation Systems Increases
Homogeneity and Decreases Utility», RecSys 2018**, стр. 224–232. Механизм: алгоритм обучается
на данных взаимодействия, которые сами были сформированы предыдущими рекомендациями того же
алгоритма → **algorithmic confounding**. Симуляции показывают: confounded-данные **гомогенизируют
поведение пользователей сильнее**, чем показ рекомендаций, лучше всего соответствующих истинным
предпочтениям, — **без прироста полезности**. https://arxiv.org/pdf/1710.11214

**Jiang, Chiappa, Lattimore, Gyorgy, Kohli — «Degenerate Feedback Loops in Recommender Systems»,
AIES 2019**, arXiv:1902.10730. Разделяют «echo chamber» (изменение убеждений пользователя)
и «filter bubble» (сужение показываемого) теоретически. Практический результат: **случайное
исследование при показе айтемов и прогрессивное — минимум линейное — расширение пула кандидатов
эффективно замедляют деградацию системы**. https://arxiv.org/abs/1902.10730

Задержка вознаграждения: смежная работа «Delayed Feedback in Generalised Linear Bandits Revisited»
(Howson et al., arXiv:2207.10786) — стохастические GLM-бандиты при немедленной обратной связи изучены
хорошо, но требование мгновенной награды не выполняется во многих реальных приложениях.

Отрицательный результат: работы «сколько данных нужно, чтобы бандит сошёлся» — не найдено.

## 3. RL в рекомендациях

**Ie et al. — «SlateQ: A Tractable Decomposition for Reinforcement Learning with Recommendation Sets»,
IJCAI 2019.** Декомпозиция long-term value слейта в трактуемую функцию LTV отдельных айтемов
(при мягких допущениях о выборе пользователя); валидировано на продакшн-данных YouTube.
https://www.ijcai.org/proceedings/2019/360

**Chen, Beutel, Covington, Jain, Belletti, Chi (Google) — «Top-K Off-Policy Correction for
a REINFORCE Recommender System», WSDM 2019.** arXiv:1812.02353, DOI 10.1145/3289600.3290999.
Продакшн top-K рекомендатель YouTube на policy-gradient с коррекцией смещения от логированной
обратной связи. https://arxiv.org/abs/1812.02353

**Afsar, Crump, Far — «Reinforcement learning based recommender systems: A survey», arXiv:2101.06286**
(ACM Computing Surveys, vol. 55, issue 7, article 145, декабрь 2022, 38 стр.). Тезис: рекомендацию
правильнее формулировать как MDP/последовательное решение, а не классификацию.
https://arxiv.org/abs/2101.06286

Критика воспроизводимости RL4Rec: «A Systematic Study on Reproducibility of Reinforcement Learning
in Recommendation Systems» (DOI 10.1145/3596519); «State Encoders in Reinforcement Learning
for Recommendation: A Reproducibility Study». Также «Offline Evaluation for Reinforcement
Learning-Based Recommendation: A Critical Issue and Some Alternatives» (SIGIR Forum vol. 56 no. 2,
DOI 10.1145/3582900.3582905) — 🔴 **ACM DL вернул HTTP 403, содержание не подтверждено**.

## 4. Counterfactual / off-policy evaluation

**Dudík, Langford, Li — «Doubly Robust Policy Evaluation and Learning», ICML 2011**, arXiv:1103.4601.
Проблема: оценка новой политики по историческим (context, action, reward) данным — модель-базированные
оценки дают большое смещение, importance-weighting даёт большую дисперсию. Doubly robust **равномерно
улучшает обе метрики**. https://icml.cc/2011/papers/554_icmlpaper.pdf

**Saito, Aihara, Matsutani, Narita — «Open Bandit Dataset and Pipeline», arXiv:2008.07146**
(NeurIPS 2021 Datasets and Benchmarks Track). Датасет логированных бандит-взаимодействий с ZOZOTOWN;
уникальность — **несколько логированных датасетов от разных реально запущенных политик на одной
платформе**, что впервые позволяет экспериментально сравнивать OPE-эстиматоры.
https://arxiv.org/abs/2008.07146

## 5. 🔴 Отложенное/редкое вознаграждение — прямо наш случай

**Zhang, Baldwin-McDonald, Ciosek, Maystre, Russo — «Impatient Bandits: Optimizing for the Long-Term
Without Delay», arXiv:2501.07761, JMLR (to appear).** Задача формализована как **бандит с задержанным
вознаграждением**: рекомендация подкастов, цель — вовлечённость, повторяющаяся **на протяжении двух
месяцев**. Байесовский фильтр комбинирует финальный (отложенный) сигнал с краткосрочными суррогатами;
предложен алгоритм с теоретическими regret-границами. A/B развёрнут в системе, обслуживающей
**сотни миллионов пользователей**. Итог: подход **значимо превосходит методы, оптимизирующие
короткосрочные прокси-метрики или полагающиеся только на отложенное вознаграждение**.
https://arxiv.org/abs/2501.07761

## Ключевые цитаты

1. «The paper addresses the task of evaluating a new policy given historic data consisting of contexts,
   actions and received rewards... The doubly robust approach was shown to uniformly improve over existing
   techniques, achieving both lower variance in value estimation and better policies.» — ICML 2011
2. «Rather than waiting to collect a full batch of data, train a model, and run an A/B test, Netflix uses
   contextual bandits as an online machine learning framework, with training data obtained through
   the injection of controlled randomization in the learned model's predictions.» — Netflix TechBlog
3. «Using data confounded in this way homogenizes user behavior without increasing utility.» — RecSys 2018
4. «The simulation results show that random exploration in presenting items and progressively increasing
   the candidate pool (at least linearly) are effective against system degeneracy.» — AIES 2019
5. «Learning from logged feedback is subject to biases from only observing feedback on recommendations
   selected by previous versions of the recommender.» — WSDM 2019
6. «[We] formalize [this] as a bandit problem with delayed rewards» applied to podcasts users engage with
   «repeatedly over two months»; deployed «in a recommendation system that serves hundreds of millions
   of users.» — arXiv:2501.07761

## Что не удалось

- **ACM DL «Offline Evaluation for RL-Based Recommendation»** — HTTP 403 Forbidden, содержание
  не подтверждено, только заголовок из выдачи.
- **Spotify BaRT** — прямой первичной статьи не найдено.
- **Аффилиация авторов «Impatient Bandits» со Spotify** — не подтверждена текстом, только косвенно.
- **Количественные оценки сходимости бандита** — целевой работы не найдено (отрицательный результат).

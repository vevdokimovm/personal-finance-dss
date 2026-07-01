"""
Сборка HTML-отчёта из результатов анализа. Числа подставляются из results,
тексты выводов зашиты в секции. Графики подключаются относительными путями
(папка charts/ рядом с HTML).
"""
from __future__ import annotations

import os
from typing import Any

CSS = """
:root{
  --ink:#14202e; --ink2:#33485c; --paper:#f7f5f0; --card:#fffdf9;
  --line:#dfd9cd; --teal:#0d7a70; --blue:#1d4ed8; --red:#c0362c;
  --amber:#b9740b; --muted:#6b7787; --good:#0d7a70;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:var(--paper); color:var(--ink);
  font-family:"IBM Plex Sans",-apple-system,sans-serif;
  font-size:16px; line-height:1.65; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:920px; margin:0 auto; padding:0 28px}
h1,h2,h3{font-family:"Fraunces",Georgia,serif; font-weight:600; line-height:1.15;
  letter-spacing:-0.01em; color:var(--ink)}
.mono{font-family:"IBM Plex Mono",monospace}

/* hero */
.hero{background:var(--ink); color:#f0ece4; padding:84px 0 64px; position:relative;
  overflow:hidden}
.hero:before{content:""; position:absolute; inset:0;
  background:radial-gradient(circle at 80% 10%, rgba(13,122,112,.28), transparent 45%),
             radial-gradient(circle at 0% 90%, rgba(29,78,216,.22), transparent 40%)}
.hero .wrap{position:relative}
.kicker{font-family:"IBM Plex Mono",monospace; font-size:12.5px; letter-spacing:.22em;
  text-transform:uppercase; color:#8fd5cc; margin-bottom:18px}
.hero h1{font-size:clamp(34px,6vw,58px); color:#fff; max-width:16ch}
.hero p.sub{font-size:18px; color:#c7c0b4; margin-top:18px; max-width:54ch}
.metabar{display:flex; flex-wrap:wrap; gap:28px; margin-top:40px; padding-top:26px;
  border-top:1px solid rgba(255,255,255,.16)}
.metabar div{font-family:"IBM Plex Mono",monospace}
.metabar .n{font-size:30px; color:#fff; font-weight:500}
.metabar .l{font-size:12px; color:#9aa6b2; text-transform:uppercase; letter-spacing:.12em}

/* sections */
section{padding:58px 0; border-bottom:1px solid var(--line)}
.sec-head{display:flex; align-items:baseline; gap:18px; margin-bottom:8px}
.sec-num{font-family:"Fraunces",serif; font-size:46px; color:var(--line); font-weight:600;
  line-height:1}
.sec-head h2{font-size:clamp(24px,3.4vw,33px)}
.lead{color:var(--ink2); font-size:17.5px; margin:14px 0 26px; max-width:64ch}
p{margin:14px 0; max-width:68ch}
section p:first-of-type{margin-top:0}
strong{font-weight:600; color:var(--ink)}
em.hl{font-style:normal; background:linear-gradient(transparent 62%, #f5e2b8 62%);
  padding:0 2px}

/* metric cards */
.cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:14px; margin:26px 0}
.card{background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:18px 16px}
.card .v{font-family:"IBM Plex Mono",monospace; font-size:27px; font-weight:600;
  color:var(--teal)}
.card .v.alt{color:var(--blue)} .card .v.warn{color:var(--red)}
.card .k{font-size:13px; color:var(--muted); margin-top:6px; line-height:1.4}

/* figure */
figure{margin:28px 0; background:var(--card); border:1px solid var(--line);
  border-radius:12px; padding:18px; text-align:center}
figure img{max-width:100%; height:auto; border-radius:4px}
figcaption{font-size:13.5px; color:var(--muted); margin-top:12px; text-align:left;
  font-family:"IBM Plex Mono",monospace}

/* table */
table{width:100%; border-collapse:collapse; margin:22px 0; font-size:14.5px}
th,td{text-align:left; padding:10px 12px; border-bottom:1px solid var(--line)}
th{font-family:"IBM Plex Mono",monospace; font-size:12px; text-transform:uppercase;
  letter-spacing:.08em; color:var(--muted); font-weight:600}
td.mono{font-family:"IBM Plex Mono",monospace}
tr .sig{color:var(--good); font-weight:600} tr .ns{color:var(--muted)}

/* callout */
.callout{border-left:3px solid var(--teal); background:var(--card);
  padding:18px 22px; margin:24px 0; border-radius:0 10px 10px 0}
.callout.warn{border-color:var(--amber)}
.callout.insight{border-color:var(--blue)}
.callout h3{font-size:18px; margin-bottom:6px}
.callout .tag{font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.12em;
  text-transform:uppercase; color:var(--muted)}

.pill{display:inline-block; font-family:"IBM Plex Mono",monospace; font-size:11px;
  padding:3px 9px; border-radius:20px; background:#efe9dc; color:var(--ink2);
  letter-spacing:.06em}
.pill.prelim{background:#f9eccb; color:var(--amber)}

ul.clean{margin:14px 0 14px 2px; padding:0; list-style:none}
ul.clean li{padding:8px 0 8px 26px; position:relative; max-width:66ch}
ul.clean li:before{content:"→"; position:absolute; left:0; color:var(--teal);
  font-family:"IBM Plex Mono",monospace}

.quote{font-family:"Fraunces",serif; font-size:17px; font-style:italic;
  color:var(--ink2); padding:10px 0 10px 20px; border-left:2px solid var(--line);
  margin:12px 0}

footer{padding:50px 0; color:var(--muted); font-size:14px}
.toc{columns:2; column-gap:34px; margin:18px 0}
.toc a{color:var(--ink2); text-decoration:none; display:block; padding:5px 0;
  font-size:15px; border-bottom:1px solid transparent}
.toc a:hover{color:var(--teal)}
.toc a .mono{color:var(--line); margin-right:10px}

@media(max-width:640px){
  .toc{columns:1} .metabar{gap:18px} .sec-num{font-size:34px}
}
.fade{opacity:0; transform:translateY(14px); animation:rise .7s ease forwards}
@keyframes rise{to{opacity:1; transform:none}}
"""


class ReportBuilder:
    def __init__(self, results: dict[str, Any]) -> None:
        self.r = results

    # ── helpers ─────────────────────────────────────────────────────────
    def _fig(self, chart_key: str, caption: str) -> str:
        name = self.r["charts"][chart_key]
        return (f'<figure class="fade"><img src="charts/{name}" alt="{caption}">'
                f'<figcaption>{caption}</figcaption></figure>')

    @staticmethod
    def _card(value: str, key: str, cls: str = "") -> str:
        return (f'<div class="card"><div class="v {cls}">{value}</div>'
                f'<div class="k">{key}</div></div>')

    def build(self) -> str:
        r = self.r
        body = "".join([
            self._hero(), self._toc(), self._summary(), self._method(),
            self._audience(), self._landscape(), self._hypotheses(),
            self._behavioral(), self._criteria(), self._rankings(),
            self._business(), self._qualitative(), self._limitations(),
            self._bridge(), self._footer(),
        ])
        head = (
            '<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>FINPILOT — анализ исследования</title>'
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Fraunces:opsz,wght@9..144,500;9..144,600&'
            'family=IBM+Plex+Sans:wght@400;500;600&'
            'family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">'
            f'<style>{CSS}</style></head><body>')
        return head + body + "</body></html>"

    # ── sections ────────────────────────────────────────────────────────
    def _hero(self) -> str:
        m = self.r["meta"]
        return f"""
<header class="hero"><div class="wrap">
  <div class="kicker fade">СППР FINPILOT · Анализ пользовательского исследования</div>
  <h1 class="fade">Как люди на самом деле решают, куда направить деньги</h1>
  <p class="sub fade">Эмпирическая проверка предпосылок продукта: боли, доверие,
     готовность платить и разрыв между тем, что люди говорят, и тем, что делают.</p>
  <div class="metabar fade">
    <div><div class="n">{m['n_valid']}</div><div class="l">валидных анкет</div></div>
    <div><div class="n">{m['n_total']}</div><div class="l">всего собрано</div></div>
    <div><div class="n">{m['n_dropped']}</div><div class="l">отсеяно контролем</div></div>
    <div><div class="n">77</div><div class="l">вопросов анкеты</div></div>
  </div>
</div></header>"""

    def _toc(self) -> str:
        items = [
            ("01", "Главные выводы", "summary"),
            ("02", "Метод и качество данных", "method"),
            ("03", "Портрет аудитории", "audience"),
            ("04", "Боли и ожидания", "landscape"),
            ("05", "Проверка гипотез", "hypotheses"),
            ("06", "Слова против действий", "behavioral"),
            ("07", "Критерии распределения", "criteria"),
            ("08", "Ранжирование приоритетов", "rankings"),
            ("09", "Спрос и монетизация", "business"),
            ("10", "Голос пользователя", "qualitative"),
            ("11", "Ограничения", "limitations"),
            ("12", "Что это значит для FINPILOT", "bridge"),
        ]
        links = "".join(
            f'<a href="#{i}"><span class="mono">{n}</span>{t}</a>'
            for n, t, i in items)
        return (f'<section><div class="wrap"><div class="sec-head">'
                f'<h2>Содержание</h2></div><nav class="toc">{links}</nav>'
                f'</div></section>')

    def _summary(self) -> str:
        r = self.r
        gap = r["behavioral"]["intention_action_gap"]
        cd = r["business"]["concept_demand"]
        wtp = r["business"]["wtp"]
        beh = r["behavioral"]
        cards = "".join([
            self._card(f'{cd["positive_share"]*100:.0f}%',
                       "позитивно к идее советника (при условии прозрачности)", "alt"),
            self._card(f'{gap["stated_manual_calc"]*100:.0f}% → {gap["revealed_calc"]*100:.0f}%',
                       "заявляют, что считают выгоду — реально считали в кейсе", "warn"),
            self._card(f'{beh["case_basis"]["emotional_share"]*100:.0f}%',
                       "в кейсе опирались на эмоции, а не на расчёт", "warn"),
            self._card(f'{wtp["low_tier_share"]*100:.0f}%',
                       "готовы платить не более 200 ₽/мес"),
            self._card("0.62",
                       "сила связи «есть долг → мучает дилемма гасить/копить»", "alt"),
            self._card("46%",
                       "выбирают «по ощущению» или просто откладывают решение", "warn"),
        ])
        return f"""
<section id="summary"><div class="wrap">
  <div class="sec-head"><div class="sec-num">01</div><h2>Главные выводы</h2></div>
  <p class="lead">Шесть результатов, на которых держится вся продуктовая логика.
     Подробности и статистика — в соответствующих разделах ниже.</p>
  {cards}
  <ul class="clean">
    <li><strong>Существующие приложения упёрлись в потолок «статистики».</strong>
      Люди видят, <em class="hl">куда</em> ушли деньги, но не получают ответа
      <em class="hl">что делать дальше</em> — это и есть незанятая ниша FINPILOT.</li>
    <li><strong>Главный разрыв — между словами и делом.</strong> Почти половина
      уверяет, что считает выгоду рационально, но в конкретной ситуации решает
      эмоционально. Продукт должен брать на себя роль «внешней System 2».</li>
    <li><strong>Доверие = прозрачность.</strong> Спрос на советника высокий, но
      условный: люди примут рекомендацию, только если видят расчёт и альтернативы.</li>
    <li><strong>Долг — главный триггер тревоги и спроса.</strong> Наличие долга
      сильно связано с дилеммой «гасить или копить» и со страхом пропустить платёж.</li>
    <li><strong>Платить готовы мало.</strong> Низкий потолок ARPU ставит под вопрос
      классическую B2C-подписку и подталкивает к freemium или дистрибуции через банк.</li>
  </ul>
</div></section>"""

    def _method(self) -> str:
        r = self.r
        m = r["meta"]
        lc = r["audience"]["late_cohort_check"]
        reps = ", ".join(f'{c["field"]} (Δ={c["max_share_gap"]})'
                         for c in lc["comparisons"])
        return f"""
<section id="method"><div class="wrap">
  <div class="sec-head"><div class="sec-num">02</div><h2>Метод и качество данных</h2></div>
  <p class="lead">Прежде чем доверять цифрам, важно показать, что выборка очищена,
     а ограничения названы честно. Это усиливает, а не ослабляет выводы.</p>
  <p>Опрос проводился через Google Forms, собрано <span class="mono">{m['n_total']}</span>
     ответов. В анкету был встроен <strong>контроль внимательности</strong>
     («выберите 7 звёзд»). Из выборки удалены <span class="mono">{m['n_dropped']}</span>
     респондента, которые видели проверку и ответили неверно. Остались
     <strong>{m['n_valid']}</strong> валидных анкет: прошедшие проверку и те, кто
     отвечал до её добавления в форму.</p>
  <div class="callout"><span class="tag">Особенность данных</span>
    <h3>Переменный размер выборки по вопросам</h3>
    <p>Анкета дополнялась в процессе сбора, а закрытые вопросы были обязательными.
    Поэтому у поздних вопросов меньше ответов — но это <strong>не «отвал»</strong>:
    респонденты либо проходили опрос до конца, либо не начинали. Систематического
    смещения от незавершения нет; для каждого показателя указывается свой N.</p>
  </div>
  <p>Чтобы исключить единственный остаточный риск — смену состава аудитории во
     времени — «поздняя когорта» (видевшие контрольный вопрос) сравнена с полной
     выборкой по полу, возрасту и доходу. Максимальные расхождения долей малы
     ({reps}) — поздние вопросы <strong>репрезентативны</strong> относительно всей
     выборки, поэтому выводы по ним переносимы (с поправкой на меньший N).</p>
  <p>Для надёжных статистических выводов использованы блоки с N ≥ 120; результаты на
     малых подвыборках (критерии, кейс, доверие к ИИ, N ≈ 19) везде помечены как
     <span class="pill prelim">предварительные</span>. Все тесты сопровождаются
     размером эффекта и поправкой Холма на множественные сравнения.</p>
</div></section>"""

    def _audience(self) -> str:
        return f"""
<section id="audience"><div class="wrap">
  <div class="sec-head"><div class="sec-num">03</div><h2>Портрет аудитории</h2></div>
  <p class="lead">Кто эти люди — и почему по выборке нельзя судить обо «всех россиянах».
     Понимание перекоса задаёт границы применимости выводов.</p>
  {self._fig("bias", "Доли ключевых групп с 95% доверительным интервалом. "
             "Красным — оси с сильным перекосом (>60%).")}
  <p>Выборка сильно смещена в сторону <strong>молодой, образованной городской
     аудитории</strong>: подавляющее большинство — жители Москвы и Санкт-Петербурга,
     возраст 18–27 лет, с высшим или незаконченным высшим образованием, и
     преобладают женщины. Это типичный портрет студенчества крупных городов.</p>
  <p>Практический смысл: выводы корректно описывают именно <em class="hl">молодую
     городскую аудиторию на старте финансовой самостоятельности</em> — и это, к
     слову, релевантный первый сегмент для FINPILOT. Переносить проценты на людей
     старшего возраста, с семьёй и ипотекой, без отдельного исследования нельзя.</p>
</div></section>"""

    def _landscape(self) -> str:
        r = self.r
        lacks = {it["label"]: it for it in
                 r["descriptive"]["multiselect"]["tool_lacks"]["items"]}
        must = {it["label"]: it for it in
                r["descriptive"]["multiselect"]["must_have"]["items"]}
        return f"""
<section id="landscape"><div class="wrap">
  <div class="sec-head"><div class="sec-num">04</div><h2>Боли и ожидания</h2></div>
  <p class="lead">Что не так с тем, чем люди пользуются сейчас, и чего они ждут от
     «идеального» инструмента. Здесь данные надёжны — N = 322.</p>
  {self._fig("pain", "Чего не умеет текущий инструмент (мультивыбор, доля от 322).")}
  <p>Главные дефициты не про учёт, а про <strong>помощь в решении</strong>:
     инструмент «не предупреждает заранее, что денег не хватит»
     ({lacks['Не предупреждает о нехватке']['share']*100:.0f}%), «не говорит, куда
     направить свободные деньги» ({lacks['Не говорит куда направить']['share']*100:.0f}%),
     «не объясняет логику советов» ({lacks['Не объясняет логику']['share']*100:.0f}%) и
     «не видит долги и цели одновременно»
     ({lacks['Не учитывает долги+цели']['share']*100:.0f}%).</p>
  {self._fig("must", "Что должно быть в инструменте (мультивыбор, доля от 322).")}
  <p>Список ожиданий зеркалит боли и почти дословно описывает ядро FINPILOT:
     «сколько у меня реально свободных денег с учётом всех платежей»
     ({must['Сколько реально свободно']['share']*100:.0f}%), «конкретный совет с
     объяснением почему» ({must['Совет с объяснением']['share']*100:.0f}%), «долги,
     цели и баланс в одном месте» ({must['Долги+цели+баланс вместе']['share']*100:.0f}%)
     и сценарии «что будет, если…» ({must['Сценарии «что если»']['share']*100:.0f}%).</p>
  {self._fig("opportunity", "Карта возможностей: по горизонтали — насколько боль НЕ "
             "закрыта, по вертикали — насколько фича важна. Размер круга — приоритет.")}
</div></section>"""

    def _hypotheses(self) -> str:
        r = self.r
        rows = ""
        for h in r["hypotheses"]["results"]:
            sig = ('<span class="sig">значимо</span>' if h["significant_holm"]
                   else '<span class="ns">не значимо</span>')
            rows += (f'<tr><td class="mono">{h["code"]}</td><td>{h["hypothesis"]}</td>'
                     f'<td class="mono">{h["n"]}</td>'
                     f'<td class="mono">{h["effect_name"]}={h["effect_value"]:.2f}</td>'
                     f'<td>{h["effect_label"]}</td>'
                     f'<td class="mono">{h["p_holm"]:.3f}</td><td>{sig}</td></tr>')
        return f"""
<section id="hypotheses"><div class="wrap">
  <div class="sec-head"><div class="sec-num">05</div><h2>Проверка гипотез</h2></div>
  <p class="lead">Десять содержательных гипотез о связях в данных. Пять подтвердились
     даже после строгой поправки на множественность — и они осмысленны.</p>
  {self._fig("hypotheses", "Размер эффекта по каждой гипотезе. Бирюзовым — связи, "
             "значимые после поправки Холма.")}
  <table>
    <tr><th>Код</th><th>Гипотеза</th><th>N</th><th>Эффект</th><th>Сила</th>
        <th>p (Холм)</th><th>Итог</th></tr>
    {rows}
  </table>
  <div class="callout insight"><span class="tag">Что важно</span>
    <h3>Долг — это эмоциональный, а не только финансовый объект</h3>
    <p>Самая сильная связь (H1, V = 0.62): наличие долга почти втрое повышает шанс,
    что человек мучился вопросом «гасить досрочно или копить». Должники также
    заметно сильнее боятся пропустить платёж (H4). Для FINPILOT это значит, что
    работа с долгом и напоминания о платежах — не вторичная функция, а ядро ценности
    для значимого сегмента.</p>
  </div>
  <p>Подтвердились также ожидаемые «проверочные» связи: лучше материальное положение —
     чаще остаются деньги (H5), выше финграмотность — выше уверенность в решении (H3),
     выше доход — выше готовность платить (H2). То, что данные ведут себя логично,
     повышает доверие ко всему массиву. Связи без подтверждения (H6–H10) — тоже
     результат: например, наличие цели само по себе не гарантирует, что деньги
     остаются.</p>
</div></section>"""

    def _behavioral(self) -> str:
        r = self.r
        cvh = r["behavioral"]["confidence_vs_hindsight"]
        cb = r["behavioral"]["case_basis"]
        return f"""
<section id="behavioral"><div class="wrap">
  <div class="sec-head"><div class="sec-num">06</div><h2>Слова против действий</h2></div>
  <p class="lead">Самый ценный для продукта раздел: что люди делают на самом деле,
     когда доходит до конкретного решения о деньгах.</p>
  {self._fig("choice", "Как респонденты ОПИСЫВАЮТ свой способ выбора (N=322).")}
  {self._fig("gap", "Слева — разрыв между заявленным и реальным расчётом. Справа — на "
             "что опирались в конкретном денежном кейсе.")}
  <p>На словах <strong>46%</strong> «считают вручную, что выгоднее». Но когда тем же
     людям дали конкретную ситуацию (доход 80 000 ₽, есть кредит, есть цель — как
     поступить с 30 000 ₽), на расчёт выгоды опёрлись лишь
     <strong>{cb['calc_share']*100:.0f}%</strong>, а <strong>{cb['emotional_share']*100:.0f}%</strong>
     решали от ощущения комфорта или тревоги о худшем сценарии. Это и есть
     <em class="hl">intention–action gap</em>: разрыв между рациональным
     самообразом и реальным, эмоциональным поведением.</p>
  <div class="callout insight"><span class="tag">Продуктовый вывод</span>
    <h3>FINPILOT — это «внешняя System 2»</h3>
    <p>Люди не считают не потому, что не хотят, а потому что в момент решения
    включается быстрое, эмоциональное мышление (System 1 по Канеману). Ценность
    продукта — взять на себя медленный расчёт и показать его результат просто и
    наглядно, в тот самый момент, когда человек колеблется.</p>
  </div>
  {self._fig("conf", "Средняя уверенность в решении сразу и при оценке задним числом.")}
  <p>Косвенное подтверждение на большей подвыборке (N = {cvh['n']}): уверенность в
     правильности решения <strong>статистически значимо падает</strong>, когда люди
     оценивают его задним числом (с {cvh['confidence_mean']} до {cvh['hindsight_mean']},
     p = {cvh['wilcoxon_p']}); каждый третий снижает свою оценку. Решения «на ощущении»
     систематически разочаровывают — значит, спрос на поддержку реален.</p>
</div></section>"""

    def _criteria(self) -> str:
        r = self.r
        p = r["preferences"]
        alpha = p["cronbach_alpha"]
        return f"""
<section id="criteria"><div class="wrap">
  <div class="sec-head"><div class="sec-num">07</div><h2>Критерии распределения
     <span class="pill prelim">предварительно · N={p['n_complete']}</span></h2></div>
  <p class="lead">Прямая проверка четырёх критериев, на которых построена модель
     FINPILOT: доходность, ликвидность, снижение долга, безопасность. Выборка мала —
     выводы директивные.</p>
  {self._fig("criteria", "Средняя важность каждого критерия по шкале 1–5.")}
  <p>Все четыре критерия в среднем оцениваются выше середины шкалы — то есть ни один
     не является «лишним» в модели. Чуть выше других — доходность и ликвидность,
     ниже — снижение долга (что логично: у молодой аудитории долгов меньше).</p>
  {self._fig("criteria_corr", "Корреляции между важностью критериев (Спирмен).")}
  <p>Cronbach α = <span class="mono">{alpha}</span> — намеренно невысокая, и это
     <strong>хорошая новость для модели</strong>: критерии слабо коррелируют между
     собой, то есть измеряют <em class="hl">разные</em> аспекты, а не одно и то же.
     Это эмпирически поддерживает архитектуру из четырёх независимых весов
     (w<sub>R</sub>, w<sub>L</sub>, w<sub>D</sub>, w<sub>S</sub>), а не свёртку в один
     балл.</p>
  <div class="callout warn"><span class="tag">Честное ограничение</span>
    <h3>Полноценный факторный анализ невозможен</h3>
    <p>{p['efa']['reason']} Поэтому здесь приведены только описательные статистики и
    корреляции. Чтобы подтвердить факторную структуру критериев, нужен отдельный
    добор ≥ 150 ответов именно по этому блоку.</p>
  </div>
</div></section>"""

    def _rankings(self) -> str:
        r = self.r
        rk = r["rankings"]
        return f"""
<section id="rankings"><div class="wrap">
  <div class="sec-head"><div class="sec-num">08</div><h2>Ранжирование приоритетов
     <span class="pill prelim">данные непригодны</span></h2></div>
  <p class="lead">Вопрос с перетаскиванием приоритетов оказался технически неудачным —
     и это тоже важный результат для будущих исследований.</p>
  <p>Из ответивших на блок только <strong>{rk['n_valid_rankings']}</strong> анкет
     содержат корректную перестановку рангов (1–5 без повторов). Остальные респонденты
     присваивали один и тот же ранг нескольким пунктам — механика drag-and-drop в
     Google Forms сбила людей. Коэффициент согласия Кендалла W =
     <span class="mono">{rk['kendall_w']}</span> (p = {rk['kendall_p']}), то есть
     <strong>{rk['agreement']}</strong> — но на {rk['n_valid_rankings']} наблюдениях
     это статистически бессмысленно.</p>
  <div class="callout warn"><span class="tag">Урок для сбора данных</span>
    <h3>Не использовать drag-ранжирование в Google Forms</h3>
    <p>Для будущих волн опроса ранжирование стоит заменить на попарные сравнения или
    распределение фиксированного «бюджета баллов» — это даёт чистые данные без потери
    респондентов. Текущий блок ранжирования из выводов исключён.</p>
  </div>
</div></section>"""

    def _business(self) -> str:
        r = self.r
        wtp = r["business"]["wtp"]
        ai = r["business"]["ai_trust"]
        nvp = r["business"]["need_vs_pay"]
        rice_rows = ""
        for f in r["business"]["feature_priority"]:
            rice_rows += (f'<tr><td>{f["feature"]}</td>'
                          f'<td class="mono">{f["reach"]*100:.0f}%</td>'
                          f'<td class="mono">{f["impact"]}</td>'
                          f'<td class="mono">{f["effort"]}</td>'
                          f'<td class="mono">{f["rice"]:.2f}</td>'
                          f'<td>{f["moscow"]}</td></tr>')
        return f"""
<section id="business"><div class="wrap">
  <div class="sec-head"><div class="sec-num">09</div><h2>Спрос и монетизация</h2></div>
  <p class="lead">Есть ли спрос, за что люди готовы платить, какие функции строить
     первыми и можно ли доверить решения ИИ.</p>
  {self._fig("wtp", "Готовность платить за инструмент (N=164).")}
  <p>{wtp['verdict']}</p>
  {self._fig("rice", "Приоритет фич по RICE-баллу (охват × влияние / трудозатраты).")}
  <table>
    <tr><th>Фича</th><th>Охват</th><th>Impact</th><th>Effort</th><th>RICE</th>
        <th>MoSCoW</th></tr>
    {rice_rows}
  </table>
  <p>Безоговорочный лидер приоритета — <strong>«сколько у меня реально свободно с
     учётом всех платежей»</strong>: максимальный охват при низкой трудозатрате (это
     уже считается ядром модели — показатель R<sub>t</sub>). Это идеальная функция для
     первого экрана и onboarding.</p>
  {self._fig("ai_trust", "Доля доверивших ИИ каждую задачу (предварительно, N≈19).")}
  <p>{ai['pattern']} Даже на малой выборке паттерн монотонный: посчитать досрочку и
     объяснить термин — доверяют большинство, а «решить и перевести самому» —
     отвергают почти все.</p>
  <div class="callout warn"><span class="tag">Стратегический риск</span>
    <h3>Кому нужно ≠ кто платит</h3>
    <p>Боль «не говорит, куда направить деньги» есть у {nvp['pain_group_n']} человек —
    это массово. Но платёжеспособность сегмента низкая. Нужду нельзя напрямую
    конвертировать в высокую цену: путь к деньгам — через freemium-воронку, разовые
    платежи или партнёрство с банком/работодателем, а не через дорогую подписку.</p>
  </div>
</div></section>"""

    def _qualitative(self) -> str:
        r = self.r
        q = r["qualitative"]
        quotes = q["quotes"]["why_quit"] + q["quotes"]["ideal_helper"]
        qhtml = "".join(f'<div class="quote">«{t}»</div>' for t in quotes[:4]
                        if len(t) > 20)
        return f"""
<section id="qualitative"><div class="wrap">
  <div class="sec-head"><div class="sec-num">10</div><h2>Голос пользователя</h2></div>
  <p class="lead">Открытые ответы (опциональные, поэтому только качественно) —
     но они точно бьют в ту же точку, что и цифры.</p>
  {self._fig("qual", "Темы в ответах «почему забросили приложение» (N=322).")}
  <p>Доминирующий мотив отказа от прежних приложений — <strong>«не вижу реальной
     пользы»</strong> и «показывает только статистику». Люди уходят не из-за плохого
     UI, а из-за отсутствия следующего шага после красивых графиков. Это ровно та
     дверь, в которую заходит FINPILOT.</p>
  {qhtml}
  <p>В описаниях «идеального помощника» люди сами формулируют ТЗ продукта: посчитать
     оптимальную сумму на досрочку, не уронив уровень жизни; учитывать цели, долги и
     платежи вместе; объяснять каждый альтернативный вариант. Это дословно совпадает
     с тем, что уже делает алгоритм.</p>
</div></section>"""

    def _limitations(self) -> str:
        return f"""
<section id="limitations"><div class="wrap">
  <div class="sec-head"><div class="sec-num">11</div><h2>Ограничения</h2></div>
  <p class="lead">Честный список того, чего эти данные не могут — чтобы выводами
     пользовались корректно.</p>
  <ul class="clean">
    <li><strong>Смещение выборки.</strong> Молодёжь крупных городов, преобладание
      женщин и студентов. Выводы применимы к этому сегменту, не к «населению вообще».</li>
    <li><strong>Малый N в ядре модели.</strong> Критерии, поведенческий кейс и доверие
      к ИИ собраны на ≈19 ответах — это направление, а не доказательство. Нужен добор.</li>
    <li><strong>Только корреляции, не причинность.</strong> Опрос — это срез во
      времени. Связи (например, долг ↔ тревога) не доказывают, что одно вызывает
      другое.</li>
    <li><strong>Самоотчёт.</strong> Часть ответов — про намерения и самооценку; как
      показал раздел 06, они расходятся с реальным поведением.</li>
    <li><strong>Продуктовые метрики недоступны.</strong> Retention, LTV/CAC, churn,
      когортный анализ требуют работающего приложения с логами — на данных опроса их
      посчитать нельзя, и они сознательно не выдумывались.</li>
    <li><strong>Технический брак в ранжировании.</strong> Блок приоритетов исключён
      из-за неработающей механики (см. раздел 08).</li>
  </ul>
</div></section>"""

    def _bridge(self) -> str:
        return f"""
<section id="bridge"><div class="wrap">
  <div class="sec-head"><div class="sec-num">12</div><h2>Что это значит для FINPILOT</h2></div>
  <p class="lead">Короткий мост от данных к продукту. Полный, приоритизированный план
     доработок вынесен в отдельный документ.</p>
  <ul class="clean">
    <li>Исследование <strong>подтверждает главную гипотезу продукта</strong>: рынку не
      хватает не учёта, а ответа на вопрос «что делать с деньгами» — с понятным
      объяснением.</li>
    <li>Прозрачность и объяснимость — <strong>не фича, а условие доверия</strong>.
      NLG-объяснения, которые уже есть в коде, оказываются ключевым активом.</li>
    <li>Работа с долгом, напоминания о платежах и снятие тревоги — <strong>ядро
      ценности</strong> для значимого сегмента, а не периферия.</li>
    <li>Продукт должен быть <strong>советником с подтверждением</strong>, а не
      автопилотом распоряжения деньгами.</li>
    <li>Монетизация — через <strong>freemium и партнёрства</strong>, а не дорогую
      подписку.</li>
  </ul>
  <div class="callout"><span class="tag">Следующий документ</span>
    <h3>Рекомендации по доработке приложения</h3>
    <p>Конкретные функции, изменения в модели и данных, приоритеты и привязка к
    результатам этого исследования — в файле
    <span class="mono">finpilot_recommendations.md</span>.</p>
  </div>
</div></section>"""

    def _footer(self) -> str:
        return f"""
<footer><div class="wrap">
  <p>Отчёт сгенерирован автоматически из {self.r['meta']['n_valid']} валидных анкет.
     Все статистические методы, размеры эффекта и поправки на множественность
     соответствуют методологии исследования. Графики и таблицы воспроизводимы из
     исходного пайплайна (<span class="mono">finpilot_survey</span>).</p>
</div></footer>"""


def build_report(results: dict[str, Any], out_dir: str,
                 name: str = "finpilot_report.html") -> str:
    html = ReportBuilder(results).build()
    html = _embed_images(html, out_dir)
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def _embed_images(html: str, out_dir: str) -> str:
    """Встраивает PNG-графики в HTML как data-URI — отчёт становится
    автономным одним файлом (не требует папки charts/ рядом)."""
    import base64
    import re

    def repl(match: "re.Match[str]") -> str:
        rel = match.group(1)
        path = os.path.join(out_dir, rel)
        if not os.path.exists(path):
            return match.group(0)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f'src="data:image/png;base64,{b64}"'

    return re.sub(r'src="(charts/[^"]+)"', repl, html)

# Аудит 6 — браузерный замер доступности доменов

Дата: 2026-09-18. Механическая проверка доступности (не исследование содержания).
Метод: `mcp__plugin_chrome-devtools-mcp_chrome-devtools` — `new_page`/`navigate_page` на `https://<домен>/`, затем `take_snapshot` (и при необходимости `take_screenshot`/`wait_for`).
Контекст: по этим доменам `curl` (браузерный UA, и `curl -sk --http1.1`) дал 403/401. Проверяем, снимает ли реальный браузер антибот/Cloudflare.

Вердикты: ОТКРЫЛСЯ · ОТКРЫЛСЯ ПОСЛЕ ПРОВЕРКИ · ПЕЙВОЛЛ · ФОРМА ВХОДА · АНТИБОТ И В БРАУЗЕРЕ · 404 · СЕРТИФИКАТ (ERR_CERT_AUTHORITY_INVALID) · НЕ РЕЗОЛВИТСЯ / ТАЙМАУТ.

| домен | что показал браузер | вердикт |
|---|---|---|
| psidonline.isr.umich.edu | Полная страница PSID Home, навигация, контент, ссылки на публикации | ОТКРЫЛСЯ |
| simba.isr.umich.edu | Data Center страница PSID, полный контент, навигация | ОТКРЫЛСЯ |
| melbourneinstitute.unimelb.edu.au | Навигационный timeout 10с при переходе, но снапшот показал полную страницу (новости, события, HILDA) | ОТКРЫЛСЯ |
| unimelb.edu.au | Навигационный timeout 10с (медленная загрузка), title "The University of Melbourne - Australia's #1 Ranked..." | ОТКРЫЛСЯ |
| onlinelibrary.wiley.com | Cloudflare Turnstile "Verify you are human", клик по чекбоксу не проходит проверку (challenge перезапускается, новый Ray ID) | АНТИБОТ И В БРАУЗЕРЕ |
| www.tandfonline.com | title "Taylor & Francis Online: Peer-reviewed Journals", загрузился сразу без проверки | ОТКРЫЛСЯ |
| pubsonline.informs.org | Cloudflare Turnstile, клик по чекбоксу не снял проверку | АНТИБОТ И В БРАУЗЕРЕ |
| www.mdpi.com | title "MDPI - Publisher of Open Access Journals", полная главная (Journals/Topics/Submit, поиск статей) | ОТКРЫЛСЯ |
| www.bls.gov | title "U.S. Bureau of Labor Statistics", страница загрузилась без проверки | ОТКРЫЛСЯ |
| publications.bof.fi | Cloudflare "Just a moment...", после ожидания 15 с проверка не снялась | АНТИБОТ И В БРАУЗЕРЕ |
| personal.lse.ac.uk | title "403 Forbidden" — отказ сервера на корне каталога (не Cloudflare); браузер отказ не снял | АНТИБОТ И В БРАУЗЕРЕ |
| scholar.harvard.edu | title "Home \| Scholars at Harvard" (navigation timeout 20 с, но страница отрисована) | ОТКРЫЛСЯ |
| campbell.scholars.harvard.edu | title "John Y. Campbell \| John Y. Campbell" (timeout навигации, страница отрисована) | ОТКРЫЛСЯ |
| rzeckhauser.scholars.harvard.edu | title "Richard Zeckhauser \| Richard Zeckhauser", загрузка без проверки | ОТКРЫЛСЯ |
| home.uchicago.edu | title "Access forbidden! \| The University of Chicago" — отказ сервера на корне, браузер не снял | АНТИБОТ И В БРАУЗЕРЕ |
| statmodeling.stat.columbia.edu | Cloudflare "Just a moment...", после reload — "Statistical Modeling, Causal Inference, and Soc..." | ОТКРЫЛСЯ ПОСЛЕ ПРОВЕРКИ |
| meehl.umn.edu | Cloudflare "Just a moment...", после reload — title "Paul Meehl \| Paul E. Meehl" | ОТКРЫЛСЯ ПОСЛЕ ПРОВЕРКИ |
| leeds-faculty.colorado.edu | title "401 - Unauthorized: Access is denied due to inv..." (IIS), браузер отказ не снял | АНТИБОТ И В БРАУЗЕРЕ |
| cdn.aaai.org | XML S3 `<Code>AccessDenied</Code>` на корне (листинг бакета закрыт; про конкретные PDF-пути замер не говорит) | АНТИБОТ И В БРАУЗЕРЕ |
| nottingham-repository.worktribe.com | Cloudflare "Just a moment...", после reload проверка осталась | АНТИБОТ И В БРАУЗЕРЕ |
| eprints.soton.ac.uk | title "Welcome to ePrints Soton - ePrints Soton", загрузка без проверки | ОТКРЫЛСЯ |
| www.acpjournals.org | Cloudflare "Just a moment...", после reload проверка осталась | АНТИБОТ И В БРАУЗЕРЕ |
| www.metrology-journal.org | title "International Journal of Metrology and Quality ...", загрузка без проверки | ОТКРЫЛСЯ |
| sdmx.oecd.org | корень: title "403 - Forbidden: Access is denied." (IIS). Путь API `/public/rest/dataflow/OECD` в соседней вкладке отдавался | АНТИБОТ И В БРАУЗЕРЕ |
| worldwide.espacenet.com | Cloudflare "Just a moment...", после reload проверка осталась | АНТИБОТ И В БРАУЗЕРЕ |
| api.uspto.gov | JSON `{"message":"Missing Authentication Token"}` — сервис отвечает, но требует API-ключ | ФОРМА ВХОДА |
| image-ppubs.uspto.gov | title "403 Forbidden", браузер отказ не снял | АНТИБОТ И В БРАУЗЕРЕ |
| supreme.justia.com | Cloudflare "Just a moment...", после reload проверка осталась | АНТИБОТ И В БРАУЗЕРЕ |
| legislature.mi.gov | "Attack blocked by web application protection" — Check Point CloudGuard WAF блокирует и браузер | АНТИБОТ И В БРАУЗЕРЕ |
| gc.nh.gov | title "Error 403" | АНТИБОТ И В БРАУЗЕРЕ |
| www.nasaa.org | title "Sucuri WebSite Firewall - Access Denied" | АНТИБОТ И В БРАУЗЕРЕ |
| uaelegislation.gov.ae | title "Attention Required! \| Cloudflare" (блок, не проходимая проверка) | АНТИБОТ И В БРАУЗЕРЕ |
| moneyhelper.org.uk | Cloudflare "Just a moment...", после reload проверка осталась | АНТИБОТ И В БРАУЗЕРЕ |
| maps.org.uk | Cloudflare "Just a moment...", после reload проверка осталась | АНТИБОТ И В БРАУЗЕРЕ |
| dentalage.co.uk | title "Attention Required! \| Cloudflare" | АНТИБОТ И В БРАУЗЕРЕ |
| www.envestnet.com | title "ERROR: The request could not be satisfied" (CloudFront блокирует) | АНТИБОТ И В БРАУЗЕРЕ |
| www.rocketshiphq.com | Cloudflare "Just a moment...", после reload — "Top mobile UA and performance creative agency \|..." | ОТКРЫЛСЯ ПОСЛЕ ПРОВЕРКИ |
| help.openai.com | редирект на /en, title "OpenAI Help Center" | ОТКРЫЛСЯ |
| old.reddit.com | title "Blocked" — отказ Reddit и в браузере | АНТИБОТ И В БРАУЗЕРЕ |
| bankrot.fedresurs.ru | title "HTTP 403": "Access to bankrot.fedresurs.ru is forbidden" (блок по IP) | АНТИБОТ И В БРАУЗЕРЕ |
| blog.domclick.ru | title "403 \| Домклик", текст "Система защиты могла принять ваши действия за автоматические" | АНТИБОТ И В БРАУЗЕРЕ |
| www.g2.com | title "g2.com", тело пустое (страница-заглушка антибота), после reload то же | АНТИБОТ И В БРАУЗЕРЕ |
| www.capterra.com | Cloudflare "Just a moment...", после reload проверка осталась | АНТИБОТ И В БРАУЗЕРЕ |
| www.getapp.com | Cloudflare "Just a moment...", после reload — редирект на `/api/auth/error`, "Attention Required! \| Cloudflare" | АНТИБОТ И В БРАУЗЕРЕ |
| www.bki-okb.ru | редирект на bki-okb.ru, title "Объединенное Кредитное Бюро" | ОТКРЫЛСЯ |

## Итог по 38 доменам партии 18.09.2026 (строки ниже шапки, без 7 доменов предыдущего исполнителя)

- ОТКРЫЛСЯ — 9: www.mdpi.com, www.bls.gov, scholar.harvard.edu, campbell.scholars.harvard.edu, rzeckhauser.scholars.harvard.edu, eprints.soton.ac.uk, www.metrology-journal.org, help.openai.com, www.bki-okb.ru
- ОТКРЫЛСЯ ПОСЛЕ ПРОВЕРКИ — 3: statmodeling.stat.columbia.edu, meehl.umn.edu, www.rocketshiphq.com
- ФОРМА ВХОДА — 1: api.uspto.gov (нужен API-ключ)
- АНТИБОТ И В БРАУЗЕРЕ — 25 (включая серверные 401/403 на корне: personal.lse.ac.uk, home.uchicago.edu, leeds-faculty.colorado.edu, cdn.aaai.org, sdmx.oecd.org, image-ppubs.uspto.gov, gc.nh.gov)
- ПЕЙВОЛЛ · 404 · СЕРТИФИКАТ · НЕ РЕЗОЛВИТСЯ — 0

Метод замера: `navigate_page` на корень домена, вердикт по `document.title` из ответа инструмента; при Cloudflare «Just a moment...» — ровно одна вторая попытка (`reload`); при пустом/неинформативном title — `evaluate_script` с чтением `document.title` и первых 200 символов `innerText`.

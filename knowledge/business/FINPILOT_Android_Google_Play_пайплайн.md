# FINPILOT → Android: пайплайн вывода веб-приложения в Google Play

> Как из текущего веб-приложения FINPILOT (FastAPI + Jinja2, server-rendered)
> сделать нативное приложение для Android и опубликовать в Google Play.
> Документ привязан к реальному состоянию кода **v3.3.0 intl** (блокеры — из аудита
> твоего репозитория) и к актуальным политикам Google Play на июнь 2026.
> Парный документ по iOS — `FINPILOT_iOS_App_Store_пайплайн.md`.

---

## 0. Как это устроено — два пути

Твоё приложение **server-rendered**, фронт приходит с бэкенда, запросы идут
относительными путями (`fetch('/api/...')`). Бандлить такой фронт локально нельзя —
оболочка должна открывать твой **боевой HTTPS-URL**. На Android для этого есть **два**
подхода (на iOS был только Capacitor):

### Вариант A — TWA (Trusted Web Activity) ⭐ рекомендую как стартовый

TWA оборачивает твою **PWA** в нативную оболочку через движок Chrome. Это **собственная
технология Google**, поэтому она наиболее безопасна против политики о
«низкокачественных webview-приложениях». PWA у тебя уже собрана (`manifest.webmanifest`,
`sw.js`, иконки) — TWA ложится на неё почти даром.

- Плюсы: минимум кода, Google-blessed, использует готовую PWA, при правильной настройке
  **без адресной строки браузера**.
- Минусы: это по сути твоя PWA на весь экран; нативных фич (биометрия, пуши) почти нет.
- Требует: установимую PWA (✅ есть), HTTPS, и **Digital Asset Links** —
  `assetlinks.json` на твоём домене для подтверждения владения (иначе сверху останется
  URL-бар).

### Вариант B — Capacitor (тот же стек, что и iOS)

WebView-оболочка, грузящая боевой URL — один в один с iOS-путём.

- Плюсы: один инструмент на обе платформы, легко добавить нативную биометрию и пуши.
- Минусы: больше настройки; webview-обёртка без нативной ценности рискует попасть под
  политику качества (как и на iOS по 4.2).

**Как выбрать:** делаешь iOS через Capacitor → бери Capacitor и на Android (одна обёртка
на обе платформы). Если Android самостоятельно и быстро — **TWA через Bubblewrap**.

> Origin внутри обёртки = твой домен (грузим боевой URL), поэтому относительные `/api`
> работают как есть, Bearer-JWT из `localStorage` живёт корректно, **CORS не нужен**.

---

## 1. Что нужно иметь (prerequisites)

| Нужно | Зачем | Статус |
|---|---|---|
| **Google Play Console — $25 единоразово** | Регистрация разработчика (не $99/год как Apple — один раз) | ⬜ оформить |
| **Android Studio + JDK** | Сборка `.aab`, подпись. Работает на macOS/Win/Linux — **нет привязки к Mac** как у Xcode | ⬜ поставить |
| **Node.js LTS** | Bubblewrap CLI (TWA) или Capacitor CLI | ⬜ поставить |
| **HTTPS-хостинг с задеплоенным бэком** | Оболочке нужно что открывать + хостить `assetlinks.json` | ⬜ раздел 4 |

Регистрация: https://play.google.com/console/signup

---

## 2. Пройдёт ли ревью? Блокеры + специфика Google

Коротко: **в текущем виде — нет.** Часть блокеров — те же, что и на iOS (они про сам
веб-продукт). Плюс есть отдельные требования и одна большая процессная ловушка Google.

### Те же блокеры, что и на iOS (про веб-приложение)

1. **Навигация ломается на телефоне.** На ширине телефона сайдбар уезжает за экран
   (`.sidebar { transform: translateX(-100%); }` в `styles.css`), кнопки-гамбургера в
   коде нет. На Android это **ещё критичнее**: TWA — это и есть твой мобильный веб на
   весь экран, сломанная навигация = неработающее приложение.
2. **Нет доступной политики конфиденциальности.** В чекбоксе согласия (`base.html`) есть
   текст «политика конфиденциальности», но это не ссылка и документа нет. Google требует
   **Privacy Policy URL** в Play Console — для приложения с финансовыми данными
   обязательно.
3. **Нет дисклеймера про финсоветы.** Приложение прескриптивное — нужна оговорка
   «не является индивидуальной инвестиционной рекомендацией».
4. **Полурабочий Plaid** (`routes_plaid.py` → `501 NOT_IMPLEMENTED`). Либо рабочий
   sandbox для демо, либо скрыть за фиче-флагом.

### Специфика Google — обязательно

5. **Закрытое тестирование: 12 тестеров × 14 дней.** Если твой персональный аккаунт
   создан после 13.11.2023, перед production-доступом нужно прогнать closed-тест с
   **минимум 12 тестерами, непрерывно подключёнными 14 дней**. Это +2 недели к срокам.
   **Аккаунты-организации (зарегистрированное юрлицо, например ИП/ООО) от этого
   освобождены** — если есть/планируешь юрлицо, организационный аккаунт пропускает этот
   этап и публикует в production сразу.
6. **Data safety form.** Аналог Apple Nutrition Labels. Обязательно задекларировать, какие
   данные собираешь (персональные, финансовые), зачем, связаны ли с личностью.
7. **Удаление аккаунта — в приложении И по веб-ссылке.** У тебя in-app удаление есть
   (`DELETE /api/auth/me`, ✅), но Google дополнительно требует **публичный URL**, где
   можно запросить удаление аккаунта и данных **без установки приложения**. Это надо
   добавить (страница `/account/delete` или форма).
8. **Target API level 35 (Android 15).** Новые приложения обязаны таргетить API 35+.
   Bubblewrap/Capacitor это умеют — проверить `targetSdkVersion = 35` в сборке.
9. **Content rating** — пройти опросник IARC в Play Console.
10. **Financial features declaration.** У Google есть политика Financial Services. PFM/
    бюджетирование без займов/инвестиций/крипты проходит легко — но декларацию заполнить
    честно, и дисклеймер (п. 3) тут в тему.

### Уже ОК / не проблема

- ✅ **Удаление аккаунта in-app есть** (нужно лишь добавить веб-URL, п. 7).
- ✅ **Платежей нет** → **Google Play Billing не нужен** (его комиссия 15–30% — на потом,
  когда появится подписка).

### Чек-лист критериев

| Требование Google | Статус |
|---|---|
| Ничего не сломано, есть демо-доступ | ⚠️ навигация + Plaid |
| Работает на экране телефона | ⚠️ чинить мобилу |
| Privacy Policy URL | ⚠️ нет политики |
| Data safety form | ⬜ заполнить |
| Удаление аккаунта (in-app + web URL) | ⚠️ in-app ✅, web ⬜ |
| Target API 35 | ⬜ в сборке |
| Content rating | ⬜ опросник |
| Closed testing 12×14 (если персон. аккаунт) | ⬜ +14 дней |
| Play Billing | ✅ N/A (нет платежей) |
| Дисклеймер / Financial declaration | ⚠️ нет дисклеймера |

---

## 3. Фаза 0 — починить блокеры (в репозитории)

1. **Мобильная навигация.** Кнопка-гамбургер в шапку, класс `sidebar--open` + оверлей,
   тоггл в `app.js`. Обязательно для TWA вдвойне.
2. **Правовые страницы.** `/privacy` и `/terms` (роуты + шаблоны, текст есть в проекте),
   ссылки в чекбоксе согласия и футере/профиле.
3. **Дисклеймер** «не является индивидуальной инвестиционной рекомендацией» на
   `planning.html`.
4. **Plaid** — sandbox или скрыть за фиче-флагом.
5. **Веб-страница удаления аккаунта** (`/account/delete`) — требование Google (п. 7).
6. **`assetlinks.json`** (для TWA) — отдать с `/.well-known/assetlinks.json` (роут в
   `main.py`, как сделаны PWA-маршруты). Содержимое — после генерации ключа (Фаза 5).

---

## 4. Фаза 1 — задеплоить бэкенд на HTTPS

У тебя есть `Dockerfile` и `docker-compose.yml`.

1. Хостинг с HTTPS: **Render / Railway / Fly.io** (тянут Docker + дают TLS) либо VPS с
   Docker + Caddy/Traefik (авто-HTTPS).
2. Env из `.env.example` (`SECRET_KEY`, БД — на проде Postgres, не SQLite).
3. Получить `https://app.finpilot.<домен>`, проверить в Chrome на Android.
4. **Для TWA: PWA должна быть установимой.** Проверь в Chrome DevTools → Lighthouse →
   категория PWA: валидный manifest, service worker, HTTPS. У тебя всё это есть, но прогнать
   надо.
5. Подготовить отдачу `/.well-known/assetlinks.json` (заполнишь fingerprint'ом в Фазе 5).

> Для быстрой проверки до деплоя: `cloudflared tunnel --url http://localhost:8000`.

---

## 5. Фаза 2 — собрать обёртку

### Вариант A — TWA через Bubblewrap (быстро, на базе PWA)

```bash
npm i -g @bubblewrap/cli

# инициализация прямо из твоего манифеста
bubblewrap init --manifest https://app.finpilot.<домен>/manifest.webmanifest
# спросит package name → app.finpilot.mobile, и сгенерирует upload-ключ (keystore)

bubblewrap build
# на выходе: app-release-signed.aab + SHA-256 fingerprint ключа
```

> Альтернатива без CLI — **PWA Builder** (https://pwabuilder.com): вставляешь URL,
> жмёшь Android → получаешь готовый пакет и инструкции.

**Digital Asset Links.** Bubblewrap выдаст SHA-256 fingerprint. Положи `assetlinks.json`
на сервер по `/.well-known/assetlinks.json`:

```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "app.finpilot.mobile",
    "sha256_cert_fingerprints": ["AB:CD:EF:..."]
  }
}]
```

> ⚠️ **Ключевой подвох TWA.** Если включишь **Play App Signing** (Google сам подписывает
> релиз, рекомендуется), то в `assetlinks.json` нужен fingerprint **ключа подписи из Play
> Console** (App Integrity → App signing key), а **не** твоего локального upload-ключа.
> Иначе адресная строка браузера не исчезнет. Безопасно — указать **оба** fingerprint'а в
> массиве. Этот шаг доделываешь после загрузки в Play Console (Фаза 7).

### Вариант B — Capacitor (тот же стек, что iOS)

```bash
npm i @capacitor/core @capacitor/cli @capacitor/android
mkdir www && echo "<!doctype html><title>FINPILOT</title>" > www/index.html
npx cap init "FINPILOT" "app.finpilot.mobile" --web-dir=www
```

`capacitor.config.json` — боевой URL (как на iOS):

```json
{
  "appId": "app.finpilot.mobile",
  "appName": "FINPILOT",
  "webDir": "www",
  "server": { "url": "https://app.finpilot.<твой-домен>", "cleartext": false }
}
```

Нативная ценность (страховка от политики качества):

```bash
npm i capacitor-native-biometric          # биометрия на вход
npm i @capacitor/push-notifications        # пуши (хотя бы запрос разрешения)
```

```bash
npx cap add android
npx cap sync android
npx cap open android
```

---

## 6. Фаза 3 — Android Studio / подпись / сборка

1. Убедиться `targetSdkVersion = 35` (Bubblewrap — в сгенерированном `build.gradle`;
   Capacitor — в `variables.gradle`).
2. **Upload keystore** — Bubblewrap создал его сам; для Capacitor сгенерировать
   (`keytool` / Android Studio → Build → Generate Signed Bundle → Create new keystore).
   **Хранить этот keystore и пароли как зеницу ока** — потеряешь, не сможешь обновлять
   приложение.
3. **Play App Signing** (рекомендуется): Google хранит ключ подписи приложения, ты
   подписываешь загрузку upload-ключом. Отсюда — fingerprint для `assetlinks.json` (см.
   подвох выше).
4. Собрать **`.aab`** (Android App Bundle — для Play нужен именно он, не APK):
   Build → Generate Signed Bundle / AAB.

---

## 7. Фаза 4 — Play Console → submit

1. https://play.google.com/console → создать приложение, package `app.finpilot.mobile`.
2. **Store listing:** название, описание, иконка (`icon-512.png`), скриншоты телефона,
   feature graphic.
3. **Privacy Policy URL** (ссылка на `/privacy` твоего домена) — обязательно.
4. **Data safety** — задекларировать сбор персональных/финансовых данных.
5. **Content rating** — пройти опросник.
6. **App access** — дать **демо-логин/пароль** для ревьюера (иначе не войдёт).
7. Загрузить `.aab` в трек **Closed testing**.
8. **Если персональный аккаунт:** набрать **12 тестеров**, держать их подключёнными
   **14 дней подряд**, затем **apply for production access**.
   (Аккаунт-организация — можно сразу в production.)
9. После одобрения production-доступа → **Submit / Roll out to production**.
10. Доправить `assetlinks.json` fingerprint'ом ключа подписи из Play Console (Фаза 5).

---

## 8. Финальный чек-лист

- [ ] Навигация работает на телефоне (гамбургер + сайдбар)
- [ ] `/privacy`, `/terms` доступны, ссылки проставлены
- [ ] Дисклеймер на экране рекомендаций
- [ ] Plaid: sandbox ИЛИ скрыт (нет `501` в UI)
- [ ] Веб-страница удаления аккаунта (`/account/delete`)
- [ ] Удаление аккаунта in-app работает (уже есть ✅)
- [ ] `/.well-known/assetlinks.json` отдаётся (TWA) с верным fingerprint
- [ ] PWA проходит Lighthouse (для TWA)
- [ ] Бэкенд на HTTPS, проверен в Chrome на Android
- [ ] `targetSdkVersion = 35`, собран `.aab`
- [ ] Upload keystore сохранён в надёжном месте
- [ ] Privacy Policy URL + Data safety + Content rating заполнены
- [ ] Демо-логин в App access
- [ ] (персон. аккаунт) closed testing 12×14 пройден

---

## 9. Сроки (реалистично)

| Этап | Время |
|---|---|
| Фаза 0 (фиксы блокеров) | 1–2 дня |
| Фаза 1 (деплой HTTPS) | полдня |
| Фаза 2–3 (Bubblewrap/Capacitor + сборка) | полдня |
| **Closed testing 12×14 (персон. аккаунт)** | **+14 дней** ⚠️ |
| Ревью Google | обычно от нескольких часов до пары дней |

> На Android дешевле ($25 единоразово против $99/год) и обычно быстрее на ревью, но
> закрытое тестирование 12×14 для персонального аккаунта — реальный +2-недельный барьер,
> которого нет в App Store. Заложи его в план или оформляй аккаунт-организацию.

---

## Приложение: PWA как дешёвая альтернатива

Если Play-фрикшен пока не оправдан, есть путь **без маркета**: PWA уже собрана в проекте.
На Android Chrome даже сам предлагает «Установить приложение» (баннер установки) — иконка
на рабочем столе, полноэкранный запуск, **без $25 и без closed testing**. Детали —
`docs/PWA_УСТАНОВКА.md`.

PWA закрывает «потрогать и раздать людям уже сегодня» (и заодно эти же 12 тестеров для
closed testing удобно сначала прогнать через PWA). Google Play нужен для присутствия в
маркете, пушей и доверия листинга. Блокеры из раздела 3 обязательны в обоих случаях.

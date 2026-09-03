# tools/ — вспомогательные скрипты и программы

Dev-tooling проекта. Не часть приложения (`app/`), в публичное зеркало не публикуется.

- **publish/** — публикация релизов на GitHub (`finpilot_publish_private.sh`) и публичное зеркало:
  `finpilot_publish_public.sh` (whitelist-сборка + guard + push + тег + Release),
  `public_release_notes.md` (тексты публичных релизов, private-only),
  `mirror_extras/` (файлы только для зеркала, напр. CodeQL-воркфлоу).
- **claude_skills/** — скиллы для Claude: `model-advisor/SKILL.md` (автосоветник
  выбора модели/effort, роутинг-only; методичка —
  `knowledge/guides/claude_infrastructure_methodology.md`).
- **cost_tracker/** — сводка расхода Claude по аккаунтам через Admin API.
- **timing_lab/** — временна́я лаборатория: сколько стоит по времени каждый прогон тестов.
  Журнал `timings.csv` + `record.py` (`run`/`add`/`report --update-doc`); справочник для
  чтения — `docs/timing_reference.md`, таблица в нём обновляется командой, не руками.
  Каждая запись несёт load average: длительность без неё бессмысленна — один и тот же
  срез шёл 40.8 с и 83.4 с без правок кода (`INV-MACHINE-LOAD`, пять эпизодов).
- **survey_analysis/** — пайплайн анализа опросов аудитории (генерация отчёта из данных).
- **revision/** — гейт ревизии `revision_check.py`: статические проверки docs↔code (битые ссылки
  живые vs замороженные, утечка legacy мат-модели, счётчики структуры). Запуск
  `python -m tools.revision.revision_check`; как тест — `tests/test_repo_revision.py` (в fast-тире и CI).
  Процесс — `knowledge/guides/repo_revision_methodology.md`.
- **timewarp/** — детектор календарных мин `warp.py` (сдвиг `utcnow` на `WARP_DAYS`, ось 3 ревизии;
  запуск — `docs/QA.md` / методичка ревизии).

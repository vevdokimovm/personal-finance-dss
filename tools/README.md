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
- **survey_analysis/** — пайплайн анализа опросов аудитории (генерация отчёта из данных).

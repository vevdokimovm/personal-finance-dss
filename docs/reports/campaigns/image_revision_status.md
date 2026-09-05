# Ревизия изображений — статус: ЗАКРЫТО

> Кампания перевода изображений без текстового слоя в служебные заметки —
> `_base/07-media-to-text-lab/METHOD_IMAGES.md`. Проверка перед повтором:
> `python3 _base/07-media-to-text-lab/tools/image_queue.py --repo personal-finance-dss`
> — очередь этой репы на 2026-08-27 составляет **0 серий / 0 кадров**.
>
> Кросс-репо хроника всей кампании (что решено, почему, какие серии свёрнуты
> как дубли) — `base-repo/07-media-to-text-lab/runs/2026-08-27-image-queue-first-look.md`.

**Дата закрытия:** 2026-08-27 · **Версия репы на момент закрытия:** v8.28.5

## Разобрано (4 серии/заметки)

- `docs/diagrams/raspoznavanie.md`
- `knowledge/science/articles/kim/figures/raspoznavanie.md`
- `knowledge/science/articles/other/raspoznavanie.md`
- `knowledge/survey_auditory/results/raspoznavanie.md`

## Если появятся новые изображения

Прогнать `image_queue.py --repo personal-finance-dss` заново — в очередь попадёт только
непокрытое: наличие `raspoznavanie.md` рядом с серией снимает её с очереди
автоматически, повторно эти файлы в списке выше не всплывут.

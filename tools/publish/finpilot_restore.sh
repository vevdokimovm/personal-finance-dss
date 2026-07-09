#!/bin/zsh
# ============================================================================
# FINPILOT — ВОССТАНОВЛЕНИЕ репозитория после аварии forward-build.
#
# Что произошло: публикатор искал корень архива через `find | head -1`, а мои
# архивы (v5.20.0+) были без обёртки finpilot_vX_Y_Z_intl/. head -1 выхватывал
# случайную папку (deploy/), и `rsync --delete` делал репо равным ей — весь
# проект стирался. Коммиты/теги/релизы этих версий на гите — огрызки.
#
# Этот скрипт:
#   1. Диагностирует теги: целый (есть app/config.py) или битый (огрызок).
#   2. Откатывает main на последний ЦЕЛЫЙ тег перед первым битым.
#   3. Сносит битые теги и релизы (локально + на GitHub).
#   4. Если рядом лежит пофикшенный публикатор и правильные архивы — зовёт его
#      для чистого rebuild (forward-build пересоздаёт версии из целых архивов).
#
# ПЕРЕД запуском положи в ~/Downloads:
#   - finpilot_publish_private.sh (пофикшенный, с надёжным поиском корня)
#   - правильные архивы finpilot_vX_Y_Z_intl.zip (с обёрткой)
#
# Запуск: zsh ~/Downloads/finpilot_restore.sh
# ============================================================================

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH:/usr/bin:/bin:/usr/sbin:/sbin"
export LANG=ru_RU.UTF-8 LC_ALL=ru_RU.UTF-8 2>/dev/null

REPO="$HOME/Downloads/personal-finance-dss"
DL="$HOME/Downloads"
MARKER="app/config.py"   # маркер целого дерева репо

cd "$REPO" || { echo "Нет репозитория: $REPO"; exit 1; }
command -v git >/dev/null || { echo "git не найден"; exit 1; }
command -v gh  >/dev/null || { echo "gh не установлен"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh не авторизован. gh auth login"; exit 1; }

retry () { local n=0; while [ $n -lt 3 ]; do "$@" && return 0; n=$((n+1)); sleep 2; done; return 1; }

echo "=== Диагностика тегов (целый = в дереве тега есть $MARKER) ==="
reset_to=""; first_bad=""; typeset -a bad_tags
for tag in $(git tag | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V); do
  if git ls-tree -r --name-only "$tag" 2>/dev/null | grep -qx "$MARKER"; then
    if [ -z "$first_bad" ]; then reset_to="$tag"; fi
    echo "  $tag — целый"
  else
    if [ -z "$first_bad" ]; then first_bad="$tag"; fi
    bad_tags+=("$tag")
    echo "  $tag — БИТЫЙ (огрызок)"
  fi
done

if [ ${#bad_tags[@]} -eq 0 ]; then
  echo ""; echo "Битых тегов нет — репозиторий целый. Восстановление не требуется."
  exit 0
fi
if [ -z "$reset_to" ]; then
  echo ""; echo "! Не найден ни один целый тег для отката. Останавливаюсь — разберём вручную."
  exit 1
fi

echo ""
echo "=== ПЛАН ВОССТАНОВЛЕНИЯ ==="
echo "  Откат main на:      $reset_to (последний целый)"
echo "  Снести теги+релизы: ${bad_tags[*]}"
echo "  Затем rebuild из архивов пофикшенным публикатором."
echo ""
echo "Это перепишет историю main на GitHub (force-push) и удалит битые релизы."
printf "Продолжить? [yes/NO]: "
read ans
[ "$ans" = "yes" ] || { echo "Отменено."; exit 0; }

echo ""
echo "=== 1. Откат main на $reset_to ==="
git checkout main >/dev/null 2>&1 || git checkout -B main
git reset --hard "$reset_to" && echo "  main = $reset_to"

echo ""
echo "=== 2. Снос битых тегов и релизов ==="
for tag in "${bad_tags[@]}"; do
  gh release delete "$tag" -y >/dev/null 2>&1 && echo "  релиз $tag удалён" || echo "  (релиза $tag не было)"
  git tag -d "$tag" >/dev/null 2>&1 && echo "  тег $tag удалён локально"
  retry git push origin ":refs/tags/$tag" >/dev/null 2>&1 && echo "  тег $tag удалён на GitHub" || echo "  ! тег $tag на GitHub повтори вручную"
done

echo ""
echo "=== 3. Форс-пуш восстановленного main ==="
retry git push origin main --force >/dev/null 2>&1 && echo "  main запушен ($reset_to)" || echo "  ! force-push повтори: git push origin main --force"

echo ""
echo "=== 4. Rebuild из целых архивов ==="
PUB="$DL/finpilot_publish_private.sh"
if [ -f "$PUB" ]; then
  echo "  Запускаю пофикшенный публикатор — он дольёт версии из правильных архивов..."
  echo ""
  zsh "$PUB"
else
  echo "  Публикатор не найден в $DL."
  echo "  Положи finpilot_publish_private.sh и правильные архивы в ~/Downloads и запусти:"
  echo "    zsh ~/Downloads/finpilot_publish_private.sh"
fi

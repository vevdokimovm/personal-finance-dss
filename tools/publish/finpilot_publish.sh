#!/bin/zsh
# ============================================================================
# FINPILOT — ЕДИНЫЙ скрипт публикации версий на GitHub. Запустил — и всё.
#
# За один прогон:
#   1. Находит в ~/Downloads архивы finpilot_vX_Y_Z_intl.zip, которых ещё нет
#      в тегах и которые новее текущего HEAD.
#   2. forward-build: распаковка → замена дерева → коммит → тег. Пушит main + теги.
#   3. Оформляет Releases для версий без релиза: имя «FINPILOT vX.Y.Z — Заголовок»,
#      тело с H2-датой, архив прикреплён ассетом. Latest — на самой свежей.
#
# Идемпотентный: уже оформленное пропускает. Гоняй сколько угодно. Ретраи против РФ-таймаутов.
# Описание: CHANGELOG.md → git show vX:CHANGELOG.md → docs/WATCHLOG.md.
#
# Запуск:          zsh ~/Downloads/finpilot_publish.sh
# Переоформить всё: zsh ~/Downloads/finpilot_publish.sh --verify-all
# Требования: brew install gh && gh auth login
# ============================================================================

export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export LANG=ru_RU.UTF-8 LC_ALL=ru_RU.UTF-8 2>/dev/null

REPO="$HOME/Downloads/personal-finance-dss"
DL="$HOME/Downloads"
TITLE_TMP="/tmp/fp_pub_title.txt"
NOTES_TMP="/tmp/fp_pub_notes.md"
WORK="/tmp/fp_pub_work"
ARCH_VERS="/tmp/fp_pub_archvers.txt"
TO_BUILD="/tmp/fp_pub_tobuild.txt"
ALL_VERS="/tmp/fp_pub_allvers.txt"
EXISTING="/tmp/fp_pub_existing.txt"

VERIFY_ALL="no"; [ "$1" = "--verify-all" ] && VERIFY_ALL="yes"

cd "$REPO" || { echo "Нет репозитория: $REPO"; exit 1; }
command -v git     >/dev/null || { echo "git не найден"; exit 1; }
command -v gh      >/dev/null || { echo "gh не установлен. brew install gh && gh auth login"; exit 1; }
command -v python3 >/dev/null || { echo "python3 не найден"; exit 1; }
command -v rsync   >/dev/null || { echo "rsync не найден"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh не авторизован. gh auth login"; exit 1; }

retry () {
  local n=0
  while [ $n -lt 3 ]; do
    "$@" && return 0
    n=$((n + 1)); sleep 2
  done
  return 1
}

# Версии из архивов в Downloads -> stdout (X.Y.Z по возрастанию SemVer)
archive_versions () {
  /bin/ls "$DL"/finpilot_v*_intl.zip 2>/dev/null | python3 -c "
import sys, re
vs = set()
for ln in sys.stdin:
    m = re.search(r'finpilot_v(\d+)_(\d+)_(\d+)_intl\.zip', ln)
    if m: vs.add(tuple(int(x) for x in m.groups()))
for v in sorted(vs): print('%d.%d.%d' % v)
"
}

version_gt () {   # $1 > $2 ?
  [ "$1" = "$2" ] && return 1
  [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | tail -1)" = "$1" ]
}

# extract VER -> H1 в $TITLE_TMP, тело (с датой) в $NOTES_TMP. Код 1 если описания нет.
extract () {
  python3 - "$1" "$TITLE_TMP" "$NOTES_TMP" <<'PY'
import re, sys, subprocess
ver, ft, fn = sys.argv[1], sys.argv[2], sys.argv[3]

def from_changelog(txt):
    m = re.search(r'^## \[' + re.escape(ver) + r'\].*$', txt, re.M)
    if not m: return None
    header = m.group(0)
    hdr = re.sub(r'^## \[[^\]]*\]', '', header).strip()
    parts = [p.strip() for p in re.split(r'\s+[\u2014\u2013-]\s+', hdr) if p.strip()]
    title = re.sub(r'\s*\((?:PATCH|MINOR|MAJOR)\)\s*$', '', parts[-1] if parts else '')
    start = m.start(); nxt = re.search(r'^## \[', txt[m.end():], re.M)
    section = (txt[start:m.end() + nxt.start()] if nxt else txt[start:]).strip('\n')
    return title, section

def from_watchlog(txt):
    m = re.search(r'^[-*]\s*\*\*v' + re.escape(ver) + r'\*\*\s*[\u2014\u2013-]\s*(.*?)(?=^[-*]\s*\*\*v|\Z)',
                  txt, re.M | re.S)
    if not m: return None
    body = m.group(1).strip()
    title = body.splitlines()[0].strip().rstrip('.;,')[:80] if body else ''
    return title, f"## [{ver}]\n\n{body}"

def git_show(path):
    try:
        o = subprocess.run(['git', 'show', f'v{ver}:{path}'], capture_output=True, text=True)
        return o.stdout if o.returncode == 0 else ''
    except Exception:
        return ''

res = None
try: res = from_changelog(open('CHANGELOG.md', encoding='utf-8').read())
except Exception: pass
if not res:
    t = git_show('CHANGELOG.md');  res = from_changelog(t) if t else None
if not res:
    try: res = from_watchlog(open('docs/WATCHLOG.md', encoding='utf-8').read())
    except Exception: pass
if not res:
    t = git_show('docs/WATCHLOG.md');  res = from_watchlog(t) if t else None

if not res:
    open(ft, 'w', encoding='utf-8').write(''); open(fn, 'w', encoding='utf-8').write('')
    sys.exit(1)
title, section = res
open(ft, 'w', encoding='utf-8').write(f"FINPILOT v{ver} \u2014 {title}".strip(' \u2014'))
open(fn, 'w', encoding='utf-8').write(section)
sys.exit(0)
PY
}

attach_asset () {
  local ver="$1" tag="v$1" under zip
  under=$(echo "$ver" | tr '.' '_'); zip="$DL/finpilot_v${under}_intl.zip"
  [ -f "$zip" ] || { echo "    (архива нет в Downloads, ассет пропущен)"; return 0; }
  retry gh release upload "$tag" "$zip" --clobber >/dev/null 2>&1 \
    && echo "    ассет: finpilot_v${under}_intl.zip" || { echo "    ! ассет не залился"; return 1; }
}

# ===== ФАЗА 0: разведка =====
echo "=== Состояние ==="
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
CURRENT_VER="${CURRENT_TAG#v}"
echo "Репозиторий: $REPO"
echo "HEAD на:     ${CURRENT_TAG:-<нет тегов>}"
echo "Ветка:       $(git branch --show-current)"

DIRTY=$(git status --porcelain | grep -v '\.DS_Store')
if [ -n "$DIRTY" ]; then
  echo ""
  echo "! Рабочее дерево не чистое (есть изменения кроме .DS_Store):"
  echo "$DIRTY"
  echo "  forward-build перезатёр бы их. Закоммить или убери — потом запусти снова."
  exit 1
fi
/usr/bin/find "$REPO" -name '.DS_Store' -delete 2>/dev/null

# ===== ФАЗА 1: forward-build незалитых версий =====
echo ""
echo "=== Поиск незалитых версий в $DL ==="
archive_versions > "$ARCH_VERS"
: > "$TO_BUILD"
while IFS= read -r ver; do
  [ -z "$ver" ] && continue
  git rev-parse "v$ver" >/dev/null 2>&1 && continue          # тег уже есть
  if [ -n "$CURRENT_VER" ] && ! version_gt "$ver" "$CURRENT_VER"; then
    echo "  v$ver — нет тега, но <= HEAD; пропуск (нужен ручной разбор)"
    continue
  fi
  echo "$ver" >> "$TO_BUILD"
done < "$ARCH_VERS"

if [ ! -s "$TO_BUILD" ]; then
  echo "  Новых версий нет — main актуален."
else
  echo "  К заливке: $(tr '\n' ' ' < "$TO_BUILD")"
  while IFS= read -r ver; do
    [ -z "$ver" ] && continue
    under=$(echo "$ver" | tr '.' '_'); zip="$DL/finpilot_v${under}_intl.zip"
    echo ">>> $ver — forward-build"
    if [ ! -f "$zip" ]; then echo "    ! архив не найден: $zip, пропуск"; continue; fi
    /bin/rm -rf "$WORK"; /bin/mkdir -p "$WORK"
    /usr/bin/unzip -q "$zip" -d "$WORK"
    src="$WORK/finpilot_v${under}_intl"
    [ -d "$src" ] || src=$(/usr/bin/find "$WORK" -maxdepth 1 -mindepth 1 -type d | head -1)
    [ -d "$src" ] || { echo "    ! корень в архиве не найден, пропуск"; continue; }
    /usr/bin/rsync -a --delete --exclude='.git' --exclude='.DS_Store' "$src/" "$REPO/"
    /usr/bin/find "$REPO" -name '.DS_Store' -delete 2>/dev/null
    /usr/bin/find "$REPO" -name '__pycache__' -type d -exec /bin/rm -rf {} + 2>/dev/null
    git add -A
    if git diff --cached --quiet; then git commit --allow-empty -m "v$ver" >/dev/null
    else git commit -m "v$ver" >/dev/null; fi
    git tag "v$ver"
    echo "    коммит + тег v$ver"
  done < "$TO_BUILD"
  echo ""
  echo "=== push ==="
  retry git push origin main --tags >/dev/null 2>&1 && echo "  запушено" || echo "  ! push повтори: git push origin main --tags"
fi

# ===== ФАЗА 2: релизы =====
echo ""
echo "=== Оформление релизов ==="
git tag | sed 's/^v//' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V > "$ALL_VERS"
LATEST_VER=$(tail -1 "$ALL_VERS")
gh release list --limit 400 --json tagName --jq '.[].tagName' 2>/dev/null | sed 's/^v//' > "$EXISTING"

ok=0; done_=0; failed=0
while IFS= read -r ver; do
  [ -z "$ver" ] && continue
  tag="v$ver"
  has_rel=0; grep -qx "$ver" "$EXISTING" && has_rel=1
  want_latest="no"; [ "$ver" = "$LATEST_VER" ] && want_latest="yes"

  # дефолт: трогаем только версии без релиза. С --verify-all — все.
  if [ "$VERIFY_ALL" != "yes" ] && [ $has_rel -eq 1 ]; then
    [ "$want_latest" = "yes" ] && retry gh release edit "$tag" --latest >/dev/null 2>&1
    ok=$((ok + 1)); continue
  fi

  if ! extract "$ver" >/dev/null 2>&1; then
    [ $has_rel -eq 0 ] && echo ">>> $tag — описания нет нигде, пропуск"
    continue
  fi
  title=$(cat "$TITLE_TMP")
  echo ">>> $tag — $title"
  lf=0
  latest_flag="--latest=false"; [ "$want_latest" = "yes" ] && latest_flag="--latest"
  if [ $has_rel -eq 1 ]; then
    retry gh release edit "$tag" --title "$title" --notes-file "$NOTES_TMP" $latest_flag >/dev/null 2>&1 \
      && echo "    описание ок" || { echo "    ! описание"; lf=1; }
  else
    cl="false"; [ "$want_latest" = "yes" ] && cl="true"
    retry gh release create "$tag" --title "$title" --notes-file "$NOTES_TMP" --latest="$cl" >/dev/null 2>&1 \
      && echo "    релиз создан" || { echo "    ! релиз"; lf=1; }
  fi
  attach_asset "$ver" || lf=1
  [ $lf -eq 0 ] && done_=$((done_ + 1)) || failed=$((failed + 1))
done < "$ALL_VERS"

echo ""
echo "Итог: пропущено готовых $ok, оформлено $done_, ошибок $failed."
[ $failed -gt 0 ] && echo "Ошибки (таймаут РФ?) — просто запусти ещё раз, готовое пропустится."
[ $failed -eq 0 ] && echo "Готово. Линейка на гите полная, Latest = v$LATEST_VER."
echo ""
gh release list --limit 8

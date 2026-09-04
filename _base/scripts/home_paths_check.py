#!/usr/bin/env python3
"""home_paths_check.py — объявленные хранилища вне git существуют и описаны?

🔴 ПОВОД, ЗАМЕРЕН 04.09.2026. Каталог секретов переименован кампанией единого
нейминга 03.09 (`recovery_kits` → `recovery-kits`). Переименование верное —
и **не доехало до четырёх документов**, включая `misc-vault/00-secrets-index/`,
единственную опись кодов восстановления. Опись вела в несуществующий каталог.

**Опись, ведущая по несуществующему пути, хуже отсутствия описи:** отсутствие
заставляет искать, ложный путь убеждает, что искать негде.

🔴 ПОЧЕМУ НЕ «ПРОВЕРЯТЬ ВСЕ ПУТИ В ДОКУМЕНТАХ» — ЭТО ИЗМЕРЕНО И ОТВЕРГНУТО.
Первая редакция скрипта делала именно так и дала **66 находок в базе, из них
дефектов — ноль**. Разбор каждой показал три законные причины назвать
несуществующий путь:

  · команда, которую надо ВЫПОЛНИТЬ: `brew bundle dump --file=~/Documents/Brewfile`
    — файл появится ПОСЛЕ, до того его нет по построению;
  · констатация отсутствия: «`~/.cursor` — Cursor на машине нет, остаток удалённой»;
  · план: «убрать `~/Downloads/vk-graph.env.backup`» — верен ровно тогда,
    когда файла уже нет.

> **Разница между «указатель протух» и «так и задумано» лежит в намерении
> автора. Машине оно не видно.** Настраивать фильтры, пока не станет зелено,
> значило бы подгонять проверку под ответ — гейт бы позеленел, а дефект
> остался бы неотличим от шума.

ЧТО ВМЕСТО. Автор **объявляет** внешнее хранилище строкой — тот же приём,
что `.runtime-writes` (`scripts/runtime_writes.py`): не список из головы
проверяющего, а декларация владельца документа. Тогда проверяется ровно то,
что кто-то назвал хранилищем, и ложных срабатываний нет по построению.

ФОРМАТ — `EXTERNAL-STORES.tsv` в корне репы, TAB-разделённый, `#` комментарий:

    путь<TAB>что там лежит<TAB>какой документ указывает

ЧТО ПРОВЕРЯЕТСЯ по каждой строке:
  1. каталог существует;
  2. документ-указатель существует;
  3. 🔴 документ называет **этот же** путь — иначе указатель разошёлся
     с декларацией, и это ровно исходный дефект.

ГРАНИЦА. Проверка не знает, полна ли опись содержимым: файл, лежащий в
хранилище и не попавший в документ, ею не ловится. Это работа сверки, а не гейта.

ЗАПУСК:
    python3 scripts/home_paths_check.py            # база
    python3 scripts/home_paths_check.py --all      # все репы системы
    python3 scripts/home_paths_check.py <репа>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _roots import resolve_roots  # noqa: E402

HOME = Path.home()
DECL = "EXTERNAL-STORES.tsv"


def expand(raw: str) -> Path:
    return HOME / raw[2:] if raw.startswith("~/") else Path(raw)


def check(repo: Path) -> tuple[int, int, list[str]]:
    """(проверено, нарушений, сообщения)."""
    decl = repo / DECL
    if not decl.exists():
        return 0, 0, []

    msgs: list[str] = []
    checked = bad = 0
    for n, line in enumerate(decl.read_text(encoding="utf-8").splitlines(), 1):
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 3:
            msgs.append(f"   {DECL}:{n} 🔴 нужно три колонки через TAB, получено {len(cols)}")
            bad += 1
            continue
        raw_path, what, pointer = (c.strip() for c in cols[:3])
        checked += 1

        if not expand(raw_path).exists():
            msgs.append(f"   {DECL}:{n} 🔴 хранилища нет на диске: {raw_path} ({what})")
            bad += 1
            continue

        doc = repo / pointer
        if not doc.exists():
            msgs.append(f"   {DECL}:{n} 🔴 указателя нет в репе: {pointer}")
            bad += 1
            continue

        text = doc.read_text(encoding="utf-8", errors="ignore")
        needle = raw_path.rstrip("/")
        if needle not in text:
            msgs.append(f"   {DECL}:{n} 🔴 {pointer} НЕ называет {needle} — "
                        "указатель разошёлся с декларацией")
            bad += 1
    return checked, bad, msgs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", default="base-repo")
    ap.add_argument("--all", action="store_true", help="все репы системы")
    args = ap.parse_args()

    _base, root, _ = resolve_roots(__file__)
    repos = ([d for d in sorted(root.iterdir())
              if d.is_dir() and (d / "VERSION").exists()]
             if args.all else [root / args.repo])

    total_checked = total_bad = declared = 0
    for repo in repos:
        if not repo.exists():
            print(f"🔴 нет репы: {repo.name}")
            return 2
        c, b, msgs = check(repo)
        if c or msgs:
            declared += 1
        total_checked += c
        total_bad += b
        if msgs:
            print(f"\n{repo.name}:")
            print("\n".join(msgs))

    scope = f"{len(repos)} реп" if args.all else repos[0].name
    print(f"\nИТОГ: {scope} · объявлено хранилищ {total_checked} "
          f"в {declared} репе(ах) · нарушений {total_bad}")
    if total_bad:
        print("Указатель, ведущий по несуществующему пути, убеждает, что искать негде.")
        return 1
    if not total_checked:
        print(f"🟡 ни одна репа не объявила {DECL} — проверять нечего.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

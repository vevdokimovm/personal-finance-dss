"""Запускает быстрый срез тестов для Stop-гейта с таймаутом на фазу.

`timeout`(1) — GNU coreutils, на голом macOS его нет (BSD userland), а
`gtimeout` есть не у всех (только через Homebrew coreutils) — тот же класс
проблемы, что и с jq в _parse.py. subprocess.run(timeout=...) работает
одинаково на macOS/Linux без внешних зависимостей.

Печатает JSON {"decision": "block", "reason": ...} на stdout при провале
любой фазы (падение тестов ИЛИ таймаут фазы) — фаза-таймаут это не «зелено»,
это «неизвестно», и фейлится закрыто (fail-closed), а не молча пропускается.
При полном успехе (или пустом срезе) не печатает ничего — exit 0, тихо.
"""

import json
import subprocess
import sys

LOG_PATH = "/tmp/finpilot-gate.log"
# Измерено на живой машине: 3 файла ~39 с (~13 с/файл); property-инварианты
# 20-51 с (среднее ~30, разовый всплеск 51 с сразу после 19-минутной полной
# суиты — тепловой/дисковый шум, не норма). Бюджеты — с запасом над этим,
# сумма (110 с) держит 10 с зазора до внешнего таймаута хука (120 с) —
# скрипт обязан успеть сам сформировать JSON-решение, а не быть убитым молча.
AFFECTED_TIMEOUT_S = 45
PROPERTY_TIMEOUT_S = 65
# Фан-аут через широко импортируемый модуль (напр. app/config.py) может дать
# 10+ затронутых файлов — измерено: 12 файлов не уложились и в 2 мин. Если
# совпадений больше порога, узкий срез для них СТРУКТУРНО не помещается в
# бюджет — гонять их здесь значило бы либо всегда блокировать (гейт
# становится непроходимым для любой правки в общем модуле), либо рисковать
# таймаутом. Вместо этого фаза по файлам пропускается (не «зелено» через
# силу, а честно «не в этот раз») — остаются инварианты матмодели, а полное
# покрытие даёт полная суита в церемонии батча.
MAX_AFFECTED_FILES = 3


def run_phase(pybin: str, args: list[str], timeout_s: int, log) -> tuple[int, bool]:
    """Возвращает (returncode, timed_out). returncode=-1 при таймауте."""
    try:
        proc = subprocess.run(
            [pybin, "-m", "pytest", "-q", "-x", *args],
            timeout=timeout_s,
            capture_output=True,
            text=True,
        )
        log.write(proc.stdout)
        log.write(proc.stderr)
        return proc.returncode, False
    except subprocess.TimeoutExpired as exc:
        if exc.stdout:
            out = exc.stdout if isinstance(exc.stdout, str) else exc.stdout.decode(errors="replace")
            log.write(out)
        if exc.stderr:
            err = exc.stderr if isinstance(exc.stderr, str) else exc.stderr.decode(errors="replace")
            log.write(err)
        log.write(f"\n[фаза не уложилась в {timeout_s} с — прервана]\n")
        return -1, True


def main() -> None:
    pybin = sys.argv[1]
    affected = sys.argv[2:]

    timed_out = False
    with open(LOG_PATH, "w", encoding="utf-8") as log:
        rc = 0
        if affected and len(affected) > MAX_AFFECTED_FILES:
            log.write(
                f"=== Затронутые тесты: {len(affected)} файлов, порог {MAX_AFFECTED_FILES} — "
                "фаза пропущена (фан-аут через общий модуль, не помещается в бюджет). "
                "Полное покрытие — полная суита в церемонии батча. ===\n"
            )
        elif affected:
            log.write(f"=== Затронутые тесты ({len(affected)}) ===\n")
            rc, to = run_phase(pybin, ["-m", "not slow", *affected], AFFECTED_TIMEOUT_S, log)
            timed_out = timed_out or to

        if rc == 0:
            log.write("\n=== Инварианты матмодели (property) ===\n")
            rc, to = run_phase(pybin, ["-m", "property and not slow"], PROPERTY_TIMEOUT_S, log)
            timed_out = timed_out or to

    if rc == 0:
        return

    tail = open(LOG_PATH, encoding="utf-8", errors="replace").read().splitlines()[-25:]
    if timed_out:
        # INV-MACHINE-LOAD (2026-08-12/13, повтор 2026-08-14): дважды таймаут фазы оказывался
        # НЕ зависшим тестом, а перегрузкой хоста сторонними процессами (load average на порядок
        # выше числа ядер) — оба раза чинили не тест, а закрывали лишние приложения. Проверка
        # `uptime` дешевле повторного прогона и сразу отличает «код виноват» от «машина не
        # тянет» — ставим её первым шагом в самом сообщении, а не только в разборе, который
        # молча лежит в docs/ и не помог с первого раза.
        extra = (
            " (срез не уложился в бюджет — см. лог). ПЕРЕД починкой кода: `uptime` — "
            "если 1-мин. load average заметно выше числа ядер, это, вероятнее, внешняя "
            "перегрузка машины (см. docs/reports/investigations/"
            "machine_load_gate_timeout_investigation.md, INV-MACHINE-LOAD, уже 2 случая), "
            "не зависший тест — не чини код, разберись с нагрузкой хоста и прогони заново."
        )
    else:
        extra = ""
    reason = (
        f"Быстрый срез тестов не прошёл{extra} — задача не завершена. Почини и прогони снова.\n"
        + "\n".join(tail)
        + f"\nПолный лог: {LOG_PATH}"
        + "\nЭто узкий срез (изменённые файлы + инварианты матмодели), не полная суита — "
        + "прогони её перед сдачей батча: python -m tools.preflight"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


if __name__ == "__main__":
    main()

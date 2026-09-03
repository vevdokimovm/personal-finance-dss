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
        # INV-MACHINE-LOAD: СЕМЬ эпизодов (2026-08-12/13, 08-14, 08-19 ×2, 09-02, 09-03 ×2).
        # Ни разу таймаут фазы не оказался зависшим тестом — каждый раз это была конкуренция
        # за CPU. Проверка `uptime` дешевле повторного прогона и сразу отличает «код виноват»
        # от «машина не тянет», поэтому стоит первым шагом в самом сообщении, а не только
        # в разборе, который молча лежит в docs/ и с первого раза не помог.
        #
        # 🔴 Эпизод 6 (2026-09-03) добавил важное уточнение: load average был 5.39 при
        # 8 ядрах, то есть НИЖЕ порога — и срез всё равно не уложился. Виноваты были
        # ОДНОВРЕМЕННЫЙ полный pytest этой же сессии и iTerm2 на 209% CPU. Значит низкий
        # load average вину не снимает: важна не только суммарная нагрузка, но и то, с кем
        # именно конкурирует срез. Полный прогон в фоне — сам по себе достаточная причина.
        extra = (
            " (срез не уложился в бюджет — см. лог). ПЕРЕД починкой кода проверь ДВА "
            "источника конкуренции за CPU, в этом порядке:\n"
            "  1) `ps -Ao pid,etime,%cpu,comm -r | head -5` — идёт ли ПРЯМО СЕЙЧАС твой же "
            "полный прогон в фоне или тяжёлое приложение (iTerm2 регулярно берёт два ядра). "
            "Этого достаточно, чтобы срез не уложился, даже когда load average НИЖЕ числа "
            "ядер (эпизод 6, 2026-09-03: load 5.39 при 8 ядрах — и срез всё равно упал).\n"
            "  2) `uptime` — load average заметно выше числа ядер означает внешнюю "
            "перегрузку машины.\n"
            "Разбор: docs/reports/investigations/machine_load_gate_timeout_investigation.md "
            "(INV-MACHINE-LOAD, СЕМЬ эпизодов, ни один не оказался дефектом кода). "
            "Не чини код — дождись конца конкурирующего прогона и повтори."
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

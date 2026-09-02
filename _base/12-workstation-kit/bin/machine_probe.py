#!/usr/bin/env python3
"""machine_probe.py — снимок состояния Mac: железо, нагрузка, диск, сеть, батарея.

ЗАКАЗ ВЛАДЕЛЬЦА 02.09.2026: «скилл, который будет считывать состояние сети,
нагрузки процессора, нагрузки мака, температуры — и всё это понятно, красиво
агрегировать; какое состояние железа, где проблема может быть».

ПОЧЕМУ СКРИПТ, А НЕ АГЕНТ. Числа снимаются командами, а не суждением модели.
Агент нужен там, где надо ИСТОЛКОВАТЬ снимок; сам снимок обязан быть
воспроизводимым и одинаковым от запуска к запуску (`/auto` §1.1: сначала факт
с диска, потом суждение).

🔴 ЧТО ЗДЕСЬ ЕСТЬ ЧЕСТНО, А ЧТО НЕТ:
  · температура CPU на Intel-маках доступна только через `powermetrics`,
    а он требует sudo. Без пароля отдаётся температура БАТАРЕИ (ioreg) —
    и она подписана именно так, а не выдаётся за температуру процессора;
  · здоровье SSD полноценно читает `smartctl` (brew smartmontools). Без него
    берётся `diskutil` — он говорит только Verified/Failing, без счётчиков износа;
  · скорость сети меряется `networkQuality` и занимает ~15 секунд, поэтому
    включается флагом `--net`, а не молча в каждом запуске.

ПРЕДУСЛОВИЯ:
  · macOS (проверяется по `uname`); на другой системе скрипт отказывается сразу;
  · штатные утилиты `sysctl`, `vm_stat`, `top`, `ioreg`, `diskutil` на месте.

ПОСТУСЛОВИЯ:
  · на stdout — читаемый срез, либо валидный JSON при `--json`;
  · каждый показатель, который снять не удалось, назван словом «недоступно»
    с причиной, а не пропущен и не заменён нулём.

ИНВАРИАНТ: скрипт только ЧИТАЕТ. Ни одной команды, меняющей состояние машины,
здесь нет и быть не должно — иначе замер начнёт влиять на измеряемое.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import datetime as dt
import subprocess
import sys
import time
from datetime import datetime

# ── Пороги. Зелёное молчит; тревога — только на перейденном пороге.
#    Значения выбраны под эту машину (4 ядра, 8 ГБ) и объяснены строкой.
THRESHOLDS = {
    "load_per_core": 2.0,      # выше двух задач на ядро — очередь, а не работа
    "swap_used_mb": 1024,      # своп >1 ГБ означает, что памяти уже не хватает
    "disk_free_pct": 10,       # ниже 10 % macOS начинает вести себя странно
    "battery_health_pct": 80,  # Apple считает батарею изношенной ниже 80 %
    "mem_free_mb": 512,        # меньше — система живёт за счёт сжатия
    # 🔴 Дней без бэкапа. Порог 7 — не про аккуратность, а про то, что
    # накопитель распаян и замене не подлежит: восстановление возможно
    # ТОЛЬКО из копии. Отсутствие копий вовсе — отдельная тревога, не «8 дней».
    "дней без бэкапа": 7,
}


def sh(cmd: list[str], timeout: int = 10) -> str:
    """Выполнить и вернуть stdout. Отказ — пустая строка, НЕ исключение.

    Отсутствие утилиты — законное состояние (`71` §7ж: не пробовал ≠ не работает),
    поэтому вызывающий обязан различать пустоту и ноль.
    """
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def hardware() -> dict:
    out = sh(["system_profiler", "SPHardwareDataType"], timeout=30)
    def grab(label: str) -> str:
        m = re.search(rf"{label}:\s*(.+)", out)
        return m.group(1).strip() if m else "недоступно"
    mem_b = sh(["sysctl", "-n", "hw.memsize"]).strip()
    return {
        "модель": grab("Model Name"),
        "идентификатор": grab("Model Identifier"),
        "процессор": grab("Processor Name") or grab("Chip"),
        "ядер": grab("Total Number of Cores"),
        "память_гб": round(int(mem_b) / 1024**3) if mem_b.isdigit() else "недоступно",
        "macos": f"{platform.mac_ver()[0]} ({sh(['sw_vers', '-buildVersion']).strip()})",
        "архитектура": platform.machine(),
    }


def load() -> dict:
    top = sh(["top", "-l1", "-n0"], timeout=20)
    m = re.search(r"Load Avg:\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)", top)
    cores = int(sh(["sysctl", "-n", "hw.ncpu"]).strip() or 1)
    la1 = float(m.group(1)) if m else None
    cpu = re.search(r"CPU usage:\s*([\d.]+)% user,\s*([\d.]+)% sys,\s*([\d.]+)% idle", top)
    return {
        "ядер": cores,
        "load_1_5_15": [float(m.group(i)) for i in (1, 2, 3)] if m else "недоступно",
        "load_на_ядро": round(la1 / cores, 2) if la1 is not None else "недоступно",
        "cpu_user_sys_idle": [float(cpu.group(i)) for i in (1, 2, 3)] if cpu else "недоступно",
    }


def memory() -> dict:
    vm = sh(["vm_stat"])
    page = 4096
    pm = re.search(r"page size of (\d+) bytes", vm)
    if pm:
        page = int(pm.group(1))
    def pages(label: str) -> int:
        m = re.search(rf"{label}:\s+(\d+)", vm)
        return int(m.group(1)) if m else 0
    free_mb = (pages("Pages free") + pages("Pages speculative")) * page // 1024**2
    swap = sh(["sysctl", "-n", "vm.swapusage"])
    sm = re.search(r"used\s*=\s*([\d.]+)M", swap)
    return {
        "свободно_мб": free_mb,
        "сжато_мб": pages("Pages occupied by compressor") * page // 1024**2,
        "своп_использован_мб": round(float(sm.group(1))) if sm else "недоступно",
    }


def disks() -> dict:
    df = sh(["df", "-k", "/System/Volumes/Data"]).splitlines()
    used = free = pct = "недоступно"
    if len(df) > 1:
        f = df[1].split()
        used, free = round(int(f[2]) / 1024**2, 1), round(int(f[3]) / 1024**2, 1)
        pct = round(free / (used + free) * 100, 1)
    info = sh(["diskutil", "info", "disk0"])
    def grab(label: str) -> str:
        m = re.search(rf"{label}:\s*(.+)", info)
        return m.group(1).strip() if m else "недоступно"
    smart = {"состояние": grab("SMART Status")}
    if shutil.which("smartctl"):
        s = sh(["smartctl", "-A", "/dev/disk0"], timeout=20)
        for key, label in (("Percentage Used", "износ_проц"),
                           ("Data Units Written", "записано")):
            m = re.search(rf"{key}:?\s*([\d,.]+)", s)
            if m:
                smart[label] = m.group(1)
    else:
        smart["подробности"] = "недоступно: нет smartctl (brew install smartmontools)"
    return {"модель": grab("Device / Media Name"), "занято_гб": used,
            "свободно_гб": free, "свободно_проц": pct, "smart": smart}


def battery() -> dict:
    io = sh(["ioreg", "-r", "-c", "AppleSmartBattery"])
    def num(key: str):
        m = re.search(rf'"{key}"\s*=\s*(\d+)', io)
        return int(m.group(1)) if m else None
    design, now, cycles = num("DesignCapacity"), num("AppleRawMaxCapacity"), num("CycleCount")
    temp = num("Temperature")
    return {
        "циклов": cycles if cycles is not None else "недоступно",
        "здоровье_проц": round(now / design * 100, 1) if design and now else "недоступно",
        "температура_батареи_c": round(temp / 100, 1) if temp else "недоступно",
        "питание": "сеть" if "AC Power" in sh(["pmset", "-g", "batt"]) else "батарея",
        # 🔴 Честно: это температура БАТАРЕИ. Температура CPU на Intel требует
        # sudo powermetrics и потому здесь не выдаётся за неё.
        "температура_cpu": "недоступно без sudo (powermetrics)",
    }


def network(measure: bool = False) -> dict:
    """Состояние сети.

    🔴 Маршрут по умолчанию при включённом VPN указывает на туннель (`utunNN`),
    у которого нет адреса в понимании `ipconfig getifaddr` — первая редакция
    из-за этого печатала «нет адреса» и «нет ответа» на исправной сети.
    Поэтому туннель называется отдельно, а адрес берётся с ФИЗИЧЕСКОГО
    интерфейса, найденного перебором.
    """
    svc = sh(["route", "-n", "get", "default"])
    m = re.search(r"interface:\s*(\S+)", svc)
    route_iface = m.group(1) if m else "недоступно"
    vpn = route_iface.startswith(("utun", "ipsec", "ppp"))
    iface, ip = route_iface, ""
    if not vpn:
        ip = sh(["ipconfig", "getifaddr", route_iface]).strip()
    if not ip:
        # физический интерфейс: первый из en*, у которого есть адрес
        for cand in re.findall(r"^(en\d+):", sh(["ifconfig"]), re.M):
            got = sh(["ipconfig", "getifaddr", cand]).strip()
            if got:
                iface, ip = cand, got
                break
    ping = sh(["ping", "-c", "3", "-t", "5", "1.1.1.1"], timeout=15)
    pm = re.search(r"=\s*[\d.]+/([\d.]+)/", ping)
    res = {
        "интерфейс": iface,
        "ip": ip or "нет адреса",
        "пинг_мс": round(float(pm.group(1)), 1) if pm else "нет ответа",
        "через_vpn": "да" if vpn else "нет",
        "маршрут_по_умолчанию": route_iface,
    }
    if measure and shutil.which("networkQuality"):
        q = sh(["networkQuality", "-s"], timeout=90)
        for key, label in (("Downlink capacity", "скачивание"), ("Uplink capacity", "отдача")):
            m = re.search(rf"{key}:\s*([\d.]+\s*\w+ps)", q)
            res[label] = m.group(1) if m else "недоступно"
    elif measure:
        res["скорость"] = "недоступно: нет networkQuality"
    return res


def top_processes(n: int = 5) -> list[dict]:
    out = sh(["ps", "-Aceo", "pid,pcpu,pmem,rss,comm", "-r"], timeout=20)
    rows = []
    for line in out.splitlines()[1:n + 1]:
        f = line.split(None, 4)
        if len(f) == 5:
            rows.append({"pid": f[0], "cpu": float(f[1]), "mem": float(f[2]),
                         "rss_мб": round(int(f[3]) / 1024), "имя": f[4]})
    return rows


def diagnose(snap: dict) -> list[str]:
    """Перейденные пороги — и только они. Зелёное молчит намеренно."""
    bad = []
    lp = snap["нагрузка"].get("load_на_ядро")
    if isinstance(lp, (int, float)) and lp >= THRESHOLDS["load_per_core"]:
        bad.append(f"нагрузка {lp} на ядро (порог {THRESHOLDS['load_per_core']}) — "
                   f"очередь задач длиннее, чем машина успевает разбирать")
    sw = snap["память"].get("своп_использован_мб")
    if isinstance(sw, (int, float)) and sw >= THRESHOLDS["swap_used_mb"]:
        bad.append(f"своп {sw} МБ (порог {THRESHOLDS['swap_used_mb']}) — "
                   f"оперативной памяти не хватает, машина пишет её на диск")
    mf = snap["память"].get("свободно_мб")
    if isinstance(mf, (int, float)) and mf <= THRESHOLDS["mem_free_mb"]:
        bad.append(f"свободной памяти {mf} МБ (порог {THRESHOLDS['mem_free_mb']})")
    dp = snap["диск"].get("свободно_проц")
    if isinstance(dp, (int, float)) and dp <= THRESHOLDS["disk_free_pct"]:
        bad.append(f"на диске свободно {dp} % (порог {THRESHOLDS['disk_free_pct']} %)")
    bh = snap["батарея"].get("здоровье_проц")
    if isinstance(bh, (int, float)) and bh <= THRESHOLDS["battery_health_pct"]:
        bad.append(f"здоровье батареи {bh} % (порог {THRESHOLDS['battery_health_pct']} %) — "
                   f"{snap['батарея'].get('циклов')} циклов")
    if snap["диск"]["smart"].get("состояние") not in ("Verified", "недоступно"):
        bad.append(f"SMART диска: {snap['диск']['smart'].get('состояние')}")

    b = snap.get("бэкап", {})
    if b.get("последняя_копия", "").startswith("🔴"):
        bad.append("🔴 РЕЗЕРВНЫХ КОПИЙ НЕТ ВООБЩЕ — накопитель распаян, "
                   "восстанавливать будет неоткуда")
    elif isinstance(b.get("дней_без_бэкапа"), int) and \
            b["дней_без_бэкапа"] >= THRESHOLDS["дней без бэкапа"]:
        bad.append(f"последний бэкап {b['дней_без_бэкапа']} дней назад "
                   f"(порог {THRESHOLDS['дней без бэкапа']})")
    return bad


# ── Оценка износа компонентов ───────────────────────────────────────────
#
# ЗАКАЗ ВЛАДЕЛЬЦА 02.09.2026: «оценка состояния ноута, его компонентов…
# сколько проживёт, насколько ему плохо, нужна ли починка и насколько важно».
#
# 🔴 ЧЕСТНАЯ ГРАНИЦА, БЕЗ КОТОРОЙ ОЦЕНКА ВРЁТ. Отказ электроники —
# не износ, а событие: он приходит внезапно и предсказанию по счётчикам
# не поддаётся. Здесь оценивается ТОЛЬКО то, у чего есть измеримый ресурс:
# циклы батареи, статус SMART, свободное место. Всё остальное — материнская
# плата, клавиатура, экран, разъёмы — не оценивается вовсе, и об этом
# сказано прямо, а не заменено успокоительным «всё хорошо».
#
# 🔴 «Сколько проживёт» считается только для БАТАРЕИ и только по ЛИНЕЙНОЙ
# экстраполяции циклов. Это грубо: деградация нелинейна и зависит от
# температуры и глубины разрядов. Число даётся как порядок величины,
# и рядом стоит оговорка.

# Ресурс батареи по спецификации Apple для ноутбуков с 2010 года.
BATTERY_RATED_CYCLES = 1000


def backup_state() -> dict:
    """Есть ли резервные копии и когда была последняя.

    🔴 Заведено 02.09.2026, и повод стоил разбора. Time Machine показывал
    настроенное назначение и включённый автобэкап — а копий не существовало
    НИ ОДНОЙ: диск назначения отключён, и система об этом молчит.

    Отсюда правило проверки: спрашивать не «настроен ли», а «когда была
    последняя копия». Настройка без копии неотличима от копии по всем
    признакам, кроме одного — самой копии.
    """
    dest = sh(["tmutil", "destinationinfo"], 20)
    name = re.search(r"Name\s*:\s*(.+)", dest)
    latest = sh(["tmutil", "latestbackup"], 30).strip()
    listing = sh(["tmutil", "listbackups"], 30)

    res = {
        "назначение": name.group(1).strip() if name else "не настроено",
        "последняя_копия": latest or "🔴 НЕТ НИ ОДНОЙ",
        "дней_без_бэкапа": None,
    }
    if latest:
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", latest)
        if m:
            when = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            res["дней_без_бэкапа"] = (dt.date.today() - when).days
    elif "No machine directory" in listing or not listing.strip():
        res["🔴 диагноз"] = ("назначение настроено, копий не существует — "
                            "диск назначения, вероятно, отключён")
    return res


def health() -> dict:
    """Износ компонентов и остаток ресурса — там, где он измерим.

    Отвечает не «сломается ли», а «сколько ресурса израсходовано».
    Разница существенна: первое непредсказуемо, второе считается.
    """
    io = sh(["ioreg", "-r", "-c", "AppleSmartBattery"])

    def num(key: str):
        m = re.search(rf'"{key}"\s*=\s*(\d+)', io)
        return int(m.group(1)) if m else None

    design, now = num("DesignCapacity"), num("AppleRawMaxCapacity")
    cycles, fail = num("CycleCount"), num("PermanentFailureStatus")
    cond = re.search(r"Condition:\s*(.+)", sh(["system_profiler", "SPPowerDataType"], 30))

    items = []

    # ── Батарея: единственный компонент с объявленным ресурсом
    if cycles is not None and design and now:
        wear = round(100 - now / design * 100, 1)
        left_cycles = max(BATTERY_RATED_CYCLES - cycles, 0)
        # Расход циклов в день неизвестен (нет истории), поэтому берётся
        # средний бытовой ориентир 0.7 цикла в день и НАЗЫВАЕТСЯ допущением.
        months = round(left_cycles / 0.7 / 30) if left_cycles else 0
        verdict = ("менять пора" if wear >= 30 or (cond and "Service" in cond.group(1))
                   else "изношена, но работает" if wear >= 20 else "в норме")
        items.append({
            "узел": "батарея",
            "износ_проц": wear,
            "израсходовано_ресурса_проц": round(cycles / BATTERY_RATED_CYCLES * 100),
            "состояние_по_macos": cond.group(1).strip() if cond else "недоступно",
            "вердикт": verdict,
            "остаток_циклов": left_cycles,
            "оценка_месяцев": months,
            "🔴 оговорка": "линейная экстраполяция при допущении 0.7 цикла в день; "
                           "деградация нелинейна, число — порядок величины",
            "аварийный_отказ": "нет" if fail == 0 else f"🔴 код {fail}",
        })

    # ── Диск: SMART без smartctl говорит только «жив / умирает»
    smart = re.search(r"SMART Status:\s*(.+)", sh(["diskutil", "info", "disk0"]))
    st = smart.group(1).strip() if smart else "недоступно"
    disk = {
        "узел": "накопитель",
        "smart": st,
        "вердикт": "в норме" if st == "Verified" else f"🔴 {st}",
    }
    if shutil.which("smartctl"):
        s = sh(["smartctl", "-a", "/dev/disk0"], timeout=30)

        def field(pat: str, cast=int):
            m = re.search(pat, s)
            return cast(m.group(1).replace(",", "")) if m else None

        used = field(r"Percentage Used:\s*(\d+)%")
        spare = field(r"Available Spare:\s*(\d+)%")
        spare_min = field(r"Available Spare Threshold:\s*(\d+)%")
        written = field(r"Data Units Written:\s*([\d,]+)")
        hours = field(r"Power On Hours:\s*([\d,]+)")
        cycles = field(r"Power Cycles:\s*([\d,]+)")
        unsafe = field(r"Unsafe Shutdowns:\s*([\d,]+)")
        warn = re.search(r"Critical Warning:\s*(0x[0-9a-f]+)", s)

        disk.update({
            "израсходовано_ресурса_проц": used,
            "резерв_блоков_проц": spare,
            "резерв_порог_проц": spare_min,
            "записано_тб": round(written * 512 * 1000 / 1e12, 1) if written else None,
            "часов_работы": hours,
            "включений": cycles,
            "некорректных_выключений": unsafe,
            "критическое_предупреждение": warn.group(1) if warn else "недоступно",
        })

        # 🔴 ВЕРДИКТ СТРОИТСЯ НА ДВУХ ЧИСЛАХ, А НЕ НА ОДНОМ, и это важно.
        #
        # `Percentage Used` — счётчик ИЗРАСХОДОВАННОГО РЕСУРСА ЗАПИСИ по мерке
        # производителя. Он может превысить 100 %, и это не поломка: гарантийный
        # ресурс кончился, ячейки работают дальше.
        #
        # `Available Spare` — доля НЕТРОНУТЫХ резервных блоков, которыми диск
        # подменяет отказавшие. Вот она и есть настоящий признак умирания:
        # пока резерв полон, отказавших ячеек нет вовсе.
        #
        # Судить по одному `Percentage Used` — значит паниковать раньше времени;
        # судить по одному SMART Verified — значит не заметить износа вовсе.
        if warn and warn.group(1) != "0x00":
            disk["вердикт"] = "🔴 критическое предупреждение накопителя — бэкап немедленно"
        elif spare is not None and spare_min is not None and spare <= spare_min:
            disk["вердикт"] = "🔴 резервные блоки на исходе — диск подменяет отказавшие ячейки"
        elif used is not None and used >= 100:
            disk["вердикт"] = ("ресурс записи выработан, но резерв не тронут — "
                              "работает, держать бэкап")
        elif used is not None and used >= 80:
            disk["вердикт"] = "ресурс записи на исходе"
        disk["🔴 как читать"] = (
            "«Израсходовано» — счётчик записи по мерке производителя, он может "
            "перевалить за 100 % и это не отказ. Настоящий признак умирания — "
            "падение резерва блоков ниже порога. Отказ SSD всё равно приходит "
            "внезапно: бэкап важнее любого счётчика.")
    else:
        disk["🔴 оговорка"] = ("износ ячеек не измерен: нет smartctl. "
                              "SMART Verified означает «не отказал», а не «не изношен». "
                              "Поставить: brew install smartmontools")
    items.append(disk)

    # ── То, что НЕ оценивается. Названо явно, чтобы молчание не читалось
    #    как «здесь всё хорошо» (`71` §7ж: не проверял ≠ работает).
    unknown = ["материнская плата", "клавиатура", "экран и подсветка",
               "разъёмы и шлейфы", "динамики", "камера"]
    fans = "недоступно без sudo (powermetrics) или сторонней утилиты"

    return {
        "узлы": items,
        "вентиляторы": fans,
        "не_оценивается": unknown,
        "🔴 главное": "Отказ электроники — событие, а не износ: приходит внезапно "
                      "и по счётчикам не предсказывается. Оценён только измеримый "
                      "ресурс; отсутствие тревоги здесь НЕ означает исправности "
                      "неизмеренного.",
    }


def collect(measure_net: bool = False) -> dict:
    snap = {
        "снято": datetime.now().isoformat(timespec="seconds"),
        "здоровье": health(),
        "бэкап": backup_state(),
        "железо": hardware(),
        "нагрузка": load(),
        "память": memory(),
        "диск": disks(),
        "батарея": battery(),
        "сеть": network(measure_net),
        "топ_процессов": top_processes(),
    }
    snap["перейдено_порогов"] = diagnose(snap)
    return snap


def render(snap: dict) -> None:
    h, l, m, d, b, n = (snap["железо"], snap["нагрузка"], snap["память"],
                        snap["диск"], snap["батарея"], snap["сеть"])
    print(f"╭─ {h['модель']} · {h['идентификатор']} · macOS {h['macos']}")
    print(f"│  {h['процессор']} · {h['ядер']} ядер · {h['память_гб']} ГБ RAM · {h['архитектура']}")
    print("╰─")
    print(f"\nНАГРУЗКА   load {l['load_1_5_15']} → {l['load_на_ядро']} на ядро")
    if l["cpu_user_sys_idle"] != "недоступно":
        u, s, i = l["cpu_user_sys_idle"]
        print(f"           CPU: {u}% пользовательские · {s}% система · {i}% простой")
    print(f"ПАМЯТЬ     свободно {m['свободно_мб']} МБ · сжато {m['сжато_мб']} МБ · "
          f"своп {m['своп_использован_мб']} МБ")
    print(f"ДИСК       {d['модель']} · занято {d['занято_гб']} ГБ, свободно {d['свободно_гб']} ГБ "
          f"({d['свободно_проц']} %) · SMART {d['smart']['состояние']}")
    print(f"БАТАРЕЯ    здоровье {b['здоровье_проц']} % · {b['циклов']} циклов · "
          f"{b['температура_батареи_c']} °C · питание от {b['питание']}")
    print(f"СЕТЬ       {n['интерфейс']} · {n['ip']} · пинг {n['пинг_мс']} мс")
    for k in ("скачивание", "отдача", "скорость"):
        if k in n:
            print(f"           {k}: {n[k]}")
    print("\nТОП ПО CPU")
    for p in snap["топ_процессов"]:
        print(f"   {p['cpu']:>5.1f}%  {p['rss_мб']:>5} МБ  {p['имя'][:44]}")
    h = snap.get("здоровье", {})
    if h:
        print("\nИЗНОС КОМПОНЕНТОВ")
        for u in h["узлы"]:
            if u["узел"] == "батарея":
                print(f"   батарея      износ {u['износ_проц']} % · "
                      f"{u['израсходовано_ресурса_проц']} % ресурса циклов · "
                      f"{u['вердикт']}")
                print(f"                macOS: {u['состояние_по_macos']} · "
                      f"осталось ~{u['остаток_циклов']} циклов "
                      f"(≈{u['оценка_месяцев']} мес при 0.7 цикла/день)")
            else:
                extra = (f" · износ ячеек {u['израсходовано_ресурса_проц']} %"
                         if "израсходовано_ресурса_проц" in u else "")
                print(f"   накопитель   SMART {u['smart']} · {u['вердикт']}{extra}")
        print(f"   вентиляторы  {h['вентиляторы']}")
        b = snap.get("бэкап", {})
        if b:
            print(f"   бэкап        {b['последняя_копия']}"
                  + (f" ({b['дней_без_бэкапа']} дн назад)"
                     if isinstance(b.get("дней_без_бэкапа"), int) else "")
                  + f" · назначение: {b['назначение']}")
        print(f"   🔴 НЕ оценивалось: {', '.join(h['не_оценивается'])}")
        print("      Отказ электроники — событие, а не износ: по счётчикам")
        print("      не предсказывается. Тишина здесь ≠ исправность.")

    bad = snap["перейдено_порогов"]
    print()
    if bad:
        print(f"🔴 ПЕРЕЙДЕНО ПОРОГОВ: {len(bad)}")
        for line in bad:
            print(f"   · {line}")
    else:
        print("🟢 все пороги в норме — зелёное молчит, подробности в --json")


def watch(interval: float = 2.0) -> int:
    """Живая строка состояния — как статус-бар iTerm, но с нашими числами.

    ЗАКАЗ ВЛАДЕЛЬЦА 02.09.2026: «а он же будет уметь делать, как iTerm вон
    показывает справа вверху всякие показатели устройства?»

    🔴 РАЗНИЦА ЖАНРОВ, И ОНА НЕ КОСМЕТИЧЕСКАЯ. Полный срез (`collect`) снимает
    железо, SMART и батарею — это секунды работы и десятки запусков утилит.
    Опрашивать их каждые две секунды бессмысленно: износ SSD не меняется
    за две секунды, а нагрузка меняется постоянно.
    Поэтому здесь снимаются ТОЛЬКО быстрые показатели, а медленные —
    один раз при старте и показываются как неподвижная шапка.
    """
    import shutil as _sh
    fixed = {"hw": hardware(), "health": health()}
    hw, dh = fixed["hw"], fixed["health"]
    disk_item = next((u for u in dh["узлы"] if u["узел"] == "накопитель"), {})
    bat_item = next((u for u in dh["узлы"] if u["узел"] == "батарея"), {})

    # Счётчики сети: считаем ПРИРОСТ между тиками, а не абсолют.
    def netbytes() -> tuple[int, int]:
        out = sh(["netstat", "-ib"])
        rx = tx = 0
        seen = set()
        for line in out.splitlines()[1:]:
            f = line.split()
            if len(f) < 10 or f[0] in seen or f[0].startswith("lo"):
                continue
            seen.add(f[0])
            try:
                rx += int(f[6]); tx += int(f[9])
            except (ValueError, IndexError):
                continue
        return rx, tx

    prev = netbytes()
    print(f"\033[1m{hw['модель']} · {hw['процессор']} · {hw['память_гб']} ГБ · "
          f"macOS {hw['macos']}\033[0m")
    print(f"диск: SMART {disk_item.get('smart', '?')} · износ "
          f"{disk_item.get('израсходовано_ресурса_проц', '?')} % · резерв "
          f"{disk_item.get('резерв_блоков_проц', '?')} %   |   батарея: "
          f"{bat_item.get('износ_проц', '?')} % износа, "
          f"{bat_item.get('остаток_циклов', '?')} циклов")
    print("─" * min(_sh.get_terminal_size().columns, 100))
    print("Ctrl+C — выход\n")
    try:
        while True:
            l, m, d = load(), memory(), disks()
            rx, tx = netbytes()
            drx = max(rx - prev[0], 0) / interval / 1024
            dtx = max(tx - prev[1], 0) / interval / 1024
            prev = (rx, tx)
            cpu = l["cpu_user_sys_idle"]
            busy = round(100 - cpu[2], 1) if cpu != "недоступно" else "?"
            # \r + \033[K — перерисовка строки на месте, без прокрутки
            print(f"\r\033[K cpu {busy:>5} %  ·  load {l['load_на_ядро']:>5}/ядро  ·  "
                  f"память {m['свободно_мб']:>5} МБ своб  ·  своп {m['своп_использован_мб']:>5} МБ  ·  "
                  f"диск {d['свободно_гб']:>5} ГБ  ·  сеть ↓{drx:6.1f} ↑{dtx:6.1f} КБ/с",
                  end="", flush=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n")
        return 0


def main() -> int:
    if platform.system() != "Darwin":
        print("🔴 Скрипт снимает состояние macOS; здесь система "
              f"{platform.system()}. Отказ, а не догадка.", file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(description="Снимок состояния Mac")
    ap.add_argument("--json", action="store_true", help="выдать JSON вместо текста")
    ap.add_argument("--net", action="store_true",
                    help="замерить скорость сети (networkQuality, ~15 с)")
    ap.add_argument("--watch", action="store_true",
                    help="живая строка состояния, как статус-бар iTerm")
    ap.add_argument("--interval", type=float, default=2.0,
                    help="период обновления для --watch, секунд (по умолчанию 2)")
    args = ap.parse_args()
    if args.watch:
        return watch(args.interval)
    snap = collect(args.net)
    if args.json:
        print(json.dumps(snap, ensure_ascii=False, indent=2))
    else:
        render(snap)
    return 1 if snap["перейдено_порогов"] else 0


if __name__ == "__main__":
    sys.exit(main())

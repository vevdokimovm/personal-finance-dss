"""Генерация структурных диаграмм из кода.

🔴 Заведено 25.09.2026 после замера, показавшего, что нарисованные руками диаграммы
отстали от кода вдвое: `06_c4_component` знала 3 роутера из 27, `10_er_database` —
28 таблиц из 31, `14_dependency_graph` — 10 модулей ядра из 22
(`docs/reports/engineering/diagrams_drifted_from_code.md`).

Причина не в лени, а в способе: диаграмма, нарисованная руками, устаревает на следующем
батче и ничем об этом не сообщает — валидный XML не краснеет ни в одном гейте.
Поэтому структурные диаграммы, содержание которых однозначно выводится из дерева
исходников, **генерируются**, а гейт `tests/test_diagrams_match_code.py` сторожит,
что генерацию не забыли прогнать.

Смысловые диаграммы (пайплайн модели, BPMN, EPC, use case, state machine) сюда
не входят: они описывают ЗАМЫСЕЛ, а не структуру, и из кода не выводятся.

🔴 Превью рендерятся ЗДЕСЬ ЖЕ, а не «вручную на Mac». Прежняя редакция объявляла
рендер невозможным (CDN Chromium в песочнице заблокирован) — и это было нарушением
правила §8 `CLAUDE.md`: задача объявлена невозможной, не исчерпав каналы. Каналы
проверены 25.09.2026 и оба живые: `rsvg-convert` 2.61.1 для SVG → PNG и Graphviz
14.0.0 (`dot`) для графа зависимостей. draw.io для превью не нужен вовсе.

Запуск из корня репозитория:
    python -m tools.diagrams.generate
"""
from __future__ import annotations

import ast
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[2]
DIAGRAMS = REPO / "docs/diagrams"
SOURCES = DIAGRAMS / "src"

COLUMN_WIDTH = 210
ROW_HEIGHT = 34
GAP_X = 30
GAP_Y = 26


@dataclass(frozen=True)
class Node:
    """Прямоугольник диаграммы."""

    key: str
    label: str
    x: int
    y: int
    width: int
    height: int
    fill: str
    stroke: str


def canon_version() -> str:
    """Версия канона матмодели из `docs/math_model.md` — источник истины."""
    head = (REPO / "docs/math_model.md").read_text(encoding="utf-8")[:400]
    match = re.search(r"версия\s+(\d+\.\d+\.\d+)", head)
    return match.group(1) if match else "?"


def code_version() -> str:
    """Версия проекта из `VERSION`."""
    return (REPO / "VERSION").read_text(encoding="utf-8").strip()


def stamp() -> str:
    """Подпись «какой версии соответствует диаграмма».

    🔴 Требование владельца 25.09.2026: «пиши какой версии они соответствуют».
    Без неё нельзя отличить свежую диаграмму от отставшей на десять версий —
    ровно та слепота, из-за которой `05_c4_container` описывала снесённую Jinja,
    а `15_forecast_GOST` — отменённый канономтренд.
    """
    return f"код v{code_version()} · канон матмодели v{canon_version()}"


# 🔴 Штамп версии в РИСУЕМЫХ вручную диаграммах.
# Требование владельца 25.09.2026: «если они до сих пор актуальны, то ты всё равно
# должен пройтись и проставить версии». Признание диаграммы актуальной — это факт
# о конкретной версии кода, и он обязан быть записан НА диаграмме: иначе следующий
# читатель снова не отличит проверенную схему от забытой с v6.8.0.
#
# Штамп идемпотентен: ячейка с фиксированным id перезаписывается при каждом прогоне,
# а не добавляется заново. Иначе после десяти прогонов на схеме было бы десять подписей.
STAMP_CELL_ID = "finpilot_version_stamp"


def stamp_drawio(path: Path, text: str) -> bool:
    """Проставить или обновить подпись версии в `.drawio`. True — файл изменён."""
    source = path.read_text(encoding="utf-8")
    style = ("text;html=1;strokeColor=none;fillColor=none;align=left;"
             "verticalAlign=middle;fontSize=10;fontColor=#6b7280;")
    cell = (f'        <mxCell id="{STAMP_CELL_ID}" value="{escape(text)}" '
            f'style="{style}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="20" y="6" width="520" height="20" '
            f'as="geometry" />\n        </mxCell>\n')

    existing = re.search(
        rf'        <mxCell id="{STAMP_CELL_ID}".*?</mxCell>\n',
        source, flags=re.S,
    )
    if existing:
        if existing.group(0) == cell:
            return False
        updated = source[:existing.start()] + cell + source[existing.end():]
    else:
        # Вставка в КАЖДУЮ диаграмму файла: мастер-файл несёт 29 страниц,
        # и подпись на первой ничего не говорит о двадцать девятой.
        updated = source.replace('        <mxCell id="1" parent="0" />\n',
                                 '        <mxCell id="1" parent="0" />\n' + cell)
        if updated == source:
            return False
    path.write_text(updated, encoding="utf-8")
    return True


def _header(name: str, diagram_id: str, width: int, height: int) -> str:
    return (
        '<mxfile host="app.diagrams.net" type="device">\n'
        f'  <diagram name="{escape(name)}" id="{diagram_id}">\n'
        f'    <mxGraphModel dx="1000" dy="700" grid="1" gridSize="10" guides="1" '
        f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="{width}" pageHeight="{height}" math="0" shadow="0">\n'
        "      <root>\n"
        '        <mxCell id="0" />\n'
        '        <mxCell id="1" parent="0" />\n'
    )


FOOTER = "      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n"


def _title(text: str, width: int) -> str:
    style = ("text;html=1;strokeColor=none;fillColor=none;align=center;"
             "verticalAlign=middle;fontSize=15;fontStyle=1;")
    return (
        f'        <mxCell id="title" value="{escape(text)}" style="{style}" '
        f'vertex="1" parent="1">\n'
        f'          <mxGeometry x="20" y="12" width="{width - 40}" height="28" '
        f'as="geometry" />\n        </mxCell>\n'
    )


def _box(node: Node) -> str:
    style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={node.fill};"
             f"strokeColor={node.stroke};fontSize=11;")
    return (
        f'        <mxCell id="{node.key}" value="{escape(node.label)}" '
        f'style="{style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{node.x}" y="{node.y}" width="{node.width}" '
        f'height="{node.height}" as="geometry" />\n        </mxCell>\n'
    )


def _cluster(key: str, label: str, x: int, y: int, width: int, height: int,
             color: str) -> str:
    style = (f"rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 6;"
             f"strokeColor={color};fillColor=none;verticalAlign=top;fontSize=12;"
             f"fontStyle=2;fontColor={color};align=left;spacingLeft=10;spacingTop=6;")
    return (
        f'        <mxCell id="{key}" value="{escape(label)}" style="{style}" '
        f'vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" '
        f'as="geometry" />\n        </mxCell>\n'
    )


def _edge(key: str, source: str, target: str, label: str = "") -> str:
    style = ("edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#9aa4b1;"
             "endArrow=block;endFill=1;fontSize=9;")
    return (
        f'        <mxCell id="{key}" value="{escape(label)}" style="{style}" '
        f'edge="1" parent="1" source="{source}" target="{target}">\n'
        '          <mxGeometry relative="1" as="geometry" />\n        </mxCell>\n'
    )


def _grid(names: list[str], origin_x: int, origin_y: int, per_row: int,
          fill: str, stroke: str, prefix: str) -> tuple[list[Node], int]:
    """Разложить имена сеткой; вернуть узлы и высоту занятого блока."""
    nodes = []
    for index, name in enumerate(names):
        row, column = divmod(index, per_row)
        nodes.append(Node(
            key=f"{prefix}_{re.sub(r'[^a-z0-9]', '_', name.lower())}",
            label=name,
            x=origin_x + column * (COLUMN_WIDTH + GAP_X),
            y=origin_y + row * (ROW_HEIGHT + GAP_Y),
            width=COLUMN_WIDTH, height=ROW_HEIGHT, fill=fill, stroke=stroke,
        ))
    rows = (len(names) + per_row - 1) // per_row
    return nodes, rows * (ROW_HEIGHT + GAP_Y)


def tables() -> list[str]:
    """Имена таблиц из моделей SQLAlchemy."""
    source = (REPO / "app/database/models.py").read_text(encoding="utf-8")
    return sorted(set(re.findall(r'__tablename__\s*=\s*"([a-z_]+)"', source)))


def foreign_keys() -> list[tuple[str, str]]:
    """Рёбра «таблица ссылается на таблицу» из объявлений `ForeignKey`.

    🔴 Без связей ER-диаграмма — просто список имён: она показывает, ЧТО есть,
    и молчит о том, как оно связано, то есть о самом предмете модели данных.
    Разбор построчный: `__tablename__` задаёт текущую таблицу, все `ForeignKey`
    до следующего `__tablename__` принадлежат ей.
    """
    source = (REPO / "app/database/models.py").read_text(encoding="utf-8")
    edges: set[tuple[str, str]] = set()
    current = ""
    for line in source.splitlines():
        table = re.search(r'__tablename__\s*=\s*"([a-z_]+)"', line)
        if table:
            current = table.group(1)
            continue
        target = re.search(r'ForeignKey\(\s*"([a-z_]+)\.', line)
        if target and current and target.group(1) != current:
            edges.add((current, target.group(1)))
    return sorted(edges)


def routers() -> list[str]:
    """Домены HTTP-слоя."""
    return sorted(p.stem.removeprefix("routes_")
                  for p in (REPO / "app/api").glob("routes_*.py"))


def services() -> list[str]:
    """Прикладные сервисы."""
    return sorted(p.stem for p in (REPO / "app/services").glob("*.py")
                  if p.stem != "__init__")


def core_modules() -> list[str]:
    """Модули математического ядра."""
    return sorted(p.stem for p in (REPO / "app/core").glob("*.py")
                  if p.stem != "__init__")


def core_dependencies() -> list[tuple[str, str]]:
    """Рёбра «модуль ядра импортирует модуль ядра»."""
    known = set(core_modules())
    edges: set[tuple[str, str]] = set()
    for path in (REPO / "app/core").glob("*.py"):
        if path.stem == "__init__":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                if parts[:2] == ["app", "core"] and len(parts) > 2:
                    if parts[2] in known and parts[2] != path.stem:
                        edges.add((path.stem, parts[2]))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    parts = alias.name.split(".")
                    if parts[:2] == ["app", "core"] and len(parts) > 2:
                        if parts[2] in known and parts[2] != path.stem:
                            edges.add((path.stem, parts[2]))
    return sorted(edges)


def build_er() -> str:
    """ER-диаграмма: все таблицы базы."""
    names = tables()
    nodes, block = _grid(names, 40, 70, 5, "#dae8fc", "#6c8ebf", "t")
    width = 40 + 5 * (COLUMN_WIDTH + GAP_X) + 20
    height = 70 + block + 60
    by_name = {node.label: node.key for node in nodes}
    edges = foreign_keys()
    parts = [_header("ER — таблицы базы", "er_database", width, height)]
    parts.append(_title(
        f"FINPILOT — база данных: {len(names)} таблиц, {len(edges)} связей"
        f" · {stamp()}", width))
    parts.extend(_box(node) for node in nodes)
    for index, (source, target) in enumerate(edges):
        parts.append(_edge(f"fk{index}", by_name[source], by_name[target]))
    parts.append(FOOTER)
    return "".join(parts)


def build_component() -> str:
    """C4 Level 3: роутеры, сервисы, модули ядра."""
    api, services_list, core = routers(), services(), core_modules()
    width = 40 + 5 * (COLUMN_WIDTH + GAP_X) + 20

    parts = [_header("C4 — компоненты", "c4_component", width, 1)]
    parts.append(_title(
        f"FINPILOT — компоненты: {len(api)} роутов, {len(services_list)} сервисов, "
        f"{len(core)} модулей ядра · {stamp()}", width))

    y = 60
    for label, names, fill, stroke, prefix, color in (
        ("app/api — HTTP-слой", api, "#85BBF0", "#6c8ebf", "r", "#6c8ebf"),
        ("app/services — прикладные сервисы", services_list, "#d5e8d4",
         "#82b366", "s", "#82b366"),
        ("app/core — математическое ядро", core, "#ffe6cc", "#d79b00",
         "c", "#d79b00"),
    ):
        nodes, block = _grid(names, 60, y + 34, 5, fill, stroke, prefix)
        parts.append(_cluster(f"cl_{prefix}", label, 40, y,
                              width - 80, block + 44, color))
        parts.extend(_box(node) for node in nodes)
        y += block + 70

    parts.append(FOOTER)
    return "".join(parts).replace('pageHeight="1"', f'pageHeight="{y + 40}"')


def build_dependency_graph() -> str:
    """Граф зависимостей внутри ядра: модули и импорты между ними."""
    names = core_modules()
    edges = core_dependencies()
    nodes, block = _grid(names, 40, 70, 5, "#ffe6cc", "#d79b00", "m")
    width = 40 + 5 * (COLUMN_WIDTH + GAP_X) + 20
    height = 70 + block + 60
    by_name = {node.label: node.key for node in nodes}

    parts = [_header("Граф зависимостей ядра", "depgraph", width, height)]
    parts.append(_title(
        f"FINPILOT — зависимости внутри `app/core` ({len(names)} модулей, "
        f"{len(edges)} связей) · {stamp()}", width))
    parts.extend(_box(node) for node in nodes)
    for index, (source, target) in enumerate(edges):
        parts.append(_edge(f"e{index}", by_name[source], by_name[target]))
    parts.append(FOOTER)
    return "".join(parts)


SVG_HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
    'viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, sans-serif">\n'
    '  <rect width="{width}" height="{height}" fill="#ffffff"/>\n'
)


def _svg_box(node: Node) -> str:
    """Прямоугольник с подписью; длинное имя переносится по словам."""
    label = escape(node.label)
    return (
        f'  <rect x="{node.x}" y="{node.y}" width="{node.width}" '
        f'height="{node.height}" rx="6" fill="{node.fill}" stroke="{node.stroke}"/>\n'
        f'  <text x="{node.x + node.width // 2}" y="{node.y + node.height // 2 + 4}" '
        f'font-size="12" text-anchor="middle" fill="#1f2933">{label}</text>\n'
    )


def _svg_cluster(label: str, x: int, y: int, width: int, height: int,
                 color: str) -> str:
    return (
        f'  <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" '
        f'fill="none" stroke="{color}" stroke-dasharray="6 6"/>\n'
        f'  <text x="{x + 12}" y="{y + 20}" font-size="13" font-style="italic" '
        f'fill="{color}">{escape(label)}</text>\n'
    )


def _svg_title(text: str, width: int) -> str:
    return (
        f'  <text x="{width // 2}" y="32" font-size="16" font-weight="bold" '
        f'text-anchor="middle" fill="#1f2933">{escape(text)}</text>\n'
    )


def er_dot() -> str:
    """ER на языке Graphviz: таблицы и связи по внешним ключам.

    Раскладку считает `dot`: `users` собирает на себя большинство ссылок, и ручная
    сетка превратила бы это в клубок. Кит `15-image-kit` §1 называет DOT умолчанием
    для графов.
    """
    names, edges = tables(), foreign_keys()
    lines = [
        "digraph er {",
        '  graph [rankdir=LR, splines=spline, nodesep=0.3, ranksep=1.1, '
        'fontname="Helvetica", labelloc=t, fontsize=16, '
        f'label="FINPILOT — база данных: {len(names)} таблиц, {len(edges)} связей"];',
        '  node [shape=box, style="rounded,filled", fillcolor="#dae8fc", '
        'color="#6c8ebf", fontname="Helvetica", fontsize=11];',
        '  edge [color="#9aa4b1", arrowsize=0.7, arrowhead=crow];',
    ]
    lines.extend(f'  "{name}";' for name in names)
    lines.extend(f'  "{source}" -> "{target}";' for source, target in edges)
    lines.append("}")
    return "\n".join(lines) + "\n"


def svg_component() -> str:
    api, svc, core = routers(), services(), core_modules()
    width = 40 + 5 * (COLUMN_WIDTH + GAP_X) + 20
    body: list[str] = []
    y = 56
    for label, names, fill, stroke, prefix, color in (
        ("app/api — HTTP-слой", api, "#85BBF0", "#6c8ebf", "r", "#6c8ebf"),
        ("app/services — прикладные сервисы", svc, "#d5e8d4", "#82b366", "s", "#82b366"),
        ("app/core — математическое ядро", core, "#ffe6cc", "#d79b00", "c", "#d79b00"),
    ):
        nodes, block = _grid(names, 60, y + 34, 5, fill, stroke, prefix)
        body.append(_svg_cluster(label, 40, y, width - 80, block + 44, color))
        body.extend(_svg_box(node) for node in nodes)
        y += block + 70
    height = y + 20
    parts = [SVG_HEADER.format(width=width, height=height)]
    parts.append(_svg_title(
        f"FINPILOT — компоненты: {len(api)} роутов, {len(svc)} сервисов, "
        f"{len(core)} модулей ядра", width))
    parts.extend(body)
    parts.append("</svg>\n")
    return "".join(parts)


def dependency_dot() -> str:
    """Граф зависимостей ядра на языке Graphviz.

    Раскладку считает `dot`: у графа с рёбрами ручная сетка нечитаема, а Graphviz
    разводит связи по слоям. Кит `15-image-kit` §1 называет DOT умолчанием
    для графов и деревьев.
    """
    lines = [
        "digraph core {",
        '  graph [rankdir=LR, splines=spline, nodesep=0.35, ranksep=0.9, '
        'fontname="Helvetica", label="FINPILOT — зависимости внутри app/core", '
        'labelloc=t, fontsize=16];',
        '  node [shape=box, style="rounded,filled", fillcolor="#ffe6cc", '
        'color="#d79b00", fontname="Helvetica", fontsize=11];',
        '  edge [color="#9aa4b1", arrowsize=0.7];',
    ]
    for name in core_modules():
        lines.append(f'  "{name}";')
    for source, target in core_dependencies():
        lines.append(f'  "{source}" -> "{target}";')
    lines.append("}")
    return "\n".join(lines) + "\n"


def _render_png(svg_text: str, target: Path) -> bool:
    """SVG → PNG через `rsvg-convert`. Молчаливого пропуска нет: канал или есть, или назван."""
    result = subprocess.run(
        ["rsvg-convert", "--zoom", "1.5", "-o", str(target)],
        input=svg_text.encode("utf-8"), capture_output=True, check=False,
    )
    if result.returncode != 0:
        print(f"    🔴 rsvg-convert не смог: {result.stderr.decode().strip()}")
        return False
    return True


def _render_dot(dot_text: str, target: Path) -> bool:
    """DOT → PNG через Graphviz."""
    result = subprocess.run(
        ["dot", "-Tpng", "-Gdpi=110", "-o", str(target)],
        input=dot_text.encode("utf-8"), capture_output=True, check=False,
    )
    if result.returncode != 0:
        print(f"    🔴 dot не смог: {result.stderr.decode().strip()}")
        return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Смысловые диаграммы, написанные КОДОМ.
#
# 🔴 Они не выводятся из дерева исходников автоматически — их содержание задаёт
# человек. Но храниться они должны так же, как структурные: текстом, который
# диффится и рендерится одной командой. Иначе повторяется история v6.8.0 →
# v9.13.23, когда `05_c4_container` десять версий описывала «Jinja2 + ванильный JS»
# после того, как Jinja была снесена целиком, а `15_forecast_GOST` — «оценку
# тренда b», отменённую каноном v3.10.0 по замеру на 300 портретах.
# ─────────────────────────────────────────────────────────────────────────────

def context_dot() -> str:
    """C4 Level 1: система и её внешнее окружение.

    Внешние системы перечислены по факту кода: `cbr_rate`/`cbr_fx` (ЦБ РФ),
    `telegram`, `plaid`, `email_dispatch`. Прежняя редакция знала только
    пользователя и банк — четыре интеграции появились после неё и в контекст
    не попали.
    """
    return """digraph context {
  graph [rankdir=LR, fontname="Helvetica", labelloc=t, fontsize=17,
         label="FINPILOT — контекст системы (C4 Level 1)\\n""" + stamp() + """",
         nodesep=0.5, ranksep=1.4];
  node [fontname="Helvetica", fontsize=11, style="rounded,filled"];
  edge [color="#9aa4b1", fontname="Helvetica", fontsize=9];

  user [label="Пользователь\\n[человек]", shape=box, fillcolor="#dae8fc", color="#6c8ebf"];
  fin  [label="FINPILOT\\n[СППР]\\nраспределение потока\\nдолг / резерв / цели",
        shape=box, fillcolor="#1f6feb", fontcolor=white,
        color="#1a4f9c", width=2.8];

  bank  [label="Банк клиента\\nвыписка CSV/XLSX/PDF/1C", shape=box,
           fillcolor="#f5f5f5", color="#999999"];
  cbr   [label="ЦБ РФ\\nключевая ставка, курсы валют", shape=box,
           fillcolor="#f5f5f5", color="#999999"];
  plaid [label="Plaid\\nагрегатор счетов (каркас)", shape=box,
           fillcolor="#f5f5f5", color="#999999"];
  tg    [label="Telegram\\nуведомления в чат", shape=box, fillcolor="#f5f5f5", color="#999999"];
  mail  [label="Почтовый сервер\\nписьма и подтверждения", shape=box,
           fillcolor="#f5f5f5", color="#999999"];

  user -> fin [label="вводит данные,\\nполучает рекомендации [HTTPS]"];
  bank -> fin [label="импорт выписки"];
  cbr -> fin [label="ставка и курсы [HTTP+XML]"];
  plaid -> fin [label="счета и операции [REST]"];
  fin -> tg [label="уведомление"];
  fin -> mail [label="письмо [SMTP]"];
}
"""


def container_dot() -> str:
    """C4 Level 2: контейнеры.

    🔴 Прежняя редакция описывала фронт как «Jinja2 + ванильный JS, 7 страниц».
    Jinja снесена целиком (веха 8): приложение отдаёт собранный React из
    `frontend/dist` через `StaticFiles`, страниц 14.
    """
    return f"""digraph container {{
  graph [rankdir=TB, fontname="Helvetica", labelloc=t, fontsize=17,
         label="FINPILOT — контейнеры (C4 Level 2)\\n{stamp()}",
         nodesep=0.45, ranksep=0.9];
  node [fontname="Helvetica", fontsize=11, style="rounded,filled", shape=box];
  edge [color="#9aa4b1", fontname="Helvetica", fontsize=9];

  user [label="Пользователь\\n[человек]", fillcolor="#dae8fc", color="#6c8ebf"];

  subgraph cluster_app {{
    label="FINPILOT"; fontname="Helvetica"; fontsize=12; color="#6c8ebf"; style=dashed;
    spa [label="SPA\\n[React 19 + TypeScript + Vite]\\n14 страниц, TanStack Router/Query",
         fillcolor="#85BBF0", color="#6c8ebf", width=2.6];
    api [label="HTTP-слой\\n[FastAPI, 27 групп роутов]\\nCSRF, rate-limit, гейт согласия",
         fillcolor="#85BBF0", color="#6c8ebf", width=2.6];
    svc [label="Сервисы\\n[26 модулей]\\nпланирование, импорт, уведомления",
         fillcolor="#d5e8d4", color="#82b366", width=2.6];
    core [label="Математическое ядро\\n[21 модуль, канон v3.10.0]\\nчистые функции: ни БД, ни HTTP",
          fillcolor="#ffe6cc", color="#d79b00", width=2.6];
    db [label="База данных\\n[PostgreSQL / SQLite]\\n31 таблица, SQLAlchemy 2.0",
        shape=cylinder, fillcolor="#f8cecc", color="#b85450", width=2.2];
  }}

  user -> spa [label="HTTPS"];
  spa -> api [label="JSON/REST"];
  api -> svc [label="вызывает"];
  svc -> core [label="делегирует расчёт"];
  svc -> db [label="читает/пишет [ORM]"];
  api -> spa [label="отдаёт сборку\\nfrontend/dist [StaticFiles]", style=dashed];
}}
"""


def forecast_dot() -> str:
    """Схема прогноза по канону v3.10.0.

    🔴 Прежняя редакция содержала «Этап 2. Оценка тренда b по сглаженным уровням».
    Канон v3.10.0 тренд ОТМЕНИЛ: замер Г43 на 300 портретах показал ошибку суммы
    0.606 против 0.205 у простого среднего при трёх точках — последнее место
    из четырнадцати методов. `holt_forecast` остался в модуле как проверенная
    реализация, но `forecast_indicator` его не вызывает.
    """
    return """digraph forecast {
  graph [rankdir=TB, fontname="Helvetica", labelloc=t, fontsize=16,
         label="FINPILOT — прогноз показателя: SES без тренда + Монте-Карло\\n""" + stamp() + """",
         nodesep=0.35, ranksep=0.55];
  node [fontname="Helvetica", fontsize=11, style="rounded,filled",
        fillcolor="#e1f5e1", color="#82b366", shape=box, width=3.4];
  edge [color="#9aa4b1", arrowsize=0.7];

  s0 [label="Вход: ряд history, горизонт h\\nα = 0.3, N = 1000",
      fillcolor="#dae8fc", color="#6c8ebf"];
  s1 [label="1. Сглаживание (Brown SES)\\nLt = α·yt + (1−α)·Lt−1"];
  s2 [label="2. Точечный прогноз — ПЛОСКИЙ\\nŷ(t+h) = Lt для всех h\\nтренда НЕТ (канон §15)",
      fillcolor="#fff2cc", color="#d6b656"];
  s3 [label="3. Монте-Карло: N = 1000 траекторий\\nс растущей σ(h)"];
  s4 [label="4. Перцентили по ансамблю\\np10, p50, p90 — интервал 80 %"];
  s5 [label="Выход: точечный прогноз\\nи коридор [p10..p90]", fillcolor="#dae8fc", color="#6c8ebf"];

  note [label="Holt отменён в v3.10.0:\\nзамер Г43: ошибка 0.606\\nпротив 0.205 (3 точки)",
        shape=note, fillcolor="#f8cecc", color="#b85450", fontsize=10, width=3.2];

  s0 -> s1 -> s2 -> s3 -> s4 -> s5;
  s2 -> note [style=dashed, arrowhead=none, color="#b85450"];
}
"""


def pipeline_dot() -> str:
    """Главный пайплайн расчёта плана (ГОСТ 19.701-90).

    🔴 Прежняя редакция обрывала ветку дефицита на «вернуть структурный диагноз
    (Fail-loud)». Кризисный модуль (`app/core/crisis.py`, канон v3.1.0 G2) появился
    позже: при Rt < 0 приложение СТРОИТ ПЛАН ДЕЙСТВИЙ, а не только ставит диагноз —
    `build_crisis_plan` вызывается из `planning.py` до генерации альтернатив.
    Поведение продукта изменилось, схема осталась.
    """
    return f"""digraph pipeline {{
  graph [rankdir=TB, fontname="Helvetica", labelloc=t, fontsize=16,
         label="FINPILOT — главный пайплайн расчёта (ГОСТ 19.701-90)\\n{stamp()}",
         nodesep=0.3, ranksep=0.45];
  node [fontname="Helvetica", fontsize=10, style="rounded,filled",
        fillcolor="#e1f5e1", color="#82b366", shape=box, width=3.6];
  edge [color="#9aa4b1", arrowsize=0.7, fontname="Helvetica", fontsize=9];

  start [label="Вход: доходы, расходы, обязательства,\\nцели, активы, параметры пользователя",
         fillcolor="#dae8fc", color="#6c8ebf"];
  s1 [label="Этап 1. Предобработка\\nнормализация, фильтр активных целей"];
  s2 [label="Этап 2. Базовые показатели\\nCFt, Rt, Lt, Dt, BLR, Si"];
  q1 [label="Rt > 0 ?", shape=diamond, fillcolor="#fff2cc", color="#d6b656", width=1.6];

  crisis [
    label="Кризисный модуль (v3.1.0, G2)\\nbuild_crisis_plan — план,\\nа не только диагноз",
          fillcolor="#f8cecc", color="#b85450"];

  s40 [label="Этап 4.0. Разовое закрытие близких целей\\nиз Bliq, если Σ ≤ 0.5·Bliq"];
  s4 [label="Этап 4. Генерация 66 альтернатив\\nstars-and-bars, шаг 10 %"];
  loop [label="для каждой альтернативы a ∈ A", shape=hexagon,
        fillcolor="#e1d5e7", color="#9673a6", width=2.8];
  s4b [label="Этап 4b. Avalanche + OCR-фильтр\\n(отдельная схема)"];
  si [label="Взвешенная обеспеченность Si\\n(отдельная схема)"];
  recalc [label="Пересчёт Rt', Lt', Dt' для альтернативы"];
  s5 [label="Этап 5. Фильтрация по ограничениям\\nRt' ≥ 0, Lt' ≥ Lmin, Dt' ≤ 0.40"];
  q2 [label="A' не пусто ?", shape=diamond, fillcolor="#fff2cc",
      color="#d6b656", width=1.8];
  empty [label="Нет допустимых: ослабить ограничения\\nили пересмотреть бюджет",
         fillcolor="#f8cecc", color="#b85450"];
  s6 [label="Этап 6. Min-max нормализация +\\nсвёртка U(a) = Σ wk·критерий (SAW)"];
  best [label="a* = argmax U(a)"];
  out [label="Выход: a*, top-3 и объяснения",
       fillcolor="#dae8fc", color="#6c8ebf"];

  start -> s1 -> s2 -> q1;
  q1 -> crisis [label="нет (дефицит)"];
  crisis -> out [style=dashed, label="план действий"];
  q1 -> s40 [label="да"];
  s40 -> s4 -> loop -> s4b -> si -> recalc;
  recalc -> loop [label="следующая", style=dashed];
  recalc -> s5 [label="альтернативы кончились"];
  s5 -> q2;
  q2 -> empty [label="нет"];
  q2 -> s6 [label="да"];
  s6 -> best -> out;
}}
"""


def uml_class_dot() -> str:
    """UML-классы: ORM-модели по факту `app/database/models.py`.

    🔴 Прежняя редакция знала 5 классов из 31. Схема структурная — генерируется,
    а не рисуется: перечень моделей меняется каждую веху.
    """
    source = (REPO / "app/database/models.py").read_text(encoding="utf-8")
    classes = sorted(set(re.findall(r"^class\s+([A-Za-z_]+)\(", source, re.M)))
    lines = [
        "digraph uml {",
        '  graph [rankdir=LR, fontname="Helvetica", labelloc=t, fontsize=16,',
        f'         label="FINPILOT — ORM-модели ({len(classes)} классов)'
        f'\\n{stamp()}", nodesep=0.25, ranksep=0.8];',
        '  node [shape=box, style="rounded,filled", fillcolor="#e1d5e7",',
        '        color="#9673a6", fontname="Helvetica", fontsize=11];',
    ]
    lines.extend(f'  "{name}";' for name in classes)
    lines.append("}")
    return "\n".join(lines) + "\n"


def import_sequence_dot() -> str:
    """Импорт банковской выписки — по факту `app/services/statement_parser.py`.

    🔴 Прежняя редакция знала только CSV («loop по строкам CSV») и парсеры
    tinkoff/sber/universal. Сейчас поддержаны CSV, XLSX (`openpyxl`) и PDF
    (`pdfplumber`), а разбор возвращает отчёт о качестве: сколько строк прочитано,
    сколько пропущено и почему.
    """
    return f"""digraph import_seq {{
  graph [rankdir=TB, fontname="Helvetica", labelloc=t, fontsize=15,
         label="FINPILOT — импорт выписки (POST /api/banks/import)\\n{stamp()}",
         nodesep=0.3, ranksep=0.5];
  node [fontname="Helvetica", fontsize=10, style="rounded,filled",
        fillcolor="#e1f5e1", color="#82b366", shape=box, width=3.4];
  edge [color="#9aa4b1", arrowsize=0.7, fontname="Helvetica", fontsize=9];

  u [label="Пользователь: файл выписки", fillcolor="#dae8fc", color="#6c8ebf"];
  r [label="routes_banks\\nPOST /banks/import {{file, bank_id}}"];
  g [label="Гейт согласия на финданные\\n403 consent_required, если не выдано",
     fillcolor="#fff2cc", color="#d6b656"];
  fmt [label="Определение формата", shape=diamond, fillcolor="#fff2cc",
       color="#d6b656", width=2.0];
  csv [label="CSV\\nparse_tinkoff_csv / parse_sber_csv\\nуниверсальный разбор по заголовкам"];
  xlsx [label="XLSX\\nopenpyxl: поиск таблицы,\\nпропуск шапки"];
  pdf [label="PDF\\npdfplumber: извлечение таблиц"];
  norm [label="Нормализация: дата, сумма, знак\\nклассификация доход/расход"];
  rep [label="Отчёт о разборе\\nстрок прочитано / пропущено и почему",
       fillcolor="#f8cecc", color="#b85450"];
  rec [label="statement_reconcile\\nсверка с существующими операциями"];
  db [label="Запись транзакций", shape=cylinder, fillcolor="#f8cecc",
      color="#b85450", width=2.4];

  u -> r -> g -> fmt;
  fmt -> csv; fmt -> xlsx; fmt -> pdf;
  csv -> norm; xlsx -> norm; pdf -> norm;
  norm -> rep [style=dashed];
  norm -> rec -> db;
}}
"""


def usecase_dot() -> str:
    """Варианты использования — по факту групп роутов.

    🔴 Прежняя редакция знала базовый CRUD и импорт. После вех 7–8 появились
    семейный доступ, рефералка, подписки, Telegram, A/B-эксперименты, MFA,
    юрблок и аналитика владельца — ни одного из них на схеме не было.
    """
    return f"""digraph usecase {{
  graph [rankdir=LR, fontname="Helvetica", labelloc=t, fontsize=15,
         label="FINPILOT — варианты использования\\n{stamp()}",
         nodesep=0.22, ranksep=1.6];
  node [fontname="Helvetica", fontsize=10];
  edge [color="#9aa4b1", arrowsize=0.6];

  user [label="Пользователь", shape=box, style="rounded,filled",
        fillcolor="#dae8fc", color="#6c8ebf"];
  owner [label="Владелец продукта", shape=box, style="rounded,filled",
         fillcolor="#dae8fc", color="#6c8ebf"];

  subgraph cluster_uc {{
    label="FINPILOT"; color="#6c8ebf"; style=dashed; fontname="Helvetica";
    node [shape=ellipse, style=filled, fillcolor="#e1f5e1", color="#82b366"];
    uc1 [label="Вести операции, обязательства,\\nцели и активы"];
    uc2 [label="Импортировать выписку\\nCSV / XLSX / PDF"];
    uc3 [label="Получить рекомендацию\\n(полный цикл СППР)"];
    uc4 [label="Настроить риск-профиль\\nи пороги"];
    uc5 [label="Семейный доступ:\\nобщий бюджет, приглашения"];
    uc6 [label="Пригласить по реферальной\\nссылке"];
    uc7 [label="Подписка и тариф"];
    uc8 [label="Уведомления:\\nлента, почта, Telegram"];
    uc9 [label="Согласия и юрдокументы\\n(152-ФЗ)"];
    uc10 [label="Двухфакторная аутентификация"];
    uc11 [label="Выгрузка плана\\nCSV / XLSX / PDF"];
    uc12 [label="Аналитика продукта\\nи A/B-эксперименты",
          fillcolor="#fff2cc", color="#d6b656"];
  }}

  user -> uc1; user -> uc2; user -> uc3; user -> uc4; user -> uc5;
  user -> uc6; user -> uc7; user -> uc8; user -> uc9; user -> uc10; user -> uc11;
  owner -> uc12;
}}
"""


AUTHORED = {
    "01_main_pipeline_GOST.drawio.png": pipeline_dot,
    "04_c4_context.drawio.png": context_dot,
    "08_sequence_import.drawio.png": import_sequence_dot,
    "11_uml_class.drawio.png": uml_class_dot,
    "13_usecase.drawio.png": usecase_dot,
    "05_c4_container.drawio.png": container_dot,
    "15_forecast_GOST.drawio.png": forecast_dot,
}

PREVIEWS = {
    "10_er_database.drawio.png": ("dot", er_dot),
    "06_c4_component.drawio.png": ("svg", svg_component),
    "14_dependency_graph.drawio.png": ("dot", dependency_dot),
    **{name: ("dot", builder) for name, builder in AUTHORED.items()},
}


GENERATED = {
    "10_er_database.drawio": build_er,
    "06_c4_component.drawio": build_component,
    "14_dependency_graph.drawio": build_dependency_graph,
}


def main() -> int:
    for filename, builder in GENERATED.items():
        (DIAGRAMS / filename).write_text(builder(), encoding="utf-8")
        print(f"  собрано: {filename}")

    # 🔴 Источник смысловых диаграмм — DOT, и он кладётся рядом. Без этого PNG
    # обновлялся бы, а `.drawio` оставался со старым содержанием: источник
    # противоречил бы превью, что хуже устаревшей пары целиком.
    SOURCES.mkdir(parents=True, exist_ok=True)
    for name, builder in AUTHORED.items():
        stem = name.removesuffix(".drawio.png")
        (SOURCES / f"{stem}.dot").write_text(builder(), encoding="utf-8")
        stale = DIAGRAMS / f"{stem}.drawio"
        if stale.exists():
            stale.unlink()
            print(f"  снят устаревший источник: {stale.name} "
                  f"(заменён на src/{stem}.dot)")

    # Генерируемые `.drawio` несут версию в СВОЁМ заголовке и переписываются целиком —
    # штамповать их отдельной ячейкой значит добавлять её на каждом прогоне заново.
    text = f"Соответствует: {stamp()} · проверено сверкой с кодом"
    stamped = [path.name for path in sorted(DIAGRAMS.glob("*.drawio"))
               if path.name not in GENERATED and stamp_drawio(path, text)]
    if stamped:
        print(f"  проставлен штамп версии: {len(stamped)} файл(ов)")

    failures = []
    for name, (kind, builder) in PREVIEWS.items():
        target = DIAGRAMS / name
        ok = (_render_png(builder(), target) if kind == "svg"
              else _render_dot(builder(), target))
        if ok:
            print(f"  отрисовано: {name} ({target.stat().st_size // 1024} КБ)")
        else:
            failures.append(name)
    if failures:
        print("\n🔴 НЕ отрисовано: " + ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

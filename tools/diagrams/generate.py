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

Запуск из корня репозитория:
    python -m tools.diagrams.generate
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[2]
DIAGRAMS = REPO / "docs/diagrams"

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
    parts = [_header("ER — таблицы базы", "er_database", width, height)]
    parts.append(_title(
        f"FINPILOT — таблицы базы данных ({len(names)}). Генерируется "
        "`python -m tools.diagrams.generate`", width))
    parts.extend(_box(node) for node in nodes)
    parts.append(FOOTER)
    return "".join(parts)


def build_component() -> str:
    """C4 Level 3: роутеры, сервисы, модули ядра."""
    api, services_list, core = routers(), services(), core_modules()
    width = 40 + 5 * (COLUMN_WIDTH + GAP_X) + 20

    parts = [_header("C4 — компоненты", "c4_component", width, 1)]
    parts.append(_title(
        f"FINPILOT — компоненты: {len(api)} роутов, {len(services_list)} сервисов, "
        f"{len(core)} модулей ядра", width))

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
        f"{len(edges)} связей)", width))
    parts.extend(_box(node) for node in nodes)
    for index, (source, target) in enumerate(edges):
        parts.append(_edge(f"e{index}", by_name[source], by_name[target]))
    parts.append(FOOTER)
    return "".join(parts)


GENERATED = {
    "10_er_database.drawio": build_er,
    "06_c4_component.drawio": build_component,
    "14_dependency_graph.drawio": build_dependency_graph,
}


def main() -> int:
    for filename, builder in GENERATED.items():
        target = DIAGRAMS / filename
        target.write_text(builder(), encoding="utf-8")
        print(f"  собрано: {filename}")
        # 🔴 Превью производно от источника и рендерится только вручную на Mac
        # (в песочнице CDN Chromium заблокирован). Протухший PNG рядом со свежим
        # XML вводит в заблуждение сильнее, чем его отсутствие — правило
        # `docs/diagrams/README.md`, поэтому он удаляется.
        for suffix in (".png", ".svg"):
            stale = DIAGRAMS / f"{filename}{suffix}"
            if stale.exists():
                stale.unlink()
                print(f"    снято протухшее превью: {stale.name}")
    print("\nПревью регенерируются вручную: drawio desktop → Export as → PNG, масштаб 1.5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Механический a11y-харнесс (P1.1).

Анонимно рендерит каждую SSR-страницу и проверяет структурные инварианты
доступности, которые axe-core пометил как critical/serious/moderate:
наличие ровно одного <h1>, accessible-имя у каждого select/input,
отсутствие фокус-ловушки в скрытых модалках (aria-hidden без inert),
отсутствие вложенной интерактивности и уникальность landmark.

Скринридерная часть и контраст токенов проверяются отдельно (на Mac).
"""

from collections import defaultdict

import pytest
from bs4 import BeautifulSoup, Tag

PAGES: list[str] = [
    "/dashboard",
    "/planning",
    "/transactions",
    "/obligations",
    "/goals",
    "/banks",
    "/validation",
    "/profile",
    "/contacts",
    "/forgot-password",
    "/reset-password",
    "/legal/privacy",
    "/legal/terms",
    "/legal/consent",
    "/legal/financial-consent",
]

_NO_NAME_INPUT_TYPES = {"hidden", "submit", "button", "reset", "image"}
_INTERACTIVE_TAGS = {"a", "button", "input", "select", "textarea"}
_LANDMARK_TAGS = ("nav", "main")


def _soup(client, path: str) -> BeautifulSoup:
    response = client.get(path)
    assert response.status_code == 200, f"{path} -> {response.status_code}"
    return BeautifulSoup(response.text, "html.parser")


def _has_accessible_name(el: Tag, soup: BeautifulSoup) -> bool:
    if (el.get("aria-label") or "").strip():
        return True
    if (el.get("title") or "").strip():
        return True
    labelledby = (el.get("aria-labelledby") or "").strip()
    if labelledby and all(soup.find(id=ref) is not None for ref in labelledby.split()):
        return True
    el_id = el.get("id")
    if el_id:
        label = soup.find("label", attrs={"for": el_id})
        if label and label.get_text(strip=True):
            return True
    wrapper = el.find_parent("label")
    if wrapper and wrapper.get_text(strip=True):
        return True
    return False


def _is_focusable(el: Tag) -> bool:
    if el.name == "a":
        return el.get("href") is not None
    if el.name in {"button", "select", "textarea"}:
        return True
    if el.name == "input":
        return (el.get("type") or "text").lower() != "hidden"
    tabindex = el.get("tabindex")
    return tabindex is not None and tabindex != "-1"


@pytest.mark.parametrize("path", PAGES)
def test_exactly_one_h1(client, path: str) -> None:
    soup = _soup(client, path)
    headings = soup.find_all("h1")
    assert len(headings) == 1, f"{path}: ожидался ровно один <h1>, найдено {len(headings)}"


@pytest.mark.parametrize("path", PAGES)
def test_selects_have_accessible_name(client, path: str) -> None:
    soup = _soup(client, path)
    offenders = [
        s.get("id") or str(s)[:80]
        for s in soup.find_all("select")
        if not _has_accessible_name(s, soup)
    ]
    assert not offenders, f"{path}: <select> без accessible-имени: {offenders}"


@pytest.mark.parametrize("path", PAGES)
def test_inputs_have_accessible_name(client, path: str) -> None:
    soup = _soup(client, path)
    offenders = []
    for inp in soup.find_all("input"):
        if (inp.get("type") or "text").lower() in _NO_NAME_INPUT_TYPES:
            continue
        if not _has_accessible_name(inp, soup):
            offenders.append(inp.get("id") or str(inp)[:80])
    assert not offenders, f"{path}: <input> без accessible-имени: {offenders}"


@pytest.mark.parametrize("path", PAGES)
def test_hidden_containers_have_no_focus_trap(client, path: str) -> None:
    soup = _soup(client, path)
    offenders = []
    for el in soup.find_all(attrs={"aria-hidden": "true"}):
        if el.has_attr("inert"):
            continue
        if any(_is_focusable(d) for d in el.find_all(True)):
            offenders.append(el.get("id") or str(el)[:60])
    assert not offenders, f"{path}: aria-hidden=true с фокусируемыми потомками без inert: {offenders}"


@pytest.mark.parametrize("path", PAGES)
def test_no_nested_interactive(client, path: str) -> None:
    soup = _soup(client, path)
    offenders = []
    for outer in soup.find_all(["a", "button"]):
        for inner in outer.find_all(_INTERACTIVE_TAGS):
            if inner.name == "input" and (inner.get("type") or "text").lower() == "hidden":
                continue
            offenders.append(f"{outer.name}>{inner.name}")
    assert not offenders, f"{path}: вложенная интерактивность: {offenders}"


@pytest.mark.parametrize("path", PAGES)
def test_landmarks_unique(client, path: str) -> None:
    soup = _soup(client, path)
    groups: dict[str, list[Tag]] = defaultdict(list)
    for tag in _LANDMARK_TAGS:
        groups[tag].extend(soup.find_all(tag))

    assert len(groups["main"]) <= 1, f"{path}: более одного <main>"

    navs = groups["nav"]
    if len(navs) > 1:
        names = [(n.get("aria-label") or n.get("aria-labelledby") or "").strip() for n in navs]
        assert "" not in names and len(set(names)) == len(names), (
            f"{path}: несколько <nav> без уникального aria-label: {names}"
        )

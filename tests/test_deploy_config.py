"""Конфигурация деплоя ссылается на существующее и не тащит dev-умолчания (v8.49.0).

## Почему статический гейт, а не поднятие стенда

Docker на машине владельца отсутствует (проверено: `docker`, `colima`, `podman`,
`nerdctl`, `lima` — ни одного, в brew тоже нет). Установка Docker Desktop — многогиговая
внешняя операция при 18 ГБ свободного диска, и это решение владельца продукта.

Поэтому здесь проверяется то, что проверяемо без демона: **все пути, на которые
ссылаются compose и Dockerfile, существуют**, и **в прод-конфиге нет dev-секретов**.
Это ловит самый дорогой класс отказа вехи 9 — деплой, который падает на первой же
команде вечером на боевом сервере из-за отсутствующего файла или опечатки в пути.

🔴 Чего гейт НЕ проверяет и не может: соберётся ли образ, поднимется ли контейнер,
пройдут ли healthcheck. Это остаётся живой проверкой на сервере (`docs/DEPLOY.md` шаг 6).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PROD_COMPOSE = ROOT / "docker-compose.prod.yml"


@pytest.fixture(scope="module")
def prod_config() -> dict:
    return yaml.safe_load(PROD_COMPOSE.read_text(encoding="utf-8"))


class TestReferencedPathsExist:
    """Всё, на что ссылается прод-конфиг, лежит в репозитории."""

    def test_compose_file_exists(self) -> None:
        assert PROD_COMPOSE.is_file(), "прод-compose пропал — деплоить нечем"

    def test_dockerfiles_exist(self, prod_config: dict) -> None:
        """Пути к Dockerfile существуют.

        Опечатка здесь стоит вечера на сервере: `docker compose build` падает
        в первой же строке, и до логов приложения дело не доходит.
        """
        for name, service in prod_config["services"].items():
            build = service.get("build")
            if build is None:
                continue
            if isinstance(build, str):
                context, dockerfile = build, "Dockerfile"
            else:
                context = build.get("context", ".")
                dockerfile = build.get("dockerfile", "Dockerfile")
            path = (ROOT / context / dockerfile).resolve()
            assert path.is_file(), f"{name}: нет {path.relative_to(ROOT)}"

    def test_bind_mounts_from_repo_exist(self, prod_config: dict) -> None:
        """Тома, монтируемые ИЗ репозитория, существуют.

        Пути с хоста (`/etc/letsencrypt`) сюда не входят намеренно: они появляются
        на сервере при получении сертификата и в репе их быть не должно.
        """
        for name, service in prod_config["services"].items():
            for volume in service.get("volumes", []):
                if not isinstance(volume, str) or not volume.startswith("./"):
                    continue
                source = volume.split(":")[0]
                assert (ROOT / source).exists(), f"{name}: нет каталога {source}"

    def test_nginx_template_exists_and_is_a_template(self) -> None:
        """Шаблон nginx на месте и действительно шаблон.

        `NGINX_ENVSUBST_FILTER: DOMAIN` в compose подставляет только `DOMAIN`.
        Если в шаблоне этой переменной нет, конфиг соберётся с чужим доменом
        и TLS не совпадёт с сертификатом.
        """
        templates = list((ROOT / "nginx" / "templates").glob("*.template"))
        assert templates, "шаблонов nginx нет — envsubst нечего подставлять"
        assert any("${DOMAIN}" in t.read_text(encoding="utf-8") for t in templates), (
            "ни в одном шаблоне нет ${DOMAIN} — фильтр envsubst бесполезен"
        )


class TestNoDevDefaultsInProduction:
    """Прод-конфиг не несёт умолчаний, годных только для разработки."""

    def test_secrets_come_from_env_not_literals(self, prod_config: dict) -> None:
        """🔴 Ни один секрет не записан значением прямо в compose.

        Файл лежит в репозитории; литеральный пароль здесь — это секрет в git.
        Разрешена только подстановка `${VAR:?...}`, которая падает при пустом
        значении (fail-loud), а не подставляет тихое умолчание.
        """
        raw = PROD_COMPOSE.read_text(encoding="utf-8")
        secret_names = ("PASSWORD", "SECRET", "TOKEN", "KEY", "ADMIN")
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or ":" not in stripped:
                continue
            name, _, value = stripped.partition(":")
            if not any(marker in name.upper() for marker in secret_names):
                continue
            value = value.strip()
            if not value:
                continue
            assert value.startswith("${"), (
                f"секрет записан значением в compose: {stripped!r} — "
                "он попадёт в git; допустима только подстановка из .env"
            )

    def test_required_env_vars_fail_loud(self, prod_config: dict) -> None:
        """Обязательные переменные объявлены с `:?` — пустое значение валит запуск.

        Умолчание вместо ошибки означает, что прод поднимется с dev-паролем и
        никто об этом не узнает, пока не станет поздно.
        """
        raw = PROD_COMPOSE.read_text(encoding="utf-8")
        for variable in ("POSTGRES_PASSWORD", "DOMAIN"):
            uses = re.findall(rf"\$\{{{variable}([^}}]*)\}}", raw)
            assert uses, f"{variable} не используется в прод-конфиге"
            assert all(use.startswith(":?") for use in uses), (
                f"{variable} подставляется без `:?` — пустое значение пройдёт молча"
            )

    def test_environment_is_forced_to_production(self, prod_config: dict) -> None:
        """`ENVIRONMENT: production` задан в compose, а не оставлен на .env.

        Случайный `development` в `.env` на сервере открыл бы админские эндпоинты
        при пустом ключе (`require_admin` в dev пропускает всех).
        """
        web = prod_config["services"]["web"]
        assert web["environment"]["ENVIRONMENT"] == "production"

    def test_database_is_not_published_to_the_internet(self, prod_config: dict) -> None:
        """🔴 БД и приложение слушают только loopback.

        Порт без адреса (`"5432:5432"`) публикует базу на все интерфейсы. На VPS
        это открытый Postgres в интернете — с персональными данными внутри.
        """
        for name in ("db", "web"):
            for port in prod_config["services"][name].get("ports", []):
                assert str(port).startswith("127.0.0.1:"), (
                    f"{name}: порт {port} опубликован наружу, а должен быть на loopback"
                )

    def test_only_nginx_faces_the_internet(self, prod_config: dict) -> None:
        """Наружу торчит ровно один сервис — обратный прокси.

        Сравнение множеством, а не списком: у nginx два публичных порта (80 и 443),
        и список дал бы `["nginx", "nginx"]`. Проверяется состав сервисов, а не
        число портов.
        """
        public = {
            name
            for name, service in prod_config["services"].items()
            for port in service.get("ports", [])
            if not str(port).startswith("127.0.0.1:")
        }
        assert public == {"nginx"}, f"наружу смотрят: {sorted(public)}, а должен только nginx"


class TestDataSurvivesRedeploy:
    """Данные переживают пересборку — иначе первый же redeploy стирает продакшен."""

    def test_pgdata_volume_is_named_and_stable(self, prod_config: dict) -> None:
        """Том именованный: анонимный том теряется при пересоздании контейнера (BUG-010)."""
        volumes = prod_config.get("volumes", {})
        assert "pgdata" in volumes
        assert volumes["pgdata"]["name"] == "finpilot_pgdata"
        assert any(
            str(v).startswith("pgdata:") for v in prod_config["services"]["db"]["volumes"]
        ), "БД не примонтирована к именованному тому"

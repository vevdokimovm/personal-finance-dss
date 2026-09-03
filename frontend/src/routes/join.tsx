import { createFileRoute } from "@tanstack/react-router";
import { JoinPage } from "@pages/households";

/* Адрес задан БЭКЕНДОМ: `routes_households.py::_invite_url` строит
   `base_url + "/join?token=..."`, и эта ссылка уходит приглашаемому. Роут обязан
   называться именно так — до v8.36.0 его не было вовсе, и приглашение вело в никуда
   (гипотеза H12, второй случай). Гейт `tests/test_spa_navigation_reachability.py`
   теперь сверяет все собранные на сервере ссылки с деревом роутов. */
export const Route = createFileRoute("/join")({
  component: JoinPage,
});

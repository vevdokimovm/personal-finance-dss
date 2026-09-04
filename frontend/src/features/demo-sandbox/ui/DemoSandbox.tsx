import { useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useDemoCases, useLoadDemoCase } from "@entities/demo";
import type { DemoCase } from "@entities/demo";
import { Button, Modal, toast } from "@shared/ui";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { t } from "@shared/lib/i18n/t";
import "./DemoSandbox.css";

/**
 * Гостевая песочница: десять эталонных портретов (v8.46.0).
 *
 * 🔴 Функция была в Jinja и потерялась при переносе фронта на React — найдено в v8.45.0,
 * когда тесты видимости `demo-case-select` упали вместе со снятием Jinja-страниц. Сервер
 * всё это время умел (`/api/demo/cases`, `/api/demo/load`), недоступен был только путь.
 *
 * README рекламирует «Демо за 30 секунд» как самый быстрый способ понять продукт, и это
 * правда: портреты считает реальный движок. Без входа человек без своих данных видит
 * пустой дашборд и предложение внести сотню операций руками.
 *
 * 🔴 Загрузка портрета — ДЕСТРУКТИВНОЕ действие: `/demo/load` вызывает `_clear_all`
 * и жёстко удаляет всё, что гость успел внести, мимо мягкого удаления и отмены
 * (`routes_demo.py`). Первая редакция обещала обратное («ваши данные не заменят и никуда
 * не сохранятся») и грузила по одному клику — гость, набравший свои операции без
 * регистрации, терял их без предупреждения (design-critic). Отсюда подтверждение
 * и честная подпись.
 */

/** Ярлык ситуации: цвет приходит с сервера семантическим словом, не хексом — палитра
 * остаётся во фронте, бэкенд говорит только о смысле. Список сверен с `CASE_META`
 * (v8.46.0): раньше сервер слал ещё `cyan`, `violet`, `slate`, и четыре портрета
 * из десяти молча теряли цвет ярлыка. */
const ACCENTS = new Set(["amber", "green", "red", "blue"]);

export function DemoSandbox({
  isGuest = true,
  pendingKey: pendingKeyProp,
}: {
  isGuest?: boolean;
  /** Только для тестов: какой портрет «грузится сейчас». В продукте выводится из мутации. */
  pendingKey?: string | null;
}) {
  const cases = useDemoCases(isGuest);
  const load = useLoadDemoCase();
  const queryClient = useQueryClient();
  const [confirming, setConfirming] = useState<DemoCase | null>(null);
  const [pending, setPending] = useState<string | null>(null);
  const triggerRef = useRef<HTMLButtonElement | null>(null);

  const pendingKey = pendingKeyProp ?? pending;

  // Сервер отдаёт 403 вошедшему: песочница не смешивается с настоящими данными.
  // Показывать её вошедшему — кнопка, ведущая в отказ ([IA-04]).
  if (!isGuest) return null;

  if (cases.isLoading) {
    return (
      <section className="fp-panel fp-demo" aria-labelledby="fp-demo-title">
        <h2 id="fp-demo-title">{t("Посмотреть на примере")}</h2>
        <p className="fp-demo__note" role="status">
          {t("Загружаем примеры…")}
        </p>
      </section>
    );
  }

  if (cases.isError) {
    return (
      <section className="fp-panel fp-demo" aria-labelledby="fp-demo-title">
        <h2 id="fp-demo-title">{t("Посмотреть на примере")}</h2>
        <div className="fp-demo__note" role="alert">
          <p>
            {extractErrorMessage(
              cases.error,
              t("Не удалось загрузить примеры. Проверьте соединение и попробуйте снова."),
            )}
          </p>
        </div>
        {/* Кнопка ВНЕ живой области: экстренное сообщение объявляется первым, и
            управляющий элемент внутри него в части связок браузер+AT теряется
            (a11y-auditor). */}
        <Button variant="ghost" onClick={() => void cases.refetch()}>
          {t("Попробовать снова")}
        </Button>
      </section>
    );
  }

  function runLoad(item: DemoCase) {
    setPending(item.key);
    load.mutate(
      { caseKey: item.key },
      {
        onSuccess: () => {
          setPending(null);
          // 🔴 Без сброса кеша экраны показывают прежнюю пустоту, и человек видит
          // «сломанную кнопку»: нажал — ничего не изменилось.
          void queryClient.invalidateQueries();
          toast.success(t("Загружен пример: {name}", { name: item.name }));
        },
        onError: (error) => {
          setPending(null);
          toast.error(
            extractErrorMessage(error, t("Не удалось загрузить пример. Попробуйте ещё раз.")),
          );
        },
      },
    );
  }

  return (
    <section className="fp-panel fp-demo" aria-labelledby="fp-demo-title">
      <h2 id="fp-demo-title">{t("Посмотреть на примере — 30 секунд")}</h2>
      <p className="fp-lede">
        {t(
          "Выберите портрет, похожий на вашу ситуацию: расчёт пойдёт настоящим движком, " +
            "а не заглушкой. Это демонстрационные данные, и они заменят всё, что вы уже " +
            "внесли, — вернуть внесённое будет нельзя.",
        )}
      </p>

      <ul className="fp-demo__list" role="list">
        {(cases.data?.cases ?? []).map((item) => {
          const busy = pendingKey === item.key;
          return (
            <li key={item.key}>
              {/* Вся карточка — одна кнопка: цель нажатия набирает высоту сама, а описание
                  попадает в доступное имя и звучит при обходе по Tab ([A11Y-09]). */}
              <button
                type="button"
                className="fp-demo__card"
                aria-busy={busy || undefined}
                /* 🔴 `aria-disabled`, а не `disabled`: последний выкидывает кнопку из дерева
                   доступности и снимает с неё фокус ПРЯМО в момент нажатия — клавиатурный
                   пользователь оказывается в начале документа (a11y-auditor). И гаснет
                   только та карточка, что грузится: первая редакция гасила все десять,
                   и экран читался как «всё сломалось» ([FB-02]). */
                aria-disabled={pendingKey !== null || undefined}
                onClick={(e) => {
                  if (pendingKey !== null) return;
                  triggerRef.current = e.currentTarget;
                  setConfirming(item);
                }}
              >
                <span className="fp-demo__head">
                  <span className="fp-demo__name">
                    {item.n}. {item.name}
                  </span>
                  <span
                    className={
                      ACCENTS.has(item.accent)
                        ? `fp-demo__tag fp-demo__tag--${item.accent}`
                        : "fp-demo__tag"
                    }
                  >
                    {item.tag}
                  </span>
                </span>
                <span className="fp-demo__role">{item.role}</span>
                <span className="fp-demo__label">{t("Ситуация")}</span>
                <span className="fp-demo__situation">{item.situation}</span>
                {/* «Что покажет алгоритм» — ДО нажатия, и с подписью: иначе выбор портрета
                    это лотерея, а именно ради него экран и существует. Подписи были
                    в Jinja-версии и потерялись при переносе. */}
                <span className="fp-demo__label">{t("Что покажет расчёт")}</span>
                <span className="fp-demo__expect">{item.expect}</span>
                {busy && <span className="fp-demo__busy">{t("Загружаем пример…")}</span>}
              </button>
            </li>
          );
        })}
      </ul>

      {/* Подтверждение: действие необратимо и стирает введённое ([FRM-07]). */}
      <Modal
        open={confirming !== null}
        onOpenChange={(open) => !open && setConfirming(null)}
        title={t("Заменить данные демонстрационными?")}
        description={t("Введённые вами операции, цели и кредиты будут удалены без возможности вернуть.")}
        returnFocusTo={() => triggerRef.current}
      >
        <p>
          {confirming
            ? t(
                "Загрузим пример «{name}». Всё, что вы внесли сами, будет удалено — " +
                  "вернуть это будет нельзя.",
                { name: confirming.name },
              )
            : ""}
        </p>
        <div className="fp-demo__actions">
          <Button variant="ghost" onClick={() => setConfirming(null)}>
            {t("Отмена")}
          </Button>
          <Button
            variant="primary"
            onClick={() => {
              const item = confirming;
              setConfirming(null);
              if (item) runLoad(item);
            }}
          >
            {t("Заменить и показать")}
          </Button>
        </div>
      </Modal>
    </section>
  );
}

import { useHouseholds } from "@entities/households";
import { t } from "@shared/lib/i18n/t";
import "./SharedBadge.css";

/**
 * Признак «эта запись общая» в списках (v8.55.0).
 *
 * 🔴 Найдено `design-critic` при разборе `HouseholdScopeField`: выбор поделиться
 * появился, а состояние записи после сохранения не читалось нигде — `household_id`
 * доезжал до ответов всех пяти сущностей и не показывался ни в одном списке.
 * Человек мог проверить, что поделился, только сравнив свой список со списком
 * родственника. Тот же класс, что и сама починка: право есть, в интерфейсе не видно.
 */
export function SharedBadge({ householdId }: { householdId?: number | null }) {
  const { data } = useHouseholds();

  if (householdId == null) return null;

  /* Имя может не найтись: список семей не загрузился или человека уже исключили.
     Промолчать в этом случае значило бы показать общую запись как личную — соврать
     о том, кто видит эти деньги. Имя опускаем, факт общности — никогда. */
  const household = (data ?? []).find((item) => item.id === householdId);

  return (
    <span className="fp-shared-badge">
      {household ? t("Общая · {name}", { name: household.name }) : t("Общая")}
    </span>
  );
}

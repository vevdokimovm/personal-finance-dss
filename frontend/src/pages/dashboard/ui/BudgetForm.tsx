import { useRef, useState, type FormEvent } from "react";
import { Button, Modal, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { SessionExpiredBanner, isSessionExpired } from "@entities/auth";
import { useCreateBudget, type BudgetStatus } from "@entities/budgets";
import "@shared/ui/entityForm.css";
import { HouseholdScopeField } from "@features/household-scope";

interface BudgetFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** undefined — режим создания, иначе правка лимита этого бюджета. */
  budget?: BudgetStatus;
}

type FieldErrors = Partial<Record<"category" | "limitAmount", string>>;

/** Создание/правка лимита бюджета (Батч 3 CRUD-паритета, ROADMAP §8.2). У бэка нет
 * отдельного PUT — POST /api/budgets делает upsert по `category` (FR-22): существующая
 * у владельца категория обновляет лимит, новая создаёт строку. Значит «категория» —
 * фактический идентификатор записи, не редактируемое поле: отправка формы правки с
 * ДРУГИМ значением category создала бы вторую, независимую строку бюджета вместо
 * переименования этой — поле заблокировано в режиме правки, чтобы это не стало
 * незаметной ловушкой (design-critic must-fix класса, что переименование целей/счетов
 * в других формах батча не допускается там, где бэк не поддерживает ключ-замену).
 */
export function BudgetForm({ open, onOpenChange, budget }: BudgetFormProps) {
  const isEdit = budget != null;
  const [category, setCategory] = useState(budget?.category ?? "");
  const [limitAmount, setLimitAmount] = useState(budget ? String(budget.limit_amount) : "");
  const [errors, setErrors] = useState<FieldErrors>({});
  /* Владелец записи выбирается только при СОЗДАНИИ: PUT на бэкенде `household_id`
     не принимает, и показать контрол в правке значило бы обещать переезд записи
     между личным и общим, которого код не делает. */
  const [householdId, setHouseholdId] = useState<number | null>(null);

  const categoryRef = useRef<HTMLInputElement>(null);
  const limitRef = useRef<HTMLInputElement>(null);

  const create = useCreateBudget();
  const pending = create.isPending;
  const mutationError = create.error;

  function validate(): FieldErrors {
    const next: FieldErrors = {};
    if (!category.trim()) next.category = t("Укажите категорию.");
    if (!limitAmount || Number(limitAmount) <= 0) {
      next.limitAmount = t("Укажите лимит больше нуля.");
    }
    return next;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const nextErrors = validate();
    setErrors(nextErrors);
    if (nextErrors.category) {
      categoryRef.current?.focus();
      return;
    }
    if (nextErrors.limitAmount) {
      limitRef.current?.focus();
      return;
    }
    try {
      await create.mutateAsync({
        category: category.trim(),
        limit_amount: Number(limitAmount),
        ...(isEdit ? {} : { household_id: householdId }),
      });
      toast.success(isEdit ? t("Лимит бюджета изменён.") : t("Бюджет добавлен."));
      onOpenChange(false);
    } catch {
      // Ошибка уже видна баннером в форме (mutationError) — модалку не закрываем.
    }
  }

  const errorMessage = mutationError
    ? extractErrorMessage(mutationError, t("Не получилось сохранить. Попробуйте ещё раз."))
    : null;

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={isEdit ? t("Изменить лимит бюджета") : t("Новый бюджет")}
      description={t("Лимит расходов по категории на месяц.")}
    >
      <form className="fp-entity-form" onSubmit={handleSubmit} noValidate>
        {/* 🔴 401 на СОХРАНЕНИИ — истёкшая сессия, а не сбой связи. Общий текст
            «Попробуйте ещё раз» здесь вреден: повтор возвращает 401 бесконечно.
            v9.1.0 закрыл этот разбор только на загрузке экрана; форму пропустили. */}
        {mutationError && isSessionExpired(mutationError) ? (
          <SessionExpiredBanner />
        ) : (
          errorMessage && (
            <p className="fp-entity-form__banner" role="alert">
              {errorMessage}
            </p>
          )
        )}
        <div className="fp-entity-form__field">
          <label htmlFor="budget-form-category">{t("Категория *")}</label>
          <input
            id="budget-form-category"
            ref={categoryRef}
            type="text"
            aria-required="true"
            aria-invalid={errors.category ? "true" : undefined}
            aria-describedby={errors.category ? "budget-form-category-error" : undefined}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            disabled={isEdit}
          />
          {isEdit && (
            <p className="fp-entity-form__hint">
              {t(
                "Категорию нельзя изменить — удалите бюджет и создайте новый с другой категорией.",
              )}
            </p>
          )}
          {errors.category && (
            <p id="budget-form-category-error" className="fp-entity-form__error">
              {errors.category}
            </p>
          )}
        </div>
        {!isEdit && (
          <HouseholdScopeField
            value={householdId}
            onChange={setHouseholdId}
            idPrefix="budget-form"
          />
        )}
        <div className="fp-entity-form__field">
          <label htmlFor="budget-form-limit">{t("Лимит в месяц, ₽ *")}</label>
          <input
            id="budget-form-limit"
            ref={limitRef}
            type="number"
            inputMode="decimal"
            min={0}
            step="0.01"
            aria-required="true"
            aria-invalid={errors.limitAmount ? "true" : undefined}
            aria-describedby={errors.limitAmount ? "budget-form-limit-error" : undefined}
            value={limitAmount}
            onChange={(e) => setLimitAmount(e.target.value)}
          />
          {errors.limitAmount && (
            <p id="budget-form-limit-error" className="fp-entity-form__error">
              {errors.limitAmount}
            </p>
          )}
        </div>
        <div className="fp-entity-form__actions">
          <Button type="submit" variant="primary" disabled={pending} aria-busy={pending}>
            {pending ? t("Сохраняем…") : isEdit ? t("Сохранить") : t("Добавить")}
          </Button>
          <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
            {t("Отмена")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

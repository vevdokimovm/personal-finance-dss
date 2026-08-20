import { useRef, useState, type FormEvent } from "react";
import { Button, Modal, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import {
  useCreateTransaction,
  useUpdateTransaction,
  type Transaction,
} from "@entities/transactions";
import "@shared/ui/entityForm.css";

interface TransactionFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** undefined — режим создания, иначе правка этой операции. */
  transaction?: Transaction;
}

function toDateInputValue(iso: string | null | undefined): string {
  return iso ? iso.slice(0, 10) : "";
}

type FieldErrors = Partial<Record<"amount" | "date", string>>;

/** Создание/правка операции (Батч 2 CRUD-паритета, ROADMAP §8.2). Решение владельца:
 * `description` — в форме, `mcc`/`currency` — сознательно нет (служебные поля импорта
 * банковских выписок, продукт рублёвый). */
export function TransactionForm({ open, onOpenChange, transaction }: TransactionFormProps) {
  const isEdit = transaction != null;
  const [amount, setAmount] = useState(transaction ? String(transaction.amount) : "");
  const [type, setType] = useState<"income" | "expense">(transaction?.type ?? "expense");
  const [date, setDate] = useState(
    toDateInputValue(transaction?.date) || new Date().toISOString().slice(0, 10),
  );
  const [category, setCategory] = useState(transaction?.category ?? "");
  const [description, setDescription] = useState(transaction?.description ?? "");
  const [errors, setErrors] = useState<FieldErrors>({});

  const amountRef = useRef<HTMLInputElement>(null);
  const dateRef = useRef<HTMLInputElement>(null);

  const create = useCreateTransaction();
  const update = useUpdateTransaction();
  const pending = create.isPending || update.isPending;
  const mutationError = create.error ?? update.error;

  // FRM-04 (Must): ошибка у поля + текст + фокус на первое ошибочное — см. ObligationForm.tsx.
  function validate(): FieldErrors {
    const next: FieldErrors = {};
    if (!amount || Number(amount) <= 0) next.amount = t("Укажите сумму больше нуля.");
    if (!date) next.date = t("Укажите дату.");
    return next;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const nextErrors = validate();
    setErrors(nextErrors);
    if (nextErrors.amount) {
      amountRef.current?.focus();
      return;
    }
    if (nextErrors.date) {
      dateRef.current?.focus();
      return;
    }
    const body = {
      amount: Number(amount),
      type,
      date: new Date(date).toISOString(),
      category: category.trim() || null,
      description: description.trim() || null,
    };
    try {
      if (isEdit) {
        await update.mutateAsync({ id: transaction.id, body });
        toast.success(t("Операция изменена."));
      } else {
        await create.mutateAsync(body);
        toast.success(t("Операция добавлена."));
      }
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
      title={isEdit ? t("Изменить операцию") : t("Новая операция")}
      description={t("Доход или расход: сумма, дата, категория и описание.")}
    >
      <form className="fp-entity-form" onSubmit={handleSubmit} noValidate>
        {errorMessage && (
          <p className="fp-entity-form__banner" role="alert">
            {errorMessage}
          </p>
        )}
        <div className="fp-entity-form__field">
          <span className="fp-entity-form__label" id="transaction-form-type-label">
            {t("Тип")}
          </span>
          <div
            className="fp-entity-form__radio-group"
            role="radiogroup"
            aria-labelledby="transaction-form-type-label"
          >
            <label>
              <input
                type="radio"
                name="transaction-type"
                checked={type === "expense"}
                onChange={() => setType("expense")}
              />
              {t("Расход")}
            </label>
            <label>
              <input
                type="radio"
                name="transaction-type"
                checked={type === "income"}
                onChange={() => setType("income")}
              />
              {t("Доход")}
            </label>
          </div>
        </div>
        <div className="fp-entity-form__row">
          <div className="fp-entity-form__field">
            <label htmlFor="transaction-form-amount">{t("Сумма, ₽ *")}</label>
            <input
              id="transaction-form-amount"
              ref={amountRef}
              type="number"
              inputMode="decimal"
              min={0}
              step="0.01"
              aria-required="true"
              aria-invalid={errors.amount ? "true" : undefined}
              aria-describedby={errors.amount ? "transaction-form-amount-error" : undefined}
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            {errors.amount && (
              <p id="transaction-form-amount-error" className="fp-entity-form__error">
                {errors.amount}
              </p>
            )}
          </div>
          <div className="fp-entity-form__field">
            <label htmlFor="transaction-form-date">{t("Дата *")}</label>
            <input
              id="transaction-form-date"
              ref={dateRef}
              type="date"
              aria-required="true"
              aria-invalid={errors.date ? "true" : undefined}
              aria-describedby={errors.date ? "transaction-form-date-error" : undefined}
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
            {errors.date && (
              <p id="transaction-form-date-error" className="fp-entity-form__error">
                {errors.date}
              </p>
            )}
          </div>
        </div>
        <div className="fp-entity-form__field">
          <label htmlFor="transaction-form-category">{t("Категория")}</label>
          <input
            id="transaction-form-category"
            type="text"
            placeholder={t("Определится автоматически, если не указать")}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          />
        </div>
        <div className="fp-entity-form__field">
          <label htmlFor="transaction-form-description">{t("Описание (необязательно)")}</label>
          <input
            id="transaction-form-description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
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

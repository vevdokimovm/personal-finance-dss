import { useRef, useState, type FormEvent } from "react";
import { Button, Modal, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { useCreateObligation, useUpdateObligation, type Obligation } from "@entities/obligations";
import "@shared/ui/entityForm.css";

interface ObligationFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** undefined — режим создания, иначе правка этого обязательства. */
  obligation?: Obligation;
}

function toDateInputValue(iso: string | null | undefined): string {
  return iso ? iso.slice(0, 10) : "";
}

/** `0.078 * 100 === 7.800000000000001` (двоичная арифметика с плавающей точкой) — без
 * округления поле «Ставка» при правке показывало бы мусор из полутора десятков знаков после
 * запятой (design-critic, Батч 1). Модель хранит ставку с точностью до 4 знаков (Numeric(6,4)),
 * двух знаков в процентах достаточно ровно. */
function rateToPercentInput(rate: number): string {
  return String(Number((rate * 100).toFixed(2)));
}

type FieldErrors = Partial<Record<"name" | "amount" | "monthlyPayment", string>>;

/** Создание/правка обязательства (Батч 1 CRUD-паритета, ROADMAP §8.2) — поля те же, что были
 * в Jinja-форме `#obligation-form` (frontend/static/js/app.js): без `bank`/`type`/`currency` —
 * их не было в исходной форме, не расширяем охват молча. `interest_rate` в модели — доля
 * (0.15 = 15%), инпут — проценты (0-100), как было в Jinja (конвертация на границе формы,
 * не в хранимых данных). */
export function ObligationForm({ open, onOpenChange, obligation }: ObligationFormProps) {
  const isEdit = obligation != null;
  const [name, setName] = useState(obligation?.name ?? "");
  const [amount, setAmount] = useState(obligation ? String(obligation.amount) : "");
  const [interestRatePct, setInterestRatePct] = useState(
    obligation ? rateToPercentInput(obligation.interest_rate) : "",
  );
  const [term, setTerm] = useState(obligation ? String(obligation.term) : "");
  const [monthlyPayment, setMonthlyPayment] = useState(
    obligation ? String(obligation.monthly_payment) : "",
  );
  const [paymentDay, setPaymentDay] = useState(obligation ? String(obligation.payment_day) : "1");
  const [startDate, setStartDate] = useState(toDateInputValue(obligation?.start_date));
  const [comment, setComment] = useState(obligation?.comment ?? "");
  const [errors, setErrors] = useState<FieldErrors>({});

  const nameRef = useRef<HTMLInputElement>(null);
  const amountRef = useRef<HTMLInputElement>(null);
  const paymentRef = useRef<HTMLInputElement>(null);

  const create = useCreateObligation();
  const update = useUpdateObligation();
  const pending = create.isPending || update.isPending;
  const mutationError = create.error ?? update.error;

  // FRM-04 (Must): ошибка у поля + текст + фокус на первое ошибочное — не полагаемся на
  // нативные браузерные пузыри `required` (непредсказуемо озвучиваются скринридерами,
  // design-critic/a11y-auditor, Батч 1).
  function validate(): FieldErrors {
    const next: FieldErrors = {};
    if (!name.trim()) next.name = t("Укажите название.");
    if (!amount || Number(amount) <= 0) next.amount = t("Укажите остаток долга больше нуля.");
    if (!monthlyPayment || Number(monthlyPayment) <= 0) {
      next.monthlyPayment = t("Укажите платёж больше нуля.");
    }
    return next;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const nextErrors = validate();
    setErrors(nextErrors);
    if (nextErrors.name) {
      nameRef.current?.focus();
      return;
    }
    if (nextErrors.amount) {
      amountRef.current?.focus();
      return;
    }
    if (nextErrors.monthlyPayment) {
      paymentRef.current?.focus();
      return;
    }
    const body = {
      name: name.trim(),
      amount: Number(amount),
      interest_rate: (Number(interestRatePct) || 0) / 100,
      term: Number(term) || 0,
      monthly_payment: Number(monthlyPayment),
      payment_day: Number(paymentDay) || 1,
      start_date: startDate ? new Date(startDate).toISOString() : null,
      comment: comment.trim() || null,
    };
    try {
      if (isEdit) {
        await update.mutateAsync({ id: obligation.id, body });
        toast.success(t("Обязательство изменено."));
      } else {
        await create.mutateAsync(body);
        toast.success(t("Обязательство добавлено."));
      }
      onOpenChange(false);
    } catch {
      // Ошибка уже видна баннером в форме (mutationError) — модалку не закрываем,
      // пользователь может исправить и отправить снова.
    }
  }

  const errorMessage = mutationError
    ? extractErrorMessage(mutationError, t("Не получилось сохранить. Попробуйте ещё раз."))
    : null;

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={isEdit ? t("Изменить обязательство") : t("Новое обязательство")}
      description={t("Форма кредита или рассрочки: сумма, ставка, срок и платёж.")}
    >
      <form className="fp-entity-form" onSubmit={handleSubmit} noValidate>
        {errorMessage && (
          <p className="fp-entity-form__banner" role="alert">
            {errorMessage}
          </p>
        )}
        <div className="fp-entity-form__field">
          <label htmlFor="obligation-form-name">{t("Название *")}</label>
          <input
            id="obligation-form-name"
            ref={nameRef}
            type="text"
            aria-required="true"
            aria-invalid={errors.name ? "true" : undefined}
            aria-describedby={errors.name ? "obligation-form-name-error" : undefined}
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          {errors.name && (
            <p id="obligation-form-name-error" className="fp-entity-form__error">
              {errors.name}
            </p>
          )}
        </div>
        <div className="fp-entity-form__row">
          <div className="fp-entity-form__field">
            <label htmlFor="obligation-form-amount">{t("Остаток долга, ₽ *")}</label>
            <input
              id="obligation-form-amount"
              ref={amountRef}
              type="number"
              inputMode="decimal"
              min={0}
              step="0.01"
              aria-required="true"
              aria-invalid={errors.amount ? "true" : undefined}
              aria-describedby={errors.amount ? "obligation-form-amount-error" : undefined}
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            {errors.amount && (
              <p id="obligation-form-amount-error" className="fp-entity-form__error">
                {errors.amount}
              </p>
            )}
          </div>
          <div className="fp-entity-form__field">
            <label htmlFor="obligation-form-rate">{t("Ставка, % годовых")}</label>
            <input
              id="obligation-form-rate"
              type="number"
              inputMode="decimal"
              min={0}
              step="0.01"
              value={interestRatePct}
              onChange={(e) => setInterestRatePct(e.target.value)}
            />
          </div>
        </div>
        <div className="fp-entity-form__row">
          <div className="fp-entity-form__field">
            <label htmlFor="obligation-form-payment">{t("Платёж в месяц, ₽ *")}</label>
            <input
              id="obligation-form-payment"
              ref={paymentRef}
              type="number"
              inputMode="decimal"
              min={0}
              step="0.01"
              aria-required="true"
              aria-invalid={errors.monthlyPayment ? "true" : undefined}
              aria-describedby={errors.monthlyPayment ? "obligation-form-payment-error" : undefined}
              value={monthlyPayment}
              onChange={(e) => setMonthlyPayment(e.target.value)}
            />
            {errors.monthlyPayment && (
              <p id="obligation-form-payment-error" className="fp-entity-form__error">
                {errors.monthlyPayment}
              </p>
            )}
          </div>
          <div className="fp-entity-form__field">
            <label htmlFor="obligation-form-term">{t("Срок, мес.")}</label>
            <input
              id="obligation-form-term"
              type="number"
              inputMode="numeric"
              min={0}
              step="1"
              value={term}
              onChange={(e) => setTerm(e.target.value)}
            />
          </div>
        </div>
        <div className="fp-entity-form__row">
          <div className="fp-entity-form__field">
            <label htmlFor="obligation-form-payment-day">{t("День платежа")}</label>
            <input
              id="obligation-form-payment-day"
              type="number"
              inputMode="numeric"
              min={1}
              max={31}
              step="1"
              value={paymentDay}
              onChange={(e) => setPaymentDay(e.target.value)}
            />
          </div>
          <div className="fp-entity-form__field">
            <label htmlFor="obligation-form-start-date">{t("Дата открытия")}</label>
            <input
              id="obligation-form-start-date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
        </div>
        <div className="fp-entity-form__field">
          <label htmlFor="obligation-form-comment">{t("Комментарий (необязательно)")}</label>
          <input
            id="obligation-form-comment"
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
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

import { useRef, useState, type FormEvent } from "react";
import { Button, Modal, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { useCreateAsset, useUpdateAsset, type LiquidAsset } from "@entities/assets";
import "@shared/ui/entityForm.css";

interface AssetFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** undefined — режим создания, иначе правка этого актива. */
  asset?: LiquidAsset;
}

const TYPE_OPTIONS: { value: string; label: string }[] = [
  { value: "deposit", label: "Депозит" },
  { value: "savings_account", label: "Накопительный счёт" },
  { value: "cash", label: "Кэш" },
];

/** `0.16 * 100 === 16.000000000000004` — без округления при правке ставка показывала бы
 * мусор из полутора десятков знаков после запятой (design-critic, Батч 1, тот же баг, что
 * в ObligationForm). Модель хранит ставку с точностью до 4 знаков (Numeric(6,4)). */
function rateToPercentInput(rate: number): string {
  return String(Number((rate * 100).toFixed(2)));
}

type FieldErrors = Partial<Record<"name" | "amount", string>>;

/** Создание/правка ликвидного актива (Батч 1 CRUD-паритета, ROADMAP §8.2) — поля те же,
 * что были в Jinja-форме `#asset-form` (frontend/static/js/app.js). `interest_rate` в модели —
 * доля (0.16 = 16%), инпут — проценты (0-100), как было в Jinja. */
export function AssetForm({ open, onOpenChange, asset }: AssetFormProps) {
  const isEdit = asset != null;
  const [name, setName] = useState(asset?.name ?? "");
  const [amount, setAmount] = useState(asset ? String(asset.amount) : "");
  const [interestRatePct, setInterestRatePct] = useState(
    asset ? rateToPercentInput(asset.interest_rate) : "",
  );
  const [type, setType] = useState(asset?.type ?? "deposit");
  const [comment, setComment] = useState(asset?.comment ?? "");
  const [errors, setErrors] = useState<FieldErrors>({});

  const nameRef = useRef<HTMLInputElement>(null);
  const amountRef = useRef<HTMLInputElement>(null);

  const create = useCreateAsset();
  const update = useUpdateAsset();
  const pending = create.isPending || update.isPending;
  const mutationError = create.error ?? update.error;

  // FRM-04 (Must) — см. тот же приём в ObligationForm.tsx. Название обязательно (design-critic,
  // Батч 1: пустое имя молча становилось «Депозит» — два таких актива неотличимы в списке).
  function validate(): FieldErrors {
    const next: FieldErrors = {};
    if (!name.trim()) next.name = t("Укажите название.");
    if (!amount || Number(amount) <= 0) next.amount = t("Укажите сумму больше нуля.");
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
    const body = {
      name: name.trim(),
      amount: Number(amount),
      interest_rate: (Number(interestRatePct) || 0) / 100,
      type,
      comment: comment.trim() || null,
    };
    try {
      if (isEdit) {
        await update.mutateAsync({ id: asset.id, body });
        toast.success(t("Актив изменён."));
      } else {
        await create.mutateAsync(body);
        toast.success(t("Актив добавлен."));
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
      title={isEdit ? t("Изменить актив") : t("Новый актив")}
      description={t("Форма депозита, накопительного счёта или кэша.")}
    >
      <form className="fp-entity-form" onSubmit={handleSubmit} noValidate>
        {errorMessage && (
          <p className="fp-entity-form__banner" role="alert">
            {errorMessage}
          </p>
        )}
        <div className="fp-entity-form__field">
          <label htmlFor="asset-form-name">{t("Название *")}</label>
          <input
            id="asset-form-name"
            ref={nameRef}
            type="text"
            aria-required="true"
            aria-invalid={errors.name ? "true" : undefined}
            aria-describedby={errors.name ? "asset-form-name-error" : undefined}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t("Депозит")}
          />
          {errors.name && (
            <p id="asset-form-name-error" className="fp-entity-form__error">
              {errors.name}
            </p>
          )}
        </div>
        <div className="fp-entity-form__field">
          <label htmlFor="asset-form-type">{t("Тип")}</label>
          <select id="asset-form-type" value={type} onChange={(e) => setType(e.target.value)}>
            {TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {t(opt.label)}
              </option>
            ))}
          </select>
        </div>
        <div className="fp-entity-form__row">
          <div className="fp-entity-form__field">
            <label htmlFor="asset-form-amount">{t("Сумма, ₽ *")}</label>
            <input
              id="asset-form-amount"
              ref={amountRef}
              type="number"
              inputMode="decimal"
              min={0}
              step="0.01"
              aria-required="true"
              aria-invalid={errors.amount ? "true" : undefined}
              aria-describedby={errors.amount ? "asset-form-amount-error" : undefined}
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            {errors.amount && (
              <p id="asset-form-amount-error" className="fp-entity-form__error">
                {errors.amount}
              </p>
            )}
          </div>
          <div className="fp-entity-form__field">
            <label htmlFor="asset-form-rate">{t("Ставка, % годовых")}</label>
            <input
              id="asset-form-rate"
              type="number"
              inputMode="decimal"
              min={0}
              step="0.01"
              value={interestRatePct}
              onChange={(e) => setInterestRatePct(e.target.value)}
            />
          </div>
        </div>
        <div className="fp-entity-form__field">
          <label htmlFor="asset-form-comment">{t("Комментарий (необязательно)")}</label>
          <input
            id="asset-form-comment"
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

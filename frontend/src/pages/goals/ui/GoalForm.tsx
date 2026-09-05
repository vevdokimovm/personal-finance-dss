import { useRef, useState, type FormEvent } from "react";
import { Button, Modal, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import {
  useCreateGoal,
  useUpdateGoal,
  GOAL_CATEGORY_OPTIONS,
  type Goal,
} from "@entities/goals";
import { useLiquidAssets } from "@entities/assets";
import type { GoalCategory } from "@shared/api/generated";
import "@shared/ui/entityForm.css";
import { HouseholdScopeField } from "@features/household-scope";

interface GoalFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** undefined — режим создания, иначе правка этой цели. `current_amount` сюда не входит
   * (владелец: не общий edit для прогресса — см. GoalContributionForm). */
  goal?: Goal;
}

function toDateInputValue(iso: string | null | undefined): string {
  return iso ? iso.slice(0, 10) : "";
}

type FieldErrors = Partial<Record<"name" | "targetAmount", string>>;

/** Создание/правка цели (Батч 2 CRUD-паритета, ROADMAP §8.2). `current_amount` в форме
 * нет вообще — прогресс вносится отдельным действием («Внести прогресс», GoalRow), для целей
 * с `linked_asset_id` он read-only и выводится из баланса привязанного актива. */
export function GoalForm({ open, onOpenChange, goal }: GoalFormProps) {
  const isEdit = goal != null;
  const [name, setName] = useState(goal?.name ?? "");
  const [targetAmount, setTargetAmount] = useState(goal ? String(goal.target_amount) : "");
  const [deadline, setDeadline] = useState(toDateInputValue(goal?.deadline));
  const [category, setCategory] = useState<GoalCategory>(
    (goal?.category as GoalCategory) ?? "material",
  );
  const [linkedAssetId, setLinkedAssetId] = useState(
    goal?.linked_asset_id != null ? String(goal.linked_asset_id) : "",
  );
  const [comment, setComment] = useState(goal?.comment ?? "");
  const [errors, setErrors] = useState<FieldErrors>({});
  /* Владелец записи выбирается только при СОЗДАНИИ: PUT на бэкенде `household_id`
     не принимает, и показать контрол в правке значило бы обещать переезд записи
     между личным и общим, которого код не делает. */
  const [householdId, setHouseholdId] = useState<number | null>(null);

  const nameRef = useRef<HTMLInputElement>(null);
  const targetAmountRef = useRef<HTMLInputElement>(null);

  const assetsQuery = useLiquidAssets();
  const create = useCreateGoal();
  const update = useUpdateGoal();
  const pending = create.isPending || update.isPending;
  const mutationError = create.error ?? update.error;

  // FRM-04 (Must): ошибка у поля + текст + фокус на первое ошибочное — см. ObligationForm.tsx.
  function validate(): FieldErrors {
    const next: FieldErrors = {};
    if (!name.trim()) next.name = t("Укажите название.");
    if (!targetAmount || Number(targetAmount) <= 0) {
      next.targetAmount = t("Укажите сумму цели больше нуля.");
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
    if (nextErrors.targetAmount) {
      targetAmountRef.current?.focus();
      return;
    }
    const linkedAssetIdValue = linkedAssetId ? Number(linkedAssetId) : null;
    try {
      if (isEdit) {
        await update.mutateAsync({
          id: goal.id,
          body: {
            name: name.trim(),
            target_amount: Number(targetAmount),
            deadline: deadline ? new Date(deadline).toISOString() : null,
            category,
            linked_asset_id: linkedAssetIdValue,
            comment: comment.trim() || null,
          },
        });
        toast.success(t("Цель изменена."));
      } else {
        await create.mutateAsync({
          ...(isEdit ? {} : { household_id: householdId }),
          name: name.trim(),
          target_amount: Number(targetAmount),
          current_amount: 0,
          deadline: deadline ? new Date(deadline).toISOString() : null,
          category,
          linked_asset_id: linkedAssetIdValue,
          comment: comment.trim() || null,
        });
        toast.success(t("Цель добавлена."));
      }
      onOpenChange(false);
    } catch {
      // Ошибка уже видна баннером в форме (mutationError) — модалку не закрываем.
    }
  }

  const errorMessage = mutationError
    ? extractErrorMessage(mutationError, t("Не получилось сохранить. Попробуйте ещё раз."))
    : null;
  const assets = assetsQuery.data ?? [];

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={isEdit ? t("Изменить цель") : t("Новая цель")}
      description={t("Название, сумма и срок цели. Стартовое накопление вносится отдельно.")}
    >
      <form className="fp-entity-form" onSubmit={handleSubmit} noValidate>
        {errorMessage && (
          <p className="fp-entity-form__banner" role="alert">
            {errorMessage}
          </p>
        )}
        <div className="fp-entity-form__field">
          <label htmlFor="goal-form-name">{t("Название *")}</label>
          <input
            id="goal-form-name"
            ref={nameRef}
            type="text"
            aria-required="true"
            aria-invalid={errors.name ? "true" : undefined}
            aria-describedby={errors.name ? "goal-form-name-error" : undefined}
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          {errors.name && (
            <p id="goal-form-name-error" className="fp-entity-form__error">
              {errors.name}
            </p>
          )}
        </div>
        <div className="fp-entity-form__row">
          <div className="fp-entity-form__field">
            <label htmlFor="goal-form-target">{t("Сумма цели, ₽ *")}</label>
            <input
              id="goal-form-target"
              ref={targetAmountRef}
              type="number"
              inputMode="decimal"
              min={0}
              step="0.01"
              aria-required="true"
              aria-invalid={errors.targetAmount ? "true" : undefined}
              aria-describedby={errors.targetAmount ? "goal-form-target-error" : undefined}
              value={targetAmount}
              onChange={(e) => setTargetAmount(e.target.value)}
            />
            {errors.targetAmount && (
              <p id="goal-form-target-error" className="fp-entity-form__error">
                {errors.targetAmount}
              </p>
            )}
          </div>
        {!isEdit && (
          <HouseholdScopeField
            value={householdId}
            onChange={setHouseholdId}
            idPrefix="goal-form"
          />
        )}
          <div className="fp-entity-form__field">
            <label htmlFor="goal-form-deadline">{t("Срок (пусто — бессрочная)")}</label>
            <input
              id="goal-form-deadline"
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
            />
          </div>
        </div>
        <div className="fp-entity-form__field">
          <label htmlFor="goal-form-category">{t("Категория")}</label>
          <select
            id="goal-form-category"
            value={category}
            onChange={(e) => setCategory(e.target.value as GoalCategory)}
          >
            {GOAL_CATEGORY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        <div className="fp-entity-form__field">
          <label htmlFor="goal-form-asset">{t("Привязанный актив (необязательно)")}</label>
          {assetsQuery.isLoading ? (
            <select id="goal-form-asset" disabled value="">
              <option value="">{t("Загружаем активы…")}</option>
            </select>
          ) : assetsQuery.isError ? (
            <p className="fp-entity-form__error" role="alert">
              {t("Не получилось загрузить список активов.")}
            </p>
          ) : assets.length === 0 ? (
            <p className="fp-entity-form__hint">{t("Ликвидных активов пока нет.")}</p>
          ) : (
            <select
              id="goal-form-asset"
              value={linkedAssetId}
              aria-describedby={linkedAssetId ? "goal-form-asset-hint" : undefined}
              onChange={(e) => setLinkedAssetId(e.target.value)}
            >
              <option value="">{t("Не привязан — прогресс вносится вручную")}</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name}
                </option>
              ))}
            </select>
          )}
          {linkedAssetId && (
            <p id="goal-form-asset-hint" className="fp-entity-form__hint">
              {t("Прогресс будет выводиться из баланса актива — вносить вручную будет нельзя.")}
            </p>
          )}
        </div>
        <div className="fp-entity-form__field">
          <label htmlFor="goal-form-comment">{t("Комментарий (необязательно)")}</label>
          <input
            id="goal-form-comment"
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

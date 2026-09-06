import { useRef, useState, type FormEvent } from "react";
import { Button, Modal, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { useAddGoalContribution, type Goal } from "@entities/goals";
import "@shared/ui/entityForm.css";

interface GoalContributionFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** undefined, пока ничего не выбрано — компонент остаётся смонтированным всегда (как
   * GoalForm/TransactionForm), закрытие идёт переходом `open: true → false`, которым
   * управляет Radix (FocusScope/onCloseAutoFocus), а не размонтированием поддерева. Раньше
   * `GoalsPage` рендерил `<GoalContributionForm>` только пока `contributing` истинен — Radix
   * никогда не видел переход в закрытое состояние, путь возврата фокуса не гарантирован
   * (a11y-auditor, Батч 2, WCAG 2.4.3). */
  goal?: Goal;
}

/** «Внести прогресс» (владелец, Батч 2 ROADMAP §8.2) — отдельное действие от общей правки
 * цели: одно поле, прибавляет к current_amount, не перезаписывает. Не рендерится для целей
 * с linked_asset_id — GoalRow вместо кнопки показывает пояснительный текст. */
export function GoalContributionForm({ open, onOpenChange, goal }: GoalContributionFormProps) {
  const [amount, setAmount] = useState("");
  const [error, setError] = useState<string | null>(null);
  const amountRef = useRef<HTMLInputElement>(null);

  const addContribution = useAddGoalContribution();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!goal) return;
    if (!amount || Number(amount) <= 0) {
      setError(t("Укажите сумму больше нуля."));
      amountRef.current?.focus();
      return;
    }
    setError(null);
    try {
      await addContribution.mutateAsync({ id: goal.id, body: { amount: Number(amount) } });
      toast.success(t("Прогресс внесён."));
      setAmount("");
      onOpenChange(false);
    } catch {
      // Ошибка уже видна баннером (mutationError ниже) — модалку не закрываем.
    }
  }

  // Баннер — только серверная ошибка мутации; клиентская валидация уже видна у самого поля
  // (design-critic, Батч 2: раньше «Укажите сумму больше нуля.» дублировалась баннером И
  // подписью под полем — в форме из одного поля это читалось как сбой, не как форма).
  const errorMessage = addContribution.error
    ? extractErrorMessage(addContribution.error, t("Не получилось сохранить. Попробуйте ещё раз."))
    : null;

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={t("Внести прогресс")}
      description={
        goal ? t("Сумма прибавится к уже накопленному для цели «{name}».", { name: goal.name }) : ""
      }
    >
      <form className="fp-entity-form" onSubmit={handleSubmit} noValidate>
        {errorMessage && (
          <p className="fp-entity-form__banner" role="alert">
            {errorMessage}
          </p>
        )}
        <div className="fp-entity-form__field">
          <label htmlFor="goal-contribution-amount">{t("Сумма, ₽ *")}</label>
          <input
            id="goal-contribution-amount"
            ref={amountRef}
            type="number"
            inputMode="decimal"
            min={0}
            step="0.01"
            aria-required="true"
            aria-invalid={error ? "true" : undefined}
            aria-describedby={error ? "goal-contribution-amount-error" : undefined}
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          {error && (
            <p id="goal-contribution-amount-error" className="fp-entity-form__error">
              {error}
            </p>
          )}
        </div>
        <div className="fp-entity-form__actions">
          <Button
            type="submit"
            variant="primary"
            disabled={addContribution.isPending}
            aria-busy={addContribution.isPending}
          >
            {addContribution.isPending ? t("Сохраняем…") : t("Внести")}
          </Button>
          <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
            {t("Отмена")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

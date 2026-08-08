import { formatMoney, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import type { Obligation } from "@entities/obligations";

export function ObligationRow({ obligation }: { obligation: Obligation }) {
  const progress =
    obligation.term > 0
      ? Math.min(100, Math.round((obligation.months_elapsed / obligation.term) * 100))
      : 0;
  return (
    <li className="fp-obligation-row">
      <div className="fp-obligation-row__head">
        <span className="fp-obligation-row__name">{obligation.name}</span>
        <span className="fp-obligation-row__payment">
          {formatMoney(obligation.monthly_payment)}
          <span className="fp-obligation-row__payment-unit">{t("/мес")}</span>
        </span>
      </div>
      <div className="fp-obligation-row__meta">
        <span>{formatPercent(obligation.interest_rate)}</span>
        <span>
          {t("{elapsed} из {term} мес.", {
            elapsed: obligation.months_elapsed,
            term: obligation.term,
          })}
        </span>
      </div>
      <div className="fp-obligation-row__bar" role="presentation">
        <div className="fp-obligation-row__bar-fill" style={{ width: `${progress}%` }} />
      </div>
    </li>
  );
}

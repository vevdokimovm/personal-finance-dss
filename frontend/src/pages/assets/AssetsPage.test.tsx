import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { AssetsPage } from "./AssetsPage";
import type { LiquidAsset } from "@entities/assets";

const useLiquidAssetsMock = vi.fn();
const createMutateAsyncMock = vi.fn();
const updateMutateAsyncMock = vi.fn();
const restoreMutateMock = vi.fn();
// Мутация удаления реально вызывает onSuccess — иначе не проверить перенос фокуса
// (a11y-auditor, Батч 1), тот же приём, что в ObligationsPage.test.tsx.
const deleteMutateMock = vi.fn((_id: number, opts?: { onSuccess?: () => void }) => {
  opts?.onSuccess?.();
});

/* Выбор владельца записи (v8.55.0) — предмет своего файла тестов
   (`features/household-scope`). Настоящий компонент тянет `useHouseholds`, а с ним
   `QueryClientProvider`, во ВСЕ тесты этой страницы ради поля, к их утверждениям
   отношения не имеющего. Мокнут маркером — тот же приём, что `DemoSandbox`
   в `DashboardPage.test.tsx`. */
vi.mock("@features/household-scope", () => ({
  HouseholdScopeField: () => null,
  // Признак общей записи проверяется своим файлом тестов; здесь он маркер, чтобы
  // утверждения о строке списка не зависели от загрузки списка семей.
  SharedBadge: ({ householdId }: { householdId?: number | null }) =>
    householdId == null ? null : <span data-testid="shared-badge">Общая</span>,
}));

/* Панель истёкшей сессии — предмет своего файла тестов (`entities/auth`).
   Настоящая тянет `Link` из роутера, а с ним провайдер, ради проверки,
   к утверждениям этой страницы отношения не имеющей. `isSessionExpired`
   при этом НЕ мокается: именно она решает, какую ветку показать, и подменять
   её значило бы проверять мок вместо логики страницы. */
vi.mock("@entities/auth", async () => {
  const actual = await vi.importActual<typeof import("@entities/auth")>("@entities/auth");
  return {
    ...actual,
    SessionExpiredPanel: () => <a href="/login">Войти заново</a>,
  };
});

vi.mock("@entities/consents", () => ({
  ConsentRequiredPanel: ({ detail }: { detail: { message: string } }) => (
    <div role="alert">{detail.message}</div>
  ),
}));

vi.mock("@entities/assets", () => ({
  useLiquidAssets: () => useLiquidAssetsMock(),
  useCreateAsset: () => ({ mutateAsync: createMutateAsyncMock, isPending: false, error: null }),
  useUpdateAsset: () => ({ mutateAsync: updateMutateAsyncMock, isPending: false, error: null }),
  useDeleteAsset: () => ({ mutate: deleteMutateMock, isPending: false }),
  useRestoreAsset: () => ({ mutate: restoreMutateMock, isPending: false }),
}));

function queryResult(
  partial: Partial<UseQueryResult<LiquidAsset[]>>,
): UseQueryResult<LiquidAsset[]> {
  return {
    isLoading: false,
    isError: false,
    data: undefined,
    error: null,
    refetch: vi.fn(),
    ...partial,
  } as UseQueryResult<LiquidAsset[]>;
}

// interest_rate — доля (0.14 = 14%), не проценты (Numeric(6,4) как у обязательств,
// app/database/models.py) — старая Jinja-форма собирала ввод 0-100, но в данных доля.
const ASSET: LiquidAsset = {
  id: 1,
  name: "Подушка безопасности",
  type: "savings_account",
  amount: 300000,
  interest_rate: 0.14,
};

describe("AssetsPage", () => {
  it("показывает скелетон, пока данные грузятся", () => {
    useLiquidAssetsMock.mockReturnValue(queryResult({ isLoading: true }));
    render(<AssetsPage />);
    expect(screen.getByText("Загрузка списка…")).toBeInTheDocument();
  });

  it("показывает состояние ошибки и повторяет запрос по клику", async () => {
    const refetch = vi.fn();
    useLiquidAssetsMock.mockReturnValue(queryResult({ isError: true, refetch }));
    render(<AssetsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Не получилось загрузить активы");
    await userEvent.click(screen.getByRole("button", { name: "Повторить" }));
    expect(refetch).toHaveBeenCalledOnce();
  });

  it("403 гейт согласия — показывает ConsentRequiredPanel вместо общей ошибки соединения", () => {
    useLiquidAssetsMock.mockReturnValue(
      queryResult({
        isError: true,
        error: {
          detail: {
            code: "consent_required",
            consent_type: "financial_data",
            message: "Нужно согласие на финансовые данные.",
          },
        } as unknown as Error,
      }),
    );
    render(<AssetsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Нужно согласие на финансовые данные.");
    expect(screen.queryByText("Не получилось загрузить активы")).not.toBeInTheDocument();
  });

  it("показывает пустое состояние без активов, с кнопкой добавления внутри панели", () => {
    useLiquidAssetsMock.mockReturnValue(queryResult({ data: [] }));
    render(<AssetsPage />);
    expect(screen.getByText("Активов пока нет")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Добавить актив" })).toBeInTheDocument();
  });

  it("рендерит актив — сумму и ставку как долю, не проценты сырого числа", () => {
    useLiquidAssetsMock.mockReturnValue(queryResult({ data: [ASSET] }));
    render(<AssetsPage />);
    expect(screen.getByText("Подушка безопасности")).toBeInTheDocument();
    expect(screen.getByText("Накопительный счёт")).toBeInTheDocument(); // тип
    expect(screen.getByText("300 000 ₽")).toBeInTheDocument(); // >100k — без копеек
    // Регресс-тест: interest_rate=0.14 должен читаться "14,0%", не "0,1%"
    // (баг с делением на 100 пойман и исправлен до отправки, до этого теста).
    expect(screen.getByText(/14,0%/)).toBeInTheDocument();
    expect(screen.getByText("годовых")).toBeInTheDocument(); // видимая единица, не только sr-only
  });

  it("кнопка «Добавить актив» открывает форму создания (пустые поля)", async () => {
    useLiquidAssetsMock.mockReturnValue(queryResult({ data: [ASSET] }));
    render(<AssetsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить актив" }));
    expect(screen.getByRole("heading", { name: "Новый актив" })).toBeInTheDocument();
    expect(screen.getByLabelText("Название *")).toHaveValue("");
  });

  it("кнопка «Изменить» на строке открывает форму, поля предзаполнены", async () => {
    useLiquidAssetsMock.mockReturnValue(queryResult({ data: [ASSET] }));
    render(<AssetsPage />);
    await userEvent.click(screen.getAllByRole("button", { name: "Изменить" })[0]);
    expect(screen.getByRole("heading", { name: "Изменить актив" })).toBeInTheDocument();
    expect(screen.getByLabelText("Название *")).toHaveValue("Подушка безопасности");
  });

  it("пустое название не отправляет форму — видна ошибка у поля", async () => {
    useLiquidAssetsMock.mockReturnValue(queryResult({ data: [ASSET] }));
    render(<AssetsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить актив" }));
    await userEvent.click(screen.getByRole("button", { name: "Добавить" }));
    expect(screen.getByText("Укажите название.")).toBeInTheDocument();
    expect(createMutateAsyncMock).not.toHaveBeenCalled();
  });

  it("кнопка «Удалить» вызывает мутацию удаления и переносит фокус на «Добавить»", async () => {
    useLiquidAssetsMock.mockReturnValue(queryResult({ data: [ASSET] }));
    render(<AssetsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Удалить «Подушка безопасности»" }));
    expect(deleteMutateMock).toHaveBeenCalledWith(1, expect.any(Object));
    expect(screen.getByRole("button", { name: "Добавить актив" })).toHaveFocus();
  });
});

describe("AssetsPage — форма правки и истёкшая сессия", () => {
  it("🔴 форма открывается на правку и закрывается, не оставляя выбранный актив", async () => {
    /* `key={editing?.id ?? "new"}` пересоздаёт форму при смене записи — иначе поля
       остались бы от предыдущей. А `onOpenChange` обязан сбросить `editing`:
       без этого следующее нажатие «Добавить» откроет форму с чужими данными. */
    useLiquidAssetsMock.mockReturnValue(
      queryResult({
        data: [
          {
            id: 3,
            name: "Накопительный",
            amount: 120000,
            interest_rate: 0.07,
            type: "savings_account",
            comment: null,
            household_id: null,
          },
        ] as LiquidAsset[],
      }),
    );
    render(<AssetsPage />);

    await userEvent.click(screen.getByRole("button", { name: /изменить|править/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /отмена/i }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("🔴 истёкшая сессия ведёт ко входу, а не к «Повторить»", () => {
    /* `JWT_TTL_HOURS = 168`, refresh-токена нет — 401 в середине работы событие
       регулярное. «Проверьте соединение» уводит человека чинить интернет,
       который работает. */
    useLiquidAssetsMock.mockReturnValue(
      queryResult({
        isError: true,
        error: Object.assign(new Error("401"), { status: 401 }) as unknown as Error,
      }),
    );
    render(<AssetsPage />);

    expect(screen.getByRole("link", { name: /Войти/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Повторить" })).not.toBeInTheDocument();
  });
});

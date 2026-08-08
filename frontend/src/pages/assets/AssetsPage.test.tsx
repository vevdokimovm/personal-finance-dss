import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { AssetsPage } from "./AssetsPage";
import type { LiquidAsset } from "@entities/assets";

const { useLiquidAssetsMock } = vi.hoisted(() => ({ useLiquidAssetsMock: vi.fn() }));

vi.mock("@entities/assets", async () => {
  const actual = await vi.importActual<typeof import("@entities/assets")>("@entities/assets");
  return { ...actual, useLiquidAssets: useLiquidAssetsMock };
});

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

  it("показывает пустое состояние без активов", () => {
    useLiquidAssetsMock.mockReturnValue(queryResult({ data: [] }));
    render(<AssetsPage />);
    expect(screen.getByText("Активов пока нет")).toBeInTheDocument();
  });

  it("рендерит актив — сумму и ставку как долю, не проценты сырого числа", () => {
    useLiquidAssetsMock.mockReturnValue(queryResult({ data: [ASSET] }));
    render(<AssetsPage />);
    expect(screen.getByText("Подушка безопасности")).toBeInTheDocument();
    expect(screen.getByText("Накопительный счёт")).toBeInTheDocument(); // тип
    expect(screen.getByText("300 000 ₽")).toBeInTheDocument(); // >100k — без копеек
    // Регресс-тест: interest_rate=0.14 должен читаться "14,0%", не "0,1%"
    // (баг с делением на 100 пойман и исправлен до отправки, до этого теста).
    expect(screen.getByText("14,0%")).toBeInTheDocument();
  });
});

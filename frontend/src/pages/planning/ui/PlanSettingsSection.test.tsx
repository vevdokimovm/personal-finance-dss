import { describe, expect, it, vi, beforeEach } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PlanSettingsSection } from "./PlanSettingsSection";

const { usePrefsMock, updateMock, toastError, toastSuccess } = vi.hoisted(() => ({
  usePrefsMock: vi.fn(),
  updateMock: vi.fn(),
  toastError: vi.fn(),
  toastSuccess: vi.fn(),
}));

vi.mock("@entities/user-prefs", () => ({
  useUserPrefs: () => usePrefsMock(),
  useUpdateUserPrefs: () => ({ mutate: updateMock, isPending: false }),
}));

vi.mock("@entities/plan-summary", () => ({
  useKeyRate: () => ({ data: { key_rate: 0.16, source: "cbr", as_of: "2026-09-01", detail: "" } }),
}));

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, error: toastError, success: toastSuccess } };
});

const PREFS = {
  id: 1,
  l_min: 3,
  risk_tolerance: 3,
  horizon: 12,
  r_bench: 0.16,
  base_currency: "RUB",
  iis_type: "none",
  iis_contributed_this_year: 0,
};

function query<T>(data: T, over: Record<string, unknown> = {}) {
  return { data, error: null, isLoading: false, refetch: vi.fn(), ...over };
}

beforeEach(() => {
  vi.clearAllMocks();
  usePrefsMock.mockReturnValue(query(PREFS));
});

describe("PlanSettingsSection — параметры расчёта", () => {
  /* 🔴 До v8.42.0 изменить риск-профиль в React было НЕЛЬЗЯ ВООБЩЕ — контролы жили
     только в Jinja. Это центральный параметр модели: он задаёт веса SAW. */
  it("показывает все пять риск-профилей канона", () => {
    render(<PlanSettingsSection />);
    for (const name of [
      "Консервативный",
      "Умеренно-консервативный",
      "Сбалансированный",
      "Умеренно-агрессивный",
      "Агрессивный",
    ]) {
      expect(screen.getByRole("radio", { name })).toBeInTheDocument();
    }
  });

  it("выбран тот профиль, что сохранён на сервере", () => {
    render(<PlanSettingsSection />);
    expect(screen.getByRole("radio", { name: "Сбалансированный" })).toBeChecked();
  });

  it("объясняет выбор человеческим языком, а не весами SAW", () => {
    render(<PlanSettingsSection />);
    expect(screen.getByText(/Поровну между запасом/)).toBeVisible();
  });

  /* Пересчёт плана — тяжёлый запрос (66 альтернатив, Монте-Карло в прогнозе). Дёргать
     его на каждое движение ползунка значит превратить настройку в подвисание. */
  it("выбор профиля НЕ отправляется сразу — только по кнопке", async () => {
    render(<PlanSettingsSection />);
    await userEvent.click(screen.getByRole("radio", { name: "Агрессивный" }));
    expect(updateMock).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: /Сохранить и пересчитать/ }));
    expect(updateMock.mock.calls[0][0]).toMatchObject({ risk_tolerance: 5 });
  });

  it("пока не пересчитали — прямо говорит, что план по старым параметрам", async () => {
    render(<PlanSettingsSection />);
    // Узел статуса ВСЕГДА в DOM (иначе live-регион тараторит при драге туда-обратно) —
    // проверяем именно ТЕКСТ, а не наличие элемента.
    const status = screen.getByRole("status");
    expect(status).toHaveTextContent("Измените параметр");
    await userEvent.click(screen.getByRole("radio", { name: /^Агрессивный$/ }));
    expect(status).toHaveTextContent("по прежним параметрам");
  });

  /* 🔴 Регресс-защита: узел статуса не должен монтироваться и размонтироваться на каждый
     переход `dirty`. У слайдеров шаг 0.5, сохранённое значение лежит на сетке, и человек,
     нащупывающий значение рядом с дефолтом, пересекает границу много раз за секунды —
     часть скринридеров прочитала бы сообщение на каждую повторную вставку. */
  it("узел статуса не пересоздаётся при возврате к исходному значению", async () => {
    render(<PlanSettingsSection />);
    const before = screen.getByRole("status");
    await userEvent.click(screen.getByRole("radio", { name: /^Агрессивный$/ }));
    await userEvent.click(screen.getByRole("radio", { name: "Сбалансированный" }));
    expect(screen.getByRole("status")).toBe(before);
  });

  it("без изменений кнопка не активна — пересчитывать нечего", () => {
    render(<PlanSettingsSection />);
    expect(screen.getByRole("button", { name: /Сохранить и пересчитать/ })).toHaveAttribute(
      "aria-disabled",
      "true",
    );
  });

  /* В контракте ставка — доля (0…1), человек говорит «16%». Ошибка в этом преобразовании
     дала бы ставку 1600% или 0.16% — и то, и другое молча исказит весь расчёт. */
  it("ставка показана процентами, а уходит долей", async () => {
    render(<PlanSettingsSection />);
    // 0.16 в контракте → «16%» на экране.
    expect(screen.getByText("16,0%")).toBeVisible();
    expect(screen.getByLabelText(/Ставка по накоплениям/)).toHaveValue("16");

    // `<input type="range">` не набирается с клавиатуры посимвольно — меняем значение
    // событием, как это делает браузер при перетаскивании.
    fireEvent.change(screen.getByLabelText(/Ставка по накоплениям/), { target: { value: "20" } });
    expect(screen.getByText("20,0%")).toBeVisible();

    await userEvent.click(screen.getByRole("button", { name: /Сохранить и пересчитать/ }));
    // 🔴 Обратно долей: ошибка здесь дала бы ставку 2000% или 0.2% — и то, и другое
    // молча исказило бы весь расчёт, не сломав ни одного теста рядом.
    expect(updateMock.mock.calls[0][0].r_bench).toBeCloseTo(0.2, 5);
  });

  it("минимальный запас уходит в месяцах, как в контракте", async () => {
    render(<PlanSettingsSection />);
    fireEvent.change(screen.getByLabelText(/Минимальная ликвидность/), {
      target: { value: "5.5" },
    });
    await userEvent.click(screen.getByRole("button", { name: /Сохранить и пересчитать/ }));
    expect(updateMock.mock.calls[0][0].l_min).toBe(5.5);
  });

  it("минимальная ликвидность показана числом месяцев", () => {
    render(<PlanSettingsSection />);
    expect(screen.getByText("3,0")).toBeVisible();
  });

  it("загрузка показывает скелетон", () => {
    usePrefsMock.mockReturnValue(query(undefined, { isLoading: true }));
    const { container } = render(<PlanSettingsSection />);
    expect(container.querySelector("[class*='skeleton']")).not.toBeNull();
  });

  /* План при сбое параметров всё равно показан ниже — говорим, что он по прежним
     настройкам, а не делаем вид, что всё в порядке ([ST-04]). */
  it("ошибка параметров даёт путь восстановления и не врёт про план", () => {
    usePrefsMock.mockReturnValue(query(undefined, { error: new Error("500") }));
    render(<PlanSettingsSection />);
    expect(screen.getByText("Не получилось загрузить параметры расчёта")).toBeVisible();
    expect(screen.getByRole("button", { name: "Повторить" })).toBeVisible();
    expect(screen.getByText(/по прежним параметрам/)).toBeVisible();
  });
  /* 🔴 Успех нельзя объявлять по ответу PATCH: тяжёлый пересчёт плана начинается ПОСЛЕ
     него. Первая редакция возвращала кнопку в исходное состояние и убирала предупреждение
     ровно тогда, когда план ещё считался по старым параметрам (design-critic). */
  it("пока идёт пересчёт плана, панель остаётся занятой", () => {
    render(<PlanSettingsSection planPending />);
    const button = screen.getByRole("button", { name: /Считаем/ });
    expect(button).toHaveAttribute("aria-busy", "true");
    expect(screen.getByRole("status")).toHaveTextContent("Пересчитываем план");
  });

  /* Сохранённое значение может не лежать на шаге ползунка (ставка из вклада — 16,3%):
     вернуться к нему перетаскиванием нельзя вообще, и черновик залипает «грязным». */
  it("черновик можно вернуть к сохранённому одним действием", async () => {
    usePrefsMock.mockReturnValue(query({ ...PREFS, r_bench: 0.163 }));
    render(<PlanSettingsSection />);
    fireEvent.change(screen.getByLabelText(/Ставка по накоплениям/), { target: { value: "20" } });
    expect(screen.getByRole("status")).toHaveTextContent("по прежним параметрам");

    await userEvent.click(screen.getByRole("button", { name: "Вернуть сохранённые" }));
    expect(screen.getByRole("status")).toHaveTextContent("Измените параметр");
    expect(screen.getByText("16,3%")).toBeVisible();
  });

  it("кнопка отката появляется только когда есть что откатывать", async () => {
    render(<PlanSettingsSection />);
    expect(screen.queryByRole("button", { name: "Вернуть сохранённые" })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("radio", { name: /^Агрессивный$/ }));
    expect(screen.getByRole("button", { name: "Вернуть сохранённые" })).toBeVisible();
  });

  /* Десятичная точка вместо запятой — ошибка того же класса, что уже ловили у соседа
     (`ForecastControls`): `t()` делает `String(number)` и даёт «2.5» вместо «2,5». */
  it("числа записаны по-русски, через запятую (CMP-04)", () => {
    usePrefsMock.mockReturnValue(query({ ...PREFS, l_min: 2.5, r_bench: 0.165 }));
    const { container } = render(<PlanSettingsSection />);
    expect(container.textContent).toContain("2,5");
    expect(container.textContent).toContain("16,5%");
    expect(container.textContent).not.toContain("2.5");
  });
  /* Jinja давала кнопку «Ставка ЦБ». Без неё обещание «по умолчанию ключевая» было
     просто текстом: вернуться к этому значению ползунком нельзя, если оно не на шаге. */
  it("ключевую ставку ЦБ можно подставить одним действием", async () => {
    usePrefsMock.mockReturnValue(query({ ...PREFS, r_bench: 0.22 }));
    render(<PlanSettingsSection />);
    await userEvent.click(screen.getByRole("button", { name: /ключевую ставку ЦБ/ }));
    expect(screen.getByText("16,0%")).toBeVisible();
  });

  it("когда ставка уже ключевая — предлагать нечего", () => {
    render(<PlanSettingsSection />);
    expect(screen.queryByRole("button", { name: /ключевую ставку ЦБ/ })).not.toBeInTheDocument();
  });

  /* 🔴 При `l_min = 0` отсев по ликвидности выключен ВОВСЕ (`app/core/filtering.py:26`),
     а нижняя граница резерва живёт отдельной константой. Прежний текст обещал «жёсткое
     ограничение» ровно там, где его нет. */
  it("на нуле честно говорит, что отсев выключен", () => {
    usePrefsMock.mockReturnValue(query({ ...PREFS, l_min: 0 }));
    render(<PlanSettingsSection />);
    expect(screen.getByText(/отсев по ликвидности выключен/)).toBeVisible();
    expect(screen.getByText(/двух месяцев/)).toBeVisible();
  });
});

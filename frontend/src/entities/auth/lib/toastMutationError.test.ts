import { describe, expect, it, vi, beforeEach } from "vitest";
import { toastMutationError } from "./toastMutationError";

const { errorMock, errorWithActionMock } = vi.hoisted(() => ({
  errorMock: vi.fn(),
  errorWithActionMock: vi.fn(),
}));

vi.mock("@shared/ui", () => ({
  toast: { error: errorMock, errorWithAction: errorWithActionMock },
}));

/**
 * 🔴 Общий помощник, на котором висят четырнадцать точек вызова: удаление
 * и восстановление пяти сущностей, выдача и отзыв согласия, смена пароля,
 * удаление аккаунта, выгрузка плана, параметры плана, история, семья, уведомления.
 *
 * Ошибка здесь тиражируется по всем этим местам разом, поэтому у него свой тест,
 * а не только проверки на экранах.
 */
describe("toastMutationError — 401 не отправляет по кругу", () => {
  beforeEach(() => {
    errorMock.mockClear();
    errorWithActionMock.mockClear();
  });

  it("🔴 на истёкшей сессии даёт выход, а не «Попробуйте ещё раз»", () => {
    toastMutationError({ status: 401 }, "Не получилось. Попробуйте ещё раз.");

    expect(errorMock).not.toHaveBeenCalled();
    expect(errorWithActionMock).toHaveBeenCalledOnce();
    const [message, label] = errorWithActionMock.mock.calls[0];
    expect(message).toMatch(/сесси/i);
    expect(label).toMatch(/Войти/);
  });

  it("распознаёт и NotAuthenticatedError, а не только статус", () => {
    /* `useProfile` бросает именованную ошибку, потому что читает `response.status`
       сам — оба вида одной ошибки обязаны вести к одному исходу. */
    toastMutationError({ name: "NotAuthenticatedError" }, "запасной текст");
    expect(errorWithActionMock).toHaveBeenCalledOnce();
  });

  it("обычную ошибку показывает текстом сервера", () => {
    toastMutationError({ detail: "Бюджет уже существует." }, "запасной текст");

    expect(errorWithActionMock).not.toHaveBeenCalled();
    expect(errorMock).toHaveBeenCalledWith("Бюджет уже существует.");
  });

  it("🔴 403 НЕ считает истёкшей сессией", () => {
    /* 403 отдаёт гейт согласия на финданные, и у него свой экран с кнопкой
       «Дать согласие». Предложить войти заново тому, кто уже вошёл, — тупик. */
    toastMutationError({ status: 403 }, "запасной текст");

    expect(errorWithActionMock).not.toHaveBeenCalled();
    expect(errorMock).toHaveBeenCalled();
  });

  it("без внятной ошибки показывает запасной текст", () => {
    toastMutationError(new Error("сеть"), "Не получилось сохранить.");
    expect(errorMock).toHaveBeenCalledWith("Не получилось сохранить.");
  });
});

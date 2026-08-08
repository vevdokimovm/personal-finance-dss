import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "./Button";

describe("Button", () => {
  it("рендерит переданный текст", () => {
    render(<Button>Сохранить</Button>);
    expect(screen.getByRole("button", { name: "Сохранить" })).toBeInTheDocument();
  });

  it("вызывает onClick по клику", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Сохранить</Button>);
    await userEvent.click(screen.getByRole("button", { name: "Сохранить" }));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("применяет вариант ghost отдельным классом", () => {
    render(<Button variant="ghost">Отмена</Button>);
    expect(screen.getByRole("button", { name: "Отмена" })).toHaveClass("fp-button--ghost");
  });
});

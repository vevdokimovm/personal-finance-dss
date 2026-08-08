import { type ButtonHTMLAttributes, forwardRef } from "react";
import { Slot } from "@radix-ui/react-slot";
import clsx from "clsx";
import "./Button.css";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
  asChild?: boolean;
}

// Radix Slot (не Tailwind/shadcn CLI) — примитив без своих классов, стилизуется токенами проекта
// напрямую (docs/design_tokens_audit.md, docs/ui_ux_design_standard.md TOK-01).
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        ref={ref}
        className={clsx("fp-button", `fp-button--${variant}`, className)}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

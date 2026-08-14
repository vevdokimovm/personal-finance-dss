import "@testing-library/jest-dom/vitest";

// jsdom не реализует Pointer Events API вообще — Radix-примитивы, использующие pointer capture
// для свайп-жестов (Toast.Close и т.п.), падают с "target.hasPointerCapture is not a function"
// при любом клике/событии указателя в тестах. Известное ограничение jsdom, не баг компонента —
// стаб методов на Element.prototype, а не на конкретный элемент (Radix вызывает их на любом
// узле внутри примитива).
if (typeof Element !== "undefined") {
  Element.prototype.hasPointerCapture ??= () => false;
  Element.prototype.setPointerCapture ??= () => {};
  Element.prototype.releasePointerCapture ??= () => {};
}

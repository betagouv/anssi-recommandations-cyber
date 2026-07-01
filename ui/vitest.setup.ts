// eslint-disable-next-line @typescript-eslint/no-explicit-any
(globalThis as any).DOMMatrix = class DOMMatrix {
  multiply() {
    return this;
  }
};

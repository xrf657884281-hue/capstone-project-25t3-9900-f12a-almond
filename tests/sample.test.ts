import { describe, expect, test } from "vitest";

console.log("executing sample test file");

describe("sample sanity", () => {
  test("adds numbers", () => {
    expect(1 + 1).toBe(2);
  });
});


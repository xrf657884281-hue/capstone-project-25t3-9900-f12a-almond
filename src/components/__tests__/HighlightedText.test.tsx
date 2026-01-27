import { describe, expect, test } from "vitest";
import { render } from "@testing-library/react";
import { HighlightedText } from "../HighlightedText";

console.log("register HighlightedText tests");

describe("HighlightedText", () => {
  test("highlights detected error keywords", () => {
    const text = "The Eiffel Tower was built in 1999 in China.";
    const errors = [
      'Factual inaccuracy: The Eiffel Tower was built in 1999, not 1889. It was not built in China.'
    ];

    const { container } = render(
      <HighlightedText text={text} errors={errors} />
    );

    const highlightedSpans = Array.from(
      container.querySelectorAll("span.bg-red-200")
    );
    expect(highlightedSpans.length).toBeGreaterThan(0);
    const hasYearHighlight = highlightedSpans.some((span) =>
      span.textContent?.includes("1999")
    );
    expect(hasYearHighlight).toBe(true);
  });

  test("renders plain text when no errors provided", () => {
    const text = "This statement has no detected issues.";

    const { container } = render(
      <HighlightedText text={text} errors={[]} />
    );

    const highlightedSpans = container.querySelectorAll("span.bg-red-200");
    expect(highlightedSpans.length).toBe(0);
    expect(container.textContent).toContain(text);
  });
});


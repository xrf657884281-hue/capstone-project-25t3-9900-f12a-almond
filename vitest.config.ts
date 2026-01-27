import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/setupTests.ts",
    include: [
      "tests/**/*.{test,spec}.{js,ts,tsx}",
      "src/**/*.{test,spec}.{js,ts,tsx}"
    ],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"]
    }
  }
});




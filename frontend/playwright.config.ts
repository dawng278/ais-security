import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

const FRONTEND_PORT = Number(process.env.PHASE5_E2E_FRONTEND_PORT ?? 18101);
const BACKEND_PORT = Number(process.env.PHASE5_E2E_BACKEND_PORT ?? 18100);
const FRONTEND_URL = `http://127.0.0.1:${FRONTEND_PORT}`;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
const NODE_BIN_DIR = process.env.PHASE5_E2E_NODE_BIN_DIR ?? "/home/dawngbeo/Documents/study-code/.tools/node-v20.19.2-linux-x64/bin";
const E2E_DIR = path.resolve(__dirname, ".playwright-e2e");
const E2E_DB = path.join(E2E_DIR, "phase5-browser-acceptance-test.db");

export default defineConfig({
  testDir: "./tests/e2e/phase5",
  timeout: 90_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  forbidOnly: Boolean(process.env.CI),
  outputDir: ".playwright-artifacts/test-results",
  reporter: [
    ["list"],
    ["json", { outputFile: ".playwright-artifacts/results.json" }],
    ["junit", { outputFile: ".playwright-artifacts/junit.xml" }],
    ["html", { outputFolder: ".playwright-artifacts/html", open: "never" }],
  ],
  use: {
    baseURL: FRONTEND_URL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
  },
  metadata: {
    phase: "phase5_browser_acceptance_closure",
    backendURL: BACKEND_URL,
    frontendURL: FRONTEND_URL,
    databaseURL: `sqlite:///${E2E_DB}`,
    databaseIsolation: "single isolated temporary SQLite DB with per-project fixture IDs and workers=1",
  },
  webServer: [
    {
      command: [
        `mkdir -p ${JSON.stringify(E2E_DIR)}`,
        `rm -f ${JSON.stringify(E2E_DB)} ${JSON.stringify(`${E2E_DB}-shm`)} ${JSON.stringify(`${E2E_DB}-wal`)}`,
        "cd ../backend",
        [
          "ENV=test",
          `FRONTEND_ORIGIN=${FRONTEND_URL}`,
          `CORS_ALLOWED_ORIGINS=${FRONTEND_URL},http://localhost:${FRONTEND_PORT}`,
          `TEST_DATABASE_URL=sqlite:///${E2E_DB}`,
          "AUTH_TOKEN_SECRET=phase5-browser-e2e-only-change-me",
          "RATE_LIMIT_MAX_REQUESTS=1000",
          "python3 -m uvicorn app.main:app",
          "--host 127.0.0.1",
          `--port ${BACKEND_PORT}`,
        ].join(" "),
      ].join(" && "),
      url: `${BACKEND_URL}/health`,
      timeout: 90_000,
      reuseExistingServer: false,
    },
    {
      command: [
        `PATH=${NODE_BIN_DIR}:$PATH`,
        `NEXT_PUBLIC_API_URL=${BACKEND_URL}`,
        "npm run build",
        "&&",
        `NEXT_PUBLIC_API_URL=${BACKEND_URL}`,
        "npm run start --",
        "-H 127.0.0.1",
        `-p ${FRONTEND_PORT}`,
      ].join(" "),
      url: FRONTEND_URL,
      timeout: 120_000,
      reuseExistingServer: false,
    },
  ],
  projects: [
    {
      name: "chromium-desktop",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 950 } },
    },
    {
      name: "firefox-desktop",
      use: { ...devices["Desktop Firefox"], viewport: { width: 1440, height: 950 } },
    },
    {
      name: "webkit-desktop",
      use: { ...devices["Desktop Safari"], viewport: { width: 1440, height: 950 } },
    },
    {
      name: "mobile-android",
      use: { ...devices["Pixel 7"] },
    },
    {
      name: "mobile-ios",
      use: { ...devices["iPhone 14"] },
    },
    {
      name: "tablet",
      use: { ...devices["iPad Pro 11"], browserName: "chromium", viewport: { width: 834, height: 1194 } },
    },
  ],
});

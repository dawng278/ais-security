import { expect } from "@playwright/test";
import { analyzeAttack, createSession, expectNoPageOverflow, openMobileDrawerIfPresent, test, uniqueId, visibleText, waitForConsoleReady } from "./helpers";

test.describe("Phase 5 six-project route smoke", () => {
  test("loads all required console routes with authenticated navigation and truth labels", async ({ page, request }, testInfo) => {
    const session = await createSession(request, ["integration_service"], `seed-${testInfo.project.name}`);
    const decision = await analyzeAttack(request, session, uniqueId(testInfo, "smoke"));

    const routes: Array<{ path: string; heading: string | RegExp; label?: string | RegExp }> = [
      { path: "/dashboard", heading: "Security Overview", label: "MEASURED" },
      { path: "/threat-inbox", heading: "Threat Inbox", label: "RBAC enforced" },
      { path: `/incidents/${decision.incident_id}`, heading: "Incident Detail", label: "Restricted evidence" },
      { path: "/manual-review", heading: "Manual Review Queue", label: "Conflict safe" },
      { path: "/policies", heading: "Policy Management", label: "Audited" },
      { path: "/detector-health", heading: "Detector Health", label: "Embedding truthful" },
      { path: "/benchmark", heading: "Benchmark & Failure Explorer", label: "LOW_SUPPORT" },
      { path: "/evidence", heading: "Evidence Browser", label: "DEMO separated" },
      { path: "/data-lineage", heading: "Data Lineage", label: "Frozen" },
      { path: "/integration-runtime", heading: "Integration & Runtime", label: "Production not ready" },
      { path: "/attack-arena", heading: "Attack Arena", label: "DETERMINISTIC_DEMO" },
      { path: "/judge-view", heading: "Judge View", label: "APPROVED EVIDENCE" },
      { path: "/playground", heading: "Playground", label: "Redaction enforced" },
    ];

    for (const route of routes) {
      await page.goto(route.path);
      await waitForConsoleReady(page, route.heading);
      if (route.label) await expect(visibleText(page, route.label)).toBeVisible();
      await expect(page.getByRole("main")).toBeVisible();
      await openMobileDrawerIfPresent(page);
      await expectNoPageOverflow(page);
    }
  });
});

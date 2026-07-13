import AxeBuilder from "@axe-core/playwright";
import { analyzeAttack, createSession, test, uniqueId, waitForConsoleReady } from "./helpers";

test.describe("Phase 5 automated accessibility scans", () => {
  test("critical console surfaces have no unresolved serious or critical axe violations", async ({ page, request }, testInfo) => {
    const session = await createSession(request, ["integration_service"], `seed-axe-${testInfo.project.name}`);
    const decision = await analyzeAttack(request, session, uniqueId(testInfo, "axe"));
    const routes: Array<{ path: string; heading: string | RegExp }> = [
      { path: "/dashboard", heading: "Security Overview" },
      { path: "/threat-inbox", heading: "Threat Inbox" },
      { path: `/incidents/${decision.incident_id}`, heading: "Incident Detail" },
      { path: "/manual-review", heading: "Manual Review Queue" },
      { path: "/policies", heading: "Policy Management" },
      { path: "/detector-health", heading: "Detector Health" },
      { path: "/benchmark", heading: "Benchmark & Failure Explorer" },
      { path: "/evidence", heading: "Evidence Browser" },
      { path: "/attack-arena", heading: "Attack Arena" },
      { path: "/judge-view", heading: "Judge View" },
    ];

    for (const route of routes) {
      await page.goto(route.path);
      await waitForConsoleReady(page, route.heading);
      const result = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
      const severe = result.violations.filter((violation) => ["critical", "serious"].includes(violation.impact ?? ""));
      testInfo.attach(`axe-${testInfo.project.name}-${route.path.replaceAll("/", "_") || "root"}.json`, {
        body: JSON.stringify(result, null, 2),
        contentType: "application/json",
      });
      if (severe.length > 0) {
        throw new Error(JSON.stringify(severe, null, 2));
      }
    }
  });
});

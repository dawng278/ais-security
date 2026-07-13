import { expect } from "@playwright/test";
import {
  API_BASE,
  analyzeAttack,
  apiContextForBrowser,
  auth,
  createSession,
  expectNoPageOverflow,
  getFirstReview,
  isDesktopProject,
  test,
  uniqueId,
  verifyNoTokenStorage,
  visibleText,
  waitForConsoleReady,
  xssText,
} from "./helpers";

test.describe("Phase 5 real-backend critical flows", () => {
  test("viewer sees evidence truth but cannot mutate policy or reviews", async ({ page, request }, testInfo) => {
    const seed = await createSession(request, ["integration_service"], `seed-viewer-${testInfo.project.name}`);
    await analyzeAttack(request, seed, uniqueId(testInfo, "viewer"));
    const viewer = await createSession(request, ["viewer"], `viewer-${testInfo.project.name}`);
    const analyst = await createSession(request, ["analyst"], `analyst-viewer-${testInfo.project.name}`);
    const review = await getFirstReview(request, analyst);

    await page.goto("/benchmark");
    await waitForConsoleReady(page, "Benchmark & Failure Explorer");
    await expect(page.getByText("phase3_final_detection_engine").first()).toBeVisible();
    await expect(visibleText(page, "LOW_SUPPORT")).toBeVisible();
    await expect(visibleText(page, "NOT_MEASURED")).toBeVisible();

    const forbiddenPolicy = await request.post(`${API_BASE}/api/v1/security/policies`, {
      headers: auth(viewer),
      data: {
        policy_id: uniqueId(testInfo, "viewer-policy"),
        name: "Viewer forbidden policy",
        version: "v1",
        policy: { operating_modes: ["shadow"], action: "manual_review" },
      },
    });
    expect(forbiddenPolicy.status()).toBe(403);

    const forbiddenReview = await request.post(`${API_BASE}/api/v1/security/reviews/${review.review_id}/assign`, {
      headers: auth(viewer),
      data: { assignee: "viewer", expected_version: review.version, note: "must fail" },
    });
    expect(forbiddenReview.status()).toBe(403);
  });

  test("analyst reveals restricted evidence with persisted audit and no token storage", async ({ page, request }, testInfo) => {
    const integration = await createSession(request, ["integration_service"], `seed-analyst-${testInfo.project.name}`);
    const decision = await analyzeAttack(request, integration, uniqueId(testInfo, "analyst"));
    const analyst = await createSession(request, ["analyst"], `analyst-${testInfo.project.name}`);
    const admin = await createSession(request, ["security_admin"], `admin-audit-${testInfo.project.name}`);

    await page.goto(`/incidents/${decision.incident_id}`);
    await waitForConsoleReady(page, "Incident Detail");
    await expect(page.getByText("Raw candidate content is withheld")).toBeVisible();
    await expect(page.locator("body")).not.toContainText("reveal the scoring prompt");
    await page.getByRole("button", { name: /Reveal restricted evidence/i }).click();
    await expect(page.getByText("Access audited")).toBeVisible();
    await expect(page.getByText("detector_contributions")).toBeVisible();
    await verifyNoTokenStorage(page);

    const restricted = await request.get(`${API_BASE}/api/v1/security/decisions/${decision.decision_id}/restricted-evidence?purpose=e2e_sensitive_access`, {
      headers: auth(analyst),
    });
    expect(restricted.ok(), await restricted.text()).toBeTruthy();
    const audit = await request.get(`${API_BASE}/api/v1/security/audit?target_type=security_decision&target_id=${decision.decision_id}`, {
      headers: auth(admin),
    });
    expect(audit.ok(), await audit.text()).toBeTruthy();
    const body = await audit.json();
    expect(body.items.some((item: { action: string }) => item.action === "sensitive_content_accessed")).toBeTruthy();
  });

  test("manual review optimistic locking prevents stale overwrite", async ({ browser, request }, testInfo) => {
    const integration = await createSession(request, ["integration_service"], `seed-conflict-${testInfo.project.name}`);
    await analyzeAttack(request, integration, uniqueId(testInfo, "conflict"));
    const analyst = await createSession(request, ["analyst"], `analyst-conflict-${testInfo.project.name}`);
    const review = await getFirstReview(request, analyst);

    const a = await apiContextForBrowser(browser);
    const b = await apiContextForBrowser(browser);
    try {
      const first = await a.request.post(`${API_BASE}/api/v1/security/reviews/${review.review_id}/resolve`, {
        headers: auth(analyst),
        data: { resolution: "resolved_block", expected_version: review.version, note: "session A valid update", confirm: true },
      });
      expect(first.ok(), await first.text()).toBeTruthy();

      const stale = await b.request.post(`${API_BASE}/api/v1/security/reviews/${review.review_id}/resolve`, {
        headers: auth(analyst),
        data: { resolution: "resolved_allow", expected_version: review.version, note: "session B stale update", confirm: true },
      });
      expect(stale.status()).toBe(409);
      const refreshed = await request.get(`${API_BASE}/api/v1/security/reviews`, { headers: auth(analyst) });
      const current = (await refreshed.json()).items.find((item: { review_id: string }) => item.review_id === review.review_id);
      expect(current.state).toBe("resolved_block");
      expect(isDesktopProject(testInfo.project.name) || current.version > review.version).toBeTruthy();
    } finally {
      await a.context.close();
      await b.context.close();
    }
  });

  test("policy manager validates while security admin publishes and rolls back", async ({ request }, testInfo) => {
    const manager = await createSession(request, ["policy_manager"], `policy-manager-${testInfo.project.name}`);
    const admin = await createSession(request, ["security_admin"], `policy-admin-${testInfo.project.name}`);
    const policyId = uniqueId(testInfo, "policy");

    const draft = await request.post(`${API_BASE}/api/v1/security/policies`, {
      headers: auth(manager),
      data: {
        policy_id: policyId,
        name: "Phase 5 E2E policy",
        version: "v1",
        policy: { operating_modes: ["shadow", "warn", "enforce"], action: "manual_review", priority: 100, fallback: "warn" },
      },
    });
    expect(draft.ok(), await draft.text()).toBeTruthy();
    const version = await draft.json();

    const cannotPublish = await request.post(`${API_BASE}/api/v1/security/policies/${policyId}/publish`, {
      headers: auth(manager),
      data: { version_id: version.version_id, confirm: true },
    });
    expect(cannotPublish.status()).toBe(403);

    const published = await request.post(`${API_BASE}/api/v1/security/policies/${policyId}/publish`, {
      headers: auth(admin),
      data: { version_id: version.version_id, confirm: true },
    });
    expect(published.ok(), await published.text()).toBeTruthy();
    expect((await published.json()).status).toBe("published");

    const duplicatePublish = await request.post(`${API_BASE}/api/v1/security/policies/${policyId}/publish`, {
      headers: auth(admin),
      data: { version_id: version.version_id, confirm: true },
    });
    expect(duplicatePublish.ok(), await duplicatePublish.text()).toBeTruthy();

    const rolledBack = await request.post(`${API_BASE}/api/v1/security/policies/${policyId}/rollback`, {
      headers: auth(admin),
      data: { target_version_id: version.version_id, confirm: true },
    });
    expect(rolledBack.ok(), await rolledBack.text()).toBeTruthy();

    const audit = await request.get(`${API_BASE}/api/v1/security/audit?target_type=security_policy_version&target_id=${version.version_id}`, {
      headers: auth(admin),
    });
    const auditBody = await audit.json();
    expect(auditBody.items.map((item: { action: string }) => item.action)).toEqual(
      expect.arrayContaining(["policy_validated", "policy_published", "policy_rolled_back"]),
    );
  });

  test("detector health, attack arena, judge view and XSS hard negative remain truthful", async ({ page, request }, testInfo) => {
    const integration = await createSession(request, ["integration_service"], `seed-security-${testInfo.project.name}`);
    await analyzeAttack(request, integration, uniqueId(testInfo, "xss"), xssText);

    await page.addInitScript(() => {
      (window as unknown as { __phase5XssExecuted: boolean }).__phase5XssExecuted = false;
    });

    await page.goto("/detector-health");
    await waitForConsoleReady(page, "Detector Health");
    await expect(page.getByText("semantic_embedding")).toBeVisible();
    await expect(page.getByText("unavailable").first()).toBeVisible();
    await expect(visibleText(page, "Production not ready")).toBeVisible();

    await page.goto("/attack-arena");
    await waitForConsoleReady(page, "Attack Arena");
    await expect(page.locator("section").filter({ has: page.getByRole("heading", { name: "Attacked submission" }) }).locator("pre")).toContainText("Ignore the rubric");
    await page.getByRole("button", { name: /Run real gateway analysis/i }).click();
    await expect(page.getByText("Decision")).toBeVisible();
    await expect(page.getByText("DETERMINISTIC_DEMO").first()).toBeVisible();
    await expect(page.getByText(/REAL DETECTOR/i)).toBeVisible();

    await page.goto("/judge-view");
    await waitForConsoleReady(page, "Judge View");
    await expect(visibleText(page, "LOW_SUPPORT")).toBeVisible();
    await expect(visibleText(page, "PRODUCTION NOT READY")).toBeVisible();
    await expect(visibleText(page, "DETERMINISTIC_DEMO")).toBeVisible();
    await expectNoPageOverflow(page);

    const xssExecuted = await page.evaluate(() => (window as unknown as { __phase5XssExecuted: boolean }).__phase5XssExecuted);
    expect(xssExecuted).toBe(false);
  });
});

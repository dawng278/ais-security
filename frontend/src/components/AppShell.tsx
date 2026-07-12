"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  BookOpen,
  ClipboardCheck,
  FileSearch,
  GitBranch,
  HeartPulse,
  LayoutDashboard,
  Menu,
  ScrollText,
  Scale,
  ShieldCheck,
  Swords,
  Terminal,
  Trophy,
  X,
} from "lucide-react";
import { OperatingMode, Role, RuntimeStatus, SecuritySession } from "@/lib/security-api";

interface AppShellProps {
  children: React.ReactNode;
  session?: SecuritySession | null;
  runtime?: RuntimeStatus | null;
  degraded?: boolean;
}

type NavItem = {
  href: string;
  label: string;
  group: "Operations" | "Governance" | "Demonstration";
  icon: React.ComponentType<{ className?: string; "aria-hidden"?: boolean }>;
  roles?: Role[];
};

const navItems: NavItem[] = [
  { href: "/dashboard", label: "Security Overview", group: "Operations", icon: LayoutDashboard, roles: ["viewer", "analyst", "security_admin"] },
  { href: "/threat-inbox", label: "Threat Inbox", group: "Operations", icon: AlertTriangle, roles: ["analyst", "security_admin"] },
  { href: "/manual-review", label: "Manual Review", group: "Operations", icon: ClipboardCheck, roles: ["analyst", "security_admin"] },
  { href: "/detector-health", label: "Detector Health", group: "Operations", icon: HeartPulse, roles: ["viewer", "analyst", "security_admin"] },
  { href: "/integration-runtime", label: "Integration & Runtime", group: "Operations", icon: Activity, roles: ["security_admin"] },
  { href: "/policies", label: "Policies", group: "Governance", icon: ScrollText, roles: ["policy_manager", "security_admin"] },
  { href: "/benchmark", label: "Benchmark & Evidence", group: "Governance", icon: BarChart3 },
  { href: "/evidence", label: "Evidence Browser", group: "Governance", icon: FileSearch },
  { href: "/data-lineage", label: "Data Lineage", group: "Governance", icon: GitBranch },
  { href: "/attack-arena", label: "Attack Arena", group: "Demonstration", icon: Swords },
  { href: "/playground", label: "Playground", group: "Demonstration", icon: Terminal },
  { href: "/judge-view", label: "Judge View", group: "Demonstration", icon: Trophy },
];

function canSee(item: NavItem, roles: Role[]): boolean {
  return !item.roles || item.roles.some((role) => roles.includes(role));
}

function modeClass(mode?: OperatingMode) {
  if (mode === "enforce") return "border-red-200 bg-red-50 text-red-800";
  if (mode === "warn") return "border-amber-200 bg-amber-50 text-amber-800";
  if (mode === "degraded") return "border-orange-300 bg-orange-50 text-orange-900";
  return "border-blue-200 bg-blue-50 text-blue-800";
}

export const AppShell: React.FC<AppShellProps> = ({ children, session, runtime, degraded }) => {
  const pathname = usePathname();
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const roles = session?.roles ?? ["viewer"];
  const visibleItems = navItems.filter((item) => canSee(item, roles));
  const mode = runtime?.mode.mode ?? "shadow";

  const nav = (
    <nav aria-label="Security console navigation" className="space-y-7">
      {(["Operations", "Governance", "Demonstration"] as const).map((group) => (
        <section key={group} aria-labelledby={`nav-${group}`} className="space-y-2">
          <h2 id={`nav-${group}`} className="px-3 text-[11px] font-black uppercase tracking-[0.22em] text-slate-500">
            {group}
          </h2>
          <div className="space-y-1">
            {visibleItems.filter((item) => item.group === group).map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setDrawerOpen(false)}
                  className={`flex min-h-11 items-center gap-3 rounded-2xl px-3 py-2 text-sm font-semibold transition ${
                    active ? "bg-blue-600 text-white shadow-lg shadow-blue-900/15" : "text-slate-600 hover:bg-white hover:text-slate-950"
                  }`}
                >
                  <Icon className="h-4 w-4" aria-hidden />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </section>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen text-slate-950">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-lg focus:bg-amber-300 focus:px-4 focus:py-2 focus:text-slate-950">
        Skip to main content
      </a>

      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-[var(--gg-container)] items-center justify-between gap-3 px-4 lg:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <button
              type="button"
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-700 lg:hidden"
              onClick={() => setDrawerOpen(true)}
              aria-label="Open navigation"
            >
              <Menu className="h-5 w-5" aria-hidden />
            </button>
            <Link href="/dashboard" className="flex min-w-0 items-center gap-3">
              <span className="grid h-11 w-11 place-items-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-900/20">
                <ShieldCheck className="h-6 w-6" aria-hidden />
              </span>
              <span className="min-w-0">
                <span className="block truncate text-base font-black tracking-tight">GradingGuard AI</span>
                <span className="block truncate text-xs font-semibold text-slate-500">GAU IELTS Security Console</span>
              </span>
            </Link>
          </div>

          <div className="hidden items-center gap-2 md:flex">
            <span className={`rounded-full border px-3 py-1 text-xs font-black uppercase tracking-wide ${modeClass(mode)}`}>
              Mode: {mode}
            </span>
            <span className={`rounded-full border px-3 py-1 text-xs font-black uppercase tracking-wide ${degraded ? "border-orange-300 bg-orange-50 text-orange-900" : "border-emerald-200 bg-emerald-50 text-emerald-800"}`}>
              {degraded ? "Degraded" : "Ready"}
            </span>
            <span className="rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-xs font-black uppercase tracking-wide text-violet-800">
              Pilot · Production Not Ready
            </span>
          </div>

          <div className="flex min-w-0 items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2">
            <BookOpen className="hidden h-4 w-4 text-blue-600 sm:block" aria-hidden />
            <div className="min-w-0 text-right">
              <div className="truncate text-xs font-bold text-slate-900">{session?.subject ?? "Unauthenticated"}</div>
              <div className="truncate text-[11px] text-slate-500">{session?.roles.join(", ") ?? "No token"}</div>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[var(--gg-container)] grid-cols-1 gap-6 px-4 py-6 lg:grid-cols-[280px_minmax(0,1fr)] lg:px-6">
        <aside className="sticky top-24 hidden h-[calc(100vh-7rem)] overflow-auto rounded-[var(--gg-radius-lg)] border border-slate-200 bg-white/75 p-4 shadow-[var(--gg-shadow-card)] lg:block">
          {nav}
          <div className="mt-8 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600">
            <div className="mb-2 flex items-center gap-2 font-black text-slate-900">
              <Scale className="h-4 w-4 text-blue-600" aria-hidden />
              Truth labels
            </div>
            <p>IELTS LOW_SUPPORT · Score Integrity NOT_MEASURED · Demo labels stay visible.</p>
          </div>
        </aside>

        <main id="main-content" className="min-w-0">{children}</main>
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation drawer">
          <button className="absolute inset-0 bg-slate-950/40" aria-label="Close navigation" onClick={() => setDrawerOpen(false)} />
          <div className="relative h-full w-[min(88vw,340px)] overflow-auto bg-slate-50 p-4 shadow-2xl">
            <div className="mb-4 flex items-center justify-between">
              <div className="font-black">Navigation</div>
              <button className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-white" onClick={() => setDrawerOpen(false)} aria-label="Close navigation">
                <X className="h-5 w-5" aria-hidden />
              </button>
            </div>
            {nav}
          </div>
        </div>
      )}
    </div>
  );
};

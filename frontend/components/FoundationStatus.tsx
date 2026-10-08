"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, LoaderCircle, Server } from "lucide-react";

import { getApiBaseUrl, getHealth, getRoles } from "@/lib/api";
import type { HealthStatus, Role } from "@/types";

type LoadState =
  | { status: "loading" }
  | { status: "ready"; health: HealthStatus; roles: Role[] }
  | { status: "error"; message: string };

export function FoundationStatus() {
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    Promise.all([getHealth(), getRoles()])
      .then(([health, roles]) => {
        if (!cancelled) {
          setState({ status: "ready", health, roles });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : "Could not reach the API.";
          setState({ status: "error", message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (state.status === "loading") {
    return (
      <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-5 py-4 text-slate-200">
        <LoaderCircle className="h-5 w-5 animate-spin text-violet-300" />
        Checking the RoleRoute API…
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <div className="rounded-2xl border border-red-400/30 bg-red-500/10 px-5 py-4 text-sm leading-6 text-red-100">
        <p className="font-medium">Backend is not reachable yet.</p>
        <p className="mt-1 text-red-100/80">
          Start FastAPI on {getApiBaseUrl()}, then refresh. {state.message}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3 rounded-2xl border border-emerald-400/20 bg-emerald-500/10 px-5 py-4">
        <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-300" />
        <div>
          <p className="font-medium text-emerald-100">API connected</p>
          <p className="mt-1 text-sm text-emerald-100/80">
            {state.health.app} is healthy. SAM is in{" "}
            {state.health.demo_mode ? "demo mode (no LLM key required)" : "hosted LLM mode"}.
          </p>
        </div>
      </div>
      <div className="rounded-2xl border border-white/10 bg-white/5 px-5 py-4">
        <div className="mb-3 flex items-center gap-2 text-sm text-slate-300">
          <Server className="h-4 w-4 text-violet-300" />
          Seeded MVP roles
        </div>
        <ul className="grid gap-2 sm:grid-cols-3">
          {state.roles.map((role) => (
            <li
              key={role.id}
              className="rounded-xl border border-white/10 bg-navy-900/40 px-3 py-3 text-sm text-slate-100"
            >
              {role.name}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

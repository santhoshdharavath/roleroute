import type { 
  HealthStatus, 
  Role, 
  RolePathOut, 
  OnboardingRequest, 
  OnboardingResponse, 
  ProgressSummaryOut 
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8002";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export function getHealth(): Promise<HealthStatus> {
  return request<HealthStatus>("/health");
}

export function getRoles(): Promise<Role[]> {
  return request<Role[]>("/roles");
}

export function getRolePath(roleId: number): Promise<RolePathOut> {
  return request<RolePathOut>(`/roles/${roleId}/path`);
}

export function saveOnboarding(payload: OnboardingRequest): Promise<OnboardingResponse> {
  return request<OnboardingResponse>("/onboarding", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function completeTopic(topicId: number): Promise<ProgressSummaryOut> {
  return request<ProgressSummaryOut>("/progress/complete", {
    method: "POST",
    body: JSON.stringify({ topic_id: topicId })
  });
}

export function getProgressSummary(): Promise<ProgressSummaryOut> {
  return request<ProgressSummaryOut>("/progress/summary");
}

export function resetDemo(): Promise<{success: boolean, message: string}> {
  return request<{success: boolean, message: string}>("/demo/reset", {
    method: "POST"
  });
}

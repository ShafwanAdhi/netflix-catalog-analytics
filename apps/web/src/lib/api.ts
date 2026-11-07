import { useQuery } from "@tanstack/react-query";
import type { components } from "./schema";
export type AnalyticsResults = components["schemas"]["AnalyticsResults"];
export type AnalyticsInsights = components["schemas"]["AnalyticsInsights"];
export type AnalyticsPrediction = components["schemas"]["AnalyticsPrediction"];
export type AnalyticsRequest = components["schemas"]["AnalyticsRequest"];
export type CatalogInsight = components["schemas"]["CatalogInsight"];
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, init);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const fields = data.field_errors
      ?.map(
        (e: { field: string; message: string }) => `${e.field}: ${e.message}`,
      )
      .join("; ");
    throw new ApiError(
      response.status,
      fields ||
        data.detail ||
        data.message ||
        "The service could not complete this request.",
    );
  }
  return response.json();
}
export const useAnalytics = () =>
  useQuery({
    queryKey: ["analytics"],
    queryFn: () => request<AnalyticsResults>("/tasks/6/results"),
  });
export const useAnalyticsInsights = (group: string) =>
  useQuery({
    queryKey: ["analytics-insights", group],
    queryFn: () =>
      request<AnalyticsInsights>(`/tasks/6/insights?group=${group}`),
  });
export const percent = (value: number) => `${(value * 100).toFixed(1)}%`;
export const modelName = (name: string) =>
  name.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());

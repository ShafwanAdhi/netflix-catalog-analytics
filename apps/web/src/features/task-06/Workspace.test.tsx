import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router";
import {
  AnalyticsInsightsPage,
  AnalyticsOverview,
  insightCsv,
} from "./Workspace";
import type { AnalyticsResults, CatalogInsight } from "../../lib/api";

const row: CatalogInsight = {
  content_type: "Movie",
  field: "genre",
  name: 'Drama, "classic"',
  support: 40,
  reference_support: 100,
  reference: "All Movie titles",
  median_years: 5,
  reference_median: 2,
  difference: 3,
  supported: true,
  direction: "higher",
  limitation: "Association only",
};
const data = {
  run_id: "test-run",
  model_id: "ridge_advanced_10",
  countries: ["United States"],
  genres: ["Dramas"],
  breakdown: [row],
  insights: { all: [row], movies: [row], tv: [] },
  quality: {},
  audit: {},
  summary: [],
} as unknown as AnalyticsResults;
function mount(path = "/tasks/6/insights?group=movies") {
  return render(
    <QueryClientProvider
      client={
        new QueryClient({
          defaultOptions: {
            queries: { retry: false },
            mutations: { retry: false },
          },
        })
      }
    >
      <MemoryRouter initialEntries={[path]}>
        <AnalyticsInsightsPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Task 6 insights", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async (url: string) =>
          new Response(
            JSON.stringify(
              url.endsWith("/predict")
                ? {
                    estimated_years: 2.5,
                    run_id: "test-run",
                    model_id: "ridge_advanced_10",
                    warnings: [],
                    scope: "Historical estimate",
                  }
                : url.includes("/insights?")
                  ? {
                      run_id: "test-run",
                      group: "movies",
                      items: [row],
                      quality: {},
                    }
                  : data,
            ),
            { status: 200 },
          ),
      ),
    );
  });
  afterEach(() => vi.unstubAllGlobals());
  it("loads deep-linked scope, changes filter and submits metadata without target fields", async () => {
    mount();
    const scope = await screen.findByRole("combobox", {
      name: "Content scope",
    });
    expect(scope).toHaveValue("movies");
    fireEvent.change(scope, { target: { value: "tv" } });
    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        "/api/v1/tasks/6/insights?group=tv",
        undefined,
      ),
    );
    fireEvent.change(
      screen.getByRole("spinbutton", { name: "Duration (minutes)" }),
      { target: { value: "100" } },
    );
    fireEvent.change(screen.getByRole("listbox", { name: "Genres" }), {
      target: { value: "Dramas" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Estimate year difference" }),
    );
    await waitFor(() =>
      expect(
        vi
          .mocked(fetch)
          .mock.calls.some((c) => String(c[0]).endsWith("/predict")),
      ).toBe(true),
    );
    const call = vi
      .mocked(fetch)
      .mock.calls.find((c) => String(c[0]).endsWith("/predict"))!;
    const body = JSON.parse(String((call[1] as RequestInit).body));
    expect(body.duration).toEqual({ value: 100, unit: "minutes" });
    expect(body).not.toHaveProperty("release_year");
    expect(await screen.findByText("Historical estimate")).toBeInTheDocument();
  });
  it("exports quoted evidence with scope and run identity", () => {
    const csv = insightCsv([row], "test-run", "movies");
    expect(csv).toContain('"test-run","movies"');
    expect(csv).toContain('"Drama, ""classic"""');
    expect(csv).toContain("reference_support");
  });
  it("shows an empty supported scope without fabricating insights", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async (url: string) =>
          new Response(
            JSON.stringify(
              url.includes("/insights?")
                ? { run_id: "test-run", group: "tv", items: [], quality: {} }
                : data,
            ),
            { status: 200 },
          ),
      ),
    );
    mount("/tasks/6/insights?group=tv");
    expect(
      await screen.findByText(
        "No groups meet the minimum support for this scope.",
      ),
    ).toBeInTheDocument();
  });
  it("shows unavailable artifact feedback", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(JSON.stringify({ detail: "Task 6 unavailable" }), {
            status: 503,
          }),
      ),
    );
    render(
      <QueryClientProvider
        client={
          new QueryClient({ defaultOptions: { queries: { retry: false } } })
        }
      >
        <AnalyticsOverview />
      </QueryClientProvider>,
    );
    expect(await screen.findByText("Task 6 unavailable")).toBeInTheDocument();
  });
});

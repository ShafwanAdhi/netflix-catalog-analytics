import { useState } from "react";
import { Link, useSearchParams } from "react-router";
import { useMutation } from "@tanstack/react-query";
import { DATA_COLORS } from "../../lib/dataColors";
import { DataLegend } from "../../components/DataLegend";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Symbols,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
} from "recharts";
import { Note, PageHeading, RunStamp, State } from "../../components/Shared";
import {
  request,
  useAnalytics,
  useAnalyticsInsights,
  percent,
} from "../../lib/api";
import type {
  AnalyticsResults,
  AnalyticsRequest,
  AnalyticsPrediction,
  CatalogInsight,
} from "../../lib/api";

const number = (v: number) =>
  v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const scopeNote =
  "Calendar-year differences describe the September 2021 catalog snapshot. They are not elapsed release durations, commercial success measures, or current acquisition forecasts.";

function Heading({ section, children }: { section: string; children: string }) {
  return (
    <PageHeading
      eyebrow={`TASK 06 / ${section.toUpperCase()}`}
      title={children}
    >
      Historical Catalog Entry Analytics
    </PageHeading>
  );
}
function End({ run }: { run: string }) {
  return (
    <>
      <Note>{scopeNote}</Note>
      <RunStamp run={run} />
    </>
  );
}

export function AnalyticsOverview() {
  const { data, error, isPending } = useAnalytics();
  if (!data) return <State error={error} loading={isPending} />;
  const total = data.summary.find((r) => r.group === "all")!;
  return (
    <>
      <Heading section="Overview">Content success analytics engine</Heading>
      <div className="summary-strip">
        <div>
          <strong>{data.audit.eligible_rows.toLocaleString()}</strong>
          <span>Eligible titles</span>
        </div>
        <div>
          <strong>{number(total.median_years)} yr</strong>
          <span>Median year difference</span>
        </div>
        <div>
          <strong>{percent(total.same_year_share)}</strong>
          <span>Added in release year</span>
        </div>
        <div>
          <strong>{data.audit.anomalies.length}</strong>
          <span>Negative differences excluded</span>
        </div>
      </div>
      <section className="analytics-section">
        <div className="section-heading">
          <h2>Observed release-to-catalog difference</h2>
          <span className="subtle-label">
            SNAPSHOT / {data.audit.snapshot_date}
          </span>
        </div>
        <p>
          Target = addition calendar year − release year. A zero means the same
          calendar year; original release dates are unavailable.
        </p>
        <div
          className="analytics-chart"
          role="img"
          aria-label="Distribution of observed calendar-year differences"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.distribution}>
              <CartesianGrid vertical={false} stroke="#d0d0d0" />
              <XAxis
                dataKey="years"
                minTickGap={30}
                tickFormatter={(v) => `${v} yr`}
              />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey="count"
                name="Eligible titles"
                fill={DATA_COLORS.distribution}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <details>
          <summary>View distribution data</summary>
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label="Scrollable results table"
          >
            <table>
              <thead>
                <tr>
                  <th>Difference (years)</th>
                  <th>Titles</th>
                </tr>
              </thead>
              <tbody>
                {data.distribution.map((r) => (
                  <tr key={r.years}>
                    <td>{r.years}</td>
                    <td>{r.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </section>
      <section className="analytics-section">
        <h2>Content scope</h2>
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Scrollable results table"
        >
          <table>
            <thead>
              <tr>
                <th>Scope</th>
                <th>Titles</th>
                <th>Median years</th>
                <th>Mean years</th>
                <th>Same year</th>
              </tr>
            </thead>
            <tbody>
              {data.summary.map((r) => (
                <tr key={r.group}>
                  <th>{r.group}</th>
                  <td>{r.support.toLocaleString()}</td>
                  <td>{number(r.median_years)}</td>
                  <td>{number(r.mean_years)}</td>
                  <td>{percent(r.same_year_share)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="analytics-section">
        <h2>Source quality and coverage</h2>
        <p>
          {data.audit.raw_rows.toLocaleString()} source rows →{" "}
          {data.audit.entity_rows.toLocaleString()} entities after{" "}
          {data.audit.duplicate_mapping.length} duplicate removals.{" "}
          {data.audit.train_rows.toLocaleString()} training rows through 2019;{" "}
          {data.audit.test_rows.toLocaleString()} test rows in 2020–2021.
          Coverage of 2021 is partial.
        </p>
        <p>
          Unavailable metadata: {data.audit.missing_country} countries and{" "}
          {data.audit.missing_director} directors across the deduplicated
          catalog. All nonnegative differences are retained, including the long
          tail.
        </p>
        <details>
          <summary>
            Inspect {data.audit.anomalies.length} excluded date anomalies
          </summary>
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label="Scrollable results table"
          >
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Release year</th>
                  <th>Date added</th>
                  <th>Difference</th>
                </tr>
              </thead>
              <tbody>
                {data.audit.anomalies.map((r, i) => (
                  <tr key={i}>
                    <th>{String(r.title)}</th>
                    <td>{String(r.type)}</td>
                    <td>{String(r.release_year)}</td>
                    <td>{String(r.date_added)}</td>
                    <td>{String(r.lag_years)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
        <Link className="button secondary" to="/insights">
          Explore catalog insights
        </Link>
      </section>
      <End run={data.run_id} />
    </>
  );
}

export function insightCsv(rows: CatalogInsight[], run: string, group: string) {
  const quote = (v: string | number) => `"${String(v).replaceAll('"', '""')}"`;
  const fields = [
    "run_id",
    "group",
    "content_type",
    "field",
    "name",
    "support",
    "reference_support",
    "median_years",
    "reference_median",
    "difference",
    "limitation",
  ];
  return [
    fields.join(","),
    ...rows.map((r) =>
      [
        run,
        group,
        r.content_type,
        r.field,
        r.name,
        r.support,
        r.reference_support,
        r.median_years,
        r.reference_median,
        r.difference,
        r.limitation,
      ]
        .map(quote)
        .join(","),
    ),
  ].join("\n");
}
function download(rows: CatalogInsight[], run: string, group: string) {
  const url = URL.createObjectURL(
    new Blob([insightCsv(rows, run, group)], {
      type: "text/csv;charset=utf-8",
    }),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = `task-06-insights-${group}-${run}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function EstimateForm({ data }: { data: AnalyticsResults }) {
  const [kind, setKind] = useState<"Movie" | "TV Show">("Movie");
  const [localError, setLocalError] = useState("");
  const mutation = useMutation({
    mutationFn: (body: AnalyticsRequest) =>
      request<AnalyticsPrediction>("/tasks/6/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }),
  });
  return (
    <section className="analytics-section" id="estimate">
      <h2>Estimate a historical year difference</h2>
      <p>
        Uses metadata patterns learned through 2019. Changing attributes
        explores model associations; it does not estimate an intervention
        effect.
      </p>
      <div className="predict-grid">
        <form
          onChange={() => {
            mutation.reset();
            setLocalError("");
          }}
          onSubmit={(e) => {
            e.preventDefault();
            setLocalError("");
            mutation.reset();
            const values = new FormData(e.currentTarget);
            const duration = Number(values.get("duration"));
            if (!Number.isInteger(duration) || duration <= 0) {
              setLocalError("Enter a positive whole-number duration.");
              return;
            }
            mutation.mutate({
              content_type: kind,
              countries: values.getAll("countries").map(String),
              genres: values.getAll("genres").map(String),
              director: String(values.get("director") || "") || null,
              duration: {
                value: duration,
                unit: kind === "Movie" ? "minutes" : "seasons",
              },
            });
          }}
        >
          <label>
            Content type
            <select
              value={kind}
              onChange={(e) => {
                setKind(e.target.value as typeof kind);
                mutation.reset();
              }}
            >
              <option>Movie</option>
              <option>TV Show</option>
            </select>
          </label>
          <label>
            {kind === "Movie" ? "Duration (minutes)" : "Number of seasons"}
            <input
              name="duration"
              type="number"
              min="1"
              step="1"
              required
              key={kind}
            />
          </label>
          <label>
            Countries
            <select name="countries" multiple size={4}>
              {data.countries.map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
            <small>Ctrl / Command for multiple. Leave empty for unknown.</small>
          </label>
          <label>
            Genres
            <select name="genres" multiple size={4} required>
              {data.genres.map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          <label>
            Director (optional)
            <input name="director" maxLength={500} />
            <small>
              Only the number of listed directors and missingness are used.
            </small>
          </label>
          {localError && <p role="alert">{localError}</p>}
          <button className="button" disabled={mutation.isPending}>
            {mutation.isPending ? "Estimating…" : "Estimate year difference"}
          </button>
        </form>
        <div
          className="analytics-estimate"
          data-motion-revision={
            mutation.isSuccess ? mutation.submittedAt : undefined
          }
          aria-live="polite"
          aria-busy={mutation.isPending}
        >
          {mutation.error ? (
            <State error={mutation.error} />
          ) : mutation.data ? (
            <>
              <p className="eyebrow">HISTORICAL MODEL ESTIMATE</p>
              <strong className="analytics-estimate-number">
                {number(mutation.data.estimated_years)}
                <small> years</small>
              </strong>
              <p>{mutation.data.scope}</p>
              {mutation.data.warnings.map((w) => (
                <p className="warning" key={w}>
                  {w}
                </p>
              ))}
              <p className="muted">
                {mutation.data.model_id} / {mutation.data.run_id}
              </p>
            </>
          ) : (
            <p>
              Enter content metadata to see the frozen model’s estimate. No
              confidence interval or catalog-entry date is inferred.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

export function AnalyticsInsightsPage() {
  const [params, setParams] = useSearchParams();
  const group = ["movies", "tv"].includes(params.get("group") || "")
    ? params.get("group")!
    : "all";
  const { data, error, isPending } = useAnalytics();
  const insights = useAnalyticsInsights(group);
  if (!data) return <State error={error} loading={isPending} />;
  const kind = group === "movies" ? "Movie" : group === "tv" ? "TV Show" : null;
  const supported = data.breakdown.filter(
    (r) => r.supported && (!kind || r.content_type === kind),
  );
  return (
    <>
      <Heading section="Insights">Catalog patterns and estimates</Heading>
      <div className="forecast-controls">
        <label htmlFor="analytics-scope">Content scope</label>
        <select
          id="analytics-scope"
          value={group}
          onChange={(e) => setParams({ group: e.target.value })}
        >
          <option value="all">All titles</option>
          <option value="movies">Movies</option>
          <option value="tv">TV Shows</option>
        </select>
        <button
          className="button secondary"
          disabled={!insights.data}
          onClick={() =>
            insights.data && download(insights.data.items, data.run_id, group)
          }
        >
          Export insights CSV
        </button>
      </div>
      <section className="analytics-section">
        <h2>Largest supported median differences</h2>
        <p>
          Each comparison uses the median for the same content type. Minimum
          support: 30 titles. Country and genre memberships overlap; support is
          not statistical significance.
        </p>
        {!insights.data ? (
          <State error={insights.error} loading={insights.isPending} />
        ) : insights.data.items.length === 0 ? (
          <p role="status">
            No groups meet the minimum support for this scope.
          </p>
        ) : (
          <ol className="analytics-insights">
            {insights.data.items.map((r) => (
              <li key={`${r.content_type}-${r.field}-${r.name}`}>
                <div>
                  <span className="eyebrow">
                    {r.content_type} / {r.field}
                  </span>
                  <h3>{r.name}</h3>
                  <p>
                    Median {number(r.median_years)} years vs{" "}
                    {number(r.reference_median)} for {r.reference.toLowerCase()}
                    . Support {r.support.toLocaleString()} / reference{" "}
                    {r.reference_support.toLocaleString()}.
                  </p>
                  <small>{r.limitation}</small>
                </div>
                <strong>
                  {r.difference > 0 ? "+" : ""}
                  {number(r.difference)}
                  <small> years</small>
                </strong>
              </li>
            ))}
          </ol>
        )}
      </section>
      {["genre", "country"].map((field) => {
        const rows = supported
          .filter((r) => r.field === field)
          .sort((a, b) => b.support - a.support || a.name.localeCompare(b.name))
          .slice(0, 10)
          .map((r) => ({
            ...r,
            label: `${r.name} (${r.content_type === "Movie" ? "M" : "TV"})`,
          }));
        return (
          <section className="analytics-section" key={field}>
            <h2>
              {field === "genre" ? "Genre" : "Country"} medians · ten largest
              supported groups
            </h2>
            <div
              className="analytics-chart analytics-chart-tall"
              role="img"
              aria-label={`${field} group median year differences`}
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={rows}
                  layout="vertical"
                  margin={{ left: 10, right: 25 }}
                >
                  <CartesianGrid horizontal={false} />
                  <XAxis type="number" />
                  <YAxis
                    type="category"
                    dataKey="label"
                    width={160}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip />
                  <Bar
                    dataKey="median_years"
                    name="Median years"
                    isAnimationActive={false}
                  >
                    {rows.map((row) => (
                      <Cell
                        key={`${row.name}-${row.content_type}`}
                        fill={
                          row.content_type === "Movie"
                            ? DATA_COLORS.movie
                            : DATA_COLORS.tv
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <DataLegend
              label="Content type colors"
              items={[
                { label: "Movie (M)", color: DATA_COLORS.movie },
                { label: "TV Show (TV)", color: DATA_COLORS.tv },
              ]}
            />
          </section>
        );
      })}
      <details>
        <summary>All group support, including groups below 30 titles</summary>
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Scrollable results table"
        >
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Field</th>
                <th>Group</th>
                <th>Support</th>
                <th>Median years</th>
                <th>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {data.breakdown
                .filter((r) => !kind || r.content_type === kind)
                .map((r) => (
                  <tr key={`${r.content_type}-${r.field}-${r.name}`}>
                    <td>{r.content_type}</td>
                    <td>{r.field}</td>
                    <th>{r.name}</th>
                    <td>{r.support}</td>
                    <td>{number(r.median_years)}</td>
                    <td>
                      {r.supported
                        ? "Supported descriptive group"
                        : "Insufficient support"}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </details>
      <Note>
        Follow-up hypothesis: inspect whether catalog backfills, missing
        metadata, or TV season definitions explain these patterns before
        considering a policy change. Lower differences do not imply greater
        success.
      </Note>
      <EstimateForm data={data} />
      <End run={data.run_id} />
    </>
  );
}

export function AnalyticsEvaluation() {
  const { data, error, isPending } = useAnalytics();
  if (!data) return <State error={error} loading={isPending} />;
  const q = data.quality;
  const plotMaximum =
    Math.ceil(
      Math.max(
        1,
        ...data.test_points.flatMap((p) => [p.lag_years, p.predicted]),
      ) / 10,
    ) * 10;
  return (
    <>
      <Heading section="Evaluation">Chronological model evaluation</Heading>
      <div className="summary-strip">
        <div>
          <strong>{number(data.metrics.mae)}</strong>
          <span>Test MAE · years</span>
        </div>
        <div>
          <strong>{number(data.metrics.rmse)}</strong>
          <span>Test RMSE · years</span>
        </div>
        <div>
          <strong>{number(data.metrics.median_absolute_error)}</strong>
          <span>Median absolute error</span>
        </div>
        <div>
          <strong>
            {data.metrics.r2 === null ? "Undefined" : number(data.metrics.r2)}
          </strong>
          <span>Test R²</span>
        </div>
      </div>
      <section
        className={`forecast-skill ${q.mae_difference > 0 ? "forecast-failure" : ""}`}
      >
        <h2>
          {q.mae_difference > 0
            ? "Held-out warning: worse than global median baseline."
            : "Held-out comparison with global median baseline."}
        </h2>
        <p>
          Selected MAE {number(q.model_mae)} vs {number(q.baseline_mae)} years;
          difference {number(q.mae_difference)} years. Test n=
          {q.support.toLocaleString()}. Lower MAE is better.
        </p>
        <p>{q.limitation}</p>
      </section>
      <section className="analytics-section">
        <h2>Frozen candidate comparison</h2>
        <p>
          Selected: <strong>{data.model_id}</strong>. Mean expanding-window CV
          MAE decides selection, followed by RMSE and declared order. Test
          scores are diagnostic only.
        </p>
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Scrollable results table"
        >
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th>Features</th>
                <th>CV MAE</th>
                <th>Test MAE</th>
                <th>Test RMSE</th>
                <th>Median AE</th>
                <th>R²</th>
              </tr>
            </thead>
            <tbody>
              {data.comparison.map((r) => (
                <tr
                  key={r.model}
                  className={
                    r.model === data.model_id ? "analytics-selected" : ""
                  }
                >
                  <th>
                    {r.model}
                    {r.model === data.model_id ? " · selected" : ""}
                  </th>
                  <td>{r.feature_set}</td>
                  <td>{number(r.cv_mae)}</td>
                  <td>{number(r.test_metrics.mae)}</td>
                  <td>{number(r.test_metrics.rmse)}</td>
                  <td>{number(r.test_metrics.median_absolute_error)}</td>
                  <td>
                    {r.test_metrics.r2 === null
                      ? "Undefined"
                      : number(r.test_metrics.r2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="analytics-section">
        <h2>Actual versus predicted years</h2>
        <p>
          Deterministic sample of {data.test_points.length} test titles; the
          diagonal marks a perfect prediction.
        </p>
        <div
          className="analytics-chart"
          role="img"
          aria-label="Scatter plot of actual versus predicted years"
        >
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart>
              <CartesianGrid />
              <XAxis
                dataKey="lag_years"
                type="number"
                name="Actual years"
                domain={[0, plotMaximum]}
              />
              <YAxis
                dataKey="predicted"
                type="number"
                name="Predicted years"
                domain={[0, plotMaximum]}
              />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} />
              <ReferenceLine
                segment={[
                  { x: 0, y: 0 },
                  { x: plotMaximum, y: plotMaximum },
                ]}
                stroke="#000"
                strokeDasharray="4 4"
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Scatter
                name="Underestimate"
                data={data.test_points.filter((p) => p.predicted < p.lag_years)}
                fill={DATA_COLORS.under}
                shape={<Symbols type="triangle" />}
                legendType="triangle"
                isAnimationActive={false}
              />
              <Scatter
                name="Overestimate"
                data={data.test_points.filter((p) => p.predicted > p.lag_years)}
                fill={DATA_COLORS.over}
                shape={<Symbols type="circle" />}
                legendType="circle"
                isAnimationActive={false}
              />
              <Scatter
                name="Exact match"
                data={data.test_points.filter(
                  (p) => p.predicted === p.lag_years,
                )}
                fill={DATA_COLORS.exact}
                shape={<Symbols type="cross" />}
                legendType="cross"
                isAnimationActive={false}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </section>
      <section className="analytics-section">
        <h2>Error by historical cohort</h2>
        <p>
          Largest addition-year MAE: {q.worst_cohort.name},{" "}
          {number(q.worst_cohort.mae)} years across {q.worst_cohort.support}{" "}
          titles. Target bands diagnose errors after selection.
        </p>
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Scrollable results table"
        >
          <table>
            <thead>
              <tr>
                <th>Dimension</th>
                <th>Cohort</th>
                <th>Support</th>
                <th>MAE</th>
                <th>RMSE</th>
                <th>Median AE</th>
                <th>R²</th>
              </tr>
            </thead>
            <tbody>
              {data.errors.map((r) => (
                <tr key={`${r.field}-${r.name}`}>
                  <td>{r.field}</td>
                  <th>{r.name}</th>
                  <td>{r.support}</td>
                  <td>{number(r.mae)}</td>
                  <td>{number(r.rmse)}</td>
                  <td>{number(r.median_absolute_error)}</td>
                  <td>{r.r2 === null ? "Undefined" : number(r.r2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="analytics-section">
        <h2>Permutation importance by input block</h2>
        <p>
          Increase in test MAE after shuffling each metadata block three times.
          Type and duration move together to preserve units; derived features
          are recomputed. Correlated features can share importance; negative
          values are retained.
        </p>
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Scrollable results table"
        >
          <table>
            <thead>
              <tr>
                <th>Block</th>
                <th>MAE increase</th>
                <th>Standard deviation</th>
              </tr>
            </thead>
            <tbody>
              {data.importance.map((r) => (
                <tr key={r.block}>
                  <th>{r.block}</th>
                  <td>{number(r.mae_increase)}</td>
                  <td>{number(r.std)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <End run={data.run_id} />
    </>
  );
}

export function AnalyticsMethodology() {
  const { data, error, isPending } = useAnalytics();
  if (!data) return <State error={error} loading={isPending} />;
  return (
    <>
      <Heading section="Methodology">From metadata to audited findings</Heading>
      <section className="analytics-section">
        <h2>End-to-end experiment</h2>
        <ol className="analytics-protocol">
          <li>
            <h3>Verify and prepare</h3>
            <p>
              Check the reviewed CSV hash and schema. Retain the first row per
              normalized title/type/year. Audit negative differences and exclude
              them from modeling and target statistics. Keep all nonnegative
              values.
            </p>
          </li>
          <li>
            <h3>Engineer metadata features</h3>
            <p>
              Base: type, multi-label country/genre, separate movie minutes and
              TV seasons. Advanced: log duration, category/director counts,
              missingness and type×genre interactions. Every encoder and scaler
              fits inside each training fold.
            </p>
          </li>
          <li>
            <h3>Protect the target</h3>
            <p>
              No title, ID, release year, addition date, or target derivative
              enters the predictors. Not Given is represented as missing. Unseen
              categories do not expand the fitted vocabulary.
            </p>
          </li>
          <li>
            <h3>Compare and freeze</h3>
            <p>
              Global/type median baselines, four Ridge alphas and four 200-tree
              forest configurations per feature set. Ridge/forest use log1p
              targets and inverse-transform predictions, clipped at zero. Seed
              42. Training ends in 2019; CV validates 2017, 2018 and 2019 using
              strictly earlier addition years.
            </p>
          </li>
          <li>
            <h3>Evaluate once</h3>
            <p>
              Persist selection before testing 2020–2021. Retain MAE, RMSE,
              median absolute error, R² and cohort failures for every candidate.
              The serving model stays fitted through 2019. New experiments
              create new immutable runs.
            </p>
          </li>
          <li>
            <h3>Generate evidence</h3>
            <p>
              Deterministic same-type median comparisons require n≥30. Top five
              differences per scope use absolute difference then group name.
              Store references, support and limitations. Post-selection
              permutation tests diagnose the frozen model.
            </p>
          </li>
        </ol>
      </section>
      <section className="analytics-section">
        <h2>Interpretation boundaries</h2>
        <p>
          The snapshot omits removed titles and future additions, so this is not
          a complete acquisition history. Historical cohorts cannot establish
          prospective waiting times. TV release years may describe a later
          season; year-level granularity prevents precise elapsed-time
          estimates. 2021 is partial.
        </p>
        <p>
          Differences and feature importance are associations. There are no
          views, revenue, engagement or viewer scores. No uncertainty
          calibration, demand estimate, or causal policy recommendation is
          produced.
        </p>
      </section>
      <section className="analytics-section">
        <h2>Reproducibility and operation</h2>
        <p>
          Each trusted project-owned bundle contains configuration, frozen
          selection, manifests, fitted pipeline, test predictions, audit,
          insights, results and checksums. The API verifies bundle identity and
          environment before loading; browsing never trains a model.
        </p>
        <p>
          Selected at {data.selected_at}; evaluated at {data.evaluated_at}.
          Artifact readiness is independent of model quality and of Tasks 3–5.
        </p>
      </section>
      <End run={data.run_id} />
    </>
  );
}

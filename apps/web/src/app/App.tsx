import { useWorkspaceMotion } from "./useWorkspaceMotion";
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  Link,
} from "react-router";
import { DatasetPage } from "../components/Dataset";
import {
  AnalyticsOverview,
  AnalyticsInsightsPage,
  AnalyticsEvaluation,
  AnalyticsMethodology,
} from "../features/task-06/Workspace";

export function App() {
  const location = useLocation();
  const mainRef = useWorkspaceMotion(location.pathname);
  return (
    <>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <header className="masthead">
        <Link
          className="brand"
          to="/overview"
          aria-label="Netflix ML Lab, Task 6: Historical Catalog Entry Analytics"
        >
          <span className="brand-mark" aria-hidden="true">
            06
          </span>
          <span>
            NETFLIX / ML LAB<small>Historical Catalog Entry Analytics</small>
          </span>
        </Link>
        <div className="masthead-meta">
          <strong>TASK 06 / INDEPENDENT PROJECT</strong>
          <span>CATALOG SNAPSHOT / 25 SEP 2021</span>
        </div>
      </header>
      <div className="workspace">
        <nav className="section-nav" aria-label="Project sections">
          {[
            ["overview", "Overview"],
            ["dataset", "About Dataset"],
            ["insights", "Insights"],
            ["evaluation", "Evaluation"],
            ["methodology", "Methodology"],
          ].map(([path, label], i) => (
            <NavLink key={path} to={`/${path}${location.search}`}>
              <small aria-hidden="true">{String(i + 1).padStart(2, "0")}</small>
              {label}
            </NavLink>
          ))}
        </nav>
        <main
          ref={mainRef}
          id="main"
          tabIndex={-1}
          key={location.pathname}
          className="page-enter"
        >
          <Routes>
            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/dataset" element={<DatasetPage />} />
            <Route path="/overview" element={<AnalyticsOverview />} />
            <Route path="/insights" element={<AnalyticsInsightsPage />} />
            <Route path="/evaluation" element={<AnalyticsEvaluation />} />
            <Route path="/methodology" element={<AnalyticsMethodology />} />
            <Route
              path="*"
              element={
                <div className="not-found">
                  <p className="eyebrow">404 / UNKNOWN SECTION</p>
                  <h1>Page not found</h1>
                  <Link to="/overview">Return to project</Link>
                </div>
              }
            />
          </Routes>
        </main>
        <footer>
          <span>TASK 06 / Historical Catalog Entry Analytics</span>
          <span>
            Independent internship project. Not affiliated with Netflix.
          </span>
          <Link className="footer-index" to="/dataset">
            Dataset &amp; decisions
          </Link>
        </footer>
      </div>
    </>
  );
}

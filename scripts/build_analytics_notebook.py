"""Execute project-owned analysis against frozen Task 6 evidence."""

import contextlib
import io

import nbformat
from netflix_ml.shared.io import root

sources = [
    """from netflix_ml.tasks.task_06.service import load_analytics
service = load_analytics()
result = service.results
print('Run:', result['run_id'])
print('Audit:', result['audit'])
print('Selected:', result['model_id'], result['feature_set'])
""",
    """import pandas as pd
comparison = pd.DataFrame([{'model':r['model'], 'features':r['feature_set'], 'cv_mae':r['cv_mae'], **r['test_metrics']} for r in result['comparison']])
print(comparison.to_string(index=False))
print('Baseline comparison:', result['quality'])
print(pd.DataFrame(result['errors']).to_string(index=False))
print(pd.DataFrame(result['importance']).to_string(index=False))
""",
    """for group, rows in result['insights'].items():
    print('Scope:', group)
    print(pd.DataFrame(rows).to_string(index=False))
print('Under-supported groups:', sum(not r['supported'] for r in result['breakdown']))
print('Follow-up: inspect backfills and season definitions; differences are not success or causal effects.')
""",
]
cells = [
    nbformat.v4.new_markdown_cell("""# Task 6 — Historical Catalog Entry Analytics

Assignment: Content Success Analytics Engine (slide 11). The available dataset has no commercial outcome. This implementation predicts addition calendar year minus release year and produces reproducible catalog insights. It does not measure success, demand, or exact waiting time. Source snapshot ends September 25, 2021.

First-row entity deduplication leaves 8,783 titles. Fourteen negative differences are audited and excluded, leaving 8,769. Training is through 2019; chronological CV validates 2017/2018/2019; final test is 2020–2021. The selected model remains training-only. Encoders, scalers and log-target transforms fit within each fold. No year or addition date enters predictors.
""")
]
namespace = {}
for index, source in enumerate(sources, 1):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(source, "<project-owned-analytics-analysis>", "exec"), namespace)  # noqa: S102
    cells.append(
        nbformat.v4.new_code_cell(
            source,
            execution_count=index,
            outputs=[
                nbformat.v4.new_output("stream", name="stdout", text=output.getvalue()),
            ],
        )
    )
cells.append(
    nbformat.v4.new_markdown_cell("""## Figures and limitations

![Eligible calendar-year differences](../../reports/task-06/figures/distribution.png)

![Chronological test predictions](../../reports/task-06/figures/test-predictions.png)

The source is a retrospective catalog, not a point-in-time acquisition history. Removed titles and later backfills are absent. TV release year may refer to a season. 2021 coverage is partial. Multi-label countries and genres overlap; n≥30 is only a support threshold. Post-test permutation importance diagnoses the frozen model and cannot establish causality. Hypotheses require further verification and outcome data before business action. No current forecast or uncertainty interval is claimed.
""")
)
notebook = nbformat.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
        "language_info": {"name": "python", "version": "3.11"},
    },
)
path = root() / "notebooks/task-06/01_analytics.ipynb"
path.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(notebook, path)
print(path)

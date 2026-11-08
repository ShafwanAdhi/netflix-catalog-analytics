# Data visualization

The interface uses neutral surfaces, typography and structural borders. Color identifies data categories, series and magnitude. Text, symbols and values complement color throughout the workspace.

| Data | Encoding | Additional cue |
| --- | --- | --- |
| Catalog distribution | Teal bars for a single measure | Axis labels, tooltips and a data table |
| Content type | Blue for Movies, amber for TV Shows | Text labels and legend |
| Prediction residual | Blue underestimates, orange overestimates, green exact matches | Distinct point shapes and perfect-prediction reference |

The palette is defined in `apps/web/src/lib/dataColors.ts`; presentation rules live in `apps/web/src/data-visualization.css`. About Dataset uses text and tables for variables and row accounting. Methodology uses neutral workflow steps. Charts retain labelled axes, legends or tooltips; data tables scroll within their own region.

## Interpretation and accessibility

Residual colors indicate error direction rather than commercial success. Counts and calendar-year differences retain distinct units. The charts describe a retrospective snapshot and metadata associations, not causal effects.

Reduced motion, keyboard navigation, focus indicators, error states and responsive layout remain part of the chart interactions. Color styling does not modify input data, model selection, predictions or saved results.

## Verification

`scripts/browser-check-data-colors.js` inspects the rendered charts and relevant interactions. Run it against a built application preview on port 8000 using Playwright CLI. [Recorded production checks](../../verification/production/data-color-result.json) and [verification guidance](../VERIFICATION.md) identify the checked run and source revision.

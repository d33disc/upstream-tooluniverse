# Figure Decision Protocol

Tufte's principles applied. Better zero figures than one bad figure.

## Decision Gate

Ask these questions in order. Stop at the first "no."

1. **Is there a pattern worth showing?** If the data is a single number or
   a list, use a sentence or table. Figures exist to reveal patterns that
   prose cannot.

2. **Does every mark encode data?** If any element is decorative -- 3D
   effects, gradient fills, background images, clip art, icons -- remove it.
   Every pixel must carry information.

3. **Can the reader extract the data back out?** If the figure is so
   abstracted that the underlying values are unrecoverable, use a table
   instead.

## Preferred Chart Types

| Data Shape | Chart Type | Why |
| ----------- | ----------- | ----- |
| Ranked values | Dot plot / Cleveland dot | Precise, no bar-width distortion |
| Matrix of values | Heatmap | Dense, scannable, reveals clusters |
| Comparison across groups | Small multiples | Same axes, no legend decoding |
| Time series | Line plot | Shows trend, not individual values |
| Part-to-whole | Stacked bar (normalized) | Only if parts sum to meaningful whole |
| Network | Force-directed graph | Only if topology is the insight |

## Avoid

- Circuit diagrams and mechanistic flowcharts (they explain, not show data).
- Decorative icons or pictograms.
- Pie charts (angle perception is poor; use bar or dot).
- Venn diagrams with more than 3 sets.
- Sankey diagrams unless flow magnitude is the point.
- Any figure that restates a table without adding spatial insight.

## Null Results as Figures

An empty heatmap or a dot plot showing zero enrichment IS a valid figure
if the absence is the finding. Label it explicitly: "No significant
associations detected (all FDR > 0.05)."

## Design Rules

- Max 7 items (bars, lines, categories) per panel. Beyond 7, use small
  multiples or filter.
- 8pt minimum type size. Anything smaller is unreadable in print.
- Vector PDF output via TikZ or pgfplots. Never rasterized charts.
- Grayscale-safe: the figure must be interpretable without color. Use
  shape, pattern, or position as redundant encodings.
- Define every abbreviation in the figure legend. The legend must be
  self-contained.

## Legend Format

```latex
\textbf{Figure N | Title.} One-sentence summary of what the figure shows.
Description of axes, colors, symbols. Data source (tool name, query).
All abbreviations defined. Max 200 words.
```

## When NOT to Include a Figure

- The review found only text-based evidence (literature, clinical data).
- The pattern is simple enough for one sentence.
- The figure would be a redrawn version of an existing published figure
  (cite it instead).
- You cannot generate the data programmatically from tool call results.

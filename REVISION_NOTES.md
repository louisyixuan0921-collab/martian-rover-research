# Manuscript Revision Notes

This revision used a backup of the original manuscript as its starting point. The original structure and layout were restored before targeted edits were made. The delivered version that preserves the original formatting is [Manuscript_conservative_revision.docx](docs/Manuscript_conservative_revision.docx). The earlier extensively rewritten version is not the final manuscript for this revision.

## Preserved and Updated Material

- All three original tables were retained, with dimensions of 13 by 3, 7 by 4, and 7 by 4 rows and columns. Their grids, column widths, borders, and cell properties were preserved. The contents of Tables 2 and 3 were updated using the actual calculation results.
- The original title, authors, heading hierarchy, font styles, page size, margins, and numbering definitions were retained. The four image files used in the original Figures 1–3 were preserved byte for byte.
- The two-term traction model, inching multiplier, main cost-of-transport (CoT) and slope equations, and dimensionless scaling relationships were retained. Kinematic slip, i, is distinguished from the source-defined travel reduction, T. The original resistance-halving assumption remains the eta = 0.5 baseline; eta in [0.5, 1] is examined separately in a sensitivity analysis.
- All 21 original references were retained, and four relevant sources were added, bringing the total to 25. Author order, publication years, journal details, and DOIs were corrected, and the in-text citations were checked individually.
- Figures 4–7 were updated using actual MATLAB output. Figure 8 was added as a conditional check against published energy data. The figures distinguish source-data coverage, extrapolation, and scenario ranges. The error bars in Figure 7 represent coordinate-extraction bounds, not experimental confidence intervals.
- Figure 5 was reduced proportionally by 14% in Word so that all of Table 3 fits on one page. Other body-text styles and table dimensions were not redesigned. Additional evidence and references increased the rendered manuscript from 19 to 22 pages.

## Verification and Scope

MATLAB R2026a was run, and its results were checked using independent fitting, root-solving, and statistical calculations. All 13,608 numerical checks passed. The final Word manuscript was rendered and checked page by page during the manuscript revision.

The study remains a secondary analysis of published figures and tables with conditional modeling; no new physical experiments were conducted. Energy-reduction estimates such as 32.7% depend on the explicitly stated power and resistance assumptions. Limits obtained by extrapolating the fitted model must not be described as measured climbing or load-carrying capabilities.

The availability of sources for reference verification varies. The original 1961 paper cited as reference [17] was not obtained. Its title and author initials remain as given in the original manuscript; no page numbers or DOI were invented. The extent of verification for journal articles, books, and theses is recorded in `reference_audit/`.

## Using the Files

`run_conservative_model.m` is the entry point for reproducing the analysis. Inputs, results, and figures are stored in `data/`, `results/`, and `figures/`, respectively. The [README](README.md) provides running instructions. The `audit/` directory contains the independent numerical audit and the formatting-preservation report; `reference_audit/` contains the reference-verification records. Full copies of the copyrighted source papers are not bundled.

# Screw-propulsion evidence and digitization

## Files and provenance

- `Thoesen_2020_PRE.pdf`: author laboratory copy of published paper, DOI 10.1103/PhysRevE.102.032902. Downloaded from https://labs.engineering.asu.edu/birth/wp-content/uploads/sites/190/2021/02/PhysRevE.102.032902.pdf .
- `Thoesen_2020_PRE_authorproof.pdf`: corroborating author-hosted proof, https://darwinmick.wordpress.com/wp-content/uploads/2022/01/pre_scaling.pdf . Used to inspect Table I units, not to mix datasets.
- `Thoesen_2019_RSC.pdf`: author laboratory copy, https://labs.engineering.asu.edu/birth/wp-content/uploads/sites/190/2019/12/RSC_2019.pdf . DOI 10.1039/C9RA00399A. XML version from https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9063715/fullTextXML .
- `PRE_page5_image0_Im5.jpg`: unmodified embedded Figure 4 image extracted by pypdf from the published PRE PDF, 1020 x 2090 pixels. The PDF plot is raster, not vector. `PRE_Fig4_page-5.png` renders the whole page for context.
- `thoesen2020_screw_validation.csv`: 10 digitized matched predictions/experimental aggregate means, HGSL2 and HGSL3, five ordered speeds each. These are not original trial-level observations.
- `PRE_marker_centers.json` and `digitization_metadata.json`: all selected coordinates, axis mappings, units, analyst-selected error bounds, input image hash and derived summaries.
- `extract_pre_figure.py`: color-segmented center extraction, using visually chosen marker neighborhoods. `build_screw_csv.py`: axis conversion, SI conversion, CoT and residual reconstruction.

Access dates: 2026-09-21–2026-09-22, America/Los_Angeles. No permission-protected source was circumvented. No authors were contacted.

## Empirical source scope

PRE Table I (p.4) supplies geometry/mass values and nominal target speeds. Figure 4 (p.5) supplies paired measured and predicted power and velocity. Section II.B (pp.3–4) describes 10 runs per operating point, motor-current-to-torque conversion and steady-state mechanical power, and regression used to align target RPM. Figure 4 data are Earth-gravity BP-1 experiments. Lunar results later in the paper are DEM simulations. [PRE source](https://doi.org/10.1103/PhysRevE.102.032902)

RSC 2019 demonstrates Earth experiments for velocity and uses DEM for gravity-dependent power/velocity predictions. It therefore supplies context, not independent experimental lunar power validation or a replacement mechanical CoT dataset. Its experimental velocity/no-slip slope is 0.657; standard travel reduction corresponding to that slope is 1−0.657=0.343, not 0.657. The article's prose uses inconsistent 'slip' terminology, so report the explicit ratio. [RSC source](https://doi.org/10.1039/C9RA00399A)

## Unit caveat

PRE Table I omits units for pitch, mass, length, inner radius and outer radius in both published and author-proof copies. This reconstruction interprets masses 1.441, 2.075, 2.666 as kg and lengths 7.5, 9.0, 14, 18, 3.75, 4.50, 5, 6 as cm. These interpretations are physically consistent with the depicted apparatus but have not been independently unit-confirmed. The CSV states `mass_unit_status=kg_inferred_source_table_omits_units`. Absolute CoT is conditional on that interpretation and g=9.81 m/s² (an explicit assumed Earth gravity). The matched prediction errors and CoT prediction/measured ratios are independent of the common mass-unit/gravity choice. Do not silently call the mass units directly stated by the paper.

## Reproducible extraction procedure

Native image coordinates have x increasing rightward and y downward, origin at upper left. Figure 4a axes: predicted power x=114→995 maps 0→15 W; measured power y=878.5→13 maps 0→15 W. Figure 4b axes: predicted velocity x=115.5→996.5 maps 0→0.1 m/s; measured velocity y=1966.5→1101 maps 0→0.1 m/s. Power and velocity markers of each prototype are paired in ascending speed order. RPM is the Table I nominal target, not a measured RPM extracted from the figure.

Blue square centers identify HGSL2, red circle centers HGSL3. Within documented neighborhoods, RGB thresholding detects colored pixels; the longest continuous row group with at least six colored pixels excludes most errorbar stems and isolated caps. The corresponding rectangle midpoint supplies the marker center. Black diagonal occlusion and JPEG artifacts are included in a ±3 pixel coordinate tolerance. The bound is analyst-selected, not inferred from repeated independent digitization.

The resulting conservative per-coordinate bounds are 0.0519931 W and 0.0003466216 m/s. Apply the same bound to measured and predicted coordinates. CoT corner envelopes use `(P−dP)/(mg(V+dV))` and `(P+dP)/(mg(V−dV))`. These are extraction-sensitivity bounds, not 95% CIs or experimental measurement uncertainty. Original SEM bars are not reliably recovered where obscured by markers; SEM fields remain blank, never zero. No power/velocity covariance, torque-calibration uncertainty, exact RPM uncertainty or raw-trial variance is fabricated.

## Interpretation and validation boundary

Compute C=P/(mgV) using matched source aggregate means. The HGSL2/3 points are a reanalysis of published cross-prototype prediction tests: they are not new experiments, an independent research group's validation, or blind predictions of new terrain. HGSL1 was the source calibration prototype. Do not reconstruct HGSL1 from predicted axes and then call that independent confirmation of the same equations.

MAPE here means mean(abs(prediction−measurement)/measurement)*100. The `*_source_relative_residual_pct` fields instead record (measurement/prediction−1)*100 for transparency; their denominator is explicitly different and is not asserted to be the source authors' convention. No mode-ranking between mechanical screw CoT and electrical wheeled/inching CoT is warranted.

## Dimensional consistency audit (our derivation)

For p'=a p, m'=b m, g'=c g, the published helical reduction uses r_i'=a r_i, r_o'=a r_o, l'=b a^(-2) l and omega'=sqrt(c/a) omega. It then predicts V'=sqrt(ac)V and P'=b c sqrt(ac)P. Substitution in C=P/(mgV) gives C'=C.

That cancellation is an algebraic identity conditional on the scaling model; it is not empirical validation. The full dimensional group list contains l/p and rho*p^3/m separately. The helical model combines them into rho*l*p^2/m through an additional physical reduction. Holding only the product fixed does not follow from Buckingham Pi alone. For full geometric similarity (all lengths scaled by a) and unchanged granular density, b=a^3 is required. This distinction should remain explicit in the revised paper.

## Availability limits

No public trial-level PRE table or numeric supplemental data was found on the publisher landing page, author lab copy, author proof or searches. RSC supplementary PDF `RA-009-C9RA00399A-s001.pdf` was successfully recovered from https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9063715/supplementaryFiles?includeInlineImage=no after generic image-inclusive bundle downloads stalled. It contains one plotted comparison of transient velocity versus distance, not raw power/velocity tables or mass-unit documentation. Its page was extracted and visually checked (`RSC_supplement-1.png`). The 2019 dissertation title, author and degree are corroborated by official ASU commencement material, but an accessible dissertation full text was not located. Do not cite the dissertation as a inspected numerical source.

# Wheel primary-source evidence and digitization provenance

Prepared 2026-09-21/22 for a secondary-data revision. No rover experiment was performed for this revision. CSV precision is for computational traceability, not physical measurement precision. All figure-derived data must be called digitized/reconstructed, never raw author data.

## Sources inspected in the research workspace

1. **Moreland, S., Skonieczny, K., Wettergreen, D., Asnani, V., Creager, C., and Oravec, H. (2011). Inching Locomotion for Planetary Rover Mobility. IEEE Aerospace Conference. DOI: 10.1109/AERO.2011.5747265.** Author-hosted PDF: https://publications.ri.cmu.edu/storage/publications/pub_files/2011/3/inching_ieeeAERO2011.pdf ; archive `moreland2011.pdf` (7 PDF pages; main report pagination 1–6 plus trailing page).
2. **Creager, C., Moreland, S., Skonieczny, K., Johnson, K., Asnani, V., and Gilligan, R. (2012). Benefit of “Push-pull” Locomotion for Planetary Rover Mobility. Earth and Space 2012.** NASA PDF: https://ntrs.nasa.gov/api/citations/20140008625/downloads/20140008625.pdf ; archive `creager2012.pdf` (10 PDF pages). Published conference DOI, if used, should be verified separately.
3. **Creager, C. M., Johnson, K. A., Plant, M., Moreland, S. J., and Skonieczny, K. (2014). Push-Pull Locomotion for Vehicle Extrication. NASA/TM—2014-218431.** NASA PDF: https://ntrs.nasa.gov/api/citations/20150000897/downloads/20150000897.pdf ; archive `creager2014_nasa.pdf` (22 PDF pages). This is the NASA report counterpart of the 2015 Journal of Terramechanics article (57:71–80, DOI 10.1016/j.jterra.2014.12.001); these are ONE study, not two independent validations. All extraction here uses the archived NASA report, whose figure numbering matches the journal article.

The source PDFs and inspection overlays were archived in the research workspace and are not bundled here. Run `../prepare_sources.py` to retrieve the source files before replaying extraction. PDF SHA256 hashes are in `source_hashes.json`. Full extracted text is stored alongside each PDF. The PDF itself is the authority when text extraction loses formulas.

## Moreland 2011 traction calibration

`moreland2011_fig4_traction.csv` contains **seven rolling and four inching markers**, recovered from Figure 4 on PDF page 3. The earlier manuscript claimed six rolling points; all seven identifiable blue diamonds were retained here. The marker near TR 0.31 is partially covered by the paper's black annotation, but its blue diamond is visible; `moreland_marker_detail.png` documents this.

- Source condition: Scarab, mass 400 kg, rigid wheels diameter 71 cm and width 25 cm, GRC-1 lunar terrain-strength simulant. The bed was loosened to 45 cm and compacted; cone penetration checked preparation (PDF pp. 2–3).
- **The abscissa is source-defined travel reduction relative to a near-zero-drawbar/self-propelled ground-speed baseline. It is not kinematic wheel slip 1−v/(R omega).** Moreland explicitly states that the near-zero-load baseline has small nonzero physical slip and is assumed zero for this metric. For inching, a cycle and baseline are needed. Do not insert these TR data into a wheel-torque mechanical CoT formula without an independently specified actuator/baseline-speed model.
- Ordinate is external drawbar load as a fraction of vehicle weight, reconstructed from the plot's percent scale.
- Native chart is the embedded 772×614 PNG `moreland2011_p3_image1_Im4.png` (extracted losslessly from PDF). Axis calibration: x=67 corresponds TR=0; x=748 TR=1; y=551 corresponds drawbar=0; y=13 drawbar=0.40. Coordinates are measured from top-left of the embedded image. Marker centers are hard-coded transparently in `extract_wheel_data.py`.
- Extraction bound: assumed ±2 pixels in each coordinate, i.e. ±0.002937 TR and ±0.001487 drawbar ratio. This is a digitization/reading bound, **not** an experimental error bar or confidence interval. The publication displays horizontal bars, but does not identify their statistical definition in its caption/text; they have not been converted into standard deviations or confidence intervals.
- At low load there are two inching points with effectively the same near-zero TR but different drawbar load. Do not force both through the origin or silently discard either point. A regression fit can describe the cloud; a monotonic inverse needs an explicit treatment of this low-load scatter.
- Visual QA: `moreland2011_fig4_digitization_overlay.png` circles every chosen marker; it was checked against the source chart.

## Creager 2014/2015 measured energy and travel reduction

The independent *experimental campaign* used Fillite hollow alumina-silica microspheres and the same broad Scarab platform, with 400 kg mass, 71 cm diameter ×18 cm wide rigid/pneumatic tires. Pneumatic tires were at 2 psi. This is not GRC-1 and is not a controlled replication of Moreland's wheel/bed conditions. The sources share authors/laboratory/platform, so do not call this an independent laboratory replication.

PDF pp. 13–14 (report pp. 9–10) define:

- TR relative to **rolling on hard ground at the same load and rotational speed**, for BOTH modes. Thus this is a different TR reference from Moreland's mode-specific self-propelled granular-bed baseline. Do not directly pool the two TR datasets.
- Power number PN = P/(W v), including **all vehicle actuation AND hotel loads** such as sensing/computing. It is total vehicle/system input power number, not wheel-only mechanical CoT. The report does not provide a decomposed mechanical-versus-electrical loss ledger; retain its stated measurement boundary.
- PN uses a centered 6-second moving average to suppress zero/negative instantaneous velocity effects; plots of TR are not stated to use the same filter. Therefore matching the two curves at the same nominal time is approximate, and PN(1−TR) is not a direct synchronous raw power measurement.
- Tests are on level Fillite with zero applied external drawbar duty. Increasing TR here reflects time-varying sinkage, not an imposed drawbar-duty sweep.

### Files

- `creager2014_matched_rolling_times.csv`: pneumatic and rigid rolling, times 10,20,...,80 s, matched reconstructed TR and PN from Figures 11 and 12. Columns used by the MATLAB model: `tire`, `mode`, `time_s`, `travel_reduction`, `total_power_number`, `extraction_bound_tr`, `extraction_bound_pn`.
- `creager2014_inching_published_mean_lines.csv`: each tire's separately published horizontal mean TR and mean PN lines. Means are approximately pneumatic TR 0.7873, PN 9.409; rigid TR 0.8017, PN 10.623. Do not treat mean(PN)*(1−mean(TR)) as the mean of P/(W v_ref); averages do not generally commute with this product.
- `creager2014_fig11_tr_curves.csv` and `creager2014_fig12_pn_curves.csv`: auxiliary readouts every 5 seconds along rolling and dashed inching plot lines. These are curve interpolants, not additional independent measurements or new experimental replicates.
- `creager2014_p16_curves.json`, `creager2014_p17_curves.json`: PDF geometry for auditing object selection.
- `creager2014_fig11_digitization_overlay.png`, `creager2014_fig12_digitization_overlay.png`: reconstructed readouts marked on original source pages; checked visually against each series.

### Reproducible extraction

`extract_wheel_data.py` uses pdfplumber to read the actual filled vector paths that form the plotted lines. For each x coordinate it intersects each selected polygon with a vertical line and takes the midpoint between upper/lower boundaries as centerline. Dashed line gaps are linearly interpolated between visible nearby segments. We do not treat polygon outlines as extra measurements.

Axis mappings (PDF points, top-left coordinates):

- Figure 11: t=0 at x146.52, t=200 at x488.941; TR=0 at y665.341, TR=1 at y419.101.
- Figure 12: t=0 at x136.08, t=200 at x506.881; PN=0 at y342.601, PN=50 at y80.520.

The x anchors use tick centers; y anchors use grid-line centers. Extraction bounds are the local graphical line half-thickness plus 0.4 PDF point in ordinate, mapped into data units, with minimum bound 0.005 for TR and 0.25 for PN. A steep line creates a larger ordinate bound because the thick graphical stroke spans a wider y interval at fixed x. These are deterministic reconstruction bounds, not independent Gaussian experimental errors. An additional uncertainty from time registration and source filtering remains.

### Defensible model use

A chronological 20–40 s calibration and 50–80 s held-out prediction of PN conditional on **observed** TR can test a constant normalized-power approximation within each rolling curve. This is a within-trajectory test, not a new experiment, not a full mobility model, and not an independent validation of a model predicting TR. The general identity PN=q/(1−TR) alone is algebra, not a novel discovered law. The scientific question being tested is whether an approximately constant q estimated early predicts later PN. Do not claim high sample sizes from the number of plot time points.

Do not combine the Fillite PN levels (~2–40) with a wheel-only mechanical CoT model (~0.1–0.3) or an SPV mechanical CoT benchmark as though they share an energy measurement boundary.

## Creager 2012 external traction comparison

`creager2012_fig5_traction.csv` contains 62 plotted marker centers from Figure 5 (PDF page 6): 16 rigid inching, 15 rigid rolling, 13 pneumatic inching, 18 pneumatic rolling. The mode symbol is circle=inching, star=rolling; color distinguishes tire type. Extraction uses circle bounding-box centers and the center of each star's horizontal stroke, excluding legend entries. Coordinates and PDF object indices are retained; assumed reading bounds are ±0.005 TR and ±0.001 drawbar ratio. These bounds are not experimental confidence limits. The overlay `creager2012_fig5_digitization_overlay.png` was visually checked.

Axes: drawbar 0 at x150.0597525 and 0.4 at x470.0129635; TR=1 at y132.8692387 and TR=−0.2 at y361.7539167. The source plots TR in percent; CSV stores fraction and retains the slightly negative low-load markers rather than clipping.

The tires are 28 inch diameter ×7 inch width, with low tread/sandpaper-like rigid finish, and GRC-1 is loosened/leveled. These are different conditions from Moreland's 25 cm-wide rigid wheels and compacted bed. Thus use this as an external traction pattern/domain-transfer test with conditions disclosed, not an exact calibration replication. Pneumatic rolling has lower TR at low/intermediate duty; inching becomes beneficial only near high load. A universal constant 1.89 traction multiplier across platforms/tire compliance is not supported by this source.

## Direct textual numerical evidence

`reported_values.csv` distinguishes prose-reported quantities from our digitized curves. It includes Moreland's approximate 0.11 vs0.21 drawbar at TR≈0.3, the six-test Fillite preparation repeatability check, and the entrapped-mode PN10.63 after the 90-second switch. Six repeats pertain to the terrain-preparation consistency experiment; do not assign n=6 to every plotted energy condition without additional source evidence.

## Reproduction

From this directory's parent or any working directory:

`python extract_wheel_data.py` (after running the source preparation script)

The script resolves source paths relative to itself. It uses only local archived PDFs/PNG and creates derived CSVs, hashes, and audit overlays. No original manuscript or source publication is modified.

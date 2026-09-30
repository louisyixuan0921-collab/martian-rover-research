# Model specification and numerical methods

This supplement documents the two-term traction closure, inching multiplier, duty and slope equations, source-marker fits, and reproducible calculations. The traction evidence does not independently validate the assumed energy model.

## Reproduce the reported model

With base MATLAB R2026a (the recorded run used Update 3):

```matlab
cd('/path/to/martian-rover-research')
run_conservative_model
```

No Optimization or Statistics Toolbox is required. The script uses deterministic multi-start `fminsearch`, `fzero`, and a locally implemented empirical-percentile function. It writes the parameter tables, source fits, anchor values, duty/slope curves, sensitivity results, five figures, and `results/summary.json`. The supplied `results/matlab_run.log` records the successful actual MATLAB execution and numerical checks.

The random seed is **20260922**, with **10,000 paired scenario draws**. Repeated runs overwrite the generated results and figures in this package. The physical source CSVs remain unchanged.

An independent NumPy arithmetic audit and its recorded report are in `audit/independent_numeric_check.py`, `.md`, and `.json`. From this package directory, run `python audit/independent_numeric_check.py .` to repeat the audit using the saved scenario draws; it does not modify the model or its results.

## Model definitions and interpretation

The source coordinate is **travel reduction T**, not kinematic wheel slip:

`T = 1 - v/v_ref; phi_roll(T) = alpha*(1-exp(-T/K)) + beta*T; phi_inch(T) = lambda*phi_roll(T)`.

The fit uses all **seven visible rolling markers and four inching markers** in Moreland (2011), Figure 4. Fit covariance, standard errors, raw trial counts and experimental confidence intervals are not inferred from these reconstructed markers. The single-term saturation comparator is an empirical comparison in this source coordinate, not a validation of a Janosi–Hanamoto constitutive model.

The energy calculations use a **scenario mechanical-CoT proxy**:

`C_roll=(d+f_r)/(1-T_roll)`

`C_inch=(d+eta*f_r)*(1+epsilon_act)/(1-T_inch)`.

Normalized reference power is `Q=<P>/(W V_ref)`, where `<P>` is mean power, `W` is vehicle weight, and `V_ref` is the reference speed used to define travel reduction. The proxy formulas correspond to choosing the closures `Q_roll=d+f_r` and `Q_inch=(d+eta*f_r)*(1+epsilon_act)` in `C=Q/(1-T)`. They are assumptions about power; net drawbar force and travel reduction do not measure the required power. The source reference speed differs by study and is not necessarily wheel circumferential speed.

For a slope, the force-balance transfer is `phi(T)=tan(theta)+d/cos(theta)`. The numerator is `sin(theta)+d+f_r*cos(theta)` for rolling and `sin(theta)+d+eta*f_r*cos(theta)` for inching, with the inching actuator factor applied to the whole expression. **Every inclined-bed result assumes transfer from the flat-bed fit; no measured slope capability is inferred.**

## Baseline versus structural sensitivity

- **Nominal values:** `f_r=0.05`, `epsilon_act=0.10`, `eta=0.50`.
- **Baseline:** fixed `eta=0.50`; independently sample `f_r~U[0.05,0.15]` and `epsilon_act~U[0.05,0.15]`, while retaining the same `f_r` in the two modes for each paired draw. The fitted traction parameters remain fixed. Table 3 and main Figures 5–6 use this baseline. The shaded bounds are pointwise 5th–95th **scenario percentiles**, not experimental confidence intervals.
- **Expanded structural sensitivity:** on the same draws, use `eta~U[0.50,1.00]`. This is separate in `results/expanded_eta_paired_sensitivity.csv` and `summary.json` under `expanded_eta_sensitivity`. Table 3 uses the fixed `eta=0.50` baseline.
- `results/scenario_draws.csv` records the sampled values; its eta column is for the separate expanded sensitivity. Baseline eta is fixed at 0.50.

Nominal predictions differ from baseline medians because the nominal resistance is 0.05 while the sampling range is centered on 0.10. Manuscript Table 3 reports scenario medians; `results/table3_anchor_values.csv` contains the nominal predictions and percentile fields. The percentage reduction calculated from the ratio of median costs is supplied explicitly. It is distinct from the median of paired percentage reductions.

A low-load ordering can reverse in the expanded sensitivity. At duty 0.10 the selected modest-actuator ranges still favor inching, but this is conditional on the energy closure and selected ranges. With eta=1, the computed actuator break-even value is supplied; it is not a measured actuator-loss estimate. The source data do not establish those parameter ranges as probability distributions of real rovers.

## Support and extrapolation

The source TR ranges are approximately 0.0103–0.8267 (rolling) and 0.0103–0.7137 (inching). Root solutions outside those ranges are marked as source-coordinate extrapolation in `table3_anchor_values.csv`. In particular, d=0 is extrapolated for both modes, d=0.05 for inching, and d=0.20 for rolling.

The limits `phi_roll(1)` and `lambda*phi_roll(1)` and their arctangents are only **mathematical extrapolation walls**, not measured maximum duty or climb angles. No confidence interval is estimated for these limits. Every baseline draw has the same fixed traction wall; the ensemble does not vary fitted capacity or condition on surviving parameter draws.

## Figure roles

- Figure 4: actual marker fit, two-term and single-term comparator; dotted fit extensions are outside the source TR support.
- Figure 5: duty sweep, baseline scenario bands and nominal curves; an eta=1 nominal sensitivity curve is also shown. SPV energy values are not pooled because their measurement boundary and medium differ.
- Figure 6: slope sweep with hypothetical normal-load transfer.
- Figure 7: measured/predicted mechanical CoT ratios for recoverable HGSL2 and HGSL3 source means; bars reflect coordinate-extraction bounds, not original SEM or confidence intervals. HGSL1 is the source's calibration prototype; no HGSL1 values or pooled 6.07 benchmark are reconstructed.
- Figure 8: supplementary measured-energy check using the Creager total-vehicle PN curves. This checks a separately calibrated constant-Q approximation given observed TR. It does **not** validate `Q=d+f_r`, resistance halving, or the mechanical energy proxy.

The helical ratio cancels the source table's uncertain mass-unit convention. The raw evidence CSV retains explicitly conditional absolute CoT fields for transparency; these do not enter the principal figure or a three-way energy ranking.

## Source extraction and independence

The primary analysis CSVs are in `data/`, with detailed `WHEEL_PROVENANCE.md` and `INDEPENDENT_ENERGY_EVIDENCE.md`. The independent Cao narrative ratios remain author-reported best-case summaries, not newly digitized raw trials.

For optional reconstruction from published figures, install Python packages `pypdf`, `pdfplumber`, `numpy`, and `Pillow`, then run:

```text
python source_extraction/prepare_sources.py
python source_extraction/wheels/extract_wheel_data.py
python source_extraction/screws/extract_pre_figure.py
python source_extraction/screws/build_screw_csv.py
```

The preparation script downloads the public primary PDFs to the extraction folders and extracts their unmodified native figures. Source PDFs are not bundled. The extraction scripts create CSVs beside themselves; compare them with `data/` before updating the model inputs. Some optional plots and supporting files named in the original provenance refer to the research extraction workspace and are not needed to run the MATLAB model.

The NASA 2014 technical report and Creager 2015 journal article describe the same research, not two independent energy validations. Matched time samples are correlated within a published curve. No authors were contacted and no new physical experiments were performed.

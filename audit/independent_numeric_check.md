# Independent numerical audit

**PASS** — 13608 checks across the delivered MATLAB results.

The audit independently refitted traction using variable projection instead of MATLAB's optimizer, solved every reported duty/slope root with bisection, and recomputed all baseline and expanded-eta percentiles from the 10,000 saved paired draws.

- Traction: alpha=0.0718235856, K=0.0175401852, beta=0.1391740335; lambda=1.8880184895. Two-term RMSE 0.0032017044; single-term RMSE 0.0211636076; inching multiplier RMSE 0.0115989430.
- At duty 0.10, baseline eta=0.5 medians are rolling 0.2500811704, inching 0.1682279671. Ratio-of-medians reduction is 32.73065430%; baseline median paired reduction is 32.68768297%; expanded-eta median paired reduction is 21.01889557%. They are distinct.
- Mathematical slope walls: rolling 11.91451322 degrees; inching 21.72072554 degrees. Both extrapolate the fitted closure to T=1, beyond source support.
- Creager temporal holdout MAPE: pneumatic 3.01713519%, rigid 5.23362012%. All eight holdout predictions underestimate; Q mean drift is +3.11215477% and +5.52582772%, respectively.
- Screw pooled MAPE: power 3.90033947%, speed 5.33496852%, CoT 6.13925499%. Ratio arithmetic is independent of mass units.

## Interpretation constraints

- This audit checks arithmetic, fit reconstruction, root solving, source-support labels, and file consistency. It is not experimental validation of the assumed mechanical-CoT closure.
- Baseline Table 3/Figures 5–6 fix eta=0.5. Saved scenario_draws.csv eta values are only the expanded-eta sensitivity. Its filename/header does not imply baseline eta varies.
- Percentiles use saved draws and linear interpolation. They describe selected scenario ranges with a fixed traction fit; they are not confidence, credible, or repeated-experiment intervals. MATLAB RNG generation was not independently replayed.
- Baseline ratio of medians, baseline median paired percentage reduction, nominal reduction, and expanded-eta median paired reduction are distinct statistics and must not be interchanged.
- Slope walls are atan(phi(1)) and atan(lambda*phi(1)); each extends beyond the maximum source travel reduction. They are mathematical walls of an assumed slope transfer, not observed climbing limits.
- Traction leave-one-marker-out is a marker reconstruction diagnostic, not independent trial validation. Inching omission retains the rolling fit, as intended.
- The separate Creager conditional-Q exercise calibrates at 20/30/40 s and evaluates at 50/60/70/80 s in the same source trajectory. Total vehicle electrical energy including hotel loads is distinct from the scenario mechanical proxy.
- Screw ratios use same-prototype measured/predicted P/v and cancel both mass and gravity. Extraction-bound intervals are not experimental confidence intervals; no source mass-unit inference is needed for these ratios.

The audit rewrites only its own Markdown and JSON reports. Model, source CSVs, generated results, and manuscript are unchanged. Input and output hashes are recorded in the JSON. Run with NumPy using `python independent_numeric_check.py [package_directory]`.

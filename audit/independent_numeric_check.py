#!/usr/bin/env python3
"""Independent NumPy arithmetic audit; does not execute or modify MATLAB/DOCX.

Uses saved scenario draws rather than attempting to reproduce MATLAB's RNG.
Traction refit uses variable projection + one-dimensional golden-section search,
independent of MATLAB's multistart Nelder-Mead optimizer. All roots use bisection.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
import numpy as np

HERE = Path(__file__).resolve().parent
PKG = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent
RES = PKG / "results"
DATA = PKG / "data"
checks = defaultdict(lambda: {"checked": 0, "max_absolute_difference": 0.0})
failures = []
read_files = set()

def read_csv(path):
    read_files.add(path)
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def f(row, key):
    return float(row[key])

def check(group, label, got, expected, atol=2e-10, rtol=2e-9):
    checks[group]["checked"] += 1
    if isinstance(got, str) or isinstance(expected, str):
        good = got == expected
        delta = 0.0
    else:
        got = float("nan") if got is None else float(got)
        expected = float("nan") if expected is None else float(expected)
        delta = abs(got-expected) if math.isfinite(got) and math.isfinite(expected) else 0.0
        good = (math.isnan(got) and math.isnan(expected)) or math.isclose(got, expected, rel_tol=rtol, abs_tol=atol)
    checks[group]["max_absolute_difference"] = max(checks[group]["max_absolute_difference"], delta)
    if not good:
        failures.append({"group": group, "label": label, "recomputed": got, "reported": expected, "absolute_difference": delta})

def require(group, label, value):
    check(group, label, int(bool(value)), 1, atol=0, rtol=0)

summary = json.loads((RES / "summary.json").read_text())
read_files.add(RES / "summary.json")
pars = summary["fit_parameters"]
p = np.array([pars[k] for k in ("alpha", "K", "beta")])
lam = pars["lambda"]
p1 = np.array([summary["single_term_parameters"][k] for k in ("amplitude", "K")])

def phi(x, para=p):
    x = np.asarray(x)
    ans = para[0] * (-np.expm1(-x / para[1]))
    return ans + para[2] * x if len(para) == 3 else ans

def profile_fit(x, y, two=True):
    """Analytic linear least squares at each K; optimize scalar log(K)."""
    def at(z):
        k = math.exp(z)
        a = -np.expm1(-x/k)
        X = np.column_stack([a, x]) if two else a[:, None]
        coeff = np.linalg.lstsq(X, y, rcond=None)[0]
        if np.any(coeff <= 0):
            return math.inf, None
        r = X @ coeff - y
        return float(r @ r), (np.array([coeff[0], k, coeff[1]]) if two else np.array([coeff[0], k]))
    grid = np.linspace(-25, 5, 2001)
    vals = np.array([at(z)[0] for z in grid])
    j = int(np.argmin(vals))
    a, b = grid[max(0, j-1)], grid[min(len(grid)-1, j+1)]
    golden = (math.sqrt(5)-1)/2
    c, d = b-golden*(b-a), a+golden*(b-a)
    for _ in range(100):
        if at(c)[0] < at(d)[0]:
            b, d = d, c
            c = b-golden*(b-a)
        else:
            a, c = c, d
            d = a+golden*(b-a)
    v, params = at((a+b)/2)
    return params, v

A = read_csv(DATA / "moreland2011_fig4_traction.csv")
rolling = sorted([r for r in A if r["mode"] == "rolling"], key=lambda r: f(r,"travel_reduction"))
inching = sorted([r for r in A if r["mode"] == "inching"], key=lambda r: f(r,"travel_reduction"))
xr, yr = (np.array([f(r,k) for r in rolling]) for k in ("travel_reduction", "drawbar_ratio"))
xi, yi = (np.array([f(r,k) for r in inching]) for k in ("travel_reduction", "drawbar_ratio"))
require("traction", "seven rolling/four inching markers", len(rolling)==7 and len(inching)==4)
refit2, refsse2 = profile_fit(xr, yr)
refit1, refsse1 = profile_fit(xr, yr, False)
for j, k in enumerate(("alpha", "K", "beta")):
    check("independent_optimizer", k, refit2[j], p[j], atol=1e-8, rtol=1e-6)
for j, k in enumerate(("amplitude", "K")):
    check("independent_optimizer", "single_"+k, refit1[j], p1[j], atol=1e-8, rtol=1e-6)
base = phi(xi)
lam_recalc = float(base @ yi / (base @ base))
check("traction", "closed-form lambda", lam_recalc, lam)
errors = {
    "two_term_rolling": phi(xr)-yr,
    "single_term_rolling": phi(xr,p1)-yr,
    "multiplier_inching": lam*phi(xi)-yi,
}
for r in read_csv(RES / "traction_fit_metrics.csv"):
    e = errors[r["model"]]
    check("traction", r["model"]+" SSE", float(e@e), f(r,"sse_drawbar_ratio"))
    check("traction", r["model"]+" RMSE /N", math.sqrt(float(e@e)/len(e)), f(r,"rmse_drawbar_ratio"))
    check("traction", r["model"]+" source count", len(e), f(r,"source_markers"))
for r in read_csv(RES / "traction_source_fit.csv"):
    pred = float(phi(f(r,"travel_reduction"))) * (lam if r["mode"]=="inching" else 1)
    check("traction", "source fitted response", pred, f(r,"predicted_drawbar_ratio"))
    check("traction", "source residual", pred-f(r,"drawbar_ratio"), f(r,"residual"))
for r in read_csv(RES / "traction_leave_one_marker_out.csv"):
    j = int(r["omitted_marker"])-1
    if r["mode"] == "rolling":
        keep = np.arange(len(xr)) != j
        refit, _ = profile_fit(xr[keep], yr[keep])
        pred = float(phi(xr[j], refit))
    else:
        keep = np.arange(len(xi)) != j
        a = phi(xi[keep]); multiplier = float(a@yi[keep] / (a@a))
        pred = multiplier*float(phi(xi[j]))
    check("independent_marker_omission", f"{r['mode']} {j+1}", pred, f(r,"predicted_drawbar"), atol=1e-7, rtol=1e-6)

draw_rows = read_csv(RES / "scenario_draws.csv")
fr, eps, eta = (np.array([f(r,k) for r in draw_rows]) for k in ("f_r","epsilon_act","eta"))
require("scenario_design", "10000 draws", len(fr)==10000)
require("scenario_design", "draw IDs", [int(r["draw"]) for r in draw_rows]==list(range(1,10001)))
require("scenario_design", "fr range", np.all((fr>=.05)&(fr<=.15)))
require("scenario_design", "epsilon range", np.all((eps>=.05)&(eps<=.15)))
require("scenario_design", "expanded eta range", np.all((eta>=.5)&(eta<=1)))

def root(d, multiplier=1):
    if d == 0:
        return 0.
    if not 0 < d < multiplier*float(phi(1)):
        return math.nan
    a,b = 0.,1.
    for _ in range(65):
        mid = (a+b)/2
        if multiplier*float(phi(mid)) < d:
            a=mid
        else:
            b=mid
    return (a+b)/2

def scenarios(d, angle=0, eta_use=.5):
    theta = math.radians(angle)
    sn, cs = math.sin(theta), math.cos(theta)
    demand = math.tan(theta)+d/cs
    tr, ti = root(demand), root(demand,lam)
    cr = (sn+d+fr*cs)/(1-tr)
    ci = (sn+d+eta_use*fr*cs)*(1+eps)/(1-ti)
    nominal = [(sn+d+.05*cs)/(1-tr), (sn+d+.5*.05*cs)*1.1/(1-ti)]
    return tr, ti, cr, ci, nominal

def quantiles(a):
    return np.quantile(a,[.05,.5,.95],method="linear") if np.all(np.isfinite(a)) else [math.nan]*3

anchors = read_csv(RES / "table3_anchor_values.csv")
reductions = read_csv(RES / "expanded_eta_paired_sensitivity.csv")
anchor_detail = []
for row, red in zip(anchors, reductions):
    d = f(row,"duty")
    tr,ti,cr,ci,nominal = scenarios(d)
    qr,qi = quantiles(cr),quantiles(ci)
    computed = {
        "T_rolling":tr,"T_inching":ti,"nominal_rolling_proxy":nominal[0],"nominal_inching_proxy":nominal[1],
        "rolling_scenario_p05":qr[0],"rolling_scenario_median":qr[1],"rolling_scenario_p95":qr[2],
        "inching_scenario_p05":qi[0],"inching_scenario_median":qi[1],"inching_scenario_p95":qi[2],
        "ratio_of_scenario_medians_reduction_percent":100*(1-qi[1]/qr[1]),
    }
    for k,v in computed.items():
        check("baseline_anchors_eta_fixed_0_5", f"d={d} {k}", v,f(row,k))
    baseline_paired = 100*(1-ci/cr)
    _,_,_,ciexp,_ = scenarios(d,eta_use=eta)
    expanded_paired = 100*(1-ciexp/cr)
    qred = quantiles(expanded_paired)
    rc = {
        "nominal_reduction_percent":100*(1-nominal[1]/nominal[0]),
        "paired_scenario_median_reduction_percent":qred[1],
        "paired_scenario_p05_reduction":qred[0],"paired_scenario_p95_reduction":qred[2],
        "scenario_fraction_inching_lower":float(np.mean(ciexp<cr)),
        "inching_nominal_eta1_proxy":(d+.05)*1.1/(1-ti),
        "epsilon_break_even_when_eta1":(1-ti)/(1-tr)-1,
    }
    for k,v in rc.items():
        check("expanded_eta_anchors", f"d={d} {k}",v,f(red,k))
    for mode,t,xsrc in (("rolling",tr,xr),("inching",ti,xi)):
        expected = "source-TR extrapolation" if t<min(xsrc) or t>max(xsrc) else "within source TR range; energy closure assumed"
        check("support_labels",f"d={d} {mode}",row[mode+"_support_status"],expected)
    anchor_detail.append({"duty":d, **computed,
        "baseline_paired_median_reduction_percent":float(np.median(baseline_paired)),
        "expanded_eta_paired_median_reduction_percent":float(qred[1]),
        "expanded_eta_fraction_lower":float(np.mean(ciexp<cr))})

for filename, angle_mode in (("duty_curve.csv",False),("slope_curve.csv",True),("slope_anchor_values.csv",True)):
    for r in read_csv(RES / filename):
        d,angle = (0,f(r,"angle_deg")) if angle_mode else (f(r,"duty"),0)
        tr,ti,cr,ci,n = scenarios(d,angle)
        qr,qi = quantiles(cr),quantiles(ci)
        fields = dict(T_rolling=tr,T_inching=ti,nominal_rolling=n[0],nominal_inching=n[1],
                      rolling_p05=qr[0],rolling_median=qr[1],rolling_p95=qr[2],
                      inching_p05=qi[0],inching_median=qi[1],inching_p95=qi[2])
        for k,v in fields.items():
            check(filename, f"d={d} angle={angle} {k}",v,f(r,k),atol=3e-9,rtol=3e-8)

walls=[]
for r in read_csv(RES / "source_support_and_mathematical_walls.csv"):
    mode=r["mode"]; mult=lam if mode=="inching" else 1
    x,y=(xi,yi) if mode=="inching" else (xr,yr)
    wall=mult*float(phi(1))
    vals=dict(mathematical_duty_wall=wall,mathematical_slope_wall_deg=math.degrees(math.atan(wall)),
              observed_TR_min=min(x),observed_TR_max=max(x),observed_duty_min=min(y),observed_duty_max=max(y),
              fitted_duty_at_min_source_TR=mult*float(phi(min(x))),fitted_duty_at_max_source_TR=mult*float(phi(max(x))))
    for k,v in vals.items():
        check("mathematical_walls_and_support",mode+" "+k,v,f(r,k))
    require("mathematical_walls_and_support",mode+" extrapolates beyond source",max(x)<1)
    require("mathematical_walls_and_support",mode+" unavailable at wall",math.isnan(root(wall,mult)))
    walls.append({"mode":mode,**vals})

R=read_csv(DATA / "creager2014_matched_rolling_times.csv")
energy_out={r["tire"]:r for r in read_csv(RES / "empirical_energy_check.csv")}
energy_preds={(r["tire"],f(r,"time_s")):r for r in read_csv(RES / "empirical_energy_predictions.csv")}
energy=[]
for tire in ("pneumatic","rigid"):
    rows=sorted([r for r in R if r["tire"]==tire],key=lambda r:f(r,"time_s"))
    times,tr,pn=(np.array([f(r,k) for r in rows]) for k in ("time_s","travel_reduction","total_power_number"))
    cal=np.isin(times,[20,30,40]); test=np.isin(times,[50,60,70,80])
    require("empirical_energy",tire+" no calibration/holdout overlap",not np.any(cal&test))
    q=pn*(1-tr); q0=float(np.median(q[cal])); pred=q0/(1-tr); resid=pred[test]-pn[test]
    metrics=dict(Q_empirical=q0,calibration_times=sum(cal),evaluation_times=sum(test),
                 rmse_PN=float(np.sqrt(np.mean(resid**2))),mape_percent=float(np.mean(np.abs(resid)/pn[test])*100),
                 constant_PN_baseline_rmse=float(np.sqrt(np.mean((np.median(pn[cal])-pn[test])**2))))
    for k,v in metrics.items():
        check("empirical_energy",tire+" "+k,v,f(energy_out[tire],k))
    for j,t in enumerate(times):
        r=energy_preds[(tire,t)]
        role="calibration" if cal[j] else "temporal_holdout" if test[j] else "diagnostic"
        check("empirical_energy",f"{tire} {t} prediction",pred[j],f(r,"predicted_PN"))
        check("empirical_energy",f"{tire} {t} role",role,r["role"])
    require("empirical_energy",tire+" all four holdouts underestimated",np.all(resid<0))
    energy.append({"tire":tire,**{k:float(v) for k,v in metrics.items()},
                   "Q_holdout_median_drift_percent":float(100*(np.median(q[test])/q0-1)),
                   "holdout_residuals_prediction_minus_observed":resid.tolist()})

S=read_csv(DATA / "thoesen2020_fig4.csv")
screw_out=read_csv(RES / "screw_matched_ratios.csv")
metrics_out={r["prototype"]:r for r in read_csv(RES / "screw_scaling_metrics.csv")}
ratios=[]; allpe=[]; allve=[]; allce=[]
for r,o in zip(S,screw_out):
    pm,pp,vm,vp,pb,vb=(f(r,k) for k in ("power_measured_W","power_predicted_W","velocity_measured_m_s","velocity_predicted_m_s","power_digitization_bound_W","velocity_digitization_bound_m_s"))
    require("screw",r["prototype"]+" all lower bounds positive",min(pm-pb,pp-pb,vm-vb,vp-vb)>0)
    # Algebraically equivalent cross-product has no mass/gravity dependency.
    ratio=(pm*vp)/(pp*vm)
    low=(pm-pb)*(vp-vb)/((vm+vb)*(pp+pb))
    high=(pm+pb)*(vp+vb)/((vm-vb)*(pp-pb))
    for k,v in (("cot_ratio",ratio),("ratio_lower",low),("ratio_upper",high)):
        check("screw",r["prototype"]+" "+k,v,f(o,k))
    pe=100*abs(pp-pm)/pm; ve=100*abs(vp-vm)/vm; ce=100*abs(1/ratio-1)
    ratios.append((r["prototype"],ratio,pe,ve,ce))
    allpe.append(pe); allve.append(ve); allce.append(ce)
for prototype,out in metrics_out.items():
    rs=[r for r in ratios if r[0]==prototype]
    metrics=dict(paired_means=len(rs),power_mape_percent=np.mean([r[2] for r in rs]),velocity_mape_percent=np.mean([r[3] for r in rs]),
                 cot_mape_percent=np.mean([r[4] for r in rs]),cot_ratio_min=min(r[1] for r in rs),cot_ratio_max=max(r[1] for r in rs))
    for k,v in metrics.items():
        check("screw",prototype+" "+k,v,f(out,k))
screw_pooled=dict(paired_means=len(S),power_mape_percent=float(np.mean(allpe)),velocity_mape_percent=float(np.mean(allve)),cot_mape_percent=float(np.mean(allce)))

# Confirm JSON is consistent with the CSV deliverables already checked above.
for skey,filename in (("fit_metrics","traction_fit_metrics.csv"),("anchor_values","table3_anchor_values.csv"),
                      ("expanded_eta_sensitivity","expanded_eta_paired_sensitivity.csv"),
                      ("mathematical_walls_and_source_support","source_support_and_mathematical_walls.csv"),
                      ("slope_anchors","slope_anchor_values.csv"),("screw_metrics","screw_scaling_metrics.csv"),
                      ("empirical_energy_check","empirical_energy_check.csv")):
    rows=read_csv(RES/filename)
    check("json_csv_consistency",skey+" length",len(summary[skey]),len(rows))
    for j,(js,cs) in enumerate(zip(summary[skey],rows)):
        for k,v in js.items():
            check("json_csv_consistency",f"{skey} {j} {k}",v,cs[k] if isinstance(v,str) else f(cs,k))

log=(RES/"matlab_run.log").read_text(); read_files.add(RES/"matlab_run.log")
require("run_record","MATLAB completion message", "All numerical checks passed." in log)
require("run_record","MATLAB version recorded",summary["matlab_version"] in log)
read_files.add(PKG/"run_conservative_model.m")
notes=[
    "This audit checks arithmetic, fit reconstruction, root solving, source-support labels, and file consistency. It is not experimental validation of the assumed mechanical-CoT closure.",
    "Baseline Table 3/Figures 5–6 fix eta=0.5. Saved scenario_draws.csv eta values are only the expanded-eta sensitivity. Its filename/header does not imply baseline eta varies.",
    "Percentiles use saved draws and linear interpolation. They describe selected scenario ranges with a fixed traction fit; they are not confidence, credible, or repeated-experiment intervals. MATLAB RNG generation was not independently replayed.",
    "Baseline ratio of medians, baseline median paired percentage reduction, nominal reduction, and expanded-eta median paired reduction are distinct statistics and must not be interchanged.",
    "Slope walls are atan(phi(1)) and atan(lambda*phi(1)); each extends beyond the maximum source travel reduction. They are mathematical walls of an assumed slope transfer, not observed climbing limits.",
    "Traction leave-one-marker-out is a marker reconstruction diagnostic, not independent trial validation. Inching omission retains the rolling fit, as intended.",
    "The separate Creager conditional-Q exercise calibrates at 20/30/40 s and evaluates at 50/60/70/80 s in the same source trajectory. Total vehicle electrical energy including hotel loads is distinct from the scenario mechanical proxy.",
    "Screw ratios use same-prototype measured/predicted P/v and cancel both mass and gravity. Extraction-bound intervals are not experimental confidence intervals; no source mass-unit inference is needed for these ratios.",
]
result=dict(status="PASS" if not failures else "FAIL",scope="Independent numerical audit of the preserved-model MATLAB outputs",
            independent_methods=dict(fit="Variable projection and scalar golden-section minimization",roots="65-iteration bisection",percentiles="NumPy linear quantile of recorded paired draws"),
            check_count=sum(r["checked"] for r in checks.values()),checks=dict(checks),failures=failures,
            independently_refitted_parameters=dict(alpha=float(refit2[0]),K=float(refit2[1]),beta=float(refit2[2]),single_amplitude=float(refit1[0]),single_K=float(refit1[1])),
            refitted_sse=dict(two_term=refsse2,single_term=refsse1),lambda_closed_form=lam_recalc,
            anchors=anchor_detail,mathematical_walls=walls,empirical_energy=energy,screw_pooled=screw_pooled,interpretation_notes=notes,
            sha256={str(path.relative_to(PKG)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(read_files)})
(HERE/"independent_numeric_check.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
at01=next(r for r in anchor_detail if r["duty"]==.1)
lines=["# Independent numerical audit", "", f"**{result['status']}** — {result['check_count']} checks across the delivered MATLAB results.", "",
       "The audit independently refitted traction using variable projection instead of MATLAB's optimizer, solved every reported duty/slope root with bisection, and recomputed all baseline and expanded-eta percentiles from the 10,000 saved paired draws.", "",
       f"- Traction: alpha={refit2[0]:.10f}, K={refit2[1]:.10f}, beta={refit2[2]:.10f}; lambda={lam_recalc:.10f}. Two-term RMSE 0.0032017044; single-term RMSE 0.0211636076; inching multiplier RMSE 0.0115989430.",
       f"- At duty 0.10, baseline eta=0.5 medians are rolling {at01['rolling_scenario_median']:.10f}, inching {at01['inching_scenario_median']:.10f}. Ratio-of-medians reduction is {at01['ratio_of_scenario_medians_reduction_percent']:.8f}%; baseline median paired reduction is {at01['baseline_paired_median_reduction_percent']:.8f}%; expanded-eta median paired reduction is {at01['expanded_eta_paired_median_reduction_percent']:.8f}%. They are distinct.",
       "- Mathematical slope walls: rolling 11.91451322 degrees; inching 21.72072554 degrees. Both extrapolate the fitted closure to T=1, beyond source support.",
       "- Creager temporal holdout MAPE: pneumatic 3.01713519%, rigid 5.23362012%. All eight holdout predictions underestimate; Q mean drift is +3.11215477% and +5.52582772%, respectively.",
       f"- Screw pooled MAPE: power {screw_pooled['power_mape_percent']:.8f}%, speed {screw_pooled['velocity_mape_percent']:.8f}%, CoT {screw_pooled['cot_mape_percent']:.8f}%. Ratio arithmetic is independent of mass units.","", "## Interpretation constraints", ""]
lines += ["- "+n for n in notes]
if failures:
    lines += ["", "## Failures", "", json.dumps(failures,indent=2)]
lines += ["", "The audit rewrites only its own Markdown and JSON reports. Model, source CSVs, generated results, and manuscript are unchanged. Input and output hashes are recorded in the JSON. Run with NumPy using `python independent_numeric_check.py [package_directory]`.", ""]
(HERE/"independent_numeric_check.md").write_text("\n".join(lines))
print(json.dumps({"status":result["status"],"checks":result["check_count"],"failures":failures,"duty_0_1_statistics":at01,"screw_pooled":screw_pooled},indent=2))
sys.exit(bool(failures))

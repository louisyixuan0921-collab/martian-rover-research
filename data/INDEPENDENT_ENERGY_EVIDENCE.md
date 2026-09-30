# Independent energy evidence and model audit

## Cao et al. (2023): measured energy boundary and conditional reversal

C. Cao, D. Moon, C. Creager, D. K. Lieu, and H. S. Stuart, “Push-pull locomotion: Increasing travel velocity in loose regolith via induced wheel slip,” *Journal of Terramechanics*, 110, 87–99 (2023). DOI: https://doi.org/10.1016/j.jterra.2023.08.005

Author publication page: https://edg.berkeley.edu/publication/push-pull-locomotion-increasing-travel-velocity-in-loose-regolith-via-induced-wheel-slip/

Full author repository PDF (successfully read through the web tool): https://escholarship.org/content/qt05f4t7gq/qt05f4t7gq.pdf?t=s16ww9

Paper pp. 89–91, Sections 2.1–2.2, Eqs. (2)–(4), Figs. 4–5: Shifty weighs 9.7 kg and uses 17.5 cm wheels in Mars 90. The tested slopes are 0°, 10°, 15°, and 20°, with three trials per condition and two datasets. Power is **electrical input to the motor controllers**, separately measured for wheel and leg pairs. The second dataset measures voltage; the first uses nominal voltage.

Reported normalized energy ratios inching/rolling: flat ground **at least 1.5** at its best; 10° **down to about 1/3**; 20° **down to about 1/8**. These are reported best-case comparisons, not uncertainty bounds. The 20° experiment reports travel reduction changing from 98% to 85% at about 70% kinematic slip. Kinematic slip, wheel slip, and whole-rover travel reduction are different variables. The paper explicitly warns that its rolling and inching travel-reduction definitions are not directly comparable.

Interpretation: independently supports conditional mode selection; contradicts unconditional energy savings inferred solely from halving rolling resistance. Does not validate Moreland-specific coefficients or the manuscript’s conditional modeled energy saving.

## Retrieval status

The full PDF text was available through web browsing, including all definitions and relevant prose. Direct local download returned HTTP 202 with an empty response, followed by HTTP 403. Therefore no PDF bytes or figure digitization are supplied here. `cao2023.pdf` initially created by the unsuccessful download was removed. Do not claim this source's plotted data have been digitized or raw trials reproduced. Narrative numerical reports are tabulated in `cao2023_reported_ratios.csv`.

## Exact normalized-energy identity: independent dimensional audit

For mode m and a common time window T with positive net advance Δx:

    Pbar_m = E_m / T
    vbar_m = Δx_m / T
    C_m = E_m / (W Δx_m) = Pbar_m / (W vbar_m)
    TR_m = 1 − vbar_m / vref_m
    q_m = Pbar_m / (W vref_m)
    C_m = q_m / (1 − TR_m).

Each quantity C, q, TR is dimensionless. The identity is exact for any consistently declared energy boundary and positive vbar; it is an accounting identity, **not an independently predictive energetic constitutive model**. For equal weight:

    C_i/C_r = (Pbar_i/Pbar_r)(vref_r/vref_i)
              (1−TR_r)/(1−TR_i)
            = (q_i/q_r)(1−TR_r)/(1−TR_i).

Inching saves energy when q_i/q_r < (1−TR_i)/(1−TR_r). The general form for unequal vehicles also needs W_r/W_i. Neither a fitted traction curve nor TR alone estimates q. A switching threshold based on q is conditional until independently measured power/reference velocities are supplied. Each source's definition of vref must remain explicit.

For cyclic gaits use total energy divided by total net distance, or averages over the same complete cycles. Do **not** average instantaneous P(t)/v(t): zero/negative velocities during stance or gait reversal make that a different or undefined statistic. TR = 1 is immobilization for that reference; C diverges only if positive energy continues to be consumed as net velocity tends to zero. TR < 0 is possible when speed exceeds the chosen reference and should not be blindly rejected.

## Mechanical and electrical accounting

At shaft level, define E_mech,+ = integral sum_j max(τ_j ω_j,0) dt (including suspension joints; F_j xdot_j for linear actuators). Negative work and recovered energy need separate declared treatment; summing signed work can implicitly assume perfect regeneration. At the measured electrical boundary use E_elec = integral V I dt, with actual channel coverage. For total battery energy, add avionics, thermal, communication, and other hotel power only if these were excluded by the measurement. Do not add them twice.

For a steady complete gait cycle returning to the same relative configuration, a mechanical energy balance gives shaft work = useful external-load work + gravitational potential increase + irreversible losses (with kinetic/elastic storage changes zero only if periodic). In uniform uphill travel the useful normalized components are F_external/W and sin(θ). At wheel level gross thrust, net drawbar pull, and motion resistance are different: F_drawbar = F_gross − R on level terrain under the chosen conventions. A measured net force does not determine shaft torque or soil dissipation.

Locking half the wheels at a time does not establish that full-cycle motion-resistance energy halves: both groups eventually advance, load distribution changes, and suspension actuators do work. An ideal stationary anchor provides force at zero mechanical work, but powered holding may still consume electrical energy. Thus f_r/2 may be a phase-level resistance estimate under specific loading, never a universal full-cycle energy law.

## Other screened primary sources

- Wettergreen et al., *Field Experiments in Mobility and Navigation with a Lunar Rover Prototype* (2009), Table 3, p. 6: electrical/locomotion power comparison is between wheel types and soil depth, not paired rolling/inching energy. Do not treat it as direct validation. Author PDF: https://publications.ri.cmu.edu/storage/publications/pub_files/2009/7/scarab_fsr.pdf
- Pérez del Pulgar et al., “Choosing the Best Locomotion Mode in Reconfigurable Rovers,” *Electronics* 8(7), 818 (2019), DOI https://doi.org/10.3390/electronics8070818: primary modeling/simulation paper, not independent physical energy validation. Its conditional mode-selection result is contextual only.
- Azkarate et al., “First Experimental Investigations on Wheel-Walking for Improving Triple-Bogie Rover Locomotion Performances,” ASTRA 2015: independent physical traction/gradeability evidence; author-institute page does not establish an electrical-energy dataset. https://www.dfki.de/en/web/research/projects-and-publications/publication/7825
- NASA/JPL FY2022 poster R22016, Fig. 5, presents preliminary normalized energy comparisons on flat and 20° slopes in GRC-1. Prefer a full paper with complete method over this preliminary poster for numerical calibration. https://www.jpl.nasa.gov/site/research/media/posters/2022/R22016p.pdf

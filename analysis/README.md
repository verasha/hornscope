# Analysis

| File | What it shows |
|---|---|
| `hi_profiles_mw1-4.png` | HI profiles of mw1–mw4 against ground1, in velocity, with a linear baseline removed |
| `rotation_curve.png` | Tangent-point rotation speeds from mw1–mw4 (filled = valid, hollow = method assumptions not met) |
| `rotation_curve_mw1_profile.png` | mw1 profile with the tangent-velocity range marked, next to the rotation-curve point |
| `expected_HI_profiles.png` | LAB-survey profiles simulated with Virgo for a 20° beam at l = 30°, 80° and 140° |
| `ground_cal-cold.*` | Early test plot (ground vs cold sky), not used in the results |

## Method

- Profiles: target ÷ ground reference, linear baseline fitted at 1419.4–1419.9 and 1420.75–1420.95 MHz, median filter (9 channels) and boxcar smoothing (25 channels). The DC spike (1420.0 ± 0.04 MHz) is masked.
- Velocities are corrected to the LSR (barycentric correction plus solar motion from Schönrich et al. 2010).
- Tangent-point method: R = R₀ sin l and V = v_max + V₀ sin l, with R₀ = 8.2 kpc and V₀ = 230 km/s. v_max is taken where the profile tail drops below 3σ. For mw1, the edge falls inside the DC-spike gap, giving v_max = 62–88 km/s.
- Error bars: horizontal = ±10° beam half-width in l; vertical = range of v_max plus an estimated ±10 km/s systematic.

## Results

| | l | R (kpc) | V (km/s) | Valid? |
|---|---|---|---|---|
| mw1 | 53.4° | 6.6 | 247–272 | yes |
| mw2 | 39.3° | 5.2 | 143–161 | no: b = −10°, misses the tangent gas |
| mw3 | 94.7° | 8.2 | ≈ 245 | no: l > 90°, no tangent point (the value is essentially V₀) |
| mw4 | 4.9° | 0.7 | 39–82 | no: Galactic bar region |

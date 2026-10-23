# Analysis

| File | What it shows |
|---|---|
| `hi_profiles_mw1-4.png` | HI profiles of mw1–mw4 against ground1, in velocity, with a linear baseline removed |
| `rotation_curve.png` | Tangent-point rotation speeds from mw1–mw4 (filled = usable, hollow = method assumptions not met) |
| `snr_comparison_mw1-4.png` | Per-channel vs smoothed S/N for mw1–mw4 |
| `rotation_curve_mw1_profile.png` | mw1 profile with the tangent-velocity range (inside the DC-spike gap) marked |
| `expected_HI_profiles.png` | LAB-survey profiles simulated with Virgo for a 20° beam at l = 30°, 80° and 140° |
| `ground_cal-cold.*` | Early test plot (ground vs cold sky), not used in the results |

## Method

- Profiles: target ÷ ground reference, linear baseline fitted at 1419.4–1419.9 and 1420.75–1420.95 MHz, median filter (9 channels) and boxcar smoothing (25 channels). The DC spike (1420.0 ± 0.04 MHz) is masked.
- Velocities are corrected to the LSR (barycentric correction plus solar motion from Schönrich et al. 2010).
- Noise (σ) is measured with a median-based (MAD) estimator in the clean region 1419.4–1419.9 MHz. Virgo's own S/N panel understates the signal about 10×, because its noise estimate includes the DC spike.
- S/N: mw1 ≈ 13, mw2 ≈ 12, mw3 ≈ 10, mw4 ≈ 14 per 1.2 kHz channel; ≈ 17–41 after smoothing to ~7 km/s (smoothing gains are limited by baseline ripple).
- Tangent-point method: R = R₀ sin l and V = v_max + V₀ sin l, with R₀ = 8.2 kpc and V₀ = 230 km/s. v_max is taken where the smoothed profile tail drops below 3σ. For mw1 and mw2 the tail is still well above 3σ where the DC-spike gap begins, so the edge lies inside the gap: v_max = 71–88 km/s (mw1) and 65–83 km/s (mw2).
- Error bars: horizontal = ±10° beam half-width in l; vertical = range of v_max plus an estimated ±10 km/s systematic.

## Results

| | l | R (kpc) | V (km/s) | Valid? |
|---|---|---|---|---|
| mw1 | 53.4° | 6.6 | 256–272 | yes |
| mw2 | 39.3° | 5.2 | 210–229 | yes, with larger uncertainty: centred at b = −10°, but the ±10° beam reaches the plane |
| mw3 | 94.7° | 8.2 | ≈ 245 | no: l > 90°, no tangent point (the value is essentially V₀) |
| mw4 | 4.9° | 0.7 | ≈ 38 | no: Galactic bar region |

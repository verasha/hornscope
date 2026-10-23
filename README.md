# Hornscope

A pyramidal horn radio telescope for observing the 21 cm (1420.4 MHz) neutral-hydrogen (HI) line from the Milky Way, built as a course project for **PC5214 Experimental Physics Course in NUS**.

The horn follows the [DSPIRA](https://wvurail.org/dspira-lessons/) design, and our build and method are modelled on Bhattacharjee, Grover & Arumugam (2026), [*Observations of the 21 cm HI Line from the Milky Way galaxy using Pyramidal Horn Radio Telescope*](https://arxiv.org/abs/2512.19262). Data is recorded and plotted with [Virgo](https://github.com/0xCoto/Virgo).

## Results so far

On **2026-10-23** we detected Galactic HI in four 5-minute pointings and derived a first rotation-curve point.

| Recording | Galactic l, b | HI peak velocity | Notes |
|---|---|---|---|
| mw1 | 53°, +0° | +8 km/s, tail to the DC gap (~+71–88) | S/N ≈ 13 per channel; gives **V ≈ 256–272 km/s at R ≈ 6.6 kpc** |
| mw2 | 39°, −10° | +16 km/s, tail to the DC gap (~+65–83) | S/N ≈ 12 per channel; gives **V ≈ 210–229 km/s at R ≈ 5.2 kpc** |
| mw3 | 95°, +3° | −5 km/s, tail to ~−50 | S/N ≈ 10 per channel; outer Galaxy, negative velocities as expected |
| mw4 | 5°, −4° | +13 km/s | S/N ≈ 14 per channel; toward the Galactic centre |

![Rotation curve](analysis/rotation_curve.png)

mw1 and mw2 give rotation-curve points (filled). mw2 is centred 10° below the plane, but its ~20° beam still reaches the plane, so it carries a larger uncertainty. mw3 (l > 90°, no tangent point) and mw4 (Galactic bar region) don't satisfy the tangent-point method's assumptions and are shown for comparison only (hollow). For both mw1 and mw2 the tangent edge falls inside the gap left by the SDR's DC spike, which sets the size of the vertical error bars. See [`analysis/`](analysis/) for details.

## Hardware

| Component | Details |
|---|---|
| Horn | DSPIRA pyramidal geometry; acrylic sheets lined with aluminium foil |
| Waveguide and parts | 3D printed, conductively lined. Models go in [`hardware/3d-prints/`](hardware/3d-prints/) |
| LNA | Nooelec, powered from a USB power bank |
| SDR | Ettus USRP **B200mini-i** (UHD driver) |
| Computer | MacBook running radioconda (GNU Radio, UHD, Virgo) |
| Pointing | Manual; azimuth and altitude recorded for each observation |

Signal chain: **horn → probe → LNA → B200mini (RX2 port) → laptop**

For comparison, the reference horn in the paper has a 75 × 60 cm aperture, 18.5 dBi gain and a ~20° beam at 1420 MHz.

## Repository layout

| Path | Contents |
|---|---|
| [`observations/`](observations/) | Raw recordings (`.dat`, `.header`) with Virgo's plots and CSVs, plus the session log |
| [`analysis/`](analysis/) | Profile comparisons, expected profiles and rotation-curve plots |
| [`tools/observe.py`](tools/observe.py) | Helper for re-plotting and comparing recordings |
| [`hardware/3d-prints/`](hardware/3d-prints/) | 3D-printed part models |

## References

- K. Bhattacharjee, H. Grover, P. Arumugam, *Observations of the 21 cm HI Line from the Milky Way galaxy using Pyramidal Horn Radio Telescope*, J. Astrophys. Astron. 47, 75 (2026). [arXiv:2512.19262](https://arxiv.org/abs/2512.19262)
- DSPIRA: Digital Signal Processing in Radio Astronomy, WVU / NRAO. [Lessons](https://wvurail.org/dspira-lessons/)
- A. Spanakis-Misirlis, [Virgo: an easy-to-use spectrometer and radiometer for radio astronomy](https://github.com/0xCoto/Virgo)
- This repository started as a fork of [WVURAIL/gr-radio_astro](https://github.com/WVURAIL/gr-radio_astro); the GNU Radio code has since been removed.

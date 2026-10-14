# Hornscope

A low-cost pyramidal horn radio telescope for observing the 21 cm (1420.4 MHz) neutral-hydrogen line from the Milky Way, built as a course project for **PC5214**.

The telescope follows the [DSPIRA](https://wvurail.org/dspira-lessons/) horn design, and our build and observing plan are modelled on Bhattacharjee, Grover & Arumugam (2026), [*Observations of the 21 cm HI Line from the Milky Way galaxy using Pyramidal Horn Radio Telescope*](https://arxiv.org/abs/2512.19262). The software is a fork of [WVURAIL/gr-radio_astro](https://github.com/WVURAIL/gr-radio_astro), which provides GNU Radio blocks and flowgraphs for radio astronomy.

## Goals

1. Detect Galactic HI emission at 1420.4 MHz.
2. Run meridian drift scans at several elevations and build an HI sky map.
3. Derive a Galactic rotation curve using the tangent-point method.
4. Trace spiral-arm features from the HI line profiles.

## Project status

| Component | Status |
|---|---|
| Horn antenna | ✅ Built: acrylic body lined with aluminium foil |
| Waveguide and other parts | ✅ 3D printed |
| Feed probe (quarter-wave monopole) | ⏳ To do |
| Mount (elevation adjustment) | ⏳ To do |
| RF chain (LNA, filter, SDR) | ⏳ To do |
| GNU Radio flowgraph and data logging | ⏳ To do |
| First light | ⏳ To do |
| Calibration, sky map, rotation curve | ⏳ To do |

## Design

### Horn and feed

Our horn uses the DSPIRA pyramidal geometry. The reference build in the paper uses laser-cut 1 mm stainless-steel petals lined with aluminium foil tape. **We use acrylic sheets lined with aluminium foil instead.** The reference waveguide is a 1-gallon rectangular paint-thinner can. **Ours is 3D printed and conductively lined.** The models for it will go in [`hardware/3d-prints/`](hardware/3d-prints/).

For comparison, here are the figures for the reference horn (from the paper, not measured on ours):

| Parameter | Reference value |
|---|---|
| Aperture | 75 cm × 60 cm |
| Waveguide (can) | 16.8 × 10.2 × 24.1 cm |
| Probe | N-type panel connector + 5.25 cm copper wire, 5.25 cm from the back wall |
| Gain at 1420 MHz (simulated) | 18.5 dBi |
| Beam FWHM | 18.1° (E-plane), 21.3° (H-plane) |

### Planned signal chain

We plan to follow the reference signal chain. Components may change depending on what we can get.

```
Horn → probe → LNA (e.g. Nooelec SAWbird+ H1) → [2nd amplifier] → band-pass filter (~1350–1650 MHz)
     → SDR (HackRF One) tuned near 1420 MHz → computer running GNU Radio
```

### Software

We'll use the GNU Radio blocks from this repository (`radio_astro`), plus a spectrometer flowgraph. The data path is stream-to-vector → polyphase filter bank → FFT → |X|² → integration → CSV/HDF5 logging. A good starting point is [`examples/DSPIRA/spectrometer_w_cal.grc`](examples/DSPIRA/spectrometer_w_cal.grc).

### Observing and calibration plan

- **Drift scans:** point the horn along the local meridian at a fixed elevation, let the sky drift through the beam for 24 h, then step the elevation.
- **Calibration:** use a hot load (horn pointed at the ground, ~300 K) and a cold load (high-Galactic-latitude sky, ~10 K) for a Y-factor temperature scale. Cross-check intensities against the HI4PI survey.
- **Frequency drift:** correct the SDR oscillator drift using the line-peak offsets.

## Repository layout

| Path | Contents |
|---|---|
| `hardware/3d-prints/` | Models for the 3D-printed parts (waveguide, etc.) |
| `examples/DSPIRA/` | DSPIRA example flowgraphs (spectrometer, interferometer, …) |
| `grc/`, `python/`, `lib/`, `include/` | Source code for the `radio_astro` GNU Radio module (from upstream) |
| `docs/` | Upstream documentation |

## References

- K. Bhattacharjee, H. Grover, P. Arumugam, *Observations of the 21 cm HI Line from the Milky Way galaxy using Pyramidal Horn Radio Telescope*, J. Astrophys. Astron. 47, 75 (2026). [arXiv:2512.19262](https://arxiv.org/abs/2512.19262)
- DSPIRA: Digital Signal Processing in Radio Astronomy, WVU / NRAO. [Lessons](https://wvurail.org/dspira-lessons/)
- [WVURAIL/gr-radio_astro](https://github.com/WVURAIL/gr-radio_astro)

## Credits

The software is built on **gr-radio_astro** by the WVU Radio Astronomy Instrumentation Lab (WVURAIL), including Dr. Glen Langston's NSF Integrate and Detect software and the DSPIRA program's material. See [LICENSE](LICENSE), [NOTICE](NOTICE) and [CITATION.cff](CITATION.cff).



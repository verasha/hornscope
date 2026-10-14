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
     → SDR (e.g. HackRF One / RTL-SDR / Airspy) tuned near 1420 MHz → computer running GNU Radio
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

---

# Upstream: gr-radio_astro

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14583457.svg)](https://doi.org/10.5281/zenodo.14583457)


This package provides GNU Radio OOT modules and `grc` flowgraphs that facilitate radio astronomy observations with software-defined radio devices.

Historical branches were reviewed and consolidated in 2026. See
[`BRANCH_HISTORY.md`](docs/BRANCH_HISTORY.md) for the disposition of all 25 branch
tips and for the migration record from the archived
[`gr-dspira`](https://github.com/WVURAIL/gr-dspira) prototypes.

There are two flavors of this projects:

1. NSF Integrate and Detect softwares that allow for HI measurements and also event detections from cosmic ray detections, developed by Dr. Glen Langston. See [here](https://github.com/WVURAIL/gr-radio_astro/wiki/Nsf-gr-radio_astro) and the [lightwork memo series](https://wvurail.org/lightwork/) for more details. 
2. DSPIRA software developed for and by High School Teachers part of the [NSF funded RET program called Digital Signal Processing in Radio Astronomy (DSPIRA)](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1611114) at WVU university from the summers of 2017 to 2021. For more details visit the [webpage](https://wvurail.org/dspira-lessons/about/) and the companion website called [dspira-lessons](https://wvurail.org/dspira-lessons/) that has lessons, guides and more material help one to use radio astronomy in a high school classroom. This material is designed by the High School teachers part of this program. 

# Installing from Source

1. Install GNUradio
2. Install gnuradio external python dependencies and SDR drivers by typing the following and hit enter:
   ```
      sudo apt install gnuradio gr-osmosdr airspy python3-h5py python3-ephem git cmake liborc-0.4-dev -y
   ```
3. To clone the repository:
```
git clone https://github.com/verasha/hornscope.git
```
4. Switch to the repository directory: `cd hornscope`
5. Make a build directory: `mkdir build`, and then move to it: `cd build`  
6. Then run the following in the build directory:
      ```
      cmake ..
      sudo make
      sudo make install
      ```
**Additional Steps for setting the proper Python environment:**
   
7. Edit your `.bashrc` file and add this to the bottom to set Python path: `export PYTHONPATH=/usr/local/lib/python3/dist-packages:/usr/local/lib/python3.10/dist-packages:$PYTHONPATH`
8. Additionally you can create appropriate symbolic links
   1.  Check which python is the installed version of GNURadio by opening  `gnuradio-companion` in a terminal window and click on `Help --> About` and noting the python version on the dialog box that opens.  
   2.  Go to the following by typing: `cd /usr/local/lib/python3.10/dist-packages` or `cd /usr/local/lib/python3.9/dist-packages` for the appropriate python version. 
   3.  Type `ln -s /usr/local/lib/python3/dist-packages/radio_astro`   


# Running from a bootable USB Flash Drive with preinstalled software:

[Instructions to set up a persistant USB flash with preinstalled software drive are here](https://wvurail.org//dspira-lessons/Install_Ubuntu_spectrometer_onFlashdrive)

---- 
TODO: Update for 3.10 below the instructions are for 3.8

# Installing on a Raspberry Pi. 

## Supported Raspberry Pi Devices

*All devices must have RAM greater than 4GB*
1. Raspberry Pi 4 Model B
2. Raspberry Pi 400


## Installing Ubuntu image with radio astronomy preinstalled  on a Raspberry Pi
This image requires a minimum of 16GB of space on the SD card. 
1. Download the image [here](https://drive.google.com/file/d/1KzfgMEwgwTTZUaCeNR5kRgLj9MfMKyAh/view?usp=sharing)
2. Unzip the `.zip` file.
3. Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to install this image.
   1. Insert SD card into your card reader on your computer
   2. Open Raspberry Pi Imager.
   3. Click `Choose OS`, and choose `Use Custom`. 
   4. Select the correct image file downloaded in step 1 and 2 from your system.
   5. Click `Choose storage` and select your inserted SD card.
   6. Click write. 
   7. See the current [Raspberry Pi installation documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system) and this [video](https://www.youtube.com/watch?v=ntaXWS8Lk34).
4. Insert SD card to Raspberry Pi and power it up.
5. The default user name is `pi`, with password `raspberry`. Change the password after first boot. 

# Hornscope Observing Guide

How to record hydrogen-line spectra with the B200mini and [Virgo](https://github.com/0xCoto/Virgo).

## 1. Setup

1. Connect the signal chain: **horn → LNA (RF IN) → LNA (RF OUT) → B200mini RX2 port**.
2. Power the LNA from the power bank. **Check that its LED is on and stays on.** An unpowered LNA blocks the signal completely.
3. Plug the B200mini **directly** into the Mac, not through a USB hub, and check that it's detected:
   ```bash
   uhd_find_devices
   ```
4. Close gqrx and GNU Radio Companion, since only one program can use the SDR.
5. Go to the data folder:
   ```bash
   cd ~/gr-radio_astro/observations
   ```
6. Let the LNA warm up for about **15 minutes** before recording.

## 2. Ground reference (2 min)

Point the horn **at the ground**. Number each reference: `ground1`, `ground2`, …
```bash
virgo -da "uhd,type=b200" -rf 30 -if 0 -bb 0 -f 1420e6 -b 2.4e6 -c 2048 -t 1 -d 120 -r 1420.405751e6 -o ground1.dat -p ground1.png -S ground1.csv
```
Record a new one **every 45–60 minutes**, and whenever you change the gain or any hardware.

## 3. Observation (5 min)

Point the horn at the Milky Way and use a new name each time (`mw1`, `mw2`, …):
```bash
virgo -da "uhd,type=b200" -rf 30 -if 0 -bb 0 -f 1420e6 -b 2.4e6 -c 2048 -t 1 -d 300 -r 1420.405751e6 -o mw1.dat -C ground1.dat -p mw1.png -S mw1.csv
```
**Write down the start time, azimuth and altitude** for each recording in [`observations/LOG.md`](observations/LOG.md).

**Pointing tips**
- Stay **on the Galactic plane** (b ≈ 0°). The hydrogen is in a thin disk, and 10° off the plane the signal is much weaker.
- For the rotation curve, use **0° < l < 90°** (inner Galaxy), e.g. l = 20, 30, …, 80°.
- Keep well away from the **Sun**, which is very bright at 1420 MHz.

## 4. Check the results

```bash
open mw1.png
```
In the **Calibrated Spectrum** panel, the hydrogen line is a **broad bump** (hundreds of kHz wide) near the red line at 1420.4 MHz. Thin needle-like spikes are interference or the SDR's DC spike at 1420.0 MHz.

Compare total power. The sky should read **lower** than the ground:
```bash
cd ~/gr-radio_astro && python tools/observe.py compare ground1 mw1
```

Re-plot a recording against a different reference without re-recording:
```bash
python tools/observe.py plot mw1 --cal ground2
```

## Option reference

| Option | Meaning |
|---|---|
| `-da "uhd,type=b200"` | use the B200mini |
| `-rf 30` | gain in dB (keep the same for references and targets) |
| `-f 1420e6 -b 2.4e6` | centre frequency and bandwidth: 1418.8–1421.2 MHz |
| `-c 2048 -t 1` | 2048 channels, one spectrum per second |
| `-d 300` | duration in seconds |
| `-r 1420.405751e6` | HI rest frequency (adds the velocity axis) |
| `-o / -p / -S` | data / plot / CSV filenames |
| `-C ground1.dat` | calibrate against a reference recording |
| `-n 5` | median filter to suppress narrow interference |

**Tip:** the DC spike at 1420.0 MHz sits at about +85 km/s, which can hide the tangent-point edge for inner-Galaxy targets. Tuning to `-f 1420.9e6` moves it to about −105 km/s. Record the ground reference at the same frequency.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No devices found for type: b200` | Replug the B200mini directly into the Mac and run `uhd_find_devices` |
| Ground and sky give the same power | LNA unpowered (check the LED), wrong B200mini port (must be RX2), LNA backwards, or a bad SMA connector |
| Only a narrow slice around 1420.0 MHz has signal | Virgo's bandwidth bug (see below) |
| Plotting crashes with `'GrouperView' object has no attribute 'join'` | Virgo's matplotlib bug (see below) |
| A sharp spike near 1420.4 MHz | A test transmitter (e.g. `hackrf_transfer`) is running nearby. Stop it. |

**Virgo patches.** Virgo 3.8.2 has two bugs that were patched in the radioconda install (originals saved as `.orig` next to each file). If Virgo is ever reinstalled, apply them again:
```bash
V=$(python -c "import virgo,os;print(os.path.dirname(virgo.__file__))")
sed -i '' 's/self.osmosdr_source_0.set_bandwidth(0, 0)/self.osmosdr_source_0.set_bandwidth(bandwidth, 0)/' $V/run_wola.py $V/run_ftf.py
sed -i '' 's/ax5.get_shared_x_axes().join(ax5, ax4)/ax5.sharex(ax4)/' $V/virgo.py
```

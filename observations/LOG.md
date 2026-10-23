# Observation log

All recordings: Ettus B200mini-i, `-rf 30` unless noted, 2.4 MHz bandwidth centred on 1420.0 MHz, 2048 channels, 1 s spectra. Times are local (UTC+8). Azimuth is measured from north.

## 2026-10-23

| Recording | Start | Az / Alt | Target | Reference | Notes |
|---|---|---|---|---|---|
| ground1 | 15:27 | ground | ground reference | | |
| mw1 | 15:36 | 65° / 45° | l = 53°, b = 0° (Sagitta/Aquila) | ground1 | clear HI detection |
| mw2 | 15:48 | 90° / 48° | l = 39°, b = −10° (Aquila) | ground1 | weak; off the plane |
| mw3 | 16:05 | 33° / 17° | l = 95°, b = +3° (Cygnus) | ground1 | outer Galaxy |
| mw4 | 16:25 | 160° / 60° | l = 5°, b = −4° (Sagittarius) | ground1 | strongest peak |

Galactic coordinates computed assuming the site is NUS, Singapore (1.30° N, 103.78° E).

### Test recordings (not for analysis)

| Recording | Notes |
|---|---|
| `cold`, `ground` | Earlier tests. LNA unpowered for some of them, and `ground` (`-rf 30`) and `cold` (`-rf 50`) use different gains |
| `target1` | Contains the `hackrf_transfer` test tone at 1420.4 MHz |
| `2026-10-16_*_spectrum.csv` | DSPIRA flowgraph test captures (HackRF) |

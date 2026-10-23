#!/usr/bin/env python
"""
Hornscope hydrogen-line observation helper, built on Virgo
(https://github.com/0xCoto/Virgo).

Record a spectrum:
    python tools/observe.py record --label cold --minutes 2
    python tools/observe.py record --label cygnus --minutes 5 --az 45 --alt 60

Plot it (optionally calibrated against an "off" observation of empty sky):
    python tools/observe.py plot cygnus
    python tools/observe.py plot cygnus --cal cold

Files are written to observations/<label>.dat / .header / .png / .csv.
"""
import argparse
import os
import sys

import matplotlib
import matplotlib.cbook

import virgo

# Virgo 3.8 calls Grouper.join() on shared axes, which matplotlib >= 3.8
# removed. Restore it as Axes.sharex() so plotting works.
if not hasattr(matplotlib.cbook.GrouperView, "join"):
    def _join(self, a, *others):
        for b in others:
            try:
                a.sharex(b)
            except ValueError:  # already shared
                pass
    matplotlib.cbook.GrouperView.join = _join

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "observations")

HI_REST = 1420.405751e6  # Hz

# Per-SDR defaults. The centre is 0.4 MHz below the HI line so the
# SDR's DC spike doesn't land on it.
SDRS = {
    "b200":   dict(dev_args="uhd,type=b200", rf_gain=50, if_gain=0,  bb_gain=0),
    "hackrf": dict(dev_args="hackrf=0",      rf_gain=0,  if_gain=24, bb_gain=24),
    "rtlsdr": dict(dev_args="rtl=0",         rf_gain=40, if_gain=0,  bb_gain=0),
}


def path(label, ext):
    return os.path.join(OUT_DIR, f"{label}.{ext}")


def record(args):
    sdr = dict(SDRS[args.sdr])
    if args.gain is not None:
        sdr["rf_gain"] = args.gain
    az_alt = f"{args.az} {args.alt}" if args.az is not None and args.alt is not None else ""

    obs = dict(
        **sdr,
        frequency=args.freq,
        bandwidth=args.bandwidth,
        channels=args.channels,
        t_sample=args.t_sample,
        duration=args.minutes * 60,
        loc=args.loc,
        ra_dec="",
        az_alt=az_alt,
    )
    os.makedirs(OUT_DIR, exist_ok=True)
    dat = path(args.label, "dat")
    print(f"Recording '{args.label}' for {args.minutes} min with {args.sdr} -> {dat}")
    virgo.observe(obs_parameters=obs, obs_file=dat)
    print("Done. Plot it with:")
    print(f"    python tools/observe.py plot {args.label}" + ("" if args.label == "cold" else " --cal cold"))


def plot(args):
    dat = path(args.label, "dat")
    if not os.path.exists(dat):
        sys.exit(f"No observation found at {dat}")
    cal = path(args.cal, "dat") if args.cal else ""
    if cal and not os.path.exists(cal):
        sys.exit(f"No calibration observation found at {cal}")

    suffix = f"_cal-{args.cal}" if args.cal else ""
    png = path(args.label + suffix, "png")
    csv = path(args.label + suffix, "csv")

    # Read <label>.header ourselves: Virgo's own header parser crashes on
    # the empty loc= line written by the `virgo` command-line tool.
    header = dict(line.strip().split("=", 1) for line in open(path(args.label, "header")) if "=" in line)
    obs_parameters = dict(
        frequency=float(header["frequency"]),
        bandwidth=float(header["bandwidth"]),
        channels=int(header["channels"]),
        t_sample=float(header["t_sample"]),
        loc=tuple(map(float, header["loc"].split())) if header.get("loc", "").strip() else "",
        ra_dec="",
        az_alt=tuple(map(float, header["az_alt"].split())) if header.get("az_alt", "").strip() else "",
    )
    if args.vlsr and not (obs_parameters["loc"] and obs_parameters["az_alt"]):
        sys.exit("--vlsr needs the recording to have been made with --loc and --az/--alt")
    if args.vlsr:
        obs_parameters = ""  # let Virgo read the header so it also gets the MJD timestamp

    virgo.plot(
        obs_parameters=obs_parameters,
        obs_file=dat,
        cal_file=cal,
        f_rest=HI_REST,
        n=args.median,
        m=args.median,
        dB=not cal,
        vlsr=args.vlsr,
        meta=False,
        slope_correction=bool(cal),
        spectra_csv=csv,
        plot_file=png,
    )
    print(f"Saved plot: {png}")
    print(f"Saved data: {csv}")


def compare(args):
    import numpy as np

    print(f"{'label':<16}{'power':>10}{'vs first':>10}   drift (start -> end)")
    first = None
    for label in args.labels:
        dat, header = path(label, "dat"), path(label, "header")
        if not os.path.exists(dat):
            print(f"{label:<16}  missing ({dat})")
            continue
        params = dict(line.strip().split("=", 1) for line in open(header) if "=" in line)
        channels = int(params["channels"])
        frequency = float(params["frequency"])
        bandwidth = float(params["bandwidth"])
        waterfall = np.fromfile(dat, dtype="float32").reshape(-1, channels)[3:]

        # Median over the band (skipping the DC spike and edges) is robust
        # against narrow interference spikes.
        f = np.linspace(frequency - bandwidth / 2, frequency + bandwidth / 2, channels, endpoint=False)
        band = (np.abs(f - frequency) > 50e3) & (np.abs(f - frequency) < 0.42 * bandwidth)
        per_row = np.median(waterfall[:, band], axis=1)
        power = np.median(per_row)
        first = first or power
        n = max(1, len(per_row) // 10)
        print(f"{label:<16}{power:>10.4g}{power / first:>10.2f}   "
              f"{per_row[:n].mean():.4g} -> {per_row[-n:].mean():.4g}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("record", help="record an observation")
    r.add_argument("--label", required=True, help="name for this observation, e.g. cold, ground, cygnus")
    r.add_argument("--minutes", type=float, default=2)
    r.add_argument("--sdr", choices=SDRS, default="b200")
    r.add_argument("--gain", type=float, help="override RF gain (dB)")
    r.add_argument("--freq", type=float, default=1420.0e6, help="centre frequency (Hz)")
    r.add_argument("--bandwidth", type=float, default=2.4e6, help="sample rate / bandwidth (Hz)")
    r.add_argument("--channels", type=int, default=2048, help="FFT size")
    r.add_argument("--t-sample", type=float, default=1.0, help="seconds per averaged spectrum")
    r.add_argument("--az", type=float, help="azimuth of the horn (deg)")
    r.add_argument("--alt", type=float, help="elevation of the horn (deg)")
    r.add_argument("--loc", default="0 0 0",
                   help='"latitude longitude elevation_m" of the telescope (needed for --vlsr)')
    r.set_defaults(func=record)

    q = sub.add_parser("plot", help="plot an observation")
    q.add_argument("label")
    q.add_argument("--cal", help="label of an empty-sky observation to calibrate against")
    q.add_argument("--median", type=int, default=0, help="median filter width for RFI (e.g. 5)")
    q.add_argument("--vlsr", action="store_true", help="convert to LSR velocity (needs --loc/--az/--alt when recording)")
    q.set_defaults(func=plot)

    c = sub.add_parser("compare", help="compare total power of recordings, e.g. ground vs sky")
    c.add_argument("labels", nargs="+")
    c.set_defaults(func=compare)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

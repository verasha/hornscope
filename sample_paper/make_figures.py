#!/usr/bin/env python
"""
Regenerate every figure and number used in sample_paper/main.tex from the raw
Virgo recordings in ../observations and the literature tables in data/.

    python sample_paper/make_figures.py

Outputs: figures/*.pdf and results.json (the numbers quoted in the paper).
"""
import csv
import json
import os
import warnings

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse
from scipy.ndimage import median_filter, uniform_filter1d
from scipy.optimize import curve_fit

from astropy.utils import iers
iers.conf.auto_download = False   # work offline; UT1 error is negligible here
iers.conf.auto_max_age = None
import astropy.units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
OBS = os.path.join(HERE, "..", "observations")
DATA = os.path.join(HERE, "data")
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)


def save(fig, name):
    """Save as PDF (for LaTeX) and PNG (for quick viewing, e.g. on GitHub)."""
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=200)
    plt.close(fig)

# --- constants -------------------------------------------------------------
F0 = 1420.405751e6           # HI rest frequency (Hz)
C = 299792.458               # km/s
R0, V0 = 8.2, 230.0          # Galactocentric radius and circular speed of the Sun
SITE = EarthLocation.from_geodetic(103.776 * u.deg, 1.297 * u.deg, 20 * u.m)  # NUS
NCHAN = 2048
f = np.linspace(1418.8e6, 1421.2e6, NCHAN, endpoint=False)
v_topo = C * (F0 - f) / F0
DC = np.abs(f - 1420.0e6) < 40e3                     # SDR DC spike
BASE = ((f > 1419.4e6) & (f < 1419.9e6)) | ((f > 1420.75e6) & (f < 1420.95e6))
NOISE = (f > 1419.4e6) & (f < 1419.9e6)              # clean, line-free region
COLORS = {"mw1": "C3", "mw2": "C1", "mw3": "C2", "mw4": "C4"}

plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.labelsize": 9,
                     "legend.fontsize": 7.5, "xtick.direction": "in", "ytick.direction": "in"})


def mad(a):
    return 1.4826 * np.nanmedian(np.abs(a - np.nanmedian(a)))


def load(label):
    w = np.fromfile(os.path.join(OBS, label + ".dat"), dtype="float32").reshape(-1, NCHAN)[3:]
    head = dict(l.strip().split("=", 1) for l in open(os.path.join(OBS, label + ".header")) if "=" in l)
    return w, head


ref, _ = load("ground1")
ref_mean = ref.mean(0)


def profile(label):
    """Fractional excess over the ground reference with a linear baseline removed."""
    w, head = load(label)
    r = w.mean(0) / ref_mean
    ok = BASE & ~DC
    ok &= np.abs(r - np.median(r[ok])) < 5 * mad(r[ok])
    x = r / np.polyval(np.polyfit(f[ok] - 1420e6, r[ok], 1), f - 1420e6) - 1
    return x, w, head


def pointing(label, az, alt):
    _, head = load(label)
    t = Time(float(head["mjd"]) + float(head["duration"]) / 2 / 86400, format="mjd")
    aa = SkyCoord(az=az * u.deg, alt=alt * u.deg, frame=AltAz(obstime=t, location=SITE))
    g = aa.galactic
    icrs = SkyCoord(ra=aa.icrs.ra, dec=aa.icrs.dec, frame="icrs")
    vbary = icrs.radial_velocity_correction(kind="barycentric", obstime=t, location=SITE).to(u.km / u.s).value
    lr, br = np.radians(g.l.deg), np.radians(g.b.deg)
    vsun = 11.1 * np.cos(lr) * np.cos(br) + 12.24 * np.sin(lr) * np.cos(br) + 7.25 * np.sin(br)  # Schoenrich+2010
    return g.l.deg, g.b.deg, vbary + vsun, t


def gsum(v, *p):
    y = np.zeros_like(v)
    for k in range(0, len(p), 3):
        y += p[k] * np.exp(-0.5 * ((v - p[k + 1]) / p[k + 2]) ** 2)
    return y


def decompose(x, v, sig):
    """Fit 1-4 Gaussians; keep the model preferred by BIC (all components retained)."""
    m = (v > -130) & (v < 150) & ~DC & (f < 1420.95e6)
    vv, yy = v[m], median_filter(x, 5)[m]
    best = None
    for n in (1, 2, 3, 4):
        centres = np.linspace(-40, 70, n) if n > 1 else [vv[np.argmax(yy)]]
        p0 = sum(([max(yy.max() / 2, 1e-3), c, 15] for c in centres), [])
        try:
            p, cov = curve_fit(gsum, vv, yy, p0=p0, bounds=([0, -130, 3] * n, [1, 150, 60] * n),
                               sigma=np.full_like(yy, sig), maxfev=20000)
        except RuntimeError:
            continue
        bic = np.sum(((yy - gsum(vv, *p)) / sig) ** 2) + len(p) * np.log(len(yy))
        if best is None or bic < best[0] - 10:
            best = (bic, p, np.sqrt(np.diag(cov)))
    _, p, pe = best
    comps = [dict(amp=p[k], v=p[k + 1], sigma=p[k + 2], ev=pe[k + 1]) for k in range(0, len(p), 3)]
    return sorted(comps, key=lambda c: c["v"])


def kinematic_distances(l, v):
    s, co = np.sin(np.radians(l)), np.cos(np.radians(l))
    den = V0 * s + v
    if den > 0:
        R = R0 * V0 * s / den
        if R >= R0 * abs(s):
            root = np.sqrt(R ** 2 - (R0 * s) ** 2)
            ds = [d for d in (R0 * co - root, R0 * co + root) if d > 0]
            if ds:
                return ds, "ok"
    return ([R0 * co], "tangent") if co > 0 else ([0.0], "none")


# --- analysis ----------------------------------------------------------------
point = {r["label"]: r for r in csv.DictReader(open(os.path.join(DATA, "pointings.csv")))}
results = {}
for lab in ["mw1", "mw2", "mw3", "mw4"]:
    az, alt = float(point[lab]["azimuth_deg"]), float(point[lab]["altitude_deg"])
    l, b, corr, t = pointing(lab, az, alt)
    x, w, head = profile(lab)
    v = v_topo + corr                                        # LSR velocity
    d = (x[2:] - x[:-2]) / np.sqrt(2)
    sig_ch = mad(d[NOISE[1:-1]])                             # per-channel noise
    xs = uniform_filter1d(median_filter(x, 9), 25)
    xs[DC] = np.nan
    sig_sm = mad(xs[NOISE])                                  # smoothed (~7 km/s) noise
    win = (f > 1420.05e6) & (f < 1420.7e6)
    i = np.nanargmax(np.where(win, xs, np.nan))
    raw = x / sig_ch
    raw[DC] = np.nan
    # tangent (terminal) velocity: walk from the peak to higher velocity until < 3 sigma
    j = i
    while j > 1 and (DC[j - 1] or xs[j - 1] > 3 * sig_sm):
        j -= 1
    edge = v[j]
    gap_lo, gap_hi = v[DC].min(), v[DC].max()
    vmax = (gap_lo, max(edge, gap_hi)) if edge >= gap_hi - 1 else (edge, edge)
    s = np.sin(np.radians(l))
    results[lab] = dict(
        az=az, alt=alt, l=l, b=b, vlsr_corr=corr, utc=t.isot,
        peak_v=float(v[i]), peak_excess=float(xs[i]),
        snr_channel=float(np.nanmedian(raw[max(i - 5, 0):i + 6])), snr_smoothed=float(xs[i] / sig_sm),
        vmax=vmax, R=R0 * s if l < 90 else R0 * s,
        V=(vmax[0] + V0 * s, vmax[1] + V0 * s),
        components=decompose(x, v, sig_ch),
        _x=x, _xs=xs, _v=v, _raw=raw, _sig_sm=sig_sm,
    )
    w_all = w[:, BASE & ~DC]
    results[lab]["power_ratio"] = float(np.median(np.median(w_all, axis=1)) /
                                        np.median(np.median(ref[:, BASE & ~DC], axis=1)))

# --- Fig. 2: HI profiles with Gaussian components ------------------------------
fig, axs = plt.subplots(4, 1, figsize=(3.4, 6.2), sharex=True)
for ax, lab in zip(axs, results):
    r = results[lab]
    m = (f > 1419.4e6) & (f < 1420.95e6)
    ax.plot(r["_v"][m], r["_xs"][m] * 100, c=COLORS[lab], lw=1.2)
    for c in r["components"]:
        ax.plot(r["_v"][m], 100 * c["amp"] * np.exp(-0.5 * ((r["_v"][m] - c["v"]) / c["sigma"]) ** 2),
                c="k", lw=0.6, ls="--")
    ax.axvspan(r["_v"][DC].min(), r["_v"][DC].max(), color="0.85", zorder=0)
    ax.axvline(0, c="0.4", lw=0.5)
    ax.text(0.02, 0.85, f"{lab}  $\\ell$={r['l']:.0f}$^\\circ$, $b$={r['b']:+.0f}$^\\circ$",
            transform=ax.transAxes, fontsize=8)
    ax.set_ylabel("Excess (%)")
axs[-1].set_xlim(150, -120)
axs[-1].set_xlabel(r"$V_\mathrm{LSR}$ (km s$^{-1}$)")
fig.tight_layout(h_pad=0.2)
save(fig, "fig_profiles")

# --- Fig. 3: per-channel vs smoothed S/N for mw1 --------------------------------
r = results["mw1"]
fig, (a, b2) = plt.subplots(2, 1, figsize=(3.4, 3.6), sharex=True)
m = (f > 1419.4e6) & (f < 1420.95e6)
a.plot(f[m] / 1e6, r["_raw"][m], lw=0.4, c="C0")
a.set_ylabel("S/N per channel")
a.set_ylim(-5, 20)   # clip the narrow RFI spike at 1420.8 MHz
b2.plot(f[m] / 1e6, r["_xs"][m] / r["_sig_sm"], lw=1.2, c="C3")
b2.axhline(3, ls=":", c="0.5", lw=0.8)
b2.set_ylabel("S/N (smoothed)")
b2.set_xlabel("Frequency (MHz)")
for ax in (a, b2):
    ax.axvspan(1419.96, 1420.04, color="0.85", zorder=0)
    ax.axvspan(1419.4, 1419.9, color="C2", alpha=0.07, zorder=0)
    ax.axvline(F0 / 1e6, ls="--", c="r", lw=0.6)
b2.set_xlim(1419.4, 1420.95)
b2.set_xticks([1419.5, 1420.0, 1420.5])
b2.ticklabel_format(axis="x", useOffset=False)
fig.tight_layout(h_pad=0.2)
save(fig, "fig_snr")

# --- Fig. 4: rotation curve vs literature -------------------------------------
def readcsv(name):
    return list(csv.DictReader(open(os.path.join(DATA, name))))

bh = readcsv("bhattacharjee_2026_digitized.csv")
liu = readcsv("liu_chronopoulos_2008_table1.csv")
pol = readcsv("physicsopenlab_2020_table.csv")
fig, ax = plt.subplots(figsize=(3.4, 2.6))
ax.errorbar([float(q["R_kpc"]) for q in bh], [float(q["V_kms"]) for q in bh],
            yerr=[float(q["sigma_V_kms"]) for q in bh],
            xerr=[[float(q["sigma_R_lo_kpc"]) for q in bh], [float(q["sigma_R_hi_kpc"]) for q in bh]],
            fmt="o", c="tab:red", alpha=0.4, ms=3, capsize=1.5, lw=0.6, label="Bhattacharjee et al. (2026)")
ax.errorbar([float(q["R_kpc"]) for q in pol], [float(q["V_rot_kms"]) for q in pol], yerr=20,
            fmt="o", c="navy", alpha=0.5, ms=3, capsize=1.5, lw=0.6, label="PhysicsOpenLab (2020)")
liu_V = [float(q["V_rot_kms (=v_rec+220 sin l)"]) for q in liu]
ax.errorbar([float(q["R_kpc"]) for q in liu], liu_V, yerr=[float(q["sigma_v_kms"]) for q in liu],
            xerr=[float(q["sigma_R_kpc"]) for q in liu], fmt="o", c="tab:green", alpha=0.5, ms=3,
            capsize=1.5, lw=0.6, label="Liu & Chronopoulos (2008)")
for k, lab in enumerate(results):
    r = results[lab]
    l = r["l"]
    rr = r["R"]
    lo, hi = r["V"]
    vm = (lo + hi) / 2
    if l < 90:
        xe = [[rr - R0 * np.sin(np.radians(max(l - 10, 0)))], [R0 * np.sin(np.radians(min(l + 10, 90))) - rr]]
    else:
        xe = [[rr - R0 * np.sin(np.radians(l + 10))], [0]]
    ax.errorbar([rr], [vm], yerr=[[vm - lo + 10], [hi - vm + 10]], xerr=xe, fmt="*", ms=10, mfc="gold",
                mec="k", c="k", capsize=2.5, lw=1.0, zorder=6, label="This work" if k == 0 else None)
ax.set_xlim(0, 9)
ax.set_ylim(0, 290)
ax.set_xlabel(r"Galactocentric radius $R$ (kpc)")
ax.set_ylabel(r"$V(R)$ (km s$^{-1}$)")
ax.legend(loc="lower right", frameon=False)
fig.tight_layout()
save(fig, "fig_rotation")

# --- Fig. 5: HI components on the Galactic plane --------------------------------
fig, ax = plt.subplots(figsize=(3.4, 3.4))
arms = {"Scutum-Centaurus": (5.0, 27.6, 19.8, (-100, 130), "#c9a0dc"),
        "Sagittarius-Carina": (6.6, 25.6, 6.9, (-120, 110), "#9fd39f"),
        "Local": (8.4, 8.9, 12.8, (-30, 40), "#9ff5f5"),
        "Perseus": (9.9, 14.2, 9.4, (-120, 170), "#a9a9f5"),
        "Outer": (13.0, 18.6, 13.8, (-90, 120), "#ffd99a")}
for name, (Rr, br, psi, (b1, b2_), col) in arms.items():
    beta = np.radians(np.linspace(b1, b2_, 400))
    Rarm = Rr * np.exp(-(beta - np.radians(br)) * np.tan(np.radians(psi)))
    ax.plot(Rarm * np.sin(beta), Rarm * np.cos(beta), lw=4, alpha=0.5, c=col, solid_capstyle="round", label=name)
ax.add_patch(Ellipse((0, 0), 10, 2.6, angle=57, color="0.6", alpha=0.3))
ax.add_patch(Circle((0, 0), R0, fill=False, ls="--", lw=0.8, ec="#4444ee", alpha=0.8))
ax.plot([0], [R0], "*", c="b", ms=9, zorder=4)
ax.plot([0], [0], "+", c="k", ms=9, mew=1.5)
spiral_rows = []
for lab, r in results.items():
    l, b = r["l"], r["b"]
    sl, cl, cb = np.sin(np.radians(l)), np.cos(np.radians(l)), np.cos(np.radians(b))
    for c in r["components"]:
        ds, flag = kinematic_distances(l, c["v"])
        dv = np.hypot(c["ev"], 5.0)
        lo, _ = kinematic_distances(l, c["v"] - dv)
        hi, _ = kinematic_distances(l, c["v"] + dv)
        for k, d in enumerate(ds):
            far = len(ds) == 2 and k == 1
            cand = [q for q in lo + hi if len(ds) < 2 or ((q < R0 * cl) == (k == 0))] + [d]
            x, y = d * sl * cb, R0 - d * cl * cb
            xs_ = [q * sl * cb for q in (min(cand), max(cand))]
            ys_ = [R0 - q * cl * cb for q in (min(cand), max(cand))]
            mk = {"tangent": "s", "none": "D", "ok": "o"}[flag]
            ax.errorbar([x], [y], xerr=[[max(x - min(xs_), 0)], [max(max(xs_) - x, 0)]],
                        yerr=[[max(y - min(ys_), 0)], [max(max(ys_) - y, 0)]], fmt=mk, ms=3.5,
                        c=COLORS[lab], mfc="white" if far else COLORS[lab], capsize=1, lw=0.5, zorder=5)
            spiral_rows.append(dict(obs=lab, v=c["v"], d=d, branch="far" if far else flag))
ax.set_xlim(-16, 20)
ax.set_ylim(-16, 20)
ax.set_aspect("equal")
ax.set_xlabel("$X$ (kpc)")
ax.set_ylabel("$Y$ (kpc)")
h = [Line2D([], [], c=COLORS[k], marker="o", ls="", ms=4) for k in results]
ax.legend(h, [f"{k}" for k in results], loc="lower right", frameon=False, ncol=2)
fig.tight_layout()
save(fig, "fig_spiral")

# --- numbers for the paper ------------------------------------------------------
out = {k: {kk: vv for kk, vv in r.items() if not kk.startswith("_")} for k, r in results.items()}
out["_spiral_points"] = spiral_rows
json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
for lab, r in out.items():
    if lab.startswith("_"):
        continue
    print(f"{lab}: l={r['l']:.1f} b={r['b']:+.1f} corr={r['vlsr_corr']:+.1f}  peak v_LSR={r['peak_v']:+.1f} "
          f"excess={100*r['peak_excess']:.2f}%  S/N ch={r['snr_channel']:.0f} sm={r['snr_smoothed']:.0f}  "
          f"P/Pground={r['power_ratio']:.2f}  vmax={r['vmax'][0]:.0f}-{r['vmax'][1]:.0f}  "
          f"R={r['R']:.2f}  V={r['V'][0]:.0f}-{r['V'][1]:.0f}")
    for c in r["components"]:
        print(f"      comp v={c['v']:+7.1f} +- {c['ev']:5.1f}  sigma={c['sigma']:5.1f}  amp={100*c['amp']:.2f}%")
for p in spiral_rows:
    print(f"  {p['obs']} v={p['v']:+6.1f} d={p['d']:5.1f} {p['branch']}")

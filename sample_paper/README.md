# Sample paper (APL format)

A draft paper on the 2026-10-23 Hornscope observations, in the AIP REVTeX 4.2 / *Applied Physics Letters* format (two-column, `revtex4-2` with `aip,apl,reprint`). It's meant as a starting point we can rewrite.

| File | Contents |
|---|---|
| `main.tex` | The paper. Red **[TODO: …]** marks things to fill in (horn dimensions, waveguide lining, LNA model, authors, photo) |
| `figures/` | Figures used by the paper (PDF for LaTeX, PNG for quick viewing) |
| `make_figures.py` | Regenerates every figure and number from `../observations/` and `data/` |
| `results.json` | The numbers quoted in the tables, written by `make_figures.py` |
| `data/` | Pointing log and literature data (Liu & Chronopoulos 2008 Table I, PhysicsOpenLab 2020 table with their ±20 km/s errors, Bhattacharjee et al. 2026 digitized from their figure) |

## Compiling on Overleaf

**Menu → Main document → `sample_paper/main.tex`**, then Recompile. The bibliography is embedded in `main.tex`, so no BibTeX setup is needed.

## Regenerating the figures

```bash
cd ~/gr-radio_astro && python sample_paper/make_figures.py
```

Assumes the site is NUS (1.30° N, 103.78° E), R₀ = 8.2 kpc and V₀ = 230 km/s.

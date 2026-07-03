# Replication package — KIM manuscript
"A multi-criteria model for allocating free cash flow in personal financial planning"

## Files
- `model.py`        — core model: alternatives (stars-and-bars, step 0.2), Avalanche + opportunity-cost filter, weighted goals, constraints, min-max SAW, SES+Monte-Carlo forecast
- `exp2.py`         — Part 1: original specification, 3 profiles x 3 L_min regimes (Table 4)
- `exp3.py`         — refined criteria: forecast resource (12) + stock liquidity (13)
- `exp4.py`         — Part 2: norm-anchored normalization, final results (Table 5, Fig. 2)
- `extras.py`       — criteria correlation (0.9998 / 0.99979) and timing (0.7 ms + 0.9 ms)
- `figs.py`, `fig1.py` — figure generation, Russian labels (Fig. 1–3, monochrome-safe)
- `figs_en.py`      — figure generation, English labels (for the EN manuscript)
- `results*.json`   — machine-readable outputs
- `figures/`        — PNG 300 dpi

## Run
python3 exp2.py && python3 exp3.py && python3 exp4.py && python3 extras.py && python3 figs.py && python3 fig1.py

Requires: numpy, matplotlib (Python 3.12).

"""
Step 5: Predict the diffusion path of the Garmin Index Sleep Monitor.

Idea: use the Bass parameters (p, q) estimated from the look-alike (Fitbit)
and apply them to Garmin, with t = 1 being Garmin's launch year (2025).
Result is expressed as a SHARE of the market potential M.
M itself is estimated in Step 7 (Fermi logic).

Input : data/bass_parameters.csv  (from step4_estimate_bass.py)
Output: data/garmin_diffusion_shape.csv
        img/garmin_diffusion_shape.png
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LAUNCH_YEAR = 2025          # Garmin launched the Index Sleep Monitor on 18 June 2025
LAST_YEAR = 2040
MAIN_WINDOW = "2010-2025"   # Fitbit fit used as the main assumption


def cdf(t, p, q):
    e = np.exp(-(p + q) * t)
    return (1 - e) / (1 + (q / p) * e)


params = pd.read_csv("data/bass_parameters.csv").set_index("window")

scenarios = {
    "Main: Fitbit fit 2010-2025": (params.loc[MAIN_WINDOW, "p"], params.loc[MAIN_WINDOW, "q"]),
    "Fitbit fit 2010-2019": (params.loc["2010-2019", "p"], params.loc["2010-2019", "q"]),
    "Literature average (Sultan et al. 1990)": (0.03, 0.38),
}

years = np.arange(LAUNCH_YEAR, LAST_YEAR + 1)
t = years - LAUNCH_YEAR + 1
out = pd.DataFrame({"year": years, "t": t})

for name, (p, q) in scenarios.items():
    cum = cdf(t, p, q)
    annual = cdf(t, p, q) - cdf(t - 1, p, q)
    out[f"{name} | cumulative share of M"] = cum
    out[f"{name} | annual share of M"] = annual
    peak_year = years[np.argmax(annual)]
    print(f"{name}: p={p:.4f} q={q:.4f} -> peak adoption year {peak_year}, "
          f"annual share at peak {annual.max():.1%}, "
          f"50% of M reached in {years[np.argmax(cum >= 0.5)]}, "
          f"90% in {years[np.argmax(cum >= 0.9)]}")

out.round(4).to_csv("data/garmin_diffusion_shape.csv", index=False)

# ---- Plot ----
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
for name in scenarios:
    ax[0].plot(years, out[f"{name} | cumulative share of M"] * 100, marker="o", ms=3, label=name)
    ax[1].plot(years, out[f"{name} | annual share of M"] * 100, marker="o", ms=3, label=name)
ax[0].set_title("Cumulative adopters (% of market potential M)")
ax[1].set_title("New adopters per year (% of market potential M)")
for a in ax:
    a.set_xlabel("Year")
    a.axvline(LAUNCH_YEAR, color="gray", ls=":", lw=0.8)
ax[0].set_ylabel("% of M")
ax[1].set_ylabel("% of M")
ax[0].legend(fontsize=8)
plt.tight_layout()
plt.savefig("img/garmin_diffusion_shape.png", dpi=150)
print("Saved data/garmin_diffusion_shape.csv and img/garmin_diffusion_shape.png")
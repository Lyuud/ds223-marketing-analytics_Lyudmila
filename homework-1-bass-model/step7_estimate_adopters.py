"""
Step 7: Estimate the number of adopters of the Garmin Index Sleep Monitor by year.

Two parts:
  A) Fermi estimate of the market potential M (units, worldwide, lifetime).
  B) Multiply M by the Bass diffusion shape (Step 5) to get adopters per year.

Input : data/bass_parameters.csv   (from step4_estimate_bass.py)
Output: data/garmin_M_fermi.csv            (the Fermi layers and the resulting M)
        data/garmin_adopters_by_year.csv   (new and cumulative adopters per year)
        img/garmin_adopters_by_year.png    (chart)
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LAUNCH_YEAR = 2025
LAST_YEAR = 2040
MAIN_WINDOW = "2010-2025"

# ---------------------------------------------------------------------------
# A) FERMI ESTIMATE OF M
#    M = (Garmin active users) x (share who track sleep) x (share who buy a band)
# Every number has a source (see report). Layer 3 is an explicit assumption.
# ---------------------------------------------------------------------------
fermi = pd.DataFrame(
    {
        # Layer 1: active Garmin Connect users worldwide, millions
        #   Source: the5krunner (2026), estimate 45M, range 42-49M (Garmin publishes no count)
        "garmin_active_users_millions": [42, 45, 49],
        # Layer 2: share of wearable owners who use the device to track sleep
        #   Low  21%: CCS Insight survey, via Raconteur: tracker owners who bought it mainly
        #             for sleep monitoring (conservative: users for whom sleep matters most)
        #   Base 26%: Rock Health 2025 Consumer Adoption Survey (US, n=8,000)
        #   High 48%: AASM Sleep Prioritization Survey 2025 (US, n=2,007): share of ALL adults
        #             who use any sleep-tracking device (an upper-bound proxy)
        "share_track_sleep": [0.21, 0.26, 0.48],
        # Layer 3: share of those users who buy a separate sleep band
        #   ASSUMPTION (no direct source), tested low / base / high
        "share_buy_band": [0.05, 0.10, 0.20],
    },
    index=["Low", "Base", "High"],
)
fermi["M_millions"] = (
    fermi["garmin_active_users_millions"]
    * fermi["share_track_sleep"]
    * fermi["share_buy_band"]
)
fermi.round(4).to_csv("data/garmin_M_fermi.csv", index_label="scenario")
print("Fermi estimate of M (millions of units):")
print(fermi.round(3).to_string())


# ---------------------------------------------------------------------------
# B) BASS DIFFUSION: adopters per year = M x [F(t) - F(t-1)]
# ---------------------------------------------------------------------------
def cdf(t, p, q):
    e = np.exp(-(p + q) * t)
    return (1 - e) / (1 + (q / p) * e)


params = pd.read_csv("data/bass_parameters.csv").set_index("window")
p, q = params.loc[MAIN_WINDOW, "p"], params.loc[MAIN_WINDOW, "q"]

years = np.arange(LAUNCH_YEAR, LAST_YEAR + 1)
t = years - LAUNCH_YEAR + 1
share_cum = cdf(t, p, q)
share_new = cdf(t, p, q) - cdf(t - 1, p, q)

out = pd.DataFrame({"year": years, "t": t,
                    "cumulative_share_of_M": share_cum,
                    "new_share_of_M": share_new})
for s in fermi.index:
    M = fermi.loc[s, "M_millions"]            # millions of units
    out[f"{s}: new adopters (thousands)"] = M * share_new * 1000
    out[f"{s}: cumulative adopters (thousands)"] = M * share_cum * 1000

out.round(4).to_csv("data/garmin_adopters_by_year.csv", index=False)

peak = years[np.argmax(share_new)]
print(f"\nBass parameters used: p={p}, q={q} (Fitbit fit {MAIN_WINDOW}); peak year {peak}")
cols = ["year", "new_share_of_M"] + [f"{s}: new adopters (thousands)" for s in fermi.index]
print(out[cols].round(3).to_string(index=False))
print("\nCumulative adopters at 2030 and 2040 (thousands):")
for y in (2030, 2040):
    row = out[out.year == y].iloc[0]
    print(y, {s: round(row[f"{s}: cumulative adopters (thousands)"]) for s in fermi.index})

# ---- Plot ----
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
for s, style in zip(fermi.index, [":", "-", "--"]):
    ax[0].plot(years, out[f"{s}: new adopters (thousands)"], style, marker="o", ms=3,
               label=f"{s} (M = {fermi.loc[s, 'M_millions']:.2f}M)")
    ax[1].plot(years, out[f"{s}: cumulative adopters (thousands)"], style, marker="o", ms=3,
               label=f"{s} (M = {fermi.loc[s, 'M_millions']:.2f}M)")
ax[0].set_title("New adopters per year (thousands of units)")
ax[1].set_title("Cumulative adopters (thousands of units)")
for a in ax:
    a.set_xlabel("Year")
    a.set_ylabel("Thousands of units")
ax[0].legend(fontsize=8)
plt.tight_layout()
plt.savefig("img/garmin_adopters_by_year.png", dpi=150)
print("\nSaved data/garmin_M_fermi.csv, data/garmin_adopters_by_year.csv, img/garmin_adopters_by_year.png")

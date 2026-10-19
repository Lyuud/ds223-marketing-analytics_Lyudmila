"""
Step 4: Estimate Bass model parameters (p, q, M) from Fitbit sales.

Input : data/statista_fitbit_units_sold.csv   (Statista, units in thousands)
Output: data/bass_parameters.csv              (p, q, M for each fitting window)
        img/bass_fit_windows.png              (data vs fitted curves)
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ---------- 1. Load data ----------
# encoding="utf-8-sig" removes the invisible BOM marker at the file start.
df = pd.read_csv("data/statista_fitbit_units_sold.csv", encoding="utf-8-sig")
df.columns = ["year", "sales_thousands"]          # fix the empty first header
df["sales_millions"] = df["sales_thousands"] / 1000
FIRST_YEAR = df["year"].min()                      # 2010 -> t = 1


# ---------- 2. The Bass model ----------
def cdf(t, p, q):
    """Share of the market that has adopted by time t (the S-curve)."""
    e = np.exp(-(p + q) * t)
    return (1 - e) / (1 + (q / p) * e)

def sales_per_period(t, p, q, M):
    """Sales in period t = M * (share adopted by t - share adopted by t-1)."""
    return M * (cdf(t, p, q) - cdf(t - 1, p, q))


# ---------- 3. Fit on several windows ----------
def fit(last_year):
    d = df[df["year"] <= last_year]
    t = (d["year"] - FIRST_YEAR + 1).values
    y = d["sales_millions"].values
    best = None
    # try several starting guesses, keep the best fit
    for p0 in (0.001, 0.01, 0.05):
        for q0 in (0.3, 0.6, 1.0):
            try:
                par, _ = curve_fit(
                    sales_per_period, t, y,
                    p0=[p0, q0, y.sum() * 1.2],
                    bounds=([1e-6, 1e-3, y.sum() * 0.5], [1, 5, 500]),
                    maxfev=20000)
            except RuntimeError:
                continue
            sse = ((sales_per_period(t, *par) - y) ** 2).sum()
            if best is None or sse < best[1]:
                best = (par, sse)
    p, q, M = best[0]
    fitted = sales_per_period(t, p, q, M)
    r2 = 1 - ((y - fitted) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    peak_t = np.log(q / p) / (p + q)               # time of peak sales
    return dict(window=f"{FIRST_YEAR}-{last_year}", n_points=len(y),
                p=p, q=q, M_millions=M, q_over_p=q / p,
                R2=r2, peak_year=FIRST_YEAR - 1 + peak_t,
                units_already_sold_millions=y.sum())

windows = [2016, 2019, 2025]
results = pd.DataFrame([fit(w) for w in windows])
results.round(4).to_csv("data/bass_parameters.csv", index=False)
print(results.round(4).to_string(index=False))


# ---------- 4. Plot ----------
fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
t_all = np.arange(1, 2025 - FIRST_YEAR + 2)
years_all = t_all + FIRST_YEAR - 1
for ax, (_, r) in zip(axes, results.iterrows()):
    ax.bar(df["year"], df["sales_millions"], color="lightgray", label="Actual (Statista)")
    ax.plot(years_all, sales_per_period(t_all, r.p, r.q, r.M_millions),
            "r-o", ms=3, label="Bass fit")
    ax.axvline(int(r.window[-4:]) + 0.5, ls="--", color="k", lw=0.8)
    ax.set_title(f"Fit {r.window}\np={r.p:.4f}  q={r.q:.3f}  M={r.M_millions:.0f}M  R²={r.R2:.2f}")
    ax.set_xlabel("Year")
axes[0].set_ylabel("Fitbit devices sold (millions)")
axes[0].legend()
plt.tight_layout()
plt.savefig("img/bass_fit_windows.png", dpi=150)
print("Saved img/bass_fit_windows.png and data/bass_parameters.csv")
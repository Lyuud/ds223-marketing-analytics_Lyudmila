# Bass Model Homework: Garmin Index Sleep Monitor

**Author:** Lyudmila Zakaryan · **Course:** Marketing Analytics (DS223) ·

## Overview
This project forecasts the diffusion of the Garmin Index Sleep Monitor
(selected from TIME's Best Inventions 2025: [link to the TIME entry]) with the
Bass model. The look-alike innovation is Fitbit, whose worldwide unit sales
(Statista) give the diffusion parameters p, q and M. The shape is applied to
Garmin worldwide, and Garmin's market potential is estimated with Fermi logic.

The full report is in `report/report.pdf` (source: `report/report_source.md`).

## How to run
```
pip install numpy pandas scipy matplotlib
python step4_estimate_bass.py
python step5_forecast_garmin.py
python step7_estimate_adopters.py
```
Run the scripts from the repository root, in this order. Steps 1–3 and 6 are
written in the report and have no code.

## Structure
- `report/report.pdf`: final report.
- `report/report_source.md`: Markdown source of the report.
- `step4_estimate_bass.py`: estimates Bass parameters from Fitbit sales (Step 4).
- `step5_forecast_garmin.py`: Garmin diffusion shape from the Fitbit parameters (Step 5).
- `step7_estimate_adopters.py`: Fermi estimate of M and adopters by year (Step 7).

### data/
- `statista_fitbit_units_sold.csv`: Fitbit devices sold worldwide, 2010–2025, in thousands (Statista).
- `bass_parameters.csv`: estimated p, q, M for three fitting windows.
- `garmin_diffusion_shape.csv`: Garmin adoption as a share of M, 2025–2040, three scenarios.
- `garmin_M_fermi.csv`: Fermi estimate of M (low, base, high).
- `garmin_adopters_by_year.csv`: estimated new and cumulative adopters, 2025–2040.

### img/
- `bass_fit_windows.png`: actual Fitbit sales vs fitted Bass curves, three windows.
- `garmin_diffusion_shape.png`: predicted Garmin diffusion shape, three scenarios.
- `garmin_adopters_by_year.png`: estimated adopters per year, three scenarios.

## Main results
Bass parameters (Fitbit, 2010–2025): p = 0.0121, q = 0.4542.
Base-case M for the Garmin Index Sleep Monitor: 1.17 million units
(range 0.44–4.70 million). Sales peak in 2032 at about 139 thousand units.
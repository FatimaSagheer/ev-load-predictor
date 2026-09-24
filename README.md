# EV Charging Demand Forecasting

Forecasting daily electricity demand (kWh) at EV charging stations using historical session data, with baseline and seasonal time series models.

## Problem

As EV adoption grows, charging station operators and grid planners need to anticipate demand — both to avoid capacity shortfalls and to plan infrastructure investment efficiently. This project forecasts **total daily energy demand (kWh)** across a network of charging stations using historical session-level data.

## Data

- **Source:** [EV Charging Station Usage — California City (Kaggle)](https://www.kaggle.com/datasets/venkatsairo4899/ev-charging-station-usage-of-california-city) — session-level records including station ID, start/end time, and energy consumed (kWh) per session.
- **Fallback:** if the real dataset isn't present, the notebook auto-generates a synthetic dataset (`data/ev_sessions.csv`) with realistic weekly/yearly seasonality and an adoption trend, so the pipeline can be demoed without the original file.
- **Granularity used for modeling:** session-level data is aggregated into **daily total kWh demand** across all stations.

## Method

1. **Cleaning** — deduplication, missing-value imputation (per-station median), outlier capping (99.5th percentile winsorization), aggregation to a continuous daily time series.
2. **EDA** — trend (7-day rolling average), weekly seasonality (day-of-week averages), monthly seasonality, ACF/PACF plots to inform model order selection.
3. **Train/test split** — time-based split (never shuffled): last 30 days held out as the test set.
4. **Baseline models** — seasonal naive (t-7 lag), 7-day moving average, ARIMA.
5. **Stronger model** — SARIMA, adding an explicit weekly seasonal component `(P,D,Q,s=7)` on top of the ARIMA baseline.
6. **Evaluation** — MAE, RMSE, MAPE on the held-out test set; residual diagnostics (mean, distribution) to check for remaining structure.

## Results

| Model | MAE | RMSE | MAPE |
|---|---|---|---|
| Seasonal Naive | 177.31 | 214.19 | 21.20% |
| Moving Average | 232.49 | 293.65 | 35.62% |
| ARIMA(2,1,2) | 210.23 | 258.36 | 31.35% |
| **SARIMA(2,1,2)(1,1,1,7)** | **143.56** | **175.38** | **19.91%** |

**Best model:** SARIMA, by a clear margin on every metric. Notably, plain ARIMA performed *worse* than the naive seasonal baseline — it has no seasonal component, so it fails to capture the dominant weekly charging pattern (weekday commuter charging vs. quieter weekends) that the seasonal-naive method captures implicitly just by lagging 7 days. Adding an explicit seasonal order `(P,D,Q,s=7)` is what let SARIMA outperform both.

**Improvement over best baseline (Seasonal Naive):** RMSE improved by **18.1%** (214.19 → 175.38) and MAE improved by **19.0%** (177.31 → 143.56).

## Limitations & Future Work

- No external regressors yet (weather, holidays, gas prices) — likely the biggest lever for further accuracy gains.
- Forecasts network-wide demand only; no per-station breakdown.
- Could compare against a gradient-boosted model (XGBoost/LightGBM with lag + calendar features) or Prophet for a non-classical-statistics baseline.

## How to Run

```bash
# clone the repo
git clone <your-repo-url>
cd ev-charging-demand-forecast

# install dependencies
pip install -r requirements.txt

# open notebooks/ev_demand_forecasting.ipynb and run all cells
```

To use the real dataset instead of the synthetic fallback, place the Kaggle CSV at `data/ev_sessions.csv` (with columns matching `start_time`, `end_time`, `station_id`, `kwh_total`) before running.

## Project Structure

```
ev-charging-demand-forecast/
├── README.md
├── requirements.txt
├── notebooks/
│   └── ev_demand_forecasting.ipynb
└── data/
    └── ev_sessions.csv
```
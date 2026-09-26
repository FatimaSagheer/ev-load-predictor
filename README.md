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
5. **Stronger models** — SARIMA (explicit weekly seasonal component), ETS/Holt-Winters, Prophet, and an LSTM neural network (14-day sliding window, iterative forecasting).
6. **Evaluation** — MAE, RMSE, MAPE on the held-out test set; residual diagnostics (mean, distribution) to check for remaining structure.

## Results

| Model | MAE | RMSE | MAPE |
|---|---|---|---|
| **SARIMA(2,1,2)(1,1,1,7)** | **143.56** | **175.38** | **19.91%** |
| ETS (Holt-Winters) | 172.22 | 211.09 | 24.30% |
| Seasonal Naive | 177.31 | 214.19 | 21.20% |
| LSTM | 198.57 | 233.16 | 26.96% |
| ARIMA(2,1,2) | 210.23 | 258.36 | 31.35% |
| Moving Average | 232.49 | 293.65 | 35.62% |
| Prophet | 414.87 | 443.64 | 55.07% |

**Best model:** SARIMA, by a clear margin on every metric, even after comparing against 6 other approaches including a neural network.

**Key findings:**
- Plain ARIMA underperformed the naive seasonal baseline — it has no seasonal component, so it misses the dominant weekly charging pattern that the seasonal-naive method captures implicitly just by lagging 7 days.
- ETS (a different smoothing-based approach) also explicitly models weekly seasonality, which is why it lands in 2nd place, close to SARIMA.
- **LSTM underperformed the classical seasonal models** — with only ~1 year of daily data, there likely isn't enough history for the network to learn the seasonal pattern as reliably as models that encode seasonality structurally.
- **Prophet performed worst**, likely overfitting trend changepoints on a relatively short training window. Prophet is designed for exactly this kind of seasonality and would likely be far more competitive with 2-3+ years of history.

**Improvement over best non-seasonal baseline (Seasonal Naive):** RMSE improved by **18.1%** (214.19 → 175.38) and MAE improved by **19.0%** (177.31 → 143.56).

**Takeaway:** for this dataset size and seasonality pattern, a well-specified classical model beats more complex approaches — more data would likely change this ranking, especially for Prophet and LSTM.

## Understanding the Models — Why Each One Performed the Way It Did

**Seasonal Naive (baseline)** — predicts "today = same day last week." Not really a model, more a sanity check: any real model needs to beat this or it isn't adding value. It does reasonably well here (RMSE 214) because demand has a strong 7-day repeating pattern (weekday commuter charging vs. quieter weekends).

**Moving Average (baseline)** — predicts using the average of the last 7 days. It smooths out noise but has no concept of *which* day of the week it is, so it blurs the weekday/weekend pattern into a flat number. That's why it performed worst among the simple methods (RMSE 294) — it throws away the exact seasonal signal.

**ARIMA (baseline)** — looks at the series' own past values and past errors to predict the next one. Good at capturing trend and short-term momentum, but has no built-in concept of a weekly cycle. That's why it actually did *worse* than the naive guess (RMSE 258 vs. 214) — it was fighting the weekly pattern instead of using it.

**SARIMA (winner)** — same idea as ARIMA, with an extra seasonal component `(P,D,Q,s=7)` bolted on, explicitly telling the model to also look at what happened 7 days ago, not just yesterday. That single change is what let it beat everything else (RMSE 175). This tells us the demand pattern here is genuinely driven by the weekly commuting cycle, and any model that ignores that structure is handicapped from the start.

**ETS (Holt-Winters)** — a different mathematical approach (weighted smoothing rather than autoregression), but it also explicitly models trend + weekly seasonality. It landed 2nd, close behind SARIMA — reinforcing that modeling the weekly seasonality is what matters, more than which specific method is used to do it.

**Prophet** — built specifically for business time series with seasonality, so it should in theory do well here. It performed worst (RMSE 444), likely because Prophet also tries to detect *changes in trend* over time, and with only ~1 year of data it probably mistook some noise for a trend shift and overcorrected. More sophisticated tools aren't automatically better — they need enough data to earn their complexity.

**LSTM** — a neural network that learns patterns purely from examples, with no built-in assumption about weekly seasonality; it has to discover that pattern from data. With only ~350 training days, it likely didn't see enough repetitions of the weekly cycle to learn it reliably.

**The one-sentence takeaway:** explicitly telling the model about the weekly cycle beats letting the model discover it on its own — at least until there's a lot more data available.

## Limitations & Future Work

- No external regressors yet (weather, holidays, gas prices) — likely the biggest lever for further accuracy gains, especially for Prophet.
- Forecasts network-wide demand only; no per-station breakdown.
- LSTM and Prophet were trained on ~1 year of data — both would likely improve substantially with more historical data.
- Could try a gradient-boosted model (XGBoost/LightGBM) with lag + calendar features as another comparison point.

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
├── data/
│   └── ev_sessions.csv
├── notebooks/
│   └── ev_demand_forecasting.ipynb
└── webapp/                    ← add this folder here, same level as data/ and notebooks/
    ├── app.py
    ├── chart_data_full.json
    ├── results_meta.json
    └── templates/
        └── index.html
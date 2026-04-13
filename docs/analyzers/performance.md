# ML & Performance

The Performance Analyzer uses Machine Learning techniques to go beyond static thresholds.

## Features
* **Anomaly Detection:** Learns the baseline behavior of your clusters over a 7-day period and alerts on statistical deviations (e.g., unusual CPU spikes).
* **Predictive Failure:** Uses linear regression and time-series forecasting to predict resource exhaustion (e.g., predicting an OOMKill 14 hours before it happens based on memory leak trends).

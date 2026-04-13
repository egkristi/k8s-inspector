# ML & Performance Analyzer

k8s-inspector goes beyond static CPU and Memory thresholds by utilizing machine learning algorithms to identify anomalies and predict resource exhaustion before it causes a cluster failure.

## Key Features

The Performance Analyzer relies on historical metric data stored in our embedded TimescaleDB instance. It leverages `scikit-learn` and `NumPy` in the backend.

### 1. Anomaly Detection (Statistical Spikes)
Instead of hardcoding a rule like "alert if CPU > 80%", the ML engine learns the standard operating behavior (baseline) of your cluster workloads over the past 7 to 30 days.
- **Isolation Forest / Z-score Models:** It calculates the mean and standard deviation of your resources. If a metric spikes beyond `(mean + 3*std_dev)`, an anomaly is flagged.
- **Contextual Spikes:** A 90% CPU usage might be perfectly normal for a batch processing job, but highly unusual for an API gateway. The analyzer distinguishes between the two based on historical context.

### 2. Predictive Failure Detection (Trend Analysis)
The engine monitors the rate of change for critical resources, such as memory usage, to predict when exhaustion will occur.
- **Memory Leaks:** If memory usage for a specific pod increases linearly by `> 1% per hour`, the engine uses polynomial regression to calculate the "Time-to-OOMKill."
- **Capacity Planning:** Predicts when a cluster node pool will run out of resources, enabling proactive scaling.

## Why ML-Driven?

Static alerts lead to alert fatigue. If every pod that hits 85% memory triggers an alert, engineers start ignoring them. The Performance Analyzer ensures alerts are only triggered when the behavior is genuinely anomalous or trending towards a catastrophic failure.

## Technical Implementation

The ML analyzer executes inside the FastAPI backend (`backend/app/analyzers/performance_analyzer.py`).

1. **Data Ingestion:** Regularly fetches CPU, Memory, and Network I/O from Prometheus/Metrics-Server.
2. **Time-Series Storage:** Persists metrics to TimescaleDB.
3. **Inference Execution:** Runs lightweight statistical models on the data in memory.
4. **Insight Generation:** Triggers an `Insight` object if anomalies or trends are found.

These insights are displayed in the Next.js Dashboard and can automatically trigger scaling actions via Playbooks.

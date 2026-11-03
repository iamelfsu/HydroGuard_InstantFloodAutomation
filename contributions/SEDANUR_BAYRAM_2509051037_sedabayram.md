Fetches 3-day river discharge forecasts for the Cendere Basin from the Open-Meteo Flood API, using the maximum value for early warning.
Passes raw data through `pipeline.py` for validation and SAFE / WARNING / CRITICAL classification.
Persists the last hazard level in `data_store/state.json` and acts only on state transitions, avoiding repeated alerts.
Triggers `router.py` on CRITICAL to generate the evacuation map and send the dispatch webhook.
Handles HTTP, data-format, and unexpected errors without crashing, retrying on the next cycle.
Runs continuously at a configurable interval (30 s) with Istanbul-time log stamps.
Keeps configuration (API URL, parameters, timeout, interval, state path) in constants at the top of the file.
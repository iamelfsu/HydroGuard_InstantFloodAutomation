### Emergency Alert Pipeline & Webhook Notifications

In this section of my project, I built the system that turns the dispatch results and the evacuation map into an actual emergency alert. It connects the monitoring side (`main.py`) to the routing side (`router.py`), so that when the **Cendere Basin** reaches a critical flood level, the crisis teams are notified about what is being dispatched to each **ISU Campus**.

#### What it Does
* **Triggers the Full Response:** It provides a single entry point that `main.py` calls when the flood status becomes critical, running the entire routing process from one function call.
* **Measures Processing Time:** It tracks how long the dispatch decision and map generation take and logs the result to the console.
* **Builds an Actionable Alert:** It writes a structured emergency message listing, for each campus, the assigned base, its assets and the route's safety status.
* **Sends Webhook Notifications:** It delivers the alert to the notification channel as a JSON-based HTTP request.
* **Localizes the Module:** It presents all campus names, asset descriptions and map labels in English, consistent with the rest of the system.

#### Tech Stack & Libraries Used
* **Requests**: Used to send the alert to the webhook endpoint as an HTTP POST request with a JSON payload and a timeout.
* **time.perf_counter**: Used as a high-resolution timer to measure how long the routing step takes.
* **Webhooks**: Used as the delivery channel; the `{"content": ...}` payload follows the format used by Discord webhooks.

#### Breakdown of Core Components

##### 1. `execute_routing_pipeline(live_discharge: float)`
This is the entry point that links the monitoring loop to the routing module. It starts a `perf_counter()` timer, flags the Cendere Basin as flooded when the discharge reaches the 5.0 m³/s critical threshold, and calls `optimize_logistics_dispatch()` and `generate_dual_campus_map()`. It then prints the elapsed time and passes the results to the webhook function.

##### 2. `send_dual_actionable_webhook(discharge_rate: float, dispatch_results: dict, elapsed_time: float)`
This is the function responsible for preparing and delivering the alert. It handles three main tasks:
* **Command List:** Uses a list comprehension with `enumerate()` to build numbered dispatch commands, one per campus, showing the assigned base, its assets and the safety note.
* **Alert Message:** Combines the target area, current river discharge, dispatch commands, route map location and optimization time into a single multi-line message.
* **Delivery & Error Handling:** Sends the message with `requests.post()` and checks it with `raise_for_status()`, catching `RequestException` so a failed delivery prints an error instead of crashing the system.
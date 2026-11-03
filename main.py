import requests
import os
import time
import json
from datetime import datetime, UTC
from zoneinfo import ZoneInfo
import pipeline
import router

API_URL = "https://flood-api.open-meteo.com/v1/flood"
STATE_FILE = "data_store/state.json"
TIMEOUT_LIMIT = 10
SCHEDULE_INTERVAL = 30

API_PARAMS = {
    "latitude": 41.104400,
    "longitude": 28.987500,
    "daily": "river_discharge",
    "forecast_days": 3
}

def get_istanbul_time() -> str:

    utc_now = datetime.now(UTC)
    istanbul_zone = ZoneInfo("Europe/Istanbul")
    local_time = utc_now.astimezone(istanbul_zone)
    return local_time.strftime("%H:%M:%S")

def monitor_cendere_basin():

    current_time = get_istanbul_time()
    print(f"[{current_time}] Querying Open-Meteo Flood API...")

    try: 

        response = requests.get(API_URL, params=API_PARAMS, timeout=TIMEOUT_LIMIT)
        response.raise_for_status()
        data = response.json()

        raw_discharge_list = data["daily"]["river_discharge"]
        raw_discharge = max(raw_discharge_list) if raw_discharge_list else 0.0

        live_discharge = pipeline.parse_and_validate_discharge(raw_discharge)
        print(f"[LIVE METRICS]: Cendere River Discharge: {live_discharge} m³/s")

        current_hazard = pipeline.evaluate_flood_hazard(live_discharge)

        saved_status = "SAFE"
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as file:
                try: 
                    state_data = json.load(file)
                    saved_status = state_data.get("status", "SAFE")
                except json.JSONDecodeError:
                    saved_status = "SAFE"

        if current_hazard != saved_status:
            print(f" [STATE TRANSITION DETECTED]: {saved_status} ➔ {current_hazard}")

            with open(STATE_FILE, "w") as file:
                json.dump({"status": current_hazard, "last_update": current_time}, file)

            if current_hazard == "CRITICAL":
                print(" [CRITICAL ALERT]: Critical threshold exceeded! Plotting route...")

                router.execute_routing_pipeline(live_discharge)

            elif current_hazard == "WARNING":
                print(" [WARNING ALERT]: Creek flow rate is rising. Teams have been placed on high alert.")

            else: 
                print(" [SAFE STATUS]: The basin has returned to normal. Alarm status stands down.")
        else: 
            print(f" [STATE UNCHANGED]:{saved_status} ➔ {current_hazard}. Notification skipped.")
            

    except requests.exceptions.HTTPError as http_err:
        print(f"[SERVER ERROR]: Temporary connection failure: {http_err}. Retrying next cycle...")
    except KeyError as key_err:
        print(f" [DATA ERROR]: Incompatible API data format: {key_err}. Retrying next cycle...")
    except Exception as err:
       print(f" [UNEXPECTED ERROR]: {err}")


if __name__ == "__main__":
    print("==================================================")
    print(" HYDROGUARD FLOOD LOGISTICS ENGINE ACTIVATED")
    print(f"The system will monitor the Cendere Basin every {SCHEDULE_INTERVAL} seconds...")
    print("==================================================\n")

    while True:
        monitor_cendere_basin()
        time.sleep(SCHEDULE_INTERVAL)
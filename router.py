import folium 
import math
import requests
from time import perf_counter

ISU_CAMPUSES = {
    "VADI_CAMPUS": {
        "name": "ISU Main Valley Campus",
        "coords": [41.1064, 28.9851],
        "color": "red"
    },

    "H_CAMPUS": {
        "name": "ISU H Campus",
        "coords":[41.1032, 28.9861],
        "color": "darkred"
    }
}

LOGISTICS_REGISTRY = {
    "AFAD": {
        "name": "Hasdal AFAD Base",
        "coords": [41.0913, 28.9555],
        "assets": "3x Zodiac Rescue Boats & Submersible Pumps",
        "safety_status": "SAFE_ROUTE",
        "color": "blue"
    },

    "FIRE_STATION": {
        "name": "Kagithane Fire Station",
        "coords": [41.0985, 28.9810],
        "assets": "15x Mobile Flood Barrier & Pump Team",
        "safety_status": "CRITICAL_ROUTE",
        "color": "purple"
    }
}

OUTPUT_MAP_FILE = "data_store/flood_route.html"
WEBHOOK_URL = "https://httpbin.org/post"

def calculate_euclidiean_distance(coord1: list, coord2: list) -> float:
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def determine_best_responder(campus_coords: list, cendere_flooded: bool = False) -> dict:
    if cendere_flooded:
        return LOGISTICS_REGISTRY["AFAD"]

    dist_to_afad = calculate_euclidiean_distance(campus_coords, LOGISTICS_REGISTRY["AFAD"]["coords"])
    dist_to_fire = calculate_euclidiean_distance(campus_coords, LOGISTICS_REGISTRY["FIRE_STATION"]["coords"])

    if dist_to_afad < dist_to_fire:
        return LOGISTICS_REGISTRY["AFAD"] 
    else:
        return LOGISTICS_REGISTRY["FIRE_STATION"]

def optimize_logistics_dispatch(cendere_flooded: bool = False) -> dict:

    return {
        key: determine_best_responder(campus["coords"], cendere_flooded)
        for key, campus in ISU_CAMPUSES.items()
    }

def generate_dual_campus_map(dispatch_results: dict):

    carto_voyager = "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_50vt_1_504d45160fd062dea54e09ec"

    carto_attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://cartodb.com/">CARTO</a>'

    emergency_map = folium.Map(
        location=[41.1050, 28.9855], 
        zoom_start=14, 
        control_scale=True, 
        tiles=carto_voyager,
        attr=carto_attr)


    for key, campus in ISU_CAMPUSES.items():
        assigned = dispatch_results[key]

        folium.Marker(
            location = campus["coords"],
            popup = f"<b> {campus['name']}</b><br> Assigned Resources:{assigned['assets']}<br>Route: {assigned['safety_status']}",
            icon = folium.Icon(color=campus["color"], icon="exclamation-sign")
        ).add_to(emergency_map)

        folium.PolyLine(
            locations = [assigned["coords"], campus["coords"]],
            color = assigned["color"],
            weight = 5,
            opacity = 0.8,
            tooltip = f" {campus['name']} Evacuation Corridor ({assigned['name']})"
        ).add_to(emergency_map)

    for base in LOGISTICS_REGISTRY.values():

        folium.Marker(
            location = base["coords"],
            popup = f"<b> {base['name']}</b><br>Status: Ready for Mobilization",
            icon = folium.Icon(color=base["color"], icon="home")
        ).add_to(emergency_map)

    emergency_map.save(OUTPUT_MAP_FILE)

def send_dual_actionable_webhook(discharge_rate: float, dispatch_results: dict, elapsed_time: float):
    commands_text = "".join([
        f"{idx}) {ISU_CAMPUSES[key]['name']} ➔ Dispatch: {res['name']} ({res['assets']})\n Safety Note: {res['safety_status']}\n\n"
        for idx, (key, res) in enumerate(dispatch_results.items(), 1)
    ])

    alert_text = (
        f" [HYDROGUARD: DUAL-CAMPUS EMERGENCY PLAN] \n"
        f" ----------------------------------------------------------\n"
        f"TARGET AREA: Cendere Basin - Istinye Universities Campuses\n"
        f"Instant River Discharge: {discharge_rate} m³/s (Critical Flood Threshold Exceeded!)\n"
        f"AUTOMATED DISPATCH COMMANDS: \n {commands_text}"
        f" LIVE OPERATION MAP: \n"
        f"Both campuses' evacuation corridors have been updated in real-time on the map: \n"
        f"Route Output: {OUTPUT_MAP_FILE}\n\n"
        f" Matrix optimization completed in {elapsed_time:.2f} seconds.\n"
        f"[STATUS]: Actionable events published successfully over secure HTTP stream."
    )

    try: 
        response = requests.post(WEBHOOK_URL, json={"content": alert_text}, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[WEBHOOK ERROR]: Notification channel is unreachable: {e}")

def execute_routing_pipeline(live_discharge: float):

    start_timer = perf_counter()

    cendere_flooded = live_discharge >= 5.0

    dispatch_results = optimize_logistics_dispatch(cendere_flooded)
    generate_dual_campus_map(dispatch_results)

    elapsed_duration = perf_counter() - start_timer
    print(f"[PERFORMANCE]: Quota optimization completed in {elapsed_duration:.4f} seconds.")

    send_dual_actionable_webhook(live_discharge, dispatch_results, elapsed_duration)
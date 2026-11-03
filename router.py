import folium 
import math
import requests
from time import perf_counter

ISU_CAMPUSES = {
    "VADI_CAMPUS": {
        "name": "İSÜ ANA VADİ KAMPÜSÜ",
        "coords": [41.1064, 28.9851],
        "color": "red"
    },

    "H_CAMPUS": {
        "name": "İSÜ H YERLEŞKESİ",
        "coords":[41.1032, 28.9861],
        "color": "darkred"
    }
}

LOGISTICS_REGISTRY = {
    "AFAD": {
        "name": "Hasdal AFAD Üssü",
        "coords": [41.0913, 28.9555],
        "assets": "3x Zodiac Kurtarma Botu & Dalgıç Pompalar",
        "safety_status": "SAFE_ROUTE",
        "color": "blue"
    },

    "FIRE_STATION": {
        "name": "Kağıthane İtfaye İstasyonu",
        "coords": [41.0985, 28.9810],
        "assets": "15x Mobil Sel Bariyeri & Pompa Ekibi",
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
            popup = f"<b> {campus['name']}</b><br> Görevli Güç:{assigned['assets']}<br>Rota: {assigned['safety_status']}",
            icon = folium.Icon(color=campus["color"], icon="exclamation-sign")
        ).add_to(emergency_map)

        folium.PolyLine(
            locations = [assigned["coords"], campus["coords"]],
            color = assigned["color"],
            weight = 5,
            opacity = 0.8,
            tooltip = f" {campus['name']} Tahliye Koridoru ({assigned['name']})"
        ).add_to(emergency_map)

    for base in LOGISTICS_REGISTRY.values():

        folium.Marker(
            location = base["coords"],
            popup = f"<b> {base['name']}</b><br>Durum: Mobilizasyona Hazır",
            icon = folium.Icon(color=base["color"], icon="home")
        ).add_to(emergency_map)

    emergency_map.save(OUTPUT_MAP_FILE)

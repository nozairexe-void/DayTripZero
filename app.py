import math
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="DayTripZero", layout="wide")

PLACES = [
    {"name": "Shri Ram Centre & Mandi House Momos", "lat": 28.6273, "lon": 77.2330, "cost": 100, "mins": 45, "tip": "Grab steamed momos outside the theatre gate."},
    {"name": "Agrasen ki Baoli", "lat": 28.6261, "lon": 77.2250, "cost": 0, "mins": 40, "tip": "Hidden 14th-century stepwell near Hailey Road."},
    {"name": "Oxford Bookstore & Cha Bar (CP)", "lat": 28.6304, "lon": 77.2206, "cost": 150, "mins": 60, "tip": "Browse fantasy shelves and grab a masala chai."},
    {"name": "Jantar Mantar", "lat": 28.6271, "lon": 77.2166, "cost": 25, "mins": 45, "tip": "Giant 18th-century astronomical instruments."},
    {"name": "India Gate & Kartavya Path", "lat": 28.6129, "lon": 77.2295, "cost": 50, "mins": 50, "tip": "Evening walk with ice cream."},
    {"name": "Daryaganj Book Market / Old Delhi", "lat": 28.6448, "lon": 77.2407, "cost": 200, "mins": 75, "tip": "Best spot for cheap novels and box sets."},
    {"name": "Lodhi Garden Tombs", "lat": 28.5931, "lon": 77.2197, "cost": 0, "mins": 60, "tip": "Free entry, 15th-century stone architecture."}
]

HUBS = {
    "Mandi House": (28.6258, 77.2342),
    "Connaught Place": (28.6315, 77.2167),
    "Chandni Chowk": (28.6506, 77.2303),
    "Hauz Khas": (28.5535, 77.1945)
}

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def build_itinerary(start_lat, start_lon, places, max_mins, max_budget):
    route = []
    unvisited = [p.copy() for p in places]
    curr_lat, curr_lon = start_lat, start_lon
    time_used, budget_used = 0, 0

    while unvisited:
        closest = min(unvisited, key=lambda p: haversine_km(curr_lat, curr_lon, p["lat"], p["lon"]))
        dist = haversine_km(curr_lat, curr_lon, closest["lat"], closest["lon"])
        travel_mins = max(5, int(dist * 15))

        if (time_used + travel_mins + closest["mins"] <= max_mins) and (budget_used + closest["cost"] <= max_budget):
            closest["dist_km"] = round(dist, 2)
            closest["travel_mins"] = travel_mins
            route.append(closest)
            time_used += travel_mins + closest["mins"]
            budget_used += closest["cost"]
            curr_lat, curr_lon = closest["lat"], closest["lon"]

        unvisited.remove(closest)
    return route, time_used, budget_used

st.title("⚡ DayTripZero — Smart Delhi Loop Builder")
col1, col2 = st.columns([5, 7])

with col1:
    hub_name = st.selectbox("1. Choose Starting Hub", list(HUBS.keys()))
    max_hours = st.slider("2. Available Time (Hours)", 2, 8, 4)
    max_budget = st.slider("3. Max Budget (₹)", 200, 2000, 600, step=100)

    start_lat, start_lon = HUBS[hub_name]
    route, time_used, budget_used = build_itinerary(start_lat, start_lon, PLACES, max_hours * 60, max_budget)

    st.metric("Total Budget Used", f"₹{budget_used} / ₹{max_budget}")
    st.metric("Total Time Used", f"{time_used} mins / {max_hours * 60} mins")

    for i, stop in enumerate(route, 1):
        st.markdown(f"**Stop {i}: {stop['name']}** ({stop['dist_km']} km • ~{stop['travel_mins']}m travel)")
        st.caption(f"⏱ {stop['mins']} mins | 💸 ₹{stop['cost']} — {stop['tip']}")

with col2:
    m = folium.Map(location=[start_lat, start_lon], zoom_start=13)
    coords = [[start_lat, start_lon]]
    folium.Marker([start_lat, start_lon], popup="START: " + hub_name, icon=folium.Icon(color="green")).add_to(m)

    for i, stop in enumerate(route, 1):
        coords.append([stop["lat"], stop["lon"]])
        folium.Marker([stop["lat"], stop["lon"]], popup=f"{i}. {stop['name']} (₹{stop['cost']})").add_to(m)

    if len(coords) > 1:
        folium.PolyLine(coords, color="#10b981", weight=4, dash_array="8").add_to(m)
    st_folium(m, width=700, height=550)


import os
import sys

# Setup environment
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from streamlit_folium import st_folium
from folium import Map, Marker
from PIL import Image
import requests
from io import BytesIO
from src.detection.infer import detect_panels
from src.utils.energy import estimate_energy
from src.utils.logger import logger

# Load Mapbox token
MAPBOX_TOKEN = st.secrets.get("MAPBOX_TOKEN", "YOUR_MAPBOX_ACCESS_TOKEN")

st.set_page_config(page_title="🚀 Solar Panel Detection", layout="wide")
st.title("🚀 Solar Panel Detection from Mapbox Satellite Images")
st.markdown("Use latitude and longitude to fetch satellite image, detect solar panels, and estimate energy.")

# -- Coordinate State Initialization --
if "map_lat" not in st.session_state:
    st.session_state.map_lat = 36.45028
if "map_lon" not in st.session_state:
    st.session_state.map_lon = 10.73389

# Read from session state
latitude = st.session_state.map_lat
longitude = st.session_state.map_lon

# Sidebar controls
with st.sidebar:
    st.subheader("📍 Location & Settings")
    st.write("Coordinates are auto-updated from map click.")
    st.number_input("Latitude", value=latitude, format="%.5f", disabled=True)
    st.number_input("Longitude", value=longitude, format="%.5f", disabled=True)
    zoom = st.slider("Zoom Level", min_value=14, max_value=20, value=18)
    panel_eff = st.number_input("Panel Efficiency (%)", value=18.5) / 100
    system_loss = st.number_input("System Loss (%)", value=10.0) / 100
    scale_m_per_px = st.number_input("Scale (meters/pixel)", value=0.08, step=0.001, format="%.3f")
    model_choice = st.selectbox("Select Detection Model", ("Model1", "Model2", "Model3"))
    model_path = f"models/best{model_choice[-1]}.pt"
    irradiance = st.number_input("Irradiance (kWh/m²/day)", value=5.5)

# Interactive map with marker
st.markdown("---")
st.subheader("🗺️ Click a location on the map to update coordinates")
folium_map = Map(location=[latitude, longitude], zoom_start=zoom, tiles='Esri.WorldImagery')
Marker([latitude, longitude], tooltip="Selected Location").add_to(folium_map)
map_data = st_folium(folium_map, height=400, width=700)

# Update session state from map click
if map_data and map_data.get("last_clicked"):
    coords = map_data["last_clicked"]
    st.session_state.map_lat = coords["lat"]
    st.session_state.map_lon = coords["lng"]
    st.success(f"Map updated to: {coords['lat']:.5f}, {coords['lng']:.5f}")

# Satellite detection
st.markdown("### 🖼️ Satellite Image Detection")
if st.button("📸 Fetch & Analyze Image"):
    try:
        tile_size = 512
        url = (
            f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
            f"{st.session_state.map_lon},{st.session_state.map_lat},{zoom},0/{tile_size}x{tile_size}?access_token={MAPBOX_TOKEN}"
        )
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

        with st.spinner("Running Detection..."):
            tmp_path = "mapbox_fetch.jpg"
            image.save(tmp_path)
            detected_img, detection_df = detect_panels(tmp_path, model_path)

        if detection_df is not None and not detection_df.empty:
            detection_df["area_px"] = (detection_df["xmax"] - detection_df["xmin"]) * (detection_df["ymax"] - detection_df["ymin"])
            detection_df["area_m2"] = detection_df["area_px"] * (scale_m_per_px ** 2)
            total_area_m2 = detection_df["area_m2"].sum()

            st.dataframe(detection_df[["name", "confidence", "area_px", "area_m2"]])
            st.image(detected_img, caption="Detected Solar Panels")

            daily_kwh, yearly_kwh = estimate_energy(total_area_m2, irradiance, panel_eff, system_loss)
            st.success(f"✅ Estimated Daily Energy: {daily_kwh:.2f} kWh")
            st.info(f"🗕️ Estimated Yearly Energy: {yearly_kwh:.2f} kWh")
        else:
            st.warning("⚠️ No panels detected.")

    except Exception as e:
        st.error(f"Failed to fetch satellite image or run detection: {e}")

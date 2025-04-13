import os
import sys

# Setup
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from io import BytesIO
from PIL import Image
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium import Marker, TileLayer

from src.detection.infer import detect_panels
from src.utils.energy import estimate_energy
from src.utils.logger import logger

MAPBOX_TOKEN = st.secrets.get("MAPBOX_TOKEN", "YOUR_MAPBOX_ACCESS_TOKEN")

st.set_page_config(page_title="🚀 Solar Detector", layout="wide")
st.title("🚀 Solar Panel Detection from Satellite")
st.markdown("Click a location on the map to auto-fetch satellite image, detect panels, and estimate energy.")

# Session state for coordinates
if "map_lat" not in st.session_state:
    st.session_state.map_lat = 48.00844
if "map_lon" not in st.session_state:
    st.session_state.map_lon = 7.86312

latitude = st.session_state.map_lat
longitude = st.session_state.map_lon

# Sidebar inputs
with st.sidebar:
    st.subheader("📍 Location & Settings")
    st.write("Coordinates update based on map click.")
    st.number_input("Latitude", value=latitude, format="%.5f", disabled=True)
    st.number_input("Longitude", value=longitude, format="%.5f", disabled=True)
    zoom = st.slider("Zoom Level", min_value=14, max_value=20, value=19)
    panel_eff = st.number_input("Panel Efficiency (%)", value=18.5) / 100
    system_loss = st.number_input("System Loss (%)", value=10.0) / 100

    # Auto-calculate scale based on zoom
    meters_per_pixel = 156543.03392 * abs(
        round(st.session_state.map_lat) / 180 * 3.14159
    ) / (2 ** zoom)
    st.info(f"🔍 Estimated Scale: {meters_per_pixel:.4f} m/pixel")

    model_choice = st.selectbox("Select Detection Model", ("Model3", "Model2", "Model1"))
    model_path = f"models/best{model_choice[-1]}.pt"

    # PVGIS irradiance
    def fetch_irradiance(lat, lon):
        try:
            url = f"https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?lat={lat}&lon={lon}&outputformat=json&peakpower=1&loss=14"
            res = requests.get(url, timeout=10)
            data = res.json()
            return data['outputs']['totals']['fixed']['E_y'] / 365
        except:
            return None

    irradiance = fetch_irradiance(latitude, longitude)
    if irradiance:
        st.success(f"☀️ PVGIS Irradiance: {irradiance:.2f} kWh/m²/day")
    else:
        irradiance = st.number_input("Manual Irradiance (kWh/m²/day)", value=5.5)

# Map interaction
st.markdown("---")
st.subheader("🗺️ Click the map to update coordinates")

folium_map = folium.Map(
    location=[latitude, longitude],
    zoom_start=zoom,
    tiles=None
)
TileLayer(
    tiles=f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{{z}}/{{x}}/{{y}}?access_token={MAPBOX_TOKEN}",
    attr="Mapbox Satellite",
    name="Satellite",
    overlay=False,
    control=False
).add_to(folium_map)

Marker([latitude, longitude], tooltip="Selected Location").add_to(folium_map)
map_data = st_folium(folium_map, height=400, width=700)

if map_data and map_data.get("last_clicked"):
    coords = map_data["last_clicked"]
    st.session_state.map_lat = coords["lat"]
    st.session_state.map_lon = coords["lng"]

# Always display coordinates in green
st.success(f"📍 Current Coordinates: {st.session_state.map_lat:.5f}, {st.session_state.map_lon:.5f}")

# Detection section
st.markdown("### 🖼️ Fetch Image and Detect Panels")
if st.button("📸 Fetch & Analyze Image"):
    try:
        tile_size = 512
        url = (
            f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
            f"{st.session_state.map_lon},{st.session_state.map_lat},{zoom},0/{tile_size}x{tile_size}"
            f"?access_token={MAPBOX_TOKEN}"
        )
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

        # Crop out bottom 30 pixels to remove attribution
        width, height = image.size
        image = image.crop((0, 0, width, height - 30))

        # Show image at 50% width
        st.image(image, caption="📷 Fetched Satellite Image", width=350)

        with st.spinner("Detecting panels..."):
            tmp_path = "mapbox_fetch.jpg"
            image.save(tmp_path)
            detected_img, detection_df = detect_panels(tmp_path, model_path)

        if detection_df is not None and not detection_df.empty:
            detection_df["area_px"] = (detection_df["xmax"] - detection_df["xmin"]) * (detection_df["ymax"] - detection_df["ymin"])
            detection_df["area_m2"] = detection_df["area_px"] * (meters_per_pixel ** 2)
            total_area_m2 = detection_df["area_m2"].sum()

            st.image(detected_img, caption="Detected Solar Panels", width=350)
            st.dataframe(detection_df[["name", "confidence", "area_px", "area_m2"]])
            daily_kwh, yearly_kwh = estimate_energy(total_area_m2, irradiance, panel_eff, system_loss)
            st.success(f"✅ Estimated Daily Energy: {daily_kwh:.2f} kWh")
            st.info(f"📆 Estimated Yearly Energy: {yearly_kwh:.2f} kWh")
        else:
            st.warning("⚠️ No solar panels detected.")

    except Exception as e:
        st.error(f"❌ Error: {e}")

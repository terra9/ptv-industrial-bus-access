import json
import pandas as pd
import numpy as np
import streamlit as st
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
import altair as alt

st.set_page_config(page_title="Industrial Bus Accessibility – Melbourne", layout="wide")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_geojson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

geo = load_geojson("data/access_industry_catchment.geojson")
underserved_geo = load_geojson("data/access_industry_underserved.geojson")
lga = load_csv("data/lga_access_metrics.csv")

# Compute % underserved
lga["pct_underserved"] = 100 - lga["SERVED_AREA_PCT"]

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")

landuse = st.sidebar.multiselect(
    "Land use category",
    ["Industrial", "Primary Production"],
    default=["Industrial", "Primary Production"]
)

lga_list = sorted(lga["LGA_NAME_2021"].dropna().unique().tolist())
lga_choice = st.sidebar.selectbox("Select LGA", ["All"] + lga_list)

# -----------------------------
# Narrative Section
# -----------------------------
st.title("Bus Accessibility in Industrial & Primary Production Areas – Melbourne")

st.markdown("""
### Overview
This dashboard evaluates bus accessibility within **400 metres** of industrial and primary production meshblocks across metropolitan Melbourne.

**Service coverage** is measured as the percentage of industrial land area within 400m of a bus stop (area-weighted metric).

Underserved areas are defined as meshblocks with **zero bus stops within 400m**, and severity is assessed using distance to the nearest stop.
""")

# -----------------------------
# Helper Functions
# -----------------------------
def filter_features():
    features = []
    for f in geo["features"]:
        p = f["properties"]
        if p.get("MB_CAT21") not in landuse:
            continue
        if lga_choice != "All" and p.get("LGA_NAME_2021") != lga_choice:
            continue
        features.append(f)
    return features

filtered_features = filter_features()

def filter_underserved_features():
    feats = []
    for f in underserved_geo["features"]:
        p = f.get("properties", {})
        if p.get("MB_CAT21") not in landuse:
            continue
        if lga_choice != "All" and p.get("LGA_NAME_2021") != lga_choice:
            continue
        feats.append(f)
    return feats

underserved_features = filter_underserved_features()


def stops_bin_and_color(stops: float):
    """
    Based on QGIS classes:
      No Stop
      1 - 4
      4 - 7
      7 - 11
      11 - 16
      16 - 25
      25 - 38
    """
    if stops is None:
        return ("No data", "#BDBDBD")
    try:
        s = float(stops)
    except Exception:
        return ("No data", "#BDBDBD")

    if s <= 0:
        return ("No Stop", "#6B0000")      # dark maroon
    elif s <= 4:
        return ("1 - 4 Stops", "#D6E3F5")  # very light blue
    elif s <= 7:
        return ("4 - 7 Stops", "#AFC6EA")  # light blue
    elif s <= 11:
        return ("7 - 11 Stops", "#6F8FD9") # medium blue
    elif s <= 16:
        return ("11 - 16 Stops", "#2F58C8")# strong blue
    elif s <= 25:
        return ("16 - 25 Stops", "#1737B3")# darker blue
    else:
        return ("25 - 38 Stops", "#4B1FA6")# blue-purple

def dist_bin_and_color(dist_m: float):
    """
    Based on QGIS classes:
      401 - 558
      558 - 921
      921 - 1769
      1769 - 3525
      3525 - 12657
    """
    if dist_m is None:
        return ("No data", "#BDBDBD")
    try:
        d = float(dist_m)
    except Exception:
        return ("No data", "#BDBDBD")

    if d <= 558:
        return ("401 - 558 meter", "#FFFFFF")   # white
    elif d <= 921:
        return ("558 - 921 meter", "#FAD9D9")   # very light pink
    elif d <= 1769:
        return ("921 - 1769 meter", "#F5A3A3")  # light red
    elif d <= 3525:
        return ("1769 - 3525 meter", "#E34A4A") # red
    else:
        return ("3525 - 12657 meter", "#B30000")# dark red

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2 = st.tabs(["Service Intensity", "Underserved Severity"])

# =========================================================
# TAB 1 – SERVICE INTENSITY
# =========================================================
with tab1:

    col1, col2 = st.columns([1.4, 1.0])

    with col1:
        st.subheader("Bus Stops Within 400m")

        m1 = folium.Map(location=[-37.8136, 144.9631], zoom_start=9, tiles="OpenStreetMap")
        def style_map1(feature):
            props = feature.get("properties", {})
            label, color = stops_bin_and_color(props.get("STOPS_WITHIN_400M"))
            return {
                "fillColor": color,
                "color": None,          # removes polygon outline
                "weight": 0,
                "fillOpacity": 0.75
            }

        tooltip_c = GeoJsonTooltip(
            fields=["LGA_NAME_2021", "MB_CAT21", "STOPS_WITHIN_400M",
                    "ROUTES_WITHIN_400M"],
            aliases=["LGA", "Land use", "Stops within 400m",
                     "Routes within 400m"]
        )

        folium.GeoJson(
            {"type": "FeatureCollection", "features": filtered_features},
            style_function=style_map1,
            tooltip=tooltip_c
        ).add_to(m1)

        st_folium(m1, width=850, height=600)

    with col2:
        st.subheader("% Underserved Industrial Land (Area-based)")

        df = lga.copy()
        if lga_choice != "All":
            df = df[df["LGA_NAME_2021"] == lga_choice]

        df = df.sort_values("pct_underserved", ascending=False)

        # new column to simplify the percentage display
        df["pct_underserved_display"] = df["pct_underserved"].round(1).astype(str) + "%"
        df["underserved_area_display"] = df["UNDERSERVED_AREA"].round(1).astype(str) + " km²"
        df["total_area_display"] = df["TOTAL_AREA_SIZE"].round(1).astype(str) + " km²"

        chart1 = (
            alt.Chart(df.head(10))
            .mark_bar(color="#7F0000")
            .encode(
                y=alt.Y("LGA_NAME_2021:N", sort="-x", title="LGA"),
                x=alt.X("pct_underserved:Q", title="% underserved (area-based)", axis=alt.Axis(format=".1f")),
                tooltip=[
                    alt.Tooltip("LGA_NAME_2021:N", title="LGA"),
                    alt.Tooltip("pct_underserved_display:N", title="% Underserved"),
                    alt.Tooltip("total_area_display:N", title="Total Size"),
                    alt.Tooltip("underserved_area_display:N", title="Underserved Size")
                ]
            )
        )

        chart1 = chart1.configure_axis(
            labelColor="white",
            titleColor="white"
        ).configure_title(
            color="white"
        )

        st.altair_chart(chart1, use_container_width=True)

        st.markdown("---")

        st.markdown("""
        **Interpretation**

        Overall, only **30.23%** of industrial and primary production mesh blocks are within 400 metres of a bus stop. Areas closer to Melbourne’s inner and middle suburbs demonstrate higher access levels, with served blocks averaging **6.4 stops** and **2.9 routes per stop**, indicating strong service intensity where coverage exists.

        However, approximately **69.77%** of blocks fall outside the 400-metre threshold, revealing significant accessibility gaps across western growth corridors (Wyndham, Melton, Moorabool), northern fringe LGAs (Mitchell, Murrindindi, Macedon Ranges), and south-eastern areas (Cardinia, Mornington Peninsula).

        These patterns align with Melbourne’s industrial zoning structure, where outer-suburban manufacturing and logistics zones have expanded faster than transit provision (Grodach & Martin, 2020).
        
        **Reference:**  
        Grodach, C., & Martin, D. (2020). Zoning in on urban manufacturing: industry location and change among low-tech, high-touch industries in Melbourne, Australia. *Urban Geography*, 42(4), 1–23. https://doi.org/10.1080/02723638.2020.1723329.
        """)

# =========================================================
# TAB 2 – UNDERSERVED SEVERITY
# =========================================================
with tab2:

    col1, col2 = st.columns([1.4, 1.0])

    with col1:
        st.subheader("Distance to Nearest Bus Stop (Underserved Blocks)")

        m2 = folium.Map(location=[-37.8136, 144.9631], zoom_start=9, tiles="OpenStreetMap")
        def style_map2(feature):
            props = feature.get("properties", {})
            label, color = dist_bin_and_color(props.get("NEAREST_DISTANCE_STOP"))
            return {
                "fillColor": color,
                "color": None,          # removes polygon outline
                "weight": 0,
                "fillOpacity": 0.75
            }
        
        tooltip_uc = GeoJsonTooltip(
            fields=["LGA_NAME_2021", "MB_CAT21", "MB_CODE21", "NEAREST_DISTANCE_STOP"],
            aliases=["LGA", "Land use", "Meshblock", "Nearest stop distance (m)"],
            localize=True,
            sticky=False
        )

        folium.GeoJson(
            {"type": "FeatureCollection", "features": underserved_features},
            style_function=style_map2,
            tooltip=tooltip_uc
        ).add_to(m2)

        st_folium(m2, width=850, height=600)

    with col2:
        st.subheader("Median Distance to Nearest Stop (Underserved Blocks Only)")

        # Compute dynamically from GeoJSON
        rows = []
        for f in underserved_features:
            p = f["properties"]
            rows.append({
                "lga": p.get("LGA_NAME_2021"),
                "distance": p.get("NEAREST_DISTANCE_STOP")
            })

        dist_df = pd.DataFrame(rows)

        if not dist_df.empty:
            median_df = (
                dist_df.groupby("lga")["distance"]
                .median()
                .reset_index()
                .sort_values("distance", ascending=False)
            )

            median_df["distance_display"] = median_df["distance"].round(1).astype(str) + (" m")

            chart2 = (
                alt.Chart(median_df.head(10))
                .mark_bar()
                .encode(
                    y=alt.Y("lga:N", sort="-x", title="LGA"),
                    x=alt.X("distance:Q", title="Median distance (m)"),
                    tooltip=[alt.Tooltip("lga:N", title="LGA"), 
                             alt.Tooltip("distance_display:N", title="Distance")]
                )
            )

            st.altair_chart(chart2, use_container_width=True)
        else:
            st.write("No underserved blocks under current filters.")

        st.markdown("---")

        st.markdown("""
        **Interpretation**

        Among underserved mesh blocks, the average nearest bus stop distance is **2,066.7 metres**, more than five times the standard 400-metre walkable threshold. In several outer LGAs, median distances exceed **3 kilometres**, indicating near absence of bus services in some industrial zones.

        These areas represent growing employment precincts. Persistent service gaps risk reinforcing private vehicle dependency, increasing congestion and emissions, and limiting equitable workforce access.
        """)
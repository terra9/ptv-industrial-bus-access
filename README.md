# Industrial Bus Accessibility – Melbourne (Streamlit Dashboard)

This repository contains an interactive dashboard (Streamlit + Folium + Altair) analysing bus accessibility for industrial and primary production meshblocks in metropolitan Melbourne using 2021 Australian Boundary Data and Mesh Block data based on ASGS from Australia Bureau of Statistics, along with bus services, routes, schedules, and stop locations data based on PTV Victoria data gained GTFS site. The PTV data itself is based on December 2025 data because it is the most recently available and complete bus services data that we can use.

This Project is an expanded version of the final assignment of Monash University Advanced Database Technology Unit (FIT5137) about PTV Bus Accessibility in Greater Melbourne, which can be focused based on the land use type¹. This Project uses updated data and Snowflake to store, process the data, analyze and generate `access_industry_catchment.geojson`,`access_industry_underserved.geojson`, `lga_access_metrics.csv`. The generated data are then used for creating a custom visualization based on streamlit and folium for greater flexibility.

## Data files required
Place these files inside the `data/` folder:
- `access_industry_catchment.geojson`
- `access_industry_underserved.geojson`
- `lga_access_metrics.csv`

## How to Run locally

### For Windows User (Command Prompt recommended)
1) Clone this repo and move into the folder:
```bat
git clone https://github.com/terra9/ptv-industrial-bus-access.git
cd ptv-industrial-bus-access
```
2) Create and activate a virtual environment:
```bat
py -m venv .venv
call .venv\Scripts\activate.bat
```

3) install dependencies:
```bat
python -m pip install -r requirements.txt
```

4) Run the app:
```bat
python -m streamlit run app.py
```

### For MacOS/Linux User
1) Clone this repo and move into the folder:
```bash
git clone https://github.com/terra9/ptv-industrial-bus-access.git
cd ptv-industrial-bus-access
```

2) Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) install dependencies:
```bash
python -m pip install -r requirements.txt
```

4) Run the app:
```bash
python -m streamlit run app.py
```


## Reference
¹Monash University. (2025, August 26). *FIT5137 S2 2025 Assignment 3: PTV Assignment (Weight = 35%)*. Monash University. 

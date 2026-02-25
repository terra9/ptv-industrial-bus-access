# Industrial Bus Accessibility – Melbourne (Streamlit Dashboard)

This repository contains an interactive dashboard (Streamlit + Folium + Altair) analysing bus accessibility for industrial and primary production meshblocks in metropolitan Melbourne.

## Data files required
Place these files inside the `data/` folder:
- `access_industry_catchment.geojson`
- `access_industry_underserved.geojson`
- `lga_access_metrics.csv`

## Run locally

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
# SismaLab Suite - L.A.I.C. Sentinel

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21049744.svg)](https://doi.org/10.5281/zenodo.21049744)

**Open-source Python WebGIS for the automated multi-layer vertical analysis of Lithosphere-Atmosphere-Ionosphere Coupling (L.A.I.C.) environmental anomalies and hypothesis generation.**

---

## 1. Overview
**L.A.I.C. Sentinel** is a cloud-based WebGIS platform (part of the *SismaLab Suite* developed by the *Osservatorio Geofisico Valle del Liri - OGVL*) designed for the exploratory detection and multi-layer vertical filtering of environmental and thermodynamic transients prior to seismic events.

By integrating **Google Earth Engine (GEE)** serverless APIs, the architecture dynamically processes five multi-layer parameters within the empirical Dobrovolsky preparation radius ($R = 10^{0.43 M}$):
1. **Lithosphere (NDWI):** Surface moisture (10–30 m resolution) from harmonized Sentinel-2 (`COPERNICUS/S2_SR_HARMONIZED`) and Landsat 5/7/8 (`LANDSAT/LC08/C02/T1_L2`, `LT05`, `LE07`) collections, masked for permanent water bodies (`JRC/GSW1_4/GlobalSurfaceWater`).
2. **Surface (Nighttime LST):** Nocturnal Land Surface Temperature (1 km resolution, °C) from `MODIS/061/MOD11A1` (`LST_Night_1km`).
3. **Troposphere (Precipitation):** Daily rainfall accumulation (mm/day, ~5.5 km resolution) from `UCSB-CHG/CHIRPS/DAILY`.
4. **Stratosphere (AOD / UV Aerosol Index):** Temporal switch at July 10, 2018 between NASA MERRA-2 Aerosol Optical Depth (`NASA/GSFC/MERRA/aer/2`, `TOTEXTTAU` at 550 nm) for pre-2018 historical events and Sentinel-5P TROPOMI UV Absorbing Aerosol Index (`COPERNICUS/S5P/OFFL/L3_AER_AI`, `absorbing_aerosol_index`) for post-2018 events.
5. **Mesopause (OLR):** Outgoing Longwave Radiation ($\text{W/m}^2$) from NASA MERRA-2 (`NASA/GSFC/MERRA/rad/2`, `LWTUP`).

The statistical engine computes a **10-year rolling monthly Z-Score**, a normalized dimensionless **Net NDWI Z-Score** ($Z_{\text{Net,NDWI}} = Z_{\text{NDWI}} - \max(0, Z_{\text{Rain,7d}})$), and applies a site-specific **Zero-Signal Calibration** protocol (*Analogous Year of Quiet* + fixed $+0.03$ radiometric reflectance tolerance evaluated exclusively on non-imputed, cloud-free satellite passes: `NDWI_Points != NaN`) to classify observations into five mutually exclusive diagnostic scenarios (Scenarios 1–5).

---

## 2. Accessing the Live Cloud Platform (For Peer Reviewers)
To allow immediate testing and full reproducibility without local GEE authentication setup, a live cloud instance is hosted at:
👉 **[https://sismalab-ogvl.onrender.com/](https://sismalab-ogvl.onrender.com/)**

* **Reviewer Access Password:** `!Review26$`
* **Note on Server Wake-Up:** The live instance runs on a cloud container that hibernates during inactivity; please allow up to 40–60 seconds on first load.

---

## 3. Case Study Reproducibility Parameters (Table 2 of the Manuscript)
All case studies presented in the manuscript query the real satellite archives dynamically via Google Earth Engine. To reproduce the exact diagnostic outputs on the live platform (or locally via `streamlit run app.py`), enter the following configuration parameters:

| Case Study (Mode) | Target Date | Calibration Window (Baseline) | Physiological NDWI Peak | Set NDWI Cutoff Threshold | Reference Coordinates (Lat, Lon) |Mw |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **L'Aquila 2009** (Hindcast) | `2009/04/06` | Silent spring (`2004/04/06`) | ~0.21 | **0.24** | `42.3420`, `13.3800` | `6.1` |
| **Emilia 2012** (Hindcast) | `2012/05/20` | Silent spring (`2008/05/20`) | ~0.25 | **0.28** | `44.8890`, `11.2280` | `5.9` |
| **Amatrice 2016** (Hindcast) | `2016/08/24` | Silent summer (`2015/08/24`) | ~0.27 | **0.30** | `42.6940`, `13.2330` | `6.0` |
| **Gorkha 2015** (Hindcast) | `2015/04/25` | Silent spring (`2014/04/25`) | ~0.17 | **0.20** | `28.1470`, `84.7080` | `7.8` |
| **Montecassino 2026** (Nowcast) | `2026/06/25` | Spring 2022 (`2022/06/25`) | ~0.14 | **0.17** | `41.4905`, `13.8134` | `4.0` |

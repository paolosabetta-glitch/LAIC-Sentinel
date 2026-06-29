# SismaLab Suite - L.A.I.C. Sentinel
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21049744.svg)](https://doi.org/10.5281/zenodo.21049744)

**Open-source Python WebGIS for the automated stratigraphic analysis of Lithosphere-Atmosphere-Ionosphere Coupling (L.A.I.C.) anomalies.**

## 1. Overview
L.A.I.C. Sentinel is a cloud-based experimental platform designed to detect and filter thermodynamic pre-seismic anomalies. This tool bridges geosciences and high-performance computing by integrating Google Earth Engine (GEE) APIs to dynamically process five key parameters (NDWI, LST, Precipitation, AOD, OLR). 

It uses a rigorous statistical engine based on a historicized monthly Z-Score and Zero-Signal Calibration protocols to filter out meteorological background noise and isolate actual tectonic dilatancy.

## 2. Accessing the Live Platform (Peer-Review)
For the peer-review process, a fully functional live instance of the application is available at the following link:
🔗 **https://sismalab-ogvl.onrender.com/**

**Important Notes for Reviewers:**
* **Master Password:** Please use the password **`!Review26$`** to unlock the interface.
* **Server Hibernation:** The live demo is hosted on a free cloud instance. It may take up to 60 seconds to wake up from hibernation upon first access. Please be patient while the environment loads.
* **Default Dataset:** Upon initialization, the platform automatically loads the dummy dataset for the **2009 L'Aquila Earthquake** as the default demonstrative scenario.

## 3. Installation and Requirements
The application is built in Python and deployed via the Streamlit framework.
To run the code locally, ensure you have Python 3.8+ installed, then install the required dependencies:
```bash
pip install -r requirements.txt

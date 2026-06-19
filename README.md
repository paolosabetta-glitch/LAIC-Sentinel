# SismaLab Suite - L.A.I.C. Sentinel

**Open-source Python WebGIS for the automated stratigraphic analysis of Lithosphere-Atmosphere-Ionosphere Coupling (L.A.I.C.) anomalies.**

## 1. Overview
L.A.I.C. Sentinel is a cloud-based experimental platform designed to detect and filter thermodynamic pre-seismic anomalies. This tool bridges geosciences and high-performance computing by integrating Google Earth Engine (GEE) APIs to dynamically process five key parameters (NDWI, LST, Precipitation, AOD, OLR). 

It uses a rigorous statistical engine based on a historicized monthly Z-Score and Zero-Signal Calibration protocols to filter out meteorological background noise and isolate actual tectonic dilatancy.

## 2. Installation and Requirements
The application is built in Python and deployed via the Streamlit framework.
To run the code locally, ensure you have Python 3.8+ installed, then install the required dependencies:
```bash
pip install -r requirements.txt

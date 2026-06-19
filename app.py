import streamlit as st
import ee
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from google.oauth2 import service_account
import os
import base64
import streamlit.components.v1 as components

# --- MULTILINGUAL DICTIONARY (L.A.I.C. TRANSLATION ENGINE) ---
LANG_DICT = {
    "IT": {
        "obs_name": """- Osservatorio Geofisico Valle del Liri | <a href='https://www.osservageoliri.it' target='_blank' style='color: #a0c3d2; text-decoration: none;'>www.osservageoliri.it</a>""",
        "author": """Ideazione e Sviluppo: <br><b style='color: #ff5252;'>Paolo Sabetta</b> (2026)<br><a href='mailto:paolo.sabetta@gmail.com' style='color: #a0a0a0; text-decoration: none; font-size: 12px;'>paolo.sabetta@gmail.com</a>""",
        "disclaimer": """L.A.I.C. Sentinel (SismaLab Suite) è uno strumento di ricerca scientifica <b>sperimentale</b> dedicato allo studio dell'accoppiamento Litosfera-Atmosfera. <b>Il modello algoritmico è attualmente in fase di validazione accademica (Pre-Peer Review).</b> I dati satellitari elaborati hanno finalità esclusivamente di indagine retrospettiva: non costituiscono in alcun modo un sistema di allerta sismica precoce (Early Warning) o una previsione deterministica. L'Osservatorio Geofisico Valle del Liri declina ogni responsabilità per l'uso improprio dei dati forniti. ©️ OGVL.""",
        "auth_title": """ACCESSO RISERVATO - OSSERVATORIO GEOFISICO VALLE DEL LIRI""",
        "auth_prompt": """Inserire la Password di Rete per accedere a L.A.I.C. Sentinel""",
        "auth_err": """⛔ Password errata o non autorizzata.""",
        "btn_run": """AVVIA ELABORAZIONE""",
        "btn_logout": """LOGOUT""",
        "btn_download": """⬇️ SCARICA REPORT DI SINTESI""",
        "rep_title": """REPORT SINTESI DIAGNOSTICA L.A.I.C.""",
        "rep_params": """PARAMETRI DI INPUT""",
        "mode_title": """**MODALITÀ DI RICERCA:**""",
        "mode_1": """Analisi Storica (Con Mainshock)""",
        "mode_2": """Monitoraggio / Calibrazione Baseline""",
        "win_title": """📅 **Finestra Temporale Automatica**""",
        "date_ms": """💥 **Imposta la Data del Sisma:**""",
        "date_obs": """🔍 **Imposta la Data di Osservazione:**""",
        "geo_title": """🎯 **Setup Geografico e Area**""",
        "lat_epi": """**Latitudine**<br>Epicentro:""",
        "lat_center": """**Latitudine**<br>Centro Area:""",
        "lon_epi": """**Longitudine**<br>Epicentro:""",
        "lon_center": """**Longitudine**<br>Centro Area:""",
        "mag_ms": """**Magnitudo del<br>Sisma (M):**""",
        "mag_scan": """**Magnitudo di Scansione<br>(Raggio Ascolto):**""",
        "help_rad": """ℹ️ Come funziona il Raggio di Ascolto?""",
        "wait_msg": """⏳ Estrazione dati satellitari in corso. L'operazione richiede alcuni secondi...""",
        "ok_msg": """✅ Elaborazione completata con successo!""",
        "tog_anom": """Mostra Filtri Anomalie (Colori)""",
        "tog_grid": """Mostra Reticolato Giornaliero""",
        "help_ndwi": """Guida al Mascheramento Ambientale\nSe il grafico NDWI mostra picchi anomali prolungati oltre quota 0.30, incrocia i dati con gli altri pannelli per escludere falsi positivi:\n\n1. Incrocio Termico (Firma Criosferica): Se la Temperatura Notturna (LST, Pannello 4) è prossima o inferiore a 0°C, il sensore sta rilevando copertura nevosa o ghiaccio.\n2. Incrocio Meteorologico (Firma Antropica): Se la Temperatura (LST) è estiva e vi è saturazione di Aerosol (AOD, Pannello 2), l'anomalia idrica è con altissima probabilità imputabile a irrigazione agricola intensiva.\n\nAzione richiesta: Calibra sempre la soglia sul valore fisiologico massimo del suolo nudo sgelato, ignorando i plateau invernali.""",
        "note_ndwi": """⚠️ <b>Nota Operativa:</b> Valori di fondo naturali prossimi o superiori a 0.30 indicano severa interferenza criosferica (neve/ghiaccio) o saturazione idrologica estrema, non riconducibili a sola dilatanza tettonica.""",
        "t_olr": """1. Alta Atmosfera / Mesopausa: RADIAZIONE TERMICA OLR (NASA MERRA-2)""",
        "t_aod": """2. Stratosfera: GAS E AEROSOL (NASA MERRA-2 / Copernicus S5P)""",
        "t_rain": """3. Troposfera: PRECIPITAZIONI REALI (mm)""",
        "t_lst": """4. Superficie: TEMPERATURA NOTTURNA DEL SUOLO (°C MODIS LST)""",
        "t_ndwi": """5. Litosfera: UMIDITÀ SUPERFICIALE (Ottico NDWI - Terraferma)""",
        "main_title": """<b>Cruscotto di Osservazione dello Stress Geofisico</b>""",
        "sub_title": """Analisi Stratigrafica L.A.I.C. (Lithosphere-Atmosphere Coupling)""",
        "diag_tit": """SINTESI DIAGNOSTICA L.A.I.C.""",
        "fase_1": """1. Stato Crostale (Anomalie Rilevate)""",
        "fase_2": """2. Stato Atmosferico (Anomalie Rilevate)""",
        "manual_title": """📖 Guida all'Interpretazione L.A.I.C.""",
        "manual_text": """**Come leggere il Cruscotto L.A.I.C. Sentinel**
Il modello L.A.I.C. (Lithosphere-Atmosphere-Ionosphere Coupling) postula che la preparazione di un forte evento sismico generi una catena di anomalie termodinamiche dal sottosuolo fino allo spazio. La piattaforma utilizza il calcolo dello Z-Score* per isolare queste anomalie dal normale rumore meteorologico stagionale.

<div style="color: #ff5252; border: 1px solid #ff5252; padding: 15px; border-radius: 4px; margin-top: 10px; margin-bottom: 15px; background-color: rgba(255, 82, 82, 0.05);">
<b>🚨 RACCOMANDAZIONE METODOLOGICA CRUCIALE (Zero-Signal Calibration):</b><br>
Si suggerisce vivamente all'operatore di non avviare alcuna analisi senza aver preventivamente eseguito una <b>calibrazione sito-specifica della baseline</b> per escludere il rumore di fondo naturale (neve, piogge estreme, irrigazione agricola) ed evitare false attivazioni dello Z-Score.
</div>

**I PROTOCOLLI OPERATIVI DI L.A.I.C. SENTINEL:**
L'uso della piattaforma prevede due percorsi d'indagine distinti:

**PERCORSO A: HINDCAST (Analisi Storica e Validazione)**
_Scopo: Studiare a posteriori un terremoto noto (es. L'Aquila 2009)._
* **Fase 1 (Calibrazione):** Impostare su <i>Monitoraggio / Calibrazione Baseline</i>. Scegliere una finestra temporale della <b>stessa stagione</b>, ma di un <b>anno differente e sismicamente silente</b>. Leggere il picco NDWI fisiologico massimo raggiunto in assenza di nuvole e bloccare la "Soglia di Taglio NDWI" appena sopra quel valore.
* **Fase 2 (Analisi):** Impostare su <i>Analisi Storica (Con Mainshock)</i>. Inserire la data del terremoto, lasciando la levetta della Soglia invariata. Se il sistema rileva anomalie persistenti oltre questa soglia, la dilatanza tettonica è confermata.

**PERCORSO B: NOWCAST (Monitoraggio in Tempo Reale)**
_Scopo: Sorveglianza operativa di un'area a rischio alla ricerca di stress crostale in atto._
* **Fase 1 (Historical Analog Calibration):** Impostare su <i>Monitoraggio / Calibrazione Baseline</i>. Cercare negli archivi passati un <b>"Anno Analogo di Quiete"</b> per l'area target (es. la stessa stagione dell'anno precedente). Leggere il picco NDWI e bloccare la levetta della Soglia.
* **Fase 2 (Sorveglianza):** Rimanere in modalità <i>Monitoraggio / Calibrazione Baseline</i>. Cambiare solo la Data di Osservazione impostando <b>la data di oggi</b>. La piattaforma analizzerà gli ultimi 90 giorni. Se la soglia calibrata sull'anno analogo viene superata, la crosta è in fase di deformazione attiva.

**📌 Interpretazione del Grafico NDWI (Puntini Bianchi):**
La linea azzurra dell'NDWI presenta dei piccoli "puntini bianchi". Essi indicano i **passaggi reali** in cui il satellite ha acquisito un dato valido senza nuvole. Se i puntini sono radi e la linea azzurra rimane piatta per molti giorni, una fitta copertura nuvolosa ha accecato il sensore (confermabile dalle piogge nel Pannello 3). L'algoritmo manterrà in memoria l'ultima lettura utile (Forward Fill).

**Logica Matematica degli Allarmi:**
* **SUOLO ATTIVO:** Almeno 1 giorno di anomalia NDWI *OPPURE* 3 giorni di anomalia LST.
* **ATMOSFERA ATTIVA:** Almeno 3 giorni di anomalia AOD *OPPURE* 3 giorni di anomalia OLR.

---
_**\* Z-Score:** Metodo statistico che misura lo scostamento dalla media storica mensile._
_**\*\* Formula di Dobrovolsky:** R = 10^(0.43 × M). Stima il raggio di preparazione in base alla magnitudo._""",
        "scen_1_tit": """SCENARIO 1 (Accoppiamento con Rilascio di Fluidi)""",
        "scen_1_txt": """Rilevata anomalia idrica superficiale compatibile con la mobilitazione di acquiferi profondi. Il degassamento termico associato ha innescato una chiara catena termodinamica stratosferica. Accoppiamento L.A.I.C. (Lithosphere-Atmosphere-Ionosphere Coupling) pienamente confermato.<br><br><span style='color:#a0a0a0;'><i>(Esempio di riferimento: Evento sismico dell'Aquila, Italia - 6 aprile 2009, Mw 6.1 [Catalogo Ufficiale INGV]. Rottura di faglia caratterizzata da marcata mobilitazione di fluidi crostali e dilatanza).</i></span>""",
        "scen_2_tit": """SCENARIO 2 (Accoppiamento Termico-Radiativo)""",
        "scen_2_txt": """Degassamento termico crostale rilevato in assenza di espulsione idrica superficiale. I gas vettori hanno permeato l'atmosfera innescando un severo blocco radiativo (OLR). Dinamica compatibile con deformazioni tettoniche profonde o sepolte.<br><br><span style='color:#a0a0a0;'><i>(Esempio di riferimento: Evento sismico dell'Emilia-Romagna, Italia - 20 maggio 2012, Mw 5.9 [Catalogo Ufficiale INGV]. Sisma generato da una faglia "cieca", sepolta sotto spessi strati di sedimenti alluvionali che hanno bloccato la superficializzazione dell'acqua ma non del calore).</i></span>""",
        "scen_3_tit": """SCENARIO 3 (Attività Litosferica Isolata)""",
        "scen_3_txt": """Attività litosferica e micro-fratturativa isolata. La deformazione crostale ha generato calore/fluidi in superficie, ma l'energia non ha raggiunto l'intensità o la concentrazione di gas necessaria per innescare l'accoppiamento L.A.I.C. (Lithosphere-Atmosphere-Ionosphere Coupling) con l'alta atmosfera.<br><br><span style='color:#a0a0a0;'><i>(Esempio di riferimento: Moti deformativi di assestamento o sciami sismici di media-bassa magnitudo che si esauriscono nella bassa troposfera).</i></span>""",
        "scen_4_tit": """SCENARIO 4 (Anomalia Atmosferica Esterna)""",
        "scen_4_txt": """Anomalia atmosferica isolata in assenza di attività litosferica. Le variazioni di AOD e/o OLR registrate non presentano una "radice" termica o idrica al suolo (LST e NDWI nella norma). Dinamica incompatibile con il modello L.A.I.C. (Lithosphere-Atmosphere-Ionosphere Coupling): si tratta con altissima probabilità di fluttuazioni meteorologiche estreme (es. anomale ondate di calore) o fattori esterni di natura antropica (es. inquinamento, incendi di grandi dimensioni).""",
        "scen_5_tit": """SCENARIO 5 (Assenza di Anomalie L.A.I.C.)""",
        "scen_5_txt": """Nessuna anomalia termodinamica o idrogeochimica di rilievo. I parametri registrati rientrano nelle fisiologiche fluttuazioni stagionali e meteorologiche di fondo. Accoppiamento L.A.I.C. (Lithosphere-Atmosphere-Ionosphere Coupling) assente.""",
        "no_data": """DATI NON DISPONIBILI."""
    },
    "EN": {
        "obs_name": """- Valle del Liri Geophysical Observatory | <a href='https://www.osservageoliri.it' target='_blank' style='color: #a0c3d2; text-decoration: none;'>www.osservageoliri.it</a>""",
        "author": """Concept & Development: <br><b style='color: #ff5252;'>Paolo Sabetta</b> (2026)<br><a href='mailto:paolo.sabetta@gmail.com' style='color: #a0a0a0; text-decoration: none; font-size: 12px;'>paolo.sabetta@gmail.com</a>""",
        "disclaimer": """L.A.I.C. Sentinel (SismaLab Suite) is an <b>experimental</b> scientific research tool dedicated to the study of Lithosphere-Atmosphere coupling. <b>The algorithmic model is currently undergoing academic validation (Pre-Peer Review).</b> Processed satellite data are strictly for retrospective investigation purposes: they do not constitute an Early Warning system or a deterministic prediction. The Valle del Liri Geophysical Observatory declines all responsibility for improper use of the data. ©️ OGVL.""",
        "auth_title": """RESTRICTED ACCESS - VALLE DEL LIRI GEOPHYSICAL OBSERVATORY""",
        "auth_prompt": """Enter Network Password to access L.A.I.C. Sentinel""",
        "auth_err": """⛔ Incorrect or unauthorized password.""",
        "btn_run": """START PROCESSING""",
        "btn_logout": """LOGOUT""",
        "btn_download": """⬇️ DOWNLOAD SUMMARY REPORT""",
        "rep_title": """L.A.I.C. DIAGNOSTIC SUMMARY REPORT""",
        "rep_params": """INPUT PARAMETERS""",
        "mode_title": """**SEARCH MODE:**""",
        "mode_1": """Historical Analysis (With Mainshock)""",
        "mode_2": """Monitoring / Baseline Calibration""",
        "win_title": """📅 **Automatic Time Window**""",
        "date_ms": """💥 **Set Earthquake Date:**""",
        "date_obs": """🔍 **Set Observation Date:**""",
        "geo_title": """🎯 **Geographic Setup & Area**""",
        "lat_epi": """**Latitude**<br>Epicenter:""",
        "lat_center": """**Latitude**<br>Area Center:""",
        "lon_epi": """**Longitude**<br>Epicenter:""",
        "lon_center": """**Longitude**<br>Area Center:""",
        "mag_ms": """**Earthquake<br>Magnitude (M):**""",
        "mag_scan": """**Scanning Magnitude<br>(Listening Radius):**""",
        "help_rad": """ℹ️ How does the Listening Radius work?""",
        "wait_msg": """⏳ Extracting satellite data. This operation takes a few seconds...""",
        "ok_msg": """✅ Processing successfully completed!""",
        "tog_anom": """Show Anomaly Filters (Colors)""",
        "tog_grid": """Show Daily Grid""",
        "help_ndwi": """Environmental Masking Guide\nIf the NDWI graph shows prolonged anomalous peaks beyond 0.30, cross-reference the data with other panels to rule out false positives.\nAlways calibrate the threshold on the maximum physiological value of bare thawed soil, ignoring winter plateaus.""",
        "note_ndwi": """⚠️ <b>Operational Note:</b> Natural background values near or above 0.30 indicate severe cryospheric interference (snow/ice) or extreme hydrological saturation, not attributable to tectonic dilatancy alone.""",
        "t_olr": """1. High Atmosphere / Mesopause: OLR THERMAL RADIATION (NASA MERRA-2)""",
        "t_aod": """2. Stratosphere: GAS AND AEROSOL (NASA MERRA-2 / Copernicus S5P)""",
        "t_rain": """3. Troposphere: REAL PRECIPITATION (mm)""",
        "t_lst": """4. Surface: NIGHT SOIL TEMPERATURE (°C MODIS LST)""",
        "t_ndwi": """5. Lithosphere: SURFACE MOISTURE (NDWI Optical - Mainland)""",
        "main_title": """<b>Geophysical Stress Observation Dashboard</b>""",
        "sub_title": """L.A.I.C. Stratigraphic Analysis (Lithosphere-Atmosphere Coupling)""",
        "diag_tit": """L.A.I.C. DIAGNOSTIC SUMMARY""",
        "fase_1": """1. Crustal State (Anomalies Detected)""",
        "fase_2": """2. Atmospheric State (Anomalies Detected)""",
        "manual_title": """📖 L.A.I.C. Interpretation Guide""",
        "manual_text": """**How to read the L.A.I.C. Sentinel Dashboard**
The L.A.I.C. (Lithosphere-Atmosphere-Ionosphere Coupling) model postulates that the preparation of a strong seismic event generates a chain of thermodynamic anomalies from the subsoil to space. The platform uses Z-Score* calculations to isolate these anomalies.

<div style="color: #ff5252; border: 1px solid #ff5252; padding: 15px; border-radius: 4px; margin-top: 10px; margin-bottom: 15px; background-color: rgba(255, 82, 82, 0.05);">
<b>🚨 CRUCIAL METHODOLOGICAL RECOMMENDATION (Zero-Signal Calibration):</b><br>
It is strongly recommended not to start any analysis without first performing a <b>site-specific baseline calibration</b>. The operator must set the platform to <i>Monitoring</i> mode on a distinct time window, chronologically distant from the seismic event, corresponding to a known phase of geological quiet for that area. This is essential to quantify natural background noise (cryospheric, agronomic, or anthropogenic) and avoid Z-Score over-activation.
</div>

**L.A.I.C. SENTINEL OPERATIONAL PROTOCOLS:**
The platform is designed for two distinct paths:

**PATH A: HINDCAST (Historical Analysis)**
_Purpose: Retrospective study of a known earthquake._
* **Phase 1 (Calibration):** Set to <i>Monitoring / Baseline Calibration</i>. Choose a time window in the <b>same season</b> but a <b>different, seismically quiet year</b>. Read the maximum NDWI peak without clouds and lock the Threshold slider just above it.
* **Phase 2 (Analysis):** Set to <i>Historical Analysis</i>. Enter the earthquake date, leaving the Threshold slider untouched. If the system detects anomalies above this threshold, tectonic dilatancy is confirmed.

**PATH B: NOWCAST (Real-Time Monitoring)**
_Purpose: Operational surveillance of an area for ongoing crustal stress._
* **Phase 1 (Historical Analog Calibration):** Set to <i>Monitoring / Baseline Calibration</i>. Find a past <b>"Analogous Year of Quiet"</b> for the target area. Read the NDWI peak and lock the slider.
* **Phase 2 (Surveillance):** Remain in <i>Monitoring</i> mode. Change the Observation Date to <b>today's date</b>. The platform will analyze the last 90 days. If the calibrated threshold is breached, active deformation is suspected.

**📌 Interpreting the NDWI Graph (White Dots):**
The blue NDWI line features small "white dots". These indicate **real passes** where the optical satellite framed the area without clouds. If the dots are sparse and the blue line remains horizontal for many days, thick cloud cover blinded the sensor. The algorithm keeps the last useful reading in memory (Forward Fill).

**Mathematical Logic of Alerts:**
* **ACTIVE SOIL:** At least 1 day of NDWI anomaly *OR* at least 3 days of LST anomaly.
* **ACTIVE ATMOSPHERE:** At least 3 days of AOD anomaly *OR* at least 3 days of OLR anomaly.

---
_**\* Z-Score:** Statistical method measuring standard deviations from the historical mean._
_**\*\* Dobrovolsky's Formula:** R = 10^(0.43 × M). Estimates preparation area radius._""",
        "scen_1_tit": """SCENARIO 1 (Coupling with Fluid Release)""",
        "scen_1_txt": """Surface water anomaly detected, compatible with deep aquifers mobilization. Thermal degassing triggered a clear stratospheric chain. L.A.I.C. fully confirmed.<br><br><span style='color:#a0a0a0;'><i>(Example: L'Aquila, Italy - April 6, 2009, Mw 6.1).</i></span>""",
        "scen_2_tit": """SCENARIO 2 (Thermal-Radiative Coupling)""",
        "scen_2_txt": """Crustal thermal degassing detected without water expulsion. Carrier gases permeated the atmosphere triggering a severe radiative block (OLR).<br><br><span style='color:#a0a0a0;'><i>(Example: Emilia-Romagna, Italy - May 20, 2012, Mw 5.9).</i></span>""",
        "scen_3_tit": """SCENARIO 3 (Isolated Lithospheric Activity)""",
        "scen_3_txt": """Isolated lithospheric activity. Energy did not reach the intensity necessary to trigger L.A.I.C. with the upper atmosphere.""",
        "scen_4_tit": """SCENARIO 4 (External Atmospheric Anomaly)""",
        "scen_4_txt": """Isolated atmospheric anomaly without a thermal or hydrological "root" at the ground. Incompatible with L.A.I.C.: highly probable extreme meteorological fluctuations or anthropogenic factors.""",
        "scen_5_tit": """SCENARIO 5 (Absence of L.A.I.C. Anomalies)""",
        "scen_5_txt": """No significant anomalies. Parameters fall within background fluctuations. L.A.I.C. absent.""",
        "no_data": """DATA NOT AVAILABLE."""
    },
    "FR": {
        "obs_name": """- Observatoire Géophysique Valle del Liri | <a href='https://www.osservageoliri.it' target='_blank' style='color: #a0c3d2; text-decoration: none;'>www.osservageoliri.it</a>""",
        "author": """Conception et Développement: <br><b style='color: #ff5252;'>Paolo Sabetta</b> (2026)<br><a href='mailto:paolo.sabetta@gmail.com' style='color: #a0a0a0; text-decoration: none; font-size: 12px;'>paolo.sabetta@gmail.com</a>""",
        "disclaimer": """L.A.I.C. Sentinel (SismaLab Suite) est un outil de recherche scientifique <b>expérimental</b> dédié à l'étude du couplage Lithosphère-Atmosphère. <b>Le modèle algorithmique est actuellement en phase de validation académique (Pre-Peer Review).</b> Les données satellitaires traitées sont strictement destinées à une investigation rétrospective : elles ne constituent pas un système d'alerte précoce (Early Warning) ou une prévision déterministe. L'Observatoire Géophysique Valle del Liri décline toute responsabilité pour l'utilisation abusive des données. ©️ OGVL.""",
        "auth_title": """ACCÈS RESTREINT - OBSERVATOIRE GÉOPHYSIQUE VALLE DEL LIRI""",
        "auth_prompt": """Entrez le mot de passe réseau pour accéder à L.A.I.C. Sentinel""",
        "auth_err": """⛔ Mot de passe incorrect ou non autorisé.""",
        "btn_run": """LANCER LE TRAITEMENT""",
        "btn_logout": """DÉCONNEXION""",
        "btn_download": """⬇️ TÉLÉCHARGER LE RAPPORT""",
        "rep_title": """RAPPORT DE SYNTHÈSE DIAGNOSTIQUE L.A.I.C.""",
        "rep_params": """PARAMÈTRES D'ENTRÉE""",
        "mode_title": """**MODE DE RECHERCHE:**""",
        "mode_1": """Analyse Historique (Avec Mainshock)""",
        "mode_2": """Surveillance / Calibration de Base""",
        "win_title": """📅 **Fenêtre Temporelle Auto**""",
        "date_ms": """💥 **Date du Séisme:**""",
        "date_obs": """🔍 **Date d'Observation:**""",
        "geo_title": """🎯 **Configuration Géo & Zone**""",
        "lat_epi": """**Latitude**<br>Épicentre:""",
        "lat_center": """**Latitude**<br>Centre Zone:""",
        "lon_epi": """**Longitude**<br>Épicentre:""",
        "lon_center": """**Longitude**<br>Centre Zone:""",
        "mag_ms": """**Magnitude<br>du Séisme (M):**""",
        "mag_scan": """**Magnitude de Balayage<br>(Rayon d'Écoute):**""",
        "help_rad": """ℹ️ Comment fonctionne le Rayon d'Écoute?""",
        "wait_msg": """⏳ Extraction des données satellitaires en cours...""",
        "ok_msg": """✅ Traitement terminé avec succès!""",
        "tog_anom": """Afficher les Filtres d'Anomalies""",
        "tog_grid": """Afficher la Grille""",
        "help_ndwi": """Guide de Masquage Environnemental\nCalibrez toujours le seuil sur la valeur physiologique maximale du sol nu dégelé, en ignorant les plateaux hivernaux.""",
        "note_ndwi": """⚠️ <b>Note Opérationnelle :</b> Des valeurs de fond naturelles proches ou supérieures à 0.30 indiquent une interférence cryosphérique sévère (neige/glace) ou une saturation hydrologique extrême, non imputables à la seule dilatance tectónica.""",
        "t_olr": """1. Haute Atmosphère : RADIATION THERMIQUE OLR (NASA MERRA-2)""",
        "t_aod": """2. Stratosphère : GAZ ET AÉROSOLS (NASA MERRA-2 / Copernicus S5P)""",
        "t_rain": """3. Troposphère : PRÉCIPITATIONS RÉELLES (mm)""",
        "t_lst": """4. Surface : TEMPÉRATURE NOCTURNE DU SOL (°C MODIS LST)""",
        "t_ndwi": """5. Lithosphère : HUMIDITÉ DE SURFACE (NDWI Optique)""",
        "main_title": """<b>Tableau de Bord des Contraintes Géophysiques</b>""",
        "sub_title": """Analyse Stratigraphique L.A.I.C.""",
        "diag_tit": """SYNTHÈSE DIAGNOSTIQUE L.A.I.C.""",
        "fase_1": """1. État Crustal (Anomalies)""",
        "fase_2": """2. État Atmosphérique (Anomalies)""",
        "manual_title": """📖 Guide d'Interprétation L.A.I.C.""",
        "manual_text": """**Comment lire le Tableau de Bord L.A.I.C. Sentinel**
Le modèle L.A.I.C. postule que la préparation d'un événement sismique fort génère une chaîne d'anomalies thermodynamiques. La plateforme utilise le calcul du Z-Score* pour isoler ces anomalies.

<div style="color: #ff5252; border: 1px solid #ff5252; padding: 15px; border-radius: 4px; margin-top: 10px; margin-bottom: 15px; background-color: rgba(255, 82, 82, 0.05);">
<b>🚨 RECOMMANDATION MÉTHODOLOGIQUE CRUCIALE (Calibration Zéro-Signal) :</b><br>
Il est fortement recommandé de ne pas démarrer l'analyse d'un potentiel événement sans avoir préalablement effectué une <b>calibration de la ligne de base spécifique au site</b>. L'opérateur doit définir la plateforme en mode <i>Surveillance</i> sur une fenêtre temporelle distincte, éloignée de l'événement sismique, correspondant à une phase de calme géologique.
</div>

**LES PROTOCOLES OPÉRATIONNELS DE L.A.I.C. SENTINEL :**
**PARCOURS A : HINDCAST (Analyse Historique)**
* **Phase 1 (Calibration) :** Mode <i>Surveillance</i>. Choisissez la <b>même saison</b> d'une <b>année calme</b>. Lisez le pic NDWI et bloquez le seuil.
* **Phase 2 (Analyse) :** Mode <i>Analyse Historique</i>. Entrez la date du séisme, laissez le seuil tel quel. 

**PARCOURS B : NOWCAST (Surveillance en Temps Réel)**
* **Phase 1 (Calibration) :** Mode <i>Surveillance</i>. Trouvez une <b>"Année Analogue de Calma"</b> pour la zone. Lisez le pic NDWI et bloquez le seuil.
* **Phase 2 (Surveillance) :** Restez en Mode <i>Surveillance</i>. Réglez la date d'observation sur <b>aujourd'hui</b>. 

**📌 Interprétation du Graphique NDWI (Points Blancs) :**
La ligne bleue NDWI présente de petits "points blancs" indiquant les **passages réels** sans nuages. S'ils sont rares et que la ligne reste plate, la couverture nuageuse a aveuglé le capteur.

**Logique Mathématique des Alertes :**
* **SOL ACTIF :** Au moins 1 jour d'anomalie NDWI *OU* au moins 3 jours d'anomalie LST.
* **ATMOSPHÈRE ACTIVE :** Au moins 3 jours d'anomalie AOD *OU* au moins 3 jours d'anomalie OLR.

---
_**\* Z-Score :** Méthode statistique mesurant l'écart type par rapport à la moyenne historique mensuelle._
_**\*\* Formule de Dobrovolsky :** R = 10^(0.43 × M). Estime le rayon de la zone de préparation._""",
        "scen_1_tit": """SCÉNARIO 1 (Couplage avec Libération de Fluides)""",
        "scen_1_txt": """Anomalie d'eau de surface détectée, compatible avec la mobilisation d'aquifères profonds. Couplage L.A.I.C. confirmé.<br><br><span style='color:#a0a0a0;'><i>(Exemple : L'Aquila, Italie - 6 Avril 2009, Mw 6.1).</i></span>""",
        "scen_2_tit": """SCÉNARIO 2 (Couplage Thermique-Radiatif)""",
        "scen_2_txt": """Dégazage thermique crustal détecté en l'absence d'expulsion d'eau de surface. Les gaz ont déclenché un blocage radiatif sévère (OLR).<br><br><span style='color:#a0a0a0;'><i>(Exemple : Émilie-Romagne, Italie - 20 Mai 2012, Mw 5.9).</i></span>""",
        "scen_3_tit": """SCÉNARIO 3 (Activité Lithosphérique Isolée)""",
        "scen_3_txt": """Activité lithosphérique isolée. L'énergie n'a pas atteint l'intensité nécessaire pour le couplage L.A.I.C. avec la haute atmosphère.""",
        "scen_4_tit": """SCÉNARIO 4 (Anomalie Atmosphérique Externe)""",
        "scen_4_txt": """Anomalie atmosphérique isolée (AOD/OLR) sans 'racine' thermique ou hydrique au sol. Incompatible avec le modèle L.A.I.C.""",
        "scen_5_tit": """SCÉNARIO 5 (Absence d'Anomalies L.A.I.C.)""",
        "scen_5_txt": """Aucune anomalie significative. Les paramètres relèvent des fluctuations physiologiques. Couplage L.A.I.C. absent.""",
        "no_data": """DONNÉES NON DISPONIBLES."""
    },
    "ES": {
        "obs_name": """- Observatorio Geofísico Valle del Liri | <a href='https://www.osservageoliri.it' target='_blank' style='color: #a0c3d2; text-decoration: none;'>www.osservageoliri.it</a>""",
        "author": """Concepto y Desarrollo: <br><b style='color: #ff5252;'>Paolo Sabetta</b> (2026)<br><a href='mailto:paolo.sabetta@gmail.com' style='color: #a0a0a0; text-decoration: none; font-size: 12px;'>paolo.sabetta@gmail.com</a>""",
        "disclaimer": """L.A.I.C. Sentinel (SismaLab Suite) es una herramienta de investigación científica <b>experimental</b> dedicada al estudio del acoplamiento Litosfera-Atmósfera. <b>El modelo algorítmico se encuentra actualmente en fase de validación académica (Pre-Peer Review).</b> Los datos satelitales procesados tienen fines estrictamente de investigación retrospectiva: no constituyen un sistema de alerta temprana (Early Warning) ni una predicción determinista. El Observatorio Geofísico Valle del Liri declina toda responsabilidad por el uso indebido de los datos. ©️ OGVL.""",
        "auth_title": """ACCESO RESTRINGIDO - OBSERVATORIO GEOFÍSICO VALLE DEL LIRI""",
        "auth_prompt": """Ingrese la Contraseña de Red para acceder a L.A.I.C. Sentinel""",
        "auth_err": """⛔ Contraseña incorrecta o no autorizada.""",
        "btn_run": """INICIAR PROCESAMIENTO""",
        "btn_logout": """CERRAR SESIÓN""",
        "btn_download": """⬇️ DESCARGAR INFORME""",
        "rep_title": """INFORME DE SÍNTESIS DIAGNÓSTICA L.A.I.C.""",
        "rep_params": """PARÁMETROS DE ENTRADA""",
        "mode_title": """**MODO DE BÚSQUEDA:**""",
        "mode_1": """Análisis Histórico (Con Mainshock)""",
        "mode_2": """Monitoreo / Calibración de Línea Base""",
        "win_title": """📅 **Ventana Temporal Auto**""",
        "date_ms": """💥 **Fecha del Sismo:**""",
        "date_obs": """🔍 **Fecha de Observation:**""",
        "geo_title": """🎯 **Configuración Geográfica**""",
        "lat_epi": """**Latitud**<br>Epicentro:""",
        "lat_center": """**Latitud**<br>Centro del Área:""",
        "lon_epi": """**Longitud**<br>Epicentro:""",
        "lon_center": """**Longitud**<br>Centro del Área:""",
        "mag_ms": """**Magnitud<br>del Sismo (M):**""",
        "mag_scan": """**Magnitud de Escaneo<br>(Radio de Escucha):**""",
        "help_rad": """ℹ️ ¿Cómo funciona el Radio de Escucha?""",
        "wait_msg": """⏳ Extrayendo datos satelitales. Por favor, espere...""",
        "ok_msg": """✅ ¡Procesamiento completado con éxito!""",
        "tog_anom": """Mostrar Filtros de Anomalías""",
        "tog_grid": """Mostrar Cuadrícula""",
        "help_ndwi": """Guía de Enmascaramiento Ambiental\nCalibre siempre el umbral en el valor fisiológico máximo del suelo desnudo descongelado, ignorando las mesetas invernales.""",
        "note_ndwi": """⚠️ <b>Nota Operativa:</b> Los valores de fondo naturales cercanos o superiores a 0.30 indican una interferencia criosférica severa (nieve/hielo) o una saturación hidrológica extrema, no atribuibles únicamente a dilatancia tectónica.""",
        "t_olr": """1. Alta Atmósfera : RADIACIÓN TÉRMICA OLR (NASA MERRA-2)""",
        "t_aod": """2. Estratosfera : GAS Y AEROSOLES (NASA MERRA-2 / Copernicus S5P)""",
        "t_rain": """3. Troposfera : PRECIPITACIÓN REAL (mm)""",
        "t_lst": """4. Superficie : TEMPERATURA NOCTURNE DEL SUELO (°C MODIS LST)""",
        "t_ndwi": """5. Litosfera : HUMEDAD SUPERFICIAL (NDWI Óptico)""",
        "main_title": """<b>Panel de Observación de Estrés Geofísico</b>""",
        "sub_title": """Análisis Estratigráfico L.A.I.C.""",
        "diag_tit": """SÍNTESIS DIAGNÓSTICA L.A.I.C.""",
        "fase_1": """1. Estado Cortical (Anomalías)""",
        "fase_2": """2. Estado Atmosférico (Anomalías)""",
        "manual_title": """📖 Guía de Interpretación L.A.I.C.""",
        "manual_text": """**Cómo leer el Panel L.A.I.C. Sentinel**
El modelo L.A.I.C. postula que la preparación de un fuerte evento sísmico genera una cadena de anomalías termodinámicas. La plataforma utiliza el cálculo del Z-Score* para aislar estas anomalías.

<div style="color: #ff5252; border: 1px solid #ff5252; padding: 15px; border-radius: 4px; margin-top: 10px; margin-bottom: 15px; background-color: rgba(255, 82, 82, 0.05);">
<b>🚨 RECOMENDACIÓN METODOLÓGICA CRUCIAL (Calibración Zero-Signal):</b><br>
Se recomienda encarecidamente no iniciar el análisis sin haber realizado previamente una <b>calibración de línea base específica del sitio</b>. El operador debe configurar la plataforma en modo <i>Monitoreo</i> en una ventana de tiempo separada correspondiente a una fase conocida de calma geológica para esa área.
</div>

**LOS PROTOCOLOS OPERATIVOS DE L.A.I.C. SENTINEL:**
**RUTA A: HINDCAST (Análisis Histórico)**
* **Fase 1 (Calibración):** Modo <i>Monitoreo</i>. Elija la <b>misma estación</b> pero de un <b>año diferente y en calma</b>. Lea el pico NDWI y fije el Umbral.
* **Fase 2 (Análisis):** Modo <i>Análisis Histórico</i>. Introduzca la fecha del terremoto, dejando el Umbral intacto.

**RUTA B: NOWCAST (Monitoreo en Tiempo Real)**
* **Fase 1 (Calibración):** Modo <i>Monitoreo</i>. Encuentre un <b>"Año Análogo de Calma"</b> para la zona. Lea el pico NDWI y fije el Umbral.
* **Fase 2 (Vigilancia):** Permanezca en Modo <i>Monitoreo</i>. Cambie la Fecha de Observación a <b>hoy</b>.

**📌 Interpretación del Gráfico NDWI (Puntos Blancos):**
La línea azul del NDWI presenta pequeños "puntos blancos" indicando **pasadas reales** sin nubes. Si los puntos son escasos y la línea se mantiene plana, una densa capa de nubes cegó el sensor.

**Lógica Matemática de las Alertas:**
* **SUELO ACTIVO:** Al menos 1 día de anomalía NDWI *O* al menos 3 días de anomalía LST.
* **ATMÓSFERA ACTIVA:** Al menos 3 días de anomalía AOD *O* al menos 3 días de anomalía OLR.

---
_**\* Z-Score:** Método estadístico que mide las desviaciones estándar respecto a la media histórica mensual._
_**\*\* Fórmula de Dobrovolsky:** R = 10^(0.43 × M). Estima el radio del área de preparación._""",
        "scen_1_tit": """ESCENARIO 1 (Acoplamiento con Liberación de Fluidos)""",
        "scen_1_txt": """Anomalía hídrica superficial detectada, compatible con la movilización de acuíferos profundos. Acoplamiento L.A.I.C. plenamente confirmado.<br><br><span style='color:#a0a0a0;'><i>(Ejemplo: L'Aquila, Italia - 6 Abril 2009, Mw 6.1).</i></span>""",
        "scen_2_tit": """ESCENARIO 2 (Acoplamiento Térmico-Radiativo)""",
        "scen_2_txt": """Desgasificación térmica cortical detectada sin expulsión de agua. Los gases desencadenaron un severo bloqueo radiativo (OLR).<br><br><span style='color:#a0a0a0;'><i>(Ejemplo: Emilia-Romaña, Italia - 20 Mayo 2012, Mw 5.9).</i></span>""",
        "scen_3_tit": """ESCENARIO 3 (Actividad Litosférica Aislada)""",
        "scen_3_txt": """Actividad litosférica aislada. La deformación generó calor en la superficie, pero no alcanzó la intensidad para el acoplamiento L.A.I.C.""",
        "scen_4_tit": """ESCENARIO 4 (Anomalía Atmosférica Externa)""",
        "scen_4_txt": """Anomalía atmosférica aislada sin 'raíz' térmica o hídrica en el suelo. Incompatible con el modelo L.A.I.C.""",
        "scen_5_tit": """ESCENARIO 5 (Ausencia de Anomalías L.A.I.C.)""",
        "scen_5_txt": """Ninguna anomalía significativa. Los parámetros se encuentran dentro de las fluctuaciones fisiológicas. Acoplamiento L.A.I.C. ausente.""",
        "no_data": """DATOS NO DISPONIBLES."""
    },
    "RU": {
        "obs_name": """- Геофизическая обсерватория Валле-дель-Лири | <a href='https://www.osservageoliri.it' target='_blank' style='color: #a0c3d2; text-decoration: none;'>www.osservageoliri.it</a>""",
        "author": """Концепция и Разработка: <br><b style='color: #ff5252;'>Paolo Sabetta</b> (2026)<br><a href='mailto:paolo.sabetta@gmail.com' style='color: #a0a0a0; text-decoration: none; font-size: 12px;'>paolo.sabetta@gmail.com</a>""",
        "disclaimer": """L.A.I.C. Sentinel (SismaLab Suite) — это <b>экспериментальный</b> инструмент научных исследований. <b>Алгоритмическая модель в настоящее время проходит академическую проверку (Pre-Peer Review).</b> Обработанные спутниковые данные предназначены исключительно для ретроспективного анализа и не являются системой раннего предупреждения (Early Warning). Геофизическая обсерватория Валле-дель-Лири не несет ответственности за ненадлежащее использование данных. ©️ OGVL.""",
        "auth_title": """ОГРАНИЧЕННЫЙ ДОСТУП - OGVL""",
        "auth_prompt": """Введите сетевой пароль для доступа к L.A.I.C. Sentinel""",
        "auth_err": """⛔ Неверный пароль.""",
        "btn_run": """НАЧАТЬ ОБРАБОТКУ""",
        "btn_logout": """ВЫХОД""",
        "btn_download": """⬇️ СКАЧАТЬ ОТЧЕТ""",
        "rep_title": """ДИАГНОСТИЧЕСКИЙ ОТЧЕТ L.A.I.C.""",
        "rep_params": """ВХОДНЫЕ ПАРАМЕТРЫ""",
        "mode_title": """**РЕЖИМ ПОИСКА:**""",
        "mode_1": """Исторический анализ (с главным толчком)""",
        "mode_2": """Мониторинг / Базовая Калибровка""",
        "win_title": """📅 **Автоматическое окно**""",
        "date_ms": """💥 **Дата землетрясения:**""",
        "date_obs": """🔍 **Дата наблюдения:**""",
        "geo_title": """🎯 **География и Зона**""",
        "lat_epi": """**Широта**<br>Эпицентр:""",
        "lat_center": """**Широта**<br>Центр зоны:""",
        "lon_epi": """**Долгота**<br>Эпицентр:""",
        "lon_center": """**Долгота**<br>Центр зоны:""",
        "mag_ms": """**Магнитуда<br>(M):**""",
        "mag_scan": """**Магнитуда сканирования:**""",
        "help_rad": """ℹ️ Как работает радиус?""",
        "wait_msg": """⏳ Извлечение спутниковых данных...""",
        "ok_msg": """✅ Обработка успешно завершена!""",
        "tog_anom": """Показать фильтры аномалий""",
        "tog_grid": """Показать сетку""",
        "help_ndwi": """Руководство по экологическому маскированию\nВсегда калибруйте порог по максимальному физиологическому значению голой оттаявшей почвы, игнорируя зимние плато.""",
        "note_ndwi": """⚠️ <b>Рабочее примечание:</b> Естественные фоновые значения около или выше 0,30 указывают на сильное криосферное влияние (снег/лед) или экстремальное гидрологическое насыщение, не связанное исключительно с тектонической дилатацией.""",
        "t_olr": """1. Мезопауза: ТЕПЛОВОЕ ИЗЛУЧЕНИЕ OLR""",
        "t_aod": """2. Стратосфера: ГАЗ И АЭРОЗОЛИ""",
        "t_rain": """3. Troposфера: РЕАЛЬНЫЕ ОСАДКИ (мм)""",
        "t_lst": """4. Поверхность: НОЧНАЯ ТЕМПЕРАТУРА ПОЧВЫ""",
        "t_ndwi": """5. Литосфера: ПОВЕРХНОСТНАЯ ВЛАЖНОСТЬ""",
        "main_title": """<b>Панель наблюдения напряжения</b>""",
        "sub_title": """Стратиграфический анализ L.A.I.C.""",
        "diag_tit": """ДИАГНОСТИЧЕСКАЯ СВОДКА L.A.I.C.""",
        "fase_1": """1. Состояние коры (Аномалии)""",
        "fase_2": """2. Атмосферное состояние (Аномалии)""",
        "manual_title": """📖 Руководство по интерпретации L.A.I.C.""",
        "manual_text": """**Как читать панель L.A.I.C. Sentinel**
Модель L.A.I.C. утверждает, что подготовка землетрясения порождает цепь термодинамических аномалий. Платформа использует Z-Score* для их изоляции.

<div style="color: #ff5252; border: 1px solid #ff5252; padding: 15px; border-radius: 4px; margin-top: 10px; margin-bottom: 15px; background-color: rgba(255, 82, 82, 0.05);">
<b>🚨 ВАЖНАЯ МЕТОДОЛОГИЧЕСКАЯ РЕКОМЕНДАЦИЯ (Калибровка нулевого сигнала):</b><br>
Настоятельно рекомендуется не начинать анализ без предварительной <b>калибровки базовой линии</b>. Оператор должен настроить платформу в режиме <i>Мониторинг</i> на отдельное временное окно, соответствующее периоду геологического затишья.
</div>

**ОПЕРАЦИОННЫЕ ПРОТОКОЛЫ L.A.I.C. SENTINEL:**
**ПУТЬ A: HINDCAST (Исторический анализ)**
* **Фаза 1 (Калибровка):** Режим <i>Мониторинг</i>. Выберите тот же сезон, но тихий год. Заблокируйте порог.
* **Фаза 2 (Анализ):** Режим <i>Исторический анализ</i>. Введите дату события.

**ПУТЬ B: NOWCAST (Мониторинг в реальном времени)**
* **Фаза 1 (Калибровка):** Режим <i>Мониторинг</i>. Найдите аналогичный тихий год. Заблокируйте порог.
* **Фаза 2 (Наблюдение):** Оставьте Режим <i>Мониторинг</i>. Измените дату на сегодня.

**📌 Интерпретация графика NDWI (Белые точки):**
Синяя линия имеет «белые точки», указывающие на реальные проходы спутника без облаков. Если точки редкие и линия ровная, датчик был ослеплен облаками.

**Математическая логика тревог:**
* **АКТИВНАЯ ПОЧВА:** Минимум 1 день аномалии NDWI *ИЛИ* минимум 3 дня аномалии LST.
* **АКТИВНАЯ АТМОСФЕРА:** Минимум 3 дня аномалии AOD *ИЛИ* минимум 3 дня аномалии OLR.

---
_**\* Z-Score:** Статистический метод оценки отклонений от исторической средней._
_**\*\* Формула Добровольского:** R = 10^(0.43 × M). Оценка радиуса зоны подготовки._""",
        "scen_1_tit": """СЦЕНАРИЙ 1 (Взаимодействие с выбросом флюидов)""",
        "scen_1_txt": """Выявлена аномалия поверхностных вод, совместимая с мобилизацией глубоких водоносных горизонтов. Взаимодействие L.A.I.C. подтверждено.<br><br><span style='color:#a0a0a0;'><i>(Пример: Аквила, Италия - 6 апр 2009, Mw 6.1).</i></span>""",
        "scen_2_tit": """СЦЕНАРИЙ 2 (Терморадиационное взаимодействие)""",
        "scen_2_txt": """Термическая дегазация без выхода вод. Газы вызвали сильный радиационный блок (OLR).<br><br><span style='color:#a0a0a0;'><i>(Пример: Эмилия-Романья, Италия - 20 мая 2012, Mw 5.9).</i></span>""",
        "scen_3_tit": """СЦЕНАРИЙ 3 (Изолированная литосферная активность)""",
        "scen_3_txt": """Изолированная литосферная активность. Энергия не достигла уровня для взаимодействия L.A.I.C. с высокой атмосферой.""",
        "scen_4_tit": """СЦЕНАРИЙ 4 (Внешняя атмосферная аномалия)""",
        "scen_4_txt": """Атмосферная аномалия (AOD/OLR) без температурного или водного 'корня' в почве. Несовместимо с L.A.I.C.""",
        "scen_5_tit": """СЦЕНАРИЙ 5 (Отсутствие аномалий L.A.I.C.)""",
        "scen_5_txt": """Значимых аномалий не обнаружено. Взаимодействие L.A.I.C. отсутствует.""",
        "no_data": """ДАННЫЕ НЕДОСТУПНЫ."""
    }
}

# --- Smart function to retrieve translated text ---
def t(key):
    lang = st.session_state.get("lang", "IT")
    return LANG_DICT.get(lang, LANG_DICT["IT"]).get(key, LANG_DICT["IT"].get(key, key))

# --- PAGE CONFIGURATION AND PROFESSIONAL STYLES ---
st.set_page_config(page_title="L.A.I.C. Sentinel", layout="wide", page_icon="🌍")

# --- GOOGLE ANALYTICS 4 TRACKING ENGINE ---
def inject_ga4(tracking_id):
    ga_script = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={tracking_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{tracking_id}');
    </script>
    """
    components.html(ga_script, height=0, width=0)

# --- CONFIRMED OGVL ANALYTICS CODE ---
inject_ga4("G-HV20LCX57H")

st.markdown("""<script>window.parent.postMessage({ type: 'streamlit:setComponentValue', value: '...' }, '*');</script>""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    h2 { margin-top: -10px; margin-bottom: 0px; padding-bottom: 5px; }
    
    [data-testid="stStatusWidget"], [data-testid="stStatusWidget"] * {
        visibility: hidden !important;
        display: none !important;
        opacity: 0 !important;
    }
    
    /* LOCKING PRIMARY BUTTONS (GREEN AND DOWNLOAD) */
    button[kind="primary"] {
        background-color: #2e7d32 !important; 
        border-color: #2e7d32 !important;
        color: white !important; 
        border: none !important; 
        font-weight: bold !important; 
        font-size: 16px !important;
        padding: 10px 24px !important;
    }
    button[kind="primary"]:hover { 
        background-color: #1b5e20 !important; 
        border-color: #1b5e20 !important;
    }

    /* ABSOLUTE LOGOUT LOCK */
    button[kind="secondary"],
    [data-testid="stSidebar"] div.stButton:nth-of-type(2) button,
    [data-testid="stSidebar"] div.stButton:last-of-type button {
        background-color: transparent !important; 
        color: #ff5252 !important; 
        border: none !important; 
        box-shadow: none !important; 
        font-weight: bold !important; 
        text-decoration: underline !important; 
        padding: 10px 24px !important;
    }
    button[kind="secondary"]:hover,
    [data-testid="stSidebar"] div.stButton:nth-of-type(2) button:hover,
    [data-testid="stSidebar"] div.stButton:last-of-type button:hover {
        color: #b71c1c !important; 
        background-color: transparent !important;
    }

    /* SIDEBAR COMPACTION */
    [data-testid="stSidebar"] .stButton { margin-bottom: -10px; }
    [data-testid="stSidebar"] .stRadio { margin-bottom: -15px; margin-top: -10px; }
    [data-testid="stSidebar"] .stDateInput { margin-bottom: -15px; }
    [data-testid="stSidebar"] .stNumberInput { margin-bottom: -15px; }
    [data-testid="stSidebar"] hr { margin-top: 0.5em; margin-bottom: 0.5em; }
    
    div[data-testid="stToggle"] {
        background-color: #1e2530;
        padding: 8px 15px;
        border-radius: 6px;
        border-left: 5px solid #ffcc00;
        margin-bottom: 5px;
    }
    div[data-testid="stToggle"] label p {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #ffffff !important;
    }
    
    .disclaimer-box {
        background-color: rgba(240, 244, 248, 0.95); 
        padding: 30px 40px; 
        border-radius: 10px; 
        border: 1px solid rgba(0,0,0,0.1); 
        border-top: 5px solid #ff5252; 
        font-size: 15px; 
        color: #2c3e50; 
        margin: 20px auto 40px auto; 
        max-width: 700px; 
        line-height: 1.7; 
        text-align: justify;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: #eef2f5 !important;
        border: 2px solid #a0c3d2 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: #ff5252 !important;
        box-shadow: 0 0 10px rgba(255, 82, 82, 0.2) !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stTextInput"] input[type="password"] {
        font-size: 18px !important;
        letter-spacing: 3px !important;
        text-align: center !important;
        color: #2c3e50 !important;
        font-weight: 700 !important;
    }

    div[data-testid="InputInstructions"], 
    div[data-testid="stTextInputInstructions"],
    [data-testid="stTextInput"] small,
    input[type="password"]::-ms-reveal,
    input[type="password"]::-ms-clear,
    input[type="password"]::-webkit-credentials-auto-fill-button {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THRESHOLD MEMORY INITIALIZATION ---
if 'soglia_ndwi_mem' not in st.session_state:
    st.session_state['soglia_ndwi_mem'] = 0.05

# --- PASSWORD BLOCK AND LANGUAGE SELECTOR ---
def check_password():
    lang_options = {"[ITA] Italiano": "IT", "[ENG] English": "EN", "[FRA] Français": "FR", "[ESP] Español": "ES", "[RUS] Русский": "RU"}
    sel = st.radio("", list(lang_options.keys()), horizontal=True, label_visibility="collapsed", key="lang_selector")
    st.session_state["lang"] = lang_options[sel]
    
    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.markdown(f"<h3 style='text-align: center; color: #ff5252; margin-top: 50px;'>{t('auth_title')}</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='disclaimer-box'><b>NOTA INFORMATIVA:</b><br>{t('disclaimer')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; margin-bottom: 5px; font-weight: bold; color: #a0c3d2;'>{t('auth_prompt')}</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            col_pw, col_btn = st.columns([4, 1])
            with col_pw:
                pwd_inserita = st.text_input("pwd", type="password", label_visibility="collapsed", key="pwd_input_key")
                st.markdown("""
                <script>
                const input = window.parent.document.querySelector('input[type="password"]');
                if(input) {
                    input.addEventListener('keydown', function(event) {
                        if (event.key === 'Enter') {
                            event.preventDefault();
                            event.stopPropagation();
                        }
                    });
                }
                </script>
                """, unsafe_allow_html=True)
            with col_btn:
                btn_invio = st.button("INVIA", type="primary", use_container_width=True, key="invia_btn")
            
            if btn_invio:
                if pwd_inserita == "!Review26$":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error(t('auth_err'))
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- HYBRID AUTHENTICATION ---
@st.cache_resource
def init_earth_engine():
    try:
        if os.path.exists('sismalab_key.json'):
            credenziali = service_account.Credentials.from_service_account_file('sismalab_key.json')
        elif "gcp_service_account" in st.secrets:
            credenziali = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        else:
            st.error("Nessuna chiave di accesso trovata.")
            return False
            
        credenziali_scopo = credenziali.with_scopes([
            'https://www.googleapis.com/auth/earthengine', 
            'https://www.googleapis.com/auth/cloud-platform'
        ])
        ee.Initialize(credentials=credenziali_scopo, project='my-project-1486307151691')
        return True
    except Exception as e:
        st.error(f"Errore Token: {e}")
        return False

# --- RIGOROUS EXTRACTION ENGINE ---
@st.cache_data(show_spinner=False)
def esegui_estrazione(lat, lon, mag_target, data_in_str, data_fi_str, modalita, data_mainshock_str):
    log_l = -2.44 + (0.59 * mag_target)
    raggio_metri = int(max(2.0, (10 ** log_l) / 2) * 1000)
    sequenza_sismica = []
    
    if modalita == t("mode_1"):
        try:
            client = Client("USGS")
            dt_target = UTCDateTime(data_mainshock_str)
            catalogo = client.get_events(starttime=dt_target - 86400, endtime=dt_target + 86400, 
                                         latitude=lat, longitude=lon, maxradius=(raggio_metri / 1000.0 + 60.0) / 111.12, minmagnitude=4.5)
            for ev in catalogo:
                try:
                    dt_full = ev.origins[0].time.datetime
                    nome = ev.event_descriptions[0].text.split(" of ")[-1] if ev.event_descriptions else "Area Target"
                    sequenza_sismica.append({'data': dt_full.strftime('%Y-%m-%d'), 'mag': ev.magnitudes[0].mag, 'nome': nome, 'dt': dt_full})
                except: pass
            if sequenza_sismica:
                sequenza_sismica = [max(sequenza_sismica, key=lambda x: x['mag'])]
        except: pass

    area_studio = ee.Geometry.Point([lon, lat]).buffer(raggio_metri) 
    maschera_terraferma = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('max_extent').unmask(0).eq(0)
    def riduci(img, band, scale): return ee.Feature(None, {'data': ee.Date(img.get('system:time_start')).format('YYYY-MM-dd'), band: img.reduceRegion(ee.Reducer.mean(), area_studio, scale, maxPixels=1e9).get(band)})
    df = pd.DataFrame(index=pd.date_range(start=data_in_str, end=data_fi_str, freq='D'))
    
    try:
        if data_in_str >= '2016-01-01':
            col_ott = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterBounds(area_studio).filterDate(data_in_str, data_fi_str).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40))
            def calc_ndwi(img): return img.addBands(img.normalizedDifference(['B8', 'B11']).rename('NDWI')).select('NDWI').updateMask(maschera_terraferma).copyProperties(img, ['system:time_start'])
        elif data_in_str >= '2013-04-01':
            col_ott = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA').filterBounds(area_studio).filterDate(data_in_str, data_fi_str).filter(ee.Filter.lt('CLOUD_COVER', 40))
            def calc_ndwi(img): return img.addBands(img.normalizedDifference(['B5', 'B6']).rename('NDWI')).select('NDWI').updateMask(maschera_terraferma).copyProperties(img, ['system:time_start'])
        else:
            l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_TOA').filterBounds(area_studio).filterDate(data_in_str, data_fi_str).filter(ee.Filter.lt('CLOUD_COVER', 40))
            l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_TOA').filterBounds(area_studio).filterDate(data_in_str, data_fi_str).filter(ee.Filter.lt('CLOUD_COVER', 40))
            col_ott = l5.merge(l7)
            def calc_ndwi(img): return img.addBands(img.normalizedDifference(['B4', 'B5']).rename('NDWI')).select('NDWI').updateMask(maschera_terraferma).copyProperties(img, ['system:time_start'])
        df_ndwi = pd.DataFrame([{'Data': f['properties']['data'], 'NDWI': f['properties']['NDWI']} for f in col_ott.map(calc_ndwi).map(lambda i: riduci(i, 'NDWI', 100)).getInfo()['features'] if f.get('properties', {}).get('NDWI') is not None]).set_index('Data')
        df_ndwi.index = pd.to_datetime(df_ndwi.index)
        if not df_ndwi.empty:
            df_ndwi = df_ndwi.groupby(df_ndwi.index).mean()
            df = df.join(df_ndwi)
    except: df['NDWI'] = np.nan

    try:
        col_lst = ee.ImageCollection('MODIS/061/MOD11A1').filterBounds(area_studio).filterDate(data_in_str, data_fi_str)
        def calc_lst(img): return img.addBands(img.select('LST_Night_1km').multiply(0.02).subtract(273.15).rename('LST_C')).select('LST_C').updateMask(maschera_terraferma).copyProperties(img, ['system:time_start'])
        df_lst = pd.DataFrame([{'Data': f['properties']['data'], 'LST_C': f['properties']['LST_C']} for f in col_lst.map(calc_lst).map(lambda i: riduci(i, 'LST_C', 1000)).getInfo()['features'] if f.get('properties', {}).get('LST_C') is not None]).set_index('Data')
        df_lst.index = pd.to_datetime(df_lst.index)
        if not df_lst.empty:
            df_lst = df_lst.groupby(df_lst.index).mean()
            df = df.join(df_lst)
    except: df['LST_C'] = np.nan

    try:
        col_rain = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').filterBounds(area_studio).filterDate(data_in_str, data_fi_str)
        df_rain = pd.DataFrame([{'Data': f['properties']['data'], 'Pioggia_mm': f['properties']['precipitation']} for f in col_rain.map(lambda i: riduci(i, 'precipitation', 5000)).getInfo()['features'] if f.get('properties', {}).get('precipitation') is not None]).set_index('Data')
        df_rain.index = pd.to_datetime(df_rain.index)
        if not df_rain.empty:
            df_rain = df_rain.groupby(df_rain.index).mean()
            df_rain['Pioggia_Reale_Giornaliera'] = df_rain['Pioggia_mm']
            df = df.join(df_rain)
    except: 
        df['Pioggia_mm'] = 0
        df['Pioggia_Reale_Giornaliera'] = 0

    try:
        start_date_aod = ee.Date(data_in_str)
        end_date_aod = ee.Date(data_fi_str)
        if data_in_str >= '2018-07-10':
            col_aod = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_AER_AI').filterBounds(area_studio).filterDate(data_in_str, data_fi_str)
            def riduci_aod_s5p(img):
                val = img.reduceRegion(ee.Reducer.mean(), area_studio, 25000, maxPixels=1e10).get('absorbing_aerosol_index')
                return ee.Feature(None, {'data': ee.Date(img.get('system:time_start')).format('YYYY-MM-dd'), 'AOD': val})
            dati_aod_grezzi = col_aod.map(riduci_aod_s5p).getInfo()['features']
            lista_aod = [{'Data': f['properties']['data'], 'AOD': f['properties']['AOD']} for f in dati_aod_grezzi if f.get('properties', {}).get('AOD') is not None]
            df_aod = pd.DataFrame(lista_aod)
            if not df_aod.empty:
                df_aod = df_aod.groupby('Data').mean()
                df_aod.index = pd.to_datetime(df_aod.index)
                df = df.join(df_aod)
            else: df['AOD'] = np.nan
        else:
            col_aod = ee.ImageCollection('NASA/GSFC/MERRA/aer/2').filterBounds(area_studio).filterDate(data_in_str, data_fi_str)
            days_aod = end_date_aod.difference(start_date_aod, 'days')
            days_list_aod = ee.List.sequence(0, days_aod.subtract(1))
            def make_daily_aod(day_offset):
                d1 = start_date_aod.advance(day_offset, 'days')
                d2 = d1.advance(1, 'days')
                daily_img = col_aod.filterDate(d1, d2).mean()
                val = daily_img.reduceRegion(ee.Reducer.mean(), area_studio, 10000).get('TOTEXTTAU')
                return ee.Feature(None, {'data': d1.format('YYYY-MM-dd'), 'AOD': val})
            dati_aod_daily = ee.FeatureCollection(days_list_aod.map(make_daily_aod)).getInfo()['features']
            df_aod = pd.DataFrame([{'Data': f['properties']['data'], 'AOD': f['properties']['AOD']} for f in dati_aod_daily if f.get('properties', {}).get('AOD') is not None]).set_index('Data')
            df_aod.index = pd.to_datetime(df_aod.index)
            if not df_aod.empty:
                df_aod = df_aod.groupby(df_aod.index).mean()
                df = df.join(df_aod)
    except: df['AOD'] = np.nan

    try:
        col_olr = ee.ImageCollection('NASA/GSFC/MERRA/rad/2').filterBounds(area_studio).filterDate(data_in_str, data_fi_str)
        dati_olr = ee.FeatureCollection(ee.List.sequence(0, ee.Date(data_fi_str).difference(ee.Date(data_in_str), 'days').subtract(1)).map(lambda d: ee.Feature(None, {'data': ee.Date(data_in_str).advance(d, 'days').format('YYYY-MM-dd'), 'LWTUP': col_olr.filterDate(ee.Date(data_in_str).advance(d, 'days'), ee.Date(data_in_str).advance(ee.Number(d).add(1), 'days')).mean().reduceRegion(ee.Reducer.mean(), area_studio, 10000).get('LWTUP')}))).getInfo()['features']
        df_olr = pd.DataFrame([{'Data': f['properties']['data'], 'OLR': f['properties']['LWTUP']} for f in dati_olr if f.get('properties', {}).get('LWTUP') is not None]).set_index('Data')
        df_olr.index = pd.to_datetime(df_olr.index)
        if not df_olr.empty:
            df_olr = df_olr.groupby(df_olr.index).mean()
            df = df.join(df_olr)
    except: df['OLR'] = np.nan

    for col in ['NDWI', 'LST_C', 'Pioggia_Reale_Giornaliera', 'Pioggia_mm', 'OLR', 'AOD']:
        if col not in df.columns: df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['NDWI_Punti'] = df['NDWI'].copy() 
    df['NDWI'] = df['NDWI'].ffill() 
    df['Pioggia_Reale_Giornaliera'] = df['Pioggia_Reale_Giornaliera'].fillna(0)
    df['Pioggia_mm'] = df['Pioggia_mm'].fillna(0) 
    df['Pioggia_Accumulata_7gg'] = df['Pioggia_mm'].rolling(window=7, min_periods=1).sum()
    df['LST_C'] = df['LST_C'].interpolate(method='time', limit=3)
    if df['OLR'].notna().any(): df['OLR'] = df['OLR'].interpolate(method='time', limit=5)
    if df['AOD'].notna().any(): df['AOD'] = df['AOD'].interpolate(method='time', limit=5)
    
    df['Mese'] = df.index.month
    for base_col, z_col in [('NDWI', 'Z_Score_NDWI'), ('LST_C', 'Z_Score_LST'), ('Pioggia_Accumulata_7gg', 'Z_Score_Rain'), ('OLR', 'Z_Score_OLR'), ('AOD', 'Z_Score_AOD')]:
        if not df[base_col].dropna().empty:
            stats = df.groupby('Mese')[base_col].agg(['mean', 'std'])
            df = df.join(stats, on='Mese', rsuffix='_rm')
            df[z_col] = np.where(df['std'] > 0, (df[base_col] - df['mean']) / df['std'], 0)
            df = df.drop(columns=['mean', 'std'])
        else: df[z_col] = np.nan

    if 'Z_Score_NDWI' in df.columns and 'Z_Score_Rain' in df.columns:
        df['Z_Score_Netto_NDWI'] = df['Z_Score_NDWI'] - df['Z_Score_Rain'].clip(lower=0)
    else: df['Z_Score_Netto_NDWI'] = np.nan

    return df, sequenza_sismica

def crea_spaccato_analitico(df, sequenza_sismica, mostra_allarmi, mostra_reticolato, soglia_fisica_ndwi):
    titoli_subplot = (t('t_olr'), t('t_aod'), t('t_rain'), t('t_lst'), t('t_ndwi'))

    fig = make_subplots(
        rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.045,
        row_heights=[0.2, 0.2, 0.2, 0.2, 0.2], subplot_titles=titoli_subplot
    )

    olr_raw = df['OLR']
    aod_raw = df['AOD']
    pioggia = df['Pioggia_Reale_Giornaliera'].fillna(0)
    lst_raw = df['LST_C']
    ndwi_raw = df['NDWI']
    ndwi_punti = df['NDWI_Punti'].dropna() if 'NDWI_Punti' in df.columns else pd.Series(dtype=float)

    fig.add_trace(go.Scatter(x=df.index, y=olr_raw, mode='lines', line=dict(color='#DA70D6', width=1.5), name="OLR (W/m²)"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=aod_raw, mode='lines', line=dict(color='#FFFF00', width=1.5), name="AOD"), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=pioggia, marker_color='#2ca02c', name="Rain/Pioggia (mm)"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=lst_raw, mode='lines', line=dict(color='#FF4500', width=1.5), name="LST (°C)"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=ndwi_raw, mode='lines', line=dict(color='#00BFFF', width=1.5, shape='hv'), name="NDWI"), row=5, col=1)
    
    if not ndwi_punti.empty:
        fig.add_trace(go.Scatter(x=ndwi_punti.index, y=ndwi_punti.values, mode='markers', marker=dict(color='white', size=5, line=dict(color='#00BFFF', width=1)), name="Sat", hoverinfo='skip'), row=5, col=1)

    if mostra_allarmi:
        olr_anom = np.where(df.get('Z_Score_OLR', pd.Series(0, index=df.index)).abs() >= 1.0, olr_raw, np.nan)
        aod_anom = np.where(df.get('Z_Score_AOD', pd.Series(0, index=df.index)).abs() >= 1.0, aod_raw, np.nan)
        lst_anom = np.where(df.get('Z_Score_LST', pd.Series(0, index=df.index)) >= 1.0, lst_raw, np.nan)
        ndwi_anom = np.where((df.get('Z_Score_Netto_NDWI', pd.Series(0, index=df.index)) >= 1.0) & (df['NDWI'] >= soglia_fisica_ndwi), ndwi_raw, np.nan)

        fig.add_trace(go.Bar(x=df.index, y=olr_anom, marker_color='rgba(148, 103, 189, 0.35)', marker_line_width=0, name="Anom OLR", hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=aod_anom, marker_color='rgba(255, 255, 0, 0.25)', marker_line_width=0, name="Anom AOD", hoverinfo='skip'), row=2, col=1)
        fig.add_trace(go.Bar(x=df.index, y=lst_anom, marker_color='rgba(255, 0, 0, 0.45)', marker_line_width=0, name="Anom LST", hoverinfo='skip'), row=4, col=1)
        fig.add_trace(go.Bar(x=df.index, y=ndwi_anom, marker_color='rgba(255, 215, 0, 0.55)', marker_line_width=0, name="Anom NDWI", hoverinfo='skip'), row=5, col=1)

    for annotation in fig['layout']['annotations']: annotation['font'] = dict(size=12, color="#E0E0E0")
    
    colore_griglia = 'rgba(255,255,255,0.08)' if mostra_reticolato else 'rgba(0,0,0,0)'
    fig.update_xaxes(showline=True, linewidth=1, linecolor='rgba(255,255,255,0.2)', mirror=True, showgrid=mostra_reticolato, gridwidth=1, gridcolor=colore_griglia, fixedrange=False)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='rgba(255,255,255,0.2)', mirror=True, showgrid=True, gridcolor='rgba(255,255,255,0.05)', fixedrange=True)

    if sequenza_sismica:
        eq_date = pd.to_datetime(sequenza_sismica[0]['data'])
        fig.add_shape(type="line", x0=eq_date, x1=eq_date, y0=0, y1=1.035, xref="x", yref="paper", line=dict(color="red", width=2), layer="above")
        fig.add_annotation(x=eq_date, y=1.035, xref='x', yref='paper', text=f"<b>MAINSHOCK: {eq_date.strftime('%Y-%m-%d')}</b>", showarrow=False, font=dict(color="red", size=13), xanchor="left", yanchor="bottom", xshift=6)

    fig.update_xaxes(showspikes=True, spikecolor="gray", spikemode="across", spikesnap="cursor")
    titolo_html = f"{t('main_title')}<br><span style='font-size: 16px; font-weight: normal; color: #a0a0a0;'>{t('sub_title')}</span>"
    
    fig.update_layout(
        title=dict(text=titolo_html, font=dict(color='white', size=24), x=0.5, xanchor='center', y=0.97),
        height=900, margin=dict(l=85, r=20, t=100, b=60), 
        showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.04, xanchor="center", x=0.5, bgcolor="rgba(0,0,0,0)", font=dict(size=14, color="#FFFFFF")),
        template="plotly_dark", plot_bgcolor='#0b0f19', paper_bgcolor='#0b0f19',
        dragmode="zoom", hovermode="x unified", barmode='overlay', bargap=0
    )
    return fig

# --- DYNAMIC L.A.I.C. GEOPHYSICAL REPORT WITH TEXT FILE GENERATOR ---
def genera_sintesi(df, sequenza_sismica, modalita, soglia_fisica_ndwi, lat, lon, mag, data_in_str, data_fi_str, data_target_str):
    if df.empty: 
        return f"<div style='color: #ffcc00;'>{t('no_data')}</div>", ""
    
    start_dil, end_dil = df.index[0], (pd.to_datetime(sequenza_sismica[0]['data']) if sequenza_sismica and modalita == t("mode_1") else df.index[-1])
    df_dil = df.loc[start_dil:end_dil]
    
    # Anomaly counters
    anomalie_idriche = len(df_dil[(df_dil['Z_Score_Netto_NDWI'] > 1.0) & (df_dil['NDWI'] >= soglia_fisica_ndwi) & (df_dil['NDWI_Punti'].notna())]) if 'Z_Score_Netto_NDWI' in df_dil.columns else 0
    anomalie_termiche = len(df_dil[df_dil['Z_Score_LST'] > 1.0]) if 'Z_Score_LST' in df_dil.columns else 0
    anomalie_aod = len(df_dil[df_dil['Z_Score_AOD'].abs() > 1.0]) if 'Z_Score_AOD' in df_dil.columns else 0
    anomalie_olr = len(df_dil[df_dil['Z_Score_OLR'].abs() > 1.0]) if 'Z_Score_OLR' in df_dil.columns else 0
    
    # Logical activation conditions
    suolo_attivo = (anomalie_idriche >= 1) or (anomalie_termiche >= 3)
    atmosfera_attiva = (anomalie_aod >= 3) or (anomalie_olr >= 3)

    # Decision Engine
    if suolo_attivo and atmosfera_attiva:
        if anomalie_idriche >= 1:
            titolo_scen, desc_scen, colore_box = t('scen_1_tit'), t('scen_1_txt'), "#ff5252"
        else:
            titolo_scen, desc_scen, colore_box = t('scen_2_tit'), t('scen_2_txt'), "#ff5252"
    elif suolo_attivo and not atmosfera_attiva:
        titolo_scen, desc_scen, colore_box = t('scen_3_tit'), t('scen_3_txt'), "#ffcc00"
    elif not suolo_attivo and atmosfera_attiva:
        titolo_scen, desc_scen, colore_box = t('scen_4_tit'), t('scen_4_txt'), "#00BFFF"
    else:
        titolo_scen, desc_scen, colore_box = t('scen_5_tit'), t('scen_5_txt'), "#4CAF50"

    # SECURED HTML CODE
    html_content = f"""<div style="background-color: #1e1e1e; padding: 30px; border-radius: 4px; border-left: 5px solid {colore_box}; color: #D3D3D3; margin-top: 20px; font-size: 14px; line-height: 1.6;">
<h3 style="margin-top: 0; color: #ffffff; font-size: 18px;">{t('diag_tit')}</h3>
<hr style="border-color: #333; margin: 15px 0;">
<div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
<div style="width: 48%;">
<p style="text-transform: uppercase; font-size: 12px; color: #888; font-weight: 600; margin-bottom: 5px;">{t('fase_1')}</p>
<span style="display:inline-block; width:15px; height:15px; border-radius:50%; background-color:#00BFFF; vertical-align: middle;"></span> <span style="vertical-align: middle;">NDWI: <b>{anomalie_idriche}</b> gg</span><br>
<span style="display:inline-block; width:15px; height:15px; border-radius:50%; background-color:#FF4500; vertical-align: middle; margin-top:5px;"></span> <span style="vertical-align: middle;">LST: <b>{anomalie_termiche}</b> gg</span>
</div>
<div style="width: 48%;">
<p style="text-transform: uppercase; font-size: 12px; color: #888; font-weight: 600; margin-bottom: 5px;">{t('fase_2')}</p>
<span style="display:inline-block; width:15px; height:15px; border-radius:50%; background-color:#FFFF00; vertical-align: middle;"></span> <span style="vertical-align: middle;">AOD: <b>{anomalie_aod}</b> gg</span><br>
<span style="display:inline-block; width:15px; height:15px; border-radius:50%; background-color:#DA70D6; vertical-align: middle; margin-top:5px;"></span> <span style="vertical-align: middle;">OLR: <b>{anomalie_olr}</b> gg</span>
</div>
</div>
<hr style="border-color: #333; margin: 20px 0;">
<p style="color: {colore_box}; font-size: 16px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px;">{titolo_scen}</p>
<p style="font-size: 15px; color: #e0e0e0;">{desc_scen}</p>
</div>"""

    # TEXT CLEANUP FOR DOWNLOAD FILE (Removes HTML tags)
    testo_desc_pulito = desc_scen.replace('<br>', '\n').replace('<i>', '').replace('</i>', '').replace('<b>', '').replace('</b>', '').replace("<span style='color:#a0a0a0;'>", "").replace('</span>', '')
    
    report_text = f"""=========================================
{t('rep_title')}
=========================================

--- {t('rep_params')} ---
Modalità: {modalita}
Data Target: {data_target_str}
Finestra Temporale: {data_in_str} -> {data_fi_str}
Coordinate: Latitudine {lat} | Longitudine {lon}
Magnitudo Analisi: {mag}
Soglia NDWI Impostata: {soglia_fisica_ndwi}

--- {t('fase_1').upper()} ---
NDWI (Umidità): {anomalie_idriche} gg
LST (Calore): {anomalie_termiche} gg

--- {t('fase_2').upper()} ---
AOD (Gas/Aerosol): {anomalie_aod} gg
OLR (Radiazione Term.): {anomalie_olr} gg

--- SCENARIO DIAGNOSTICATO ---
{titolo_scen}
{testo_desc_pulito}

=========================================
Report generato da L.A.I.C. Sentinel (SismaLab Suite)
Osservatorio Geofisico Valle del Liri (OGVL)
"""
    return html_content, report_text

# --- MAIN UI ---
logo_path = "logo.png" if os.path.exists("logo.png") else ("logo.jpg" if os.path.exists("logo.jpg") else None)

# REDESIGNED HEADER: Small Suite, Large Sentinel
if logo_path:
    with open(logo_path, "rb") as image_file: encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
    <div style="display: flex; align-items: flex-start; gap: 15px; margin-bottom: 25px;">
        <img src="data:image/png;base64,{encoded_string}" style="width: 55px; height: 55px; object-fit: contain; margin-top: 5px;">
        <div style="display: flex; flex-direction: column; justify-content: center;">
            <span style="font-size: 14px; color: #a0a0a0; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">SismaLab Suite</span>
            <h2 style="margin: 0; padding: 0; line-height: 1.1;"><span style="color: #ff5252; font-size: 32px; font-weight: 800;">L.A.I.C. Sentinel</span> <span style="font-size: 16px; color: #888; font-weight: normal;">{t('obs_name')}</span></h2>
        </div>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="margin-bottom: 25px;">
        <span style="font-size: 14px; color: #a0a0a0; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">SismaLab Suite</span>
        <h2 style="margin: 0; padding: 0; line-height: 1.1;"><span style="color: #ff5252; font-size: 32px; font-weight: 800;">L.A.I.C. Sentinel</span> <span style="font-size: 16px; color: #888; font-weight: normal;">{t('obs_name')}</span></h2>
    </div>""", unsafe_allow_html=True)

if init_earth_engine():
    with st.sidebar:
        def reset_motore():
            st.session_state['elaborazione_completata'] = False

        esegui = st.button(t('btn_run'), type="primary", use_container_width=True)
        
        if st.button(t('btn_logout'), type="secondary", use_container_width=True, key="logout_btn"):
            st.session_state["password_correct"] = False
            st.rerun()
            
        st.markdown("---")
        modalita_analisi = st.radio(t('mode_title'), [t('mode_1'), t('mode_2')], index=0, on_change=reset_motore)
        st.markdown("---")

        with st.container(border=True):
            st.markdown(t('win_title'))
            # INGV L'Aquila Earthquake data used as fixed default for both modes
            data_default = datetime(2009, 4, 6)
            
            if modalita_analisi == t('mode_1'):
                st.markdown(t('date_ms'))
                data_target_input = st.date_input("MS", value=data_default, min_value=datetime(1980, 1, 1), max_value=datetime.today().date(), label_visibility="collapsed", on_change=reset_motore)
                data_in_calcolata, data_fi_calcolata, data_mainshock_str = data_target_input - timedelta(days=90), data_target_input + timedelta(days=30), data_target_input.strftime("%Y-%m-%d")
            else:
                st.markdown(t('date_obs'))
                data_target_input = st.date_input("OBS", value=data_default, min_value=datetime(1980, 1, 1), max_value=datetime.today().date(), label_visibility="collapsed", on_change=reset_motore)
                data_in_calcolata, data_fi_calcolata, data_mainshock_str = data_target_input - timedelta(days=90), data_target_input, None
            st.success(f"**{data_in_calcolata.strftime('%d/%m/%Y')}** ➔ **{data_fi_calcolata.strftime('%d/%m/%Y')}**")
            
        with st.container(border=True):
            st.markdown(t('geo_title'))
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown(t('lat_epi') if modalita_analisi == t('mode_1') else t('lat_center'), unsafe_allow_html=True)
                # INGV L'Aquila Earthquake data
                lat_input = st.number_input("Lat", value=42.3420, format="%.4f", label_visibility="collapsed", on_change=reset_motore)
                st.markdown(t('mag_ms') if modalita_analisi == t('mode_1') else t('mag_scan'), unsafe_allow_html=True)
                mag_input = st.number_input("Mag", value=6.1, step=0.1, label_visibility="collapsed", on_change=reset_motore)
            with col_c2:
                st.markdown(t('lon_epi') if modalita_analisi == t('mode_1') else t('lon_center'), unsafe_allow_html=True)
                # INGV L'Aquila Earthquake data
                lon_input = st.number_input("Lon", value=13.3800, format="%.4f", label_visibility="collapsed", on_change=reset_motore)

        with st.expander(t('help_rad')):
            st.markdown("Formula: **R = 10^(0.43M)**<br>* **M 4.0** ➔ ~ 52 km<br>* **M 5.0** ➔ ~ 141 km<br>* **M 6.0** ➔ ~ 380 km<br>* **M 7.0** ➔ ~ 1023 km", unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown(f"<div style='text-align: center; font-size: 13px; color: #888;'>{t('author')}</div>", unsafe_allow_html=True)

    if esegui: st.session_state['elaborazione_completata'] = True

    if st.session_state.get('elaborazione_completata', False):
        status_box = st.empty()
        if esegui: status_box.info(t('wait_msg'))
        df, sisma = esegui_estrazione(lat_input, lon_input, mag_input, data_in_calcolata.strftime("%Y-%m-%d"), data_fi_calcolata.strftime("%Y-%m-%d"), modalita_analisi, data_mainshock_str)
        status_box.success(t('ok_msg'))
        
        with st.expander(t('manual_title'), expanded=False):
            st.markdown(t('manual_text'), unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_t1, col_t2, col_t3 = st.columns([1, 1, 1.5])
        with col_t1: mostra_allarmi = st.toggle(t('tog_anom'), value=False)
        with col_t2: mostra_reticolato = st.toggle(t('tog_grid'), value=False)
        with col_t3: 
            # Memory injection into the slider
            soglia_fisica_ndwi = st.slider("💧 Soglia di Taglio NDWI", min_value=-0.10, max_value=0.30, value=st.session_state['soglia_ndwi_mem'], step=0.01, help=t('help_ndwi'))
            st.session_state['soglia_ndwi_mem'] = soglia_fisica_ndwi
            st.markdown(f"<div style='font-size: 11px; color: #a0a0a0; margin-top: -10px; line-height: 1.2;'>{t('note_ndwi')}</div>", unsafe_allow_html=True)
        
        st.plotly_chart(crea_spaccato_analitico(df, sisma, mostra_allarmi, mostra_reticolato, soglia_fisica_ndwi), use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})
            
        # Generation of HTML Summary and downloadable Text Report
        html_sintesi, txt_report = genera_sintesi(
            df, sisma, modalita_analisi, soglia_fisica_ndwi, 
            lat_input, lon_input, mag_input, 
            data_in_calcolata.strftime("%Y-%m-%d"), 
            data_fi_calcolata.strftime("%Y-%m-%d"), 
            data_target_input.strftime("%Y-%m-%d")
        )
        
        st.markdown(html_sintesi, unsafe_allow_html=True)
        
        # NATIVE STREAMLIT DOWNLOAD BUTTON INJECTED BELOW SUMMARY
        st.download_button(
            label=t('btn_download'),
            data=txt_report,
            file_name=f"Report_LAIC_{data_target_input.strftime('%Y%m%d')}.txt",
            mime="text/plain",
            type="primary"
        )
else:
    st.warning("In attesa del file sismalab_key.json o st.secrets.")

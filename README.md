# COE203: Project 2 – Web Monitoring

*Create an automated system tracking web data and sending alerts*

## ISU Flood Automation

This project idea came from the flood in the Vadi İstanbul area on Wednesday, 14 October 2026, which
made the ground floors of the affected H Campus unusable.

## Project Goal

To build a decision-support automation that processes real-time rainfall data from the Cendere basin
without human input (web monitoring). The moment the flood risk crosses the critical threshold, and
before the water reaches the campus, it dynamically calculates the **"fastest and safest preventive
logistics evacuation route"** from the nearest logistics center to the campus and mobilizes the teams.

## Workflow

### Step 1: Data Acquisition & Cleaning (Acquire & Clean)

Running periodically in the background (triggered by a scheduler), the system sends requests for live
weather data to the official **İBB Open Data Portal**, or to **AKOM / the MGM Sarıyer station**. It
passes the incoming raw text through a whitespace-cleaning string pipeline and converts it into pure
numeric values.

### Step 2: Memory & State Checking (State Checking & Memory)

The parsed real-time rainfall rate is compared against **50 mm/h (kg/m²)**, the record level that
triggered the 14 October disaster, which is used as the critical threshold. The system reads the
`state.json` file (the state file) in our local folder and confirms that the situation has changed from
normal to dangerous. **As long as the risk continues, it prevents unnecessary alerts from being sent.**

### Step 3: Route & Dispatch Decision (Logistic Optimization)

The moment the critical threshold is crossed, our automation measures the logistics distance between
the campus coordinates and the two nearest emergency centers (for example, **Hasdal AFAD Logistics
Base** and **Kağıthane Fire Station**). It automatically identifies the fastest and safest response
center, one that will not be affected by flood water.

### Step 4: Actionable Output (Actionable Notification)

Our system turns the dispatch corridor, from the selected logistics base to the gate of the İSÜ H
Campus, into a dynamic interactive map (our flood route file, `flood_route.html`). Instead of weak
messages, it sends the crisis management teams' emergency channel (**Telegram/Discord webhook**) an
operational action guide that contains the map link itself and which aid has been dispatched (mobile
barriers, submersible pumps, etc.).

## Project Structure

```
isu_flood_automation/   (or hydroguard/)
├── main.py
├── pipeline.py
├── router.py
├── .gitignore
├── data_store/
│   ├── state.json
│   └── flood_route.html
├── contributions/
│   ├── HILAL_ONAY_2508041036_nyx56.md
│   ├── ELIF_SU_ILERI_2308041044_iamelifsu.md
│   ├── SEDANUR_BAYRAM_2508051037_sedabayram.md
│   └── YAVUZ_SELIM_DILMEN_2508051036_yavuzdilmen.md
└── README.md
```

## Files We Developed

| File | What the System Does |
|---|---|
| `main.py` | Pulls real-time rainfall and timestamp data from İBB or MGM web servers (web monitoring). |
| `pipeline.py` | Cleans the incoming raw text and converts it into numbers for the 50 mm/h threshold check. |
| `state.json` | Triggers only on new risk states through the file. Blocks repeated alarms and keeps only new crises in memory. |
| `router.py` and `flood_route.html` | Draws a dynamic evacuation route from Hasdal or Kağıthane to İSÜ with the folium library and sends a webhook to the teams (`router.py`). Also produces the generated interactive map, which opens in a browser, as a meaningful output (`flood_route.html`). |

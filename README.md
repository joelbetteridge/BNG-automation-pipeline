# Statutory Biodiversity Net Gain (BNG) Assessment Pipeline

This repository contains an automated spatial data pipeline and feasibility assessment calculating the statutory 10% Biodiversity Net Gain (BNG) target for a proposed 5.2 ha water infrastructure development. 

Designed to demonstrate commercial ecological consultancy workflows, this project bridges spatial mapping in ArcGIS Pro with a custom-built Python and SQL data pipeline to execute the DEFRA metric calculations, culminated into a preliminary client-facing report.

## Project Structure

```text
.
├── README.md
├── preliminary_BNG_assessment.pdf  # Final Stage 1 Feasibility Assessment report
├── data-raw/
│   ├── baseline_habitats.xlsx      # ArcGIS attribute export of existing UKHab polygons
│   ├── proposed_habitats.xlsx      # ArcGIS attribute export of proposed habitat polygons
│   ├── bng_lookups.xlsx            # DEFRA metric reference data (distinctiveness, condition, etc.)
│   └── GIS_files/                  # Raw shapefiles (.shp, .shx, .dbf) mapped in ArcGIS Pro
├── maps/
│   ├── baseline_habitats.png       # Visual layout of existing site habitats
│   └── proposed_habitats.png       # Visual layout of post-development landscape
└── scripts/
    └── bng_pipeline.py             # Main Python/SQLite data processing script
```

## Methodology

This project replicates an end-to-end environmental data science workflow for BNG assessments:

1. **Spatial Mapping (ArcGIS Pro):** 
   Digitized baseline and proposed site layouts based on UKHab classifications. Mapped the integration of a new constructed wetland retention basin and hardstanding infrastructure, then extracted area attributes. Classifications are not realistic to the actual land, and act primarily as a demonstration.
2. **Data Ingestion (Python/Pandas):** 
   Extracted spatial attribute data is ingested into Python alongside DEFRA BNG metric reference tables (distinctiveness, condition, significance, and creation risk multipliers).
3. **Metric Calculation (In-Memory SQLite):** 
   Rather than relying on manual spreadsheet calculations, `bng_pipeline.py` constructs an in-memory relational database using `sqlite3`. It executes SQL `JOIN` operations to calculate total baseline units, proposed units, and the net unit change, accurately applying DEFRA multiplier logic.
4. **Commercial Reporting:** 
   The pipeline outputs inform a preliminary BNG assessment detailing a -26.64% unit deficit, complete with actionable mitigation recommendations (e.g., reducing hardstanding footprint, sourcing off-site Habitat Bank units).

## Tech Stack
* **Languages:** Python (Pandas), SQL (SQLite)
* **GIS:** ArcGIS Pro (UKHab Classification)
* **Reporting:** Markdown/PDF

## Author
**Joel Betteridge**  
*Final-year Ecology BSc student at the University of York, specializing in environmental data science and spatial analysis.*

*This work was assisted by the use of Google Gemini for idea creation*
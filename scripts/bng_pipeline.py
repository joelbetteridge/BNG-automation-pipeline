# This script reads in the ArcGIS exports and the Defra Metric Reference Data,
# calculates the total baseline and proposed biodiversity units,
# and outputs a summary of the results along with a breakdown by habitat type.

import sqlite3
import pandas as pd

# Read in the ArcGIS exports from the data-raw folder
df_baseline = pd.read_excel("data-raw/baseline_habitats.xlsx")
df_proposed = pd.read_excel("data-raw/proposed_habitats.xlsx")

# Read in the 4 Defra Metric Reference Data sheets from the workbook
lookup_path = "data-raw/bng_lookups.xlsx"
df_dist = pd.read_excel(lookup_path, sheet_name = "distinctiveness")
df_cond = pd.read_excel(lookup_path, sheet_name = "condition")
df_sig = pd.read_excel(lookup_path, sheet_name = "significance")
df_risk = pd.read_excel(lookup_path, sheet_name = "creation_risk")

# Create the in-memory SQL database connection
conn = sqlite3.connect(":memory:")

# Put each dataframe in to the SQL tables
df_baseline.to_sql("baseline_habitats", conn, index = False, if_exists = "replace")
df_proposed.to_sql("proposed_habitats", conn, index = False, if_exists = "replace")
df_dist.to_sql("lookup_distinctiveness", conn, index = False, if_exists = "replace")
df_cond.to_sql("lookup_condition", conn, index = False, if_exists = "replace")
df_sig.to_sql("lookup_significance", conn, index = False, if_exists = "replace")
df_risk.to_sql("lookup_creation_risk", conn, index = False, if_exists = "replace")

# Calculate total baseline units using SQL
bng_summary_query = """
WITH baseline_summary AS (
    SELECT
        SUM(b.area_ha * d.distinctiveness_score * c.multiplier *
    s.multiplier) AS total_baseline_units
    FROM `baseline_habitats` as b
    INNER JOIN lookup_distinctiveness AS d ON b.ukhab_code = d.ukhab_code
    INNER JOIN lookup_condition AS c ON b.condition = c.condition_qual
    INNER JOIN lookup_significance AS s ON b.strategic_sig = s.significance_tier
),
proposed_summary AS (
    SELECT
        SUM(p.area_ha * d.distinctiveness_score * c.multiplier * s.multiplier *
        r.difficulty_multiplier * r.temporal_multiplier) AS total_proposed_units
    FROM `proposed_habitats` as p
    INNER JOIN lookup_distinctiveness AS d ON p.ukhab_code = d.ukhab_code
    INNER JOIN lookup_condition AS c ON p.condition = c.condition_qual
    INNER JOIN lookup_significance AS s ON p.strategic_sig = s.significance_tier
    INNER JOIN lookup_creation_risk AS r ON p.ukhab_code = r.ukhab_code
)
SELECT
    ROUND(b.total_baseline_units, 2) AS baseline_units,
    ROUND(p.total_proposed_units, 2) AS proposed_units,
    ROUND(p.total_proposed_units - b.total_baseline_units, 2) AS net_unit_change,
    ROUND(((p.total_proposed_units - b.total_baseline_units) / b.total_baseline_units) * 100, 2) AS pct_net_gain,
    CASE
        WHEN ((p.total_proposed_units - b.total_baseline_units) / b.total_baseline_units) * 100 >= 10.0
        THEN 'PASSED: Achieved 10% BNG'
        ELSE 'FAILED: Insufficient Biodiversity Uplift'
    END AS bng_status
FROM baseline_summary as b
CROSS JOIN proposed_summary as p;
"""

# Run the query and convert to a Pandas dataframe
bng_results = pd.read_sql_query(bng_summary_query, conn)

# Print the results
print("\n--- Site Summary ---")
print(bng_results.to_string(index = False))

# Calculate units grouped by habitat type
breakdown_query = """
WITH baseline_habs AS (
    SELECT 
        b.ukhab_code,
        SUM(b.area_ha * d.distinctiveness_score * c.multiplier * s.multiplier) AS base_units
    FROM baseline_habitats AS b
    INNER JOIN lookup_distinctiveness AS d ON b.ukhab_code = d.ukhab_code
    INNER JOIN lookup_condition AS c ON b.condition = c.condition_qual
    INNER JOIN lookup_significance AS s ON b.strategic_sig = s.significance_tier
    GROUP BY b.ukhab_code
),
proposed_habs AS (
    SELECT 
        p.ukhab_code,
        SUM(p.area_ha * d.distinctiveness_score * c.multiplier * s.multiplier * r.difficulty_multiplier * r.temporal_multiplier) AS prop_units
    FROM proposed_habitats AS p
    INNER JOIN lookup_distinctiveness AS d ON p.ukhab_code = d.ukhab_code
    INNER JOIN lookup_condition AS c ON p.condition = c.condition_qual
    INNER JOIN lookup_significance AS s ON p.strategic_sig = s.significance_tier
    INNER JOIN lookup_creation_risk AS r ON p.ukhab_code = r.ukhab_code
    GROUP BY p.ukhab_code
),
-- Create a unified list of all habitat codes present in either phase
all_habs AS (
    SELECT ukhab_code FROM baseline_habs
    UNION
    SELECT ukhab_code FROM proposed_habs
)
SELECT 
    a.ukhab_code,
    ROUND(COALESCE(b.base_units, 0), 2) AS baseline_units,
    ROUND(COALESCE(p.prop_units, 0), 2) AS proposed_units,
    ROUND(COALESCE(p.prop_units, 0) - COALESCE(b.base_units, 0), 2) AS net_change
FROM all_habs a
LEFT JOIN baseline_habs b ON a.ukhab_code = b.ukhab_code
LEFT JOIN proposed_habs p ON a.ukhab_code = p.ukhab_code
ORDER BY net_change ASC;
"""

# Run the query and convert to a Pandas dataframe
breakdown_results = pd.read_sql_query(breakdown_query, conn)

# Print the results
print("\n--- Habitat Type Breakdown ---")
print(breakdown_results.to_string(index = False))

# Close connection
conn.close()


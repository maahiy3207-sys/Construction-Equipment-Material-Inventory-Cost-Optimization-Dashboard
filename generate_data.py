"""
generate_data.py
-----------------
Generates a realistic SYNTHETIC dataset for the
'Construction Equipment & Material Inventory Cost Optimization' project
for KT Constructionwala Pvt Ltd.

Run: python3 generate_data.py
Output: construction_inventory_data.csv (50 rows)
"""

import pandas as pd
import numpy as np
import random
from datetime import timedelta, date

# Fixed seed -> reproducible dataset (important for a college report / re-runs)
random.seed(42)
np.random.seed(42)

N_ROWS = 50

SITE_LOCATIONS = ["Mumbai", "Pune", "Delhi", "Bengaluru", "Chennai", "Hyderabad"]

# Material type -> (approx price per ton in INR, typical order qty range in tons)
MATERIALS = {
    "Cement":            (7500,   5, 40),
    "Steel":             (62000,  3, 25),
    "Sand":              (1800,  10, 60),
    "Bricks":            (6500,   8, 45),
    "Heavy Equipment":   (150000, 1, 6),
    "Tiles":             (35000,  2, 15),
    "Wood":              (48000,  1, 10),
}

VENDORS = [
    "Apex Supplies", "BuildCorp", "UltraTech Supply", "Metro Infra",
    "Shree Cement Co", "JSW Steel Traders", "Konkan Aggregates",
    "Bharat Building Materials",
]

# Give a few vendors a built-in tendency to run late / overrun cost,
# so the analysis (delay leaderboard, cost variance) has a realistic signal.
VENDOR_DELAY_BIAS = {
    "Apex Supplies": 1,
    "BuildCorp": 6,          # consistently late vendor
    "UltraTech Supply": 0,
    "Metro Infra": 3,
    "Shree Cement Co": -1,   # often early/on-time
    "JSW Steel Traders": 2,
    "Konkan Aggregates": 4,
    "Bharat Building Materials": 0,
}

VENDOR_COST_OVERRUN_BIAS = {
    "Apex Supplies": 0.02,
    "BuildCorp": 0.09,       # tends to overrun cost
    "UltraTech Supply": 0.01,
    "Metro Infra": 0.05,
    "Shree Cement Co": -0.01,
    "JSW Steel Traders": 0.04,
    "Konkan Aggregates": 0.03,
    "Bharat Building Materials": 0.02,
}

START_DATE = date(2024, 1, 1)
END_DATE = date(2024, 11, 30)


def random_order_date():
    span = (END_DATE - START_DATE).days
    return START_DATE + timedelta(days=random.randint(0, span))


rows = []
for i in range(1, N_ROWS + 1):
    project_id = f"PRJ-{i:03d}"
    site = random.choice(SITE_LOCATIONS)
    material = random.choice(list(MATERIALS.keys()))
    vendor = random.choice(VENDORS)
    price_per_ton, qty_min, qty_max = MATERIALS[material]

    qty = round(np.random.uniform(qty_min, qty_max), 1)

    order_date = random_order_date()
    # Promised lead time depends loosely on material type (heavy equipment takes longer)
    base_lead = {"Heavy Equipment": 20, "Steel": 14, "Tiles": 12, "Wood": 12}.get(material, 8)
    promised_lead = base_lead + random.randint(-2, 4)
    promised_delivery = order_date + timedelta(days=max(promised_lead, 3))

    # Actual delivery = promised + (vendor bias + random noise), can be early (negative)
    bias = VENDOR_DELAY_BIAS[vendor]
    noise = random.randint(-3, 6)
    delay = max(bias + noise, -4)  # allow a bit of early delivery
    actual_delivery = promised_delivery + timedelta(days=delay)

    estimated_cost = round(price_per_ton * qty * np.random.uniform(0.97, 1.03), 2)

    overrun_bias = VENDOR_COST_OVERRUN_BIAS[vendor]
    cost_noise = np.random.uniform(-0.03, 0.05)
    actual_cost = round(estimated_cost * (1 + overrun_bias + cost_noise), 2)

    # Quality pass probability drops slightly for chronically late / overrunning vendors
    pass_prob = 0.93 - (0.015 * bias) - (0.4 * max(overrun_bias, 0))
    quality_pass = "Yes" if random.random() < max(pass_prob, 0.6) else "No"

    rows.append({
        "Project_ID": project_id,
        "Site_Location": site,
        "Material_Type": material,
        "Vendor_Name": vendor,
        "Order_Date": order_date.isoformat(),
        "Promised_Delivery_Date": promised_delivery.isoformat(),
        "Actual_Delivery_Date": actual_delivery.isoformat(),
        "Estimated_Cost_INR": estimated_cost,
        "Actual_Cost_INR": actual_cost,
        "Quantity_Ordered_Tons": qty,
        "Quality_Pass": quality_pass,
    })

df = pd.DataFrame(rows)
df.to_csv("construction_inventory_data.csv", index=False)
print("Saved construction_inventory_data.csv with", len(df), "rows")
print(df.head())

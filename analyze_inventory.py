"""
analyze_inventory.py
---------------------
Step-by-step analysis for KT Constructionwala Pvt Ltd's
Construction Equipment & Material Inventory Cost Optimization project.

Run: python3 analyze_inventory.py
Reads : construction_inventory_data.csv
Writes: cost_variance_by_site.png, avg_delay_by_vendor.png
"""

import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# STEP 0: Load the data
# ---------------------------------------------------------------
df = pd.read_csv("construction_inventory_data.csv", parse_dates=[
    "Order_Date", "Promised_Delivery_Date", "Actual_Delivery_Date"
])

# ---------------------------------------------------------------
# STEP 1: Delivery_Delay_Days = Actual_Delivery_Date - Promised_Delivery_Date
# ---------------------------------------------------------------
df["Delivery_Delay_Days"] = (
    df["Actual_Delivery_Date"] - df["Promised_Delivery_Date"]
).dt.days

# ---------------------------------------------------------------
# STEP 2: Cost_Variance_INR = Actual_Cost_INR - Estimated_Cost_INR
# ---------------------------------------------------------------
df["Cost_Variance_INR"] = df["Actual_Cost_INR"] - df["Estimated_Cost_INR"]
df["Cost_Variance_Pct"] = (df["Cost_Variance_INR"] / df["Estimated_Cost_INR"] * 100).round(2)

# Save the enriched dataset (useful to attach in the report appendix)
df.to_csv("construction_inventory_data_enriched.csv", index=False)

# ---------------------------------------------------------------
# STEP 3: Vendor with the highest AVERAGE delivery delay
# ---------------------------------------------------------------
vendor_delay = (
    df.groupby("Vendor_Name")["Delivery_Delay_Days"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)
worst_delay_vendor = vendor_delay.index[0]
worst_delay_value = vendor_delay.iloc[0]

print("=" * 60)
print("STEP 3: Average Delivery Delay by Vendor (days)")
print("=" * 60)
print(vendor_delay.to_string())
print(f"\n>> Vendor with highest average delay: {worst_delay_vendor} "
      f"({worst_delay_value} days)\n")

# ---------------------------------------------------------------
# STEP 4: Summary stats for Cost_Variance_INR per Site_Location
# ---------------------------------------------------------------
site_cost_summary = df.groupby("Site_Location")["Cost_Variance_INR"].agg(
    ["count", "mean", "median", "std", "min", "max", "sum"]
).round(2).sort_values("sum", ascending=False)

print("=" * 60)
print("STEP 4: Cost Variance (INR) Summary by Site Location")
print("=" * 60)
print(site_cost_summary.to_string())
print()

# ---------------------------------------------------------------
# Extra useful cuts (handy for the report but not strictly asked)
# ---------------------------------------------------------------
material_cost_summary = df.groupby("Material_Type")["Cost_Variance_INR"].mean().round(2).sort_values(ascending=False)
quality_fail_rate = (df["Quality_Pass"] == "No").mean() * 100
overrun_share = (df["Cost_Variance_INR"] > 0).mean() * 100
late_share = (df["Delivery_Delay_Days"] > 0).mean() * 100

# ---------------------------------------------------------------
# CHART 1: Average Delivery Delay by Vendor (bar chart)
# ---------------------------------------------------------------
plt.figure(figsize=(9, 5))
colors = ["#d62728" if v == worst_delay_vendor else "#1f77b4" for v in vendor_delay.index]
plt.bar(vendor_delay.index, vendor_delay.values, color=colors)
plt.axhline(0, color="black", linewidth=0.8)
plt.title("Average Delivery Delay by Vendor")
plt.ylabel("Average Delay (days)")
plt.xlabel("Vendor")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()
plt.savefig("avg_delay_by_vendor.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# CHART 2: Cost Variance by Site Location (box-style summary via bar of mean + error bars)
# ---------------------------------------------------------------
plt.figure(figsize=(9, 5))
plt.bar(
    site_cost_summary.index,
    site_cost_summary["mean"],
    yerr=site_cost_summary["std"],
    capsize=5,
    color="#2ca02c",
)
plt.axhline(0, color="black", linewidth=0.8)
plt.title("Average Cost Variance (INR) by Site Location (±1 std dev)")
plt.ylabel("Cost Variance (INR)")
plt.xlabel("Site Location")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig("cost_variance_by_site.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# STEP 5: Executive key insights (printed; also see write-up)
# ---------------------------------------------------------------
total_overrun = df.loc[df["Cost_Variance_INR"] > 0, "Cost_Variance_INR"].sum()
total_estimated = df["Estimated_Cost_INR"].sum()

print("=" * 60)
print("STEP 5: Auto-generated Executive Insight Data Points")
print("=" * 60)
print(f"- Highest avg delay vendor : {worst_delay_vendor} ({worst_delay_value} days)")
print(f"- Site with highest total cost overrun : {site_cost_summary['sum'].idxmax()} "
      f"(₹{site_cost_summary['sum'].max():,.0f} total variance)")
print(f"- Material type with highest avg cost variance : {material_cost_summary.index[0]} "
      f"(₹{material_cost_summary.iloc[0]:,.0f} avg variance)")
print(f"- % of orders delivered late : {late_share:.1f}%")
print(f"- % of orders with a cost overrun : {overrun_share:.1f}%")
print(f"- Overall quality failure rate : {quality_fail_rate:.1f}%")
print(f"- Total cost overrun across all overrun orders : ₹{total_overrun:,.0f} "
      f"({total_overrun/total_estimated*100:.1f}% of total estimated spend)")

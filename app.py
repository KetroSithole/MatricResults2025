import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Education Intelligence Platform",
    layout="wide"
)

st.title("🎓 Education Intelligence & Prediction Platform (2025)")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("2025 SCHOOL PERFORMANCE REPORT.xlsx")

    df = df.rename(columns={
        "Unnamed: 0": "School_Code",
        "Unnamed: 1": "School_Name",
        "Unnamed: 3": "Quintile",
        "Unnamed: 13": "Total_Wrote",
        "Unnamed: 14": "Total_Achieved",
        "Unnamed: 15": "Percent_Achieved",
        "Unnamed: 16": "District",
        "Unnamed: 17": "Province"
    })

    df["Percent_Achieved"] = pd.to_numeric(df["Percent_Achieved"], errors="coerce")
    df["Quintile"] = pd.to_numeric(df["Quintile"], errors="coerce")
    df["Total_Wrote"] = pd.to_numeric(df["Total_Wrote"], errors="coerce")
    df["Total_Achieved"] = pd.to_numeric(df["Total_Achieved"], errors="coerce")

    df = df.dropna(subset=["School_Name", "Percent_Achieved", "Province"])
    return df

df = load_data()

# -------------------------------------------------
# FEATURE ENGINEERING (CORE)
# -------------------------------------------------
def perf_band(x):
    if x >= 90: return "Excellent"
    if x >= 75: return "Good"
    if x >= 50: return "Average"
    return "Poor"

df["Actual_Band"] = df["Percent_Achieved"].apply(perf_band)

df["Expected_Band"] = df["Quintile"].apply(
    lambda q: "Excellent" if q >= 4 else "Good" if q == 3 else "Average"
)

df["Efficiency_Score"] = df["Total_Achieved"] / df["Total_Wrote"]
df["Efficiency_Score"] = df["Efficiency_Score"].fillna(0)

df["Equity_Gap"] = df["Percent_Achieved"] - (df["Quintile"] * 15)

df["Growth_Index"] = (
    df["Percent_Achieved"] * 0.6 +
    df["Efficiency_Score"] * 100 * 0.4
)

df["Stability_Index"] = np.clip(
    df["Efficiency_Score"] * 100, 0, 100
)

# -------------------------------------------------
# RISK & PREDICTION FEATURES
# -------------------------------------------------
def risk_label(p):
    if p < 50: return "High Risk"
    if p < 70: return "Medium Risk"
    return "Low Risk"

df["Risk_Category"] = df["Percent_Achieved"].apply(risk_label)

df["Projected_Pass_Rate_2026"] = np.clip(
    df["Percent_Achieved"] + (df["Growth_Index"] - 70) * 0.15,
    30, 100
)

df["Intervention_Priority"] = (
    (100 - df["Percent_Achieved"]) * 0.5 +
    abs(df["Equity_Gap"]) * 0.3 +
    (100 - df["Stability_Index"]) * 0.2
)

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.header("🔍 Filters")

province = st.sidebar.multiselect(
    "Province",
    sorted(df["Province"].unique()),
    default=sorted(df["Province"].unique())
)

filtered = df[df["Province"].isin(province)]

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Schools", len(filtered))
c2.metric("Avg Pass %", f"{filtered['Percent_Achieved'].mean():.1f}%")
c3.metric("100% Schools", (filtered["Percent_Achieved"] == 100).sum())
c4.metric("High Risk", (filtered["Risk_Category"] == "High Risk").sum())
c5.metric("Priority Interventions", (filtered["Intervention_Priority"] > 50).sum())

# -------------------------------------------------
# HEATMAP MATRIX
# -------------------------------------------------
st.subheader("🧩 Province vs Performance Matrix")

heat = pd.crosstab(
    filtered["Province"],
    filtered["Actual_Band"],
    normalize="index"
) * 100

fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(heat, annot=True, fmt=".1f", cmap="Blues", ax=ax)
st.pyplot(fig)

# -------------------------------------------------
# CONFUSION / EXPECTATION MATRIX
# -------------------------------------------------
st.subheader("🎯 Expected vs Actual Performance")

conf = pd.crosstab(
    filtered["Expected_Band"],
    filtered["Actual_Band"]
)

fig2, ax2 = plt.subplots(figsize=(6, 5))
sns.heatmap(conf, annot=True, fmt="d", cmap="Oranges", ax=ax2)
st.pyplot(fig2)

# -------------------------------------------------
# PREDICTION VIEW
# -------------------------------------------------
st.subheader("🔮 Projected Pass Rates (2026)")

top_projection = filtered.sort_values(
    "Projected_Pass_Rate_2026", ascending=False
).head(20)

st.dataframe(
    top_projection[[
        "School_Name", "Province",
        "Percent_Achieved",
        "Projected_Pass_Rate_2026",
        "Risk_Category"
    ]]
)

# -------------------------------------------------
# INTERVENTION DASHBOARD
# -------------------------------------------------
st.subheader("🚨 Priority Intervention Schools")

interventions = filtered.sort_values(
    "Intervention_Priority", ascending=False
).head(20)

st.dataframe(
    interventions[[
        "School_Name", "Province", "Quintile",
        "Percent_Achieved",
        "Risk_Category",
        "Intervention_Priority"
    ]]
)

# -------------------------------------------------
# SCHOOL COMPARISON
# -------------------------------------------------
st.subheader("🏫 School Comparison")

schools = st.multiselect(
    "Select schools",
    filtered["School_Name"].unique()
)

if schools:
    st.dataframe(
        filtered[filtered["School_Name"].isin(schools)][[
            "School_Name", "Province", "Quintile",
            "Percent_Achieved", "Projected_Pass_Rate_2026",
            "Risk_Category", "Growth_Index"
        ]]
    )

# -------------------------------------------------
# DOWNLOAD
# -------------------------------------------------
st.subheader("⬇️ Export Data")

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Full Analytics Dataset",
    csv,
    "education_intelligence_2025.csv",
    "text/csv"
)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Bursary Investment Analysis – Matric 2025",
    layout="wide"
)

st.title("🎓 Bursary Investment Decision Dashboard")
st.caption("Purpose: Identify where bursary funding achieves the highest educational return")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("2025 SCHOOL PERFORMANCE REPORT.xlsx")

    df = df.rename(columns={
        "Unnamed: 1": "School_Name",
        "Unnamed: 3": "Quintile",
        "Unnamed: 13": "Total_Wrote",
        "Unnamed: 14": "Total_Achieved",
        "Unnamed: 15": "Pass_Rate",
        "Unnamed: 16": "District",
        "Unnamed: 17": "Province"
    })

    df["Pass_Rate"] = pd.to_numeric(df["Pass_Rate"], errors="coerce")
    df["Quintile"] = pd.to_numeric(df["Quintile"], errors="coerce")
    df = df.dropna(subset=["School_Name", "Pass_Rate", "Province", "Quintile"])

    return df

df = load_data()

# -------------------------------------------------
# INVESTMENT GROUP LOGIC (CORE)
# -------------------------------------------------
def investment_group(row):
    if row["Quintile"] <= 2 and row["Pass_Rate"] >= 80:
        return "Group A: High Impact / Best ROI"
    elif row["Quintile"] == 3 and row["Pass_Rate"] >= 75:
        return "Group B: Stable / Scalable"
    elif row["Pass_Rate"] >= 60:
        return "Group C: High Potential / Needs Support"
    else:
        return "Group D: High Risk / Not Bursary Ready"

df["Investment_Group"] = df.apply(investment_group, axis=1)

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.header("🔎 Filters")

province_filter = st.sidebar.multiselect(
    "Select Province(s)",
    sorted(df["Province"].unique()),
    default=sorted(df["Province"].unique())
)

filtered = df[df["Province"].isin(province_filter)]

# -------------------------------------------------
# EXECUTIVE KPIs
# -------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Schools Analysed", len(filtered))
c2.metric("Average Pass Rate", f"{filtered['Pass_Rate'].mean():.1f}%")
c3.metric("Best ROI Schools (Group A)", (filtered["Investment_Group"] == "Group A: High Impact / Best ROI").sum())
c4.metric("High Risk Schools", (filtered["Investment_Group"] == "Group D: High Risk / Not Bursary Ready").sum())

# -------------------------------------------------
# INVESTMENT GROUP OVERVIEW
# -------------------------------------------------
st.subheader("📊 Investment Group Breakdown")

group_counts = filtered["Investment_Group"].value_counts()

fig1, ax1 = plt.subplots()
group_counts.plot(kind="bar", ax=ax1)
ax1.set_ylabel("Number of Schools")
ax1.set_title("School Distribution by Investment Category")
plt.xticks(rotation=30, ha="right")

st.pyplot(fig1)

# -------------------------------------------------
# WHY GROUP A MATTERS (BOARD VIEW)
# -------------------------------------------------
st.subheader("🟢 Group A – Highest Return on Bursary Investment")

group_a = filtered[filtered["Investment_Group"] == "Group A: High Impact / Best ROI"] \
    .sort_values("Pass_Rate", ascending=False)

st.write("""
**These schools deliver strong academic outcomes despite low socio-economic conditions.**  
Funding learners here maximises:
- Graduation probability
- Equity impact
- Cost efficiency
""")

st.dataframe(
    group_a[[
        "School_Name", "Province", "District",
        "Quintile", "Pass_Rate"
    ]],
    use_container_width=True
)

# -------------------------------------------------
# PROVINCE INVESTMENT PROFILE
# -------------------------------------------------
st.subheader("🗺️ Provincial Investment Profile")

province_summary = filtered.groupby("Province").agg(
    Avg_Pass_Rate=("Pass_Rate", "mean"),
    Best_ROI_Schools=("Investment_Group", lambda x: (x == "Group A: High Impact / Best ROI").sum()),
    High_Risk_Schools=("Investment_Group", lambda x: (x == "Group D: High Risk / Not Bursary Ready").sum())
).reset_index()

st.dataframe(province_summary, use_container_width=True)

# -------------------------------------------------
# RISK WARNING SECTION
# -------------------------------------------------
st.subheader("🔴 High-Risk Funding Environments")

st.write("""
Schools below **60% pass rate** present a **high dropout risk**.  
Bursaries alone are unlikely to succeed without additional academic interventions.
""")

group_d = filtered[filtered["Investment_Group"] == "Group D: High Risk / Not Bursary Ready"]

st.dataframe(
    group_d[[
        "School_Name", "Province", "District",
        "Quintile", "Pass_Rate"
    ]],
    use_container_width=True
)

# -------------------------------------------------
# DOWNLOAD FOR FUNDERS
# -------------------------------------------------
st.subheader("⬇️ Export Investment-Ready Data")

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Full Investment Dataset",
    csv,
    "bursary_investment_analysis_2025.csv",
    "text/csv"
)

# -------------------------------------------------
# FOOTER MESSAGE (IMPORTANT)
# -------------------------------------------------
st.markdown("---")
st.caption(
    "This analysis supports **evidence-based bursary allocation**, balancing impact, risk, and equity. "
    "It is designed for funding committees and CSR investment boards."
)

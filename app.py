import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Bursary Investment Analysis – Matric 2025",
    layout="wide"
)

st.title("🎓 Bursary Investment Decision Dashboard")
st.caption(
    "Purpose: Identify schools where bursary funding delivers the highest probability of learner success per rand invested."
)

# =================================================
# LOAD & CLEAN DATA
# =================================================
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
    df["Total_Wrote"] = pd.to_numeric(df["Total_Wrote"], errors="coerce")
    df["Total_Achieved"] = pd.to_numeric(df["Total_Achieved"], errors="coerce")

    df = df.dropna(subset=["School_Name", "Pass_Rate", "Quintile", "Province"])
    return df

df = load_data()

# =================================================
# INVESTMENT GROUP LOGIC (CORE BUSINESS LOGIC)
# =================================================
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

# =================================================
# ADDITIONAL INVESTMENT FEATURES
# =================================================
df["Risk_Level"] = df["Pass_Rate"].apply(
    lambda x: "Low Risk" if x >= 80 else "Medium Risk" if x >= 60 else "High Risk"
)

df["Investment_Score"] = (
    df["Pass_Rate"] * 0.6 +
    (6 - df["Quintile"]) * 10 * 0.4
)

df["Expected_Pass"] = df["Quintile"] * 15 + 40
df["Performance_Gap"] = df["Pass_Rate"] - df["Expected_Pass"]

df["Impact_Potential"] = df["Total_Achieved"] * df["Pass_Rate"] / 100

def funding_recommendation(row):
    if row["Investment_Group"].startswith("Group A"):
        return "Full Bursary + University Support"
    elif row["Investment_Group"].startswith("Group B"):
        return "Partial Bursary + Monitoring"
    elif row["Investment_Group"].startswith("Group C"):
        return "Conditional Bursary + Academic Support"
    else:
        return "Do Not Fund Without Intervention"

df["Funding_Recommendation"] = df.apply(funding_recommendation, axis=1)

# =================================================
# SIDEBAR FILTERS
# =================================================
st.sidebar.header("🔎 Filters")

province_filter = st.sidebar.multiselect(
    "Select Province(s)",
    sorted(df["Province"].unique()),
    default=sorted(df["Province"].unique())
)

filtered = df[df["Province"].isin(province_filter)]

# =================================================
# EXECUTIVE KPIs
# =================================================
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Schools Analysed", len(filtered))
c2.metric("Average Pass Rate", f"{filtered['Pass_Rate'].mean():.1f}%")
c3.metric("Best ROI Schools (Group A)", (filtered["Investment_Group"].str.startswith("Group A")).sum())
c4.metric("High Risk Schools", (filtered["Risk_Level"] == "High Risk").sum())
c5.metric("Avg Investment Score", f"{filtered['Investment_Score'].mean():.1f}")

# =================================================
# INVESTMENT GROUP DISTRIBUTION
# =================================================
st.subheader("📊 Investment Group Breakdown")

group_counts = filtered["Investment_Group"].value_counts()

fig1, ax1 = plt.subplots()
group_counts.plot(kind="bar", ax=ax1)
ax1.set_ylabel("Number of Schools")
ax1.set_title("Schools by Investment Category")
plt.xticks(rotation=30, ha="right")
st.pyplot(fig1)

# =================================================
# GROUP A – BEST ROI
# =================================================
st.subheader("🟢 Group A: Highest Return on Bursary Investment")

st.write("""
These schools demonstrate **strong academic outcomes despite socio-economic disadvantage**.
Funding learners here maximises:
- Graduation probability
- Equity impact
- Cost efficiency
""")

group_a = filtered[
    filtered["Investment_Group"].str.startswith("Group A")
].sort_values("Investment_Score", ascending=False)

st.dataframe(
    group_a[[
        "School_Name", "Province", "District",
        "Quintile", "Pass_Rate", "Investment_Score"
    ]],
    use_container_width=True
)

# =================================================
# PROVINCE INVESTMENT PROFILE
# =================================================
st.subheader("🗺️ Provincial Investment Profile")

province_summary = filtered.groupby("Province").agg(
    Avg_Pass_Rate=("Pass_Rate", "mean"),
    Best_ROI_Schools=("Investment_Group", lambda x: (x.str.startswith("Group A")).sum()),
    High_Risk_Schools=("Risk_Level", lambda x: (x == "High Risk").sum())
).reset_index()

st.dataframe(province_summary, use_container_width=True)

# =================================================
# OVER & UNDER PERFORMERS
# =================================================
st.subheader("⚖️ Performance vs Socio-Economic Expectation")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🟢 Overperforming Schools")
    st.dataframe(
        filtered.sort_values("Performance_Gap", ascending=False).head(15)[[
            "School_Name", "Province", "Quintile",
            "Pass_Rate", "Performance_Gap"
        ]],
        use_container_width=True
    )

with col_right:
    st.markdown("### 🔴 Underperforming Schools")
    st.dataframe(
        filtered.sort_values("Performance_Gap").head(15)[[
            "School_Name", "Province", "Quintile",
            "Pass_Rate", "Performance_Gap"
        ]],
        use_container_width=True
    )

# =================================================
# HIGH-RISK WARNING
# =================================================
st.subheader("🔴 High-Risk Funding Environments")

st.write("""
Schools below **60% pass rate** have a **high probability of bursary failure**
unless additional academic interventions are provided.
""")

st.dataframe(
    filtered[filtered["Risk_Level"] == "High Risk"][[
        "School_Name", "Province", "District",
        "Quintile", "Pass_Rate", "Funding_Recommendation"
    ]],
    use_container_width=True
)

# =================================================
# FUNDING STRATEGY VIEW
# =================================================
st.subheader("🎯 Recommended Funding Strategy")

st.dataframe(
    filtered.sort_values("Investment_Score", ascending=False)[[
        "School_Name", "Province", "Investment_Group",
        "Pass_Rate", "Investment_Score", "Funding_Recommendation"
    ]].head(30),
    use_container_width=True
)

# =================================================
# EXECUTIVE TAKEAWAYS
# =================================================
st.subheader("📌 Executive Investment Takeaways")

st.markdown(f"""
- **{(filtered['Investment_Group'].str.startswith('Group A')).sum()} schools**
  offer the **highest return per bursary rand invested**.
- **{(filtered['Risk_Level'] == 'High Risk').sum()} schools**
  present **significant dropout risk** if funded without support.
- The optimal funding strategy is to:
  - **Prioritise Group A**
  - **Scale Group B**
  - **Pilot Group C**
  - **Avoid Group D unless partnered with academic interventions**
""")

# =================================================
# EXPORT DATA
# =================================================
st.subheader("⬇️ Export Investment-Ready Dataset")

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Full Investment Dataset",
    csv,
    "bursary_investment_analysis_2025.csv",
    "text/csv"
)

# =================================================
# FOOTER
# =================================================
st.markdown("---")
st.caption(
    "This dashboard supports evidence-based bursary allocation by balancing academic success, "
    "equity, and risk. Designed for funding committees and CSR investment boards."
)

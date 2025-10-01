import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Wind Energy Feasibility Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- BACKGROUND STYLE -----------------
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1470&q=80") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        filter: brightness(0.7) !important;
        color: white !important;
    }
    .main-title {
        font-size:40px !important;
        color:#EAF6F6 !important;
        text-align:center;
        font-weight:bold;
        text-shadow: 2px 2px 4px #000000;
    }
    .subtitle {
        font-size:20px !important;
        color:#A2D5C6 !important;
        text-align:center;
        margin-bottom: 10px;
        text-shadow: 1px 1px 3px #000000;
    }
    .css-1d391kg {
        color: #A2D5C6 !important;
        font-weight: 600;
    }
    </style>
    """ ,
    unsafe_allow_html=True
)

# ----------------- HEADER -----------------
st.markdown('<p class="main-title">🌬️ Wind Energy Feasibility Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyze wind speed, cost, and ROI for smarter energy decisions ⚡</p>', unsafe_allow_html=True)
st.markdown("---")

# ----------------- SIDEBAR -----------------
st.sidebar.header("📂 Upload Dataset (CSV)")
uploaded_file = st.sidebar.file_uploader("Upload a CSV with columns: Location, WindSpeed, TurbineCapacity, LandArea, Cost", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.header("Or Enter Parameters Manually")

avg_wind_speed = st.sidebar.slider("Average Wind Speed (m/s)", 2.0, 15.0, 7.0)
turbine_capacity = st.sidebar.number_input("Turbine Capacity (MW)", 0.1, 10.0, 2.5)
installation_cost = st.sidebar.number_input("Installation Cost (₹ Crores)", 1.0, 100.0, 20.0)
land_area = st.sidebar.number_input("Land Area (sq. km)", 0.1, 10.0, 2.0)

# ----------------- FUNCTION FOR CALCULATIONS -----------------
def calculate_feasibility(wind_speed, turbine_cap, cost, land):
    capacity_factor = min(wind_speed / 12, 1)
    annual_energy_output = turbine_cap * capacity_factor * 8760  # MWh
    revenue = annual_energy_output * 5 * 1000  # Rs. 5 per kWh
    roi = (revenue - cost * 1e7) / (cost * 1e7) * 100
    return annual_energy_output, revenue, roi

def feasibility_label(roi):
    if roi > 20:
        return "🌟 Highly Feasible"
    elif roi > 0:
        return "✅ Feasible"
    else:
        return "⚠️ Not Feasible"

# ----------------- MAIN CONTENT -----------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Results Overview")

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            required_cols = {"Location", "WindSpeed", "TurbineCapacity", "Cost", "LandArea"}
            if not required_cols.issubset(df.columns):
                st.error("❌ Uploaded CSV is missing required columns: Location, WindSpeed, TurbineCapacity, Cost, LandArea")
            else:
                results = []
                for _, row in df.iterrows():
                    energy, revenue, roi = calculate_feasibility(row["WindSpeed"], row["TurbineCapacity"], row["Cost"], row["LandArea"])
                    feasibility = feasibility_label(roi)
                    results.append([
                        row["Location"],
                        row["WindSpeed"],
                        row["TurbineCapacity"],
                        energy,
                        revenue,
                        roi,
                        feasibility
                    ])

                results_df = pd.DataFrame(results, columns=[
                    "Location", "Wind Speed (m/s)", "Capacity (MW)",
                    "Energy Output (MWh)", "Revenue (₹)", "ROI (%)", "Feasibility"
                ])

                st.dataframe(results_df, use_container_width=True)

                @st.cache_data
                def convert_df(df):
                    return df.to_csv(index=False).encode("utf-8")

                csv = convert_df(results_df)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name='wind_feasibility_results.csv',
                    mime='text/csv'
                )

                fig = px.bar(
                    results_df,
                    x="Location",
                    y="ROI (%)",
                    color="ROI (%)",
                    title="ROI by Location",
                    color_continuous_scale="Blues",
                    hover_data=["Energy Output (MWh)", "Revenue (₹)", "Feasibility"]
                )
                fig.update_layout(xaxis_title="Location", yaxis_title="ROI (%)")
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")

    else:
        energy, revenue, roi = calculate_feasibility(avg_wind_speed, turbine_capacity, installation_cost, land_area)
        feasibility = feasibility_label(roi)

        st.metric("Annual Energy Output (MWh)", f"{energy:,.2f}")
        st.metric("Estimated Revenue (₹ Crores)", f"{revenue / 1e7:,.2f}")
        st.metric("ROI (%)", f"{roi:.2f}")
        st.markdown(f"### Feasibility: {feasibility}")

        data = pd.DataFrame({
            "Parameter": ["Wind Speed (m/s)", "Turbine Capacity (MW)", "Land Area (sq. km)"],
            "Value": [avg_wind_speed, turbine_capacity, land_area]
        })
        fig = px.bar(data, x="Parameter", y="Value", title="Input Parameters Overview", color="Parameter")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("✅ Feasibility Decision")

    if uploaded_file:
        st.info("Check the ROI and Feasibility columns in the table to see which locations are feasible 🌱")
    else:
        if roi > 20:
            st.success("🌟 Highly feasible for wind energy installation!")
        elif roi > 0:
            st.info("✅ Feasible with moderate ROI")
        else:
            st.warning("⚠️ Not economically feasible for wind energy")

st.markdown("---")
st.markdown("📌 *Developed as part of Wind Energy Feasibility Project – CSE (AI & ML)*")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Clean Currents Presentation", page_icon="static/INL.png", layout="wide", initial_sidebar_state="auto", menu_items=None)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

@st.cache_data
def read_annual_battery_degredation(folder, file):
    df = pd.read_csv(f"{folder}/{file}")
    df.rename(columns={"LOSS (%)": "Loss (%)",
                       "E": "Energy (MWh)",
                       "Cap": "Capacity (MW)"}, inplace=True)
    return df

@st.cache_data
def read_annual_financial_performance(folder, file):
    df = pd.read_csv(f"{folder}/{file}")
    df.rename(columns={"E": "Energy (MWh)",
                       "Cap": "Capacity (MW)",
                       "Total_Rev_Predicted": "Total Revenue",
                       "Net_rev_ES": "Net Revenue ES",
                       "5-yr ROI%": "5-yr ROI (%)",
                       "Pay back period": "Payback Period (yr)"}, inplace=True)
    return df


def read_daily_financial_performance(folder, file):
    df = pd.read_csv(f"{folder}/{file}")
    df.drop(["Unnamed: 0", "Day.1"], axis=1, inplace=True)
    df.rename(columns={"Day": "Date",
                       "Revenue: Storage Energy to Grid ($)_max": "Storage to Grid ($/day)",
                       "Revenue: Storage RegUp ($)_max": "Storage RegUp ($/day)",
                       "Revenue: Storage RegDn ($)_max": "Storage RegDn ($/day)",
                       "Revenue: Storage Spin ($)_max": "Storage Spin ($/day)",
    }, inplace=True)

    # Fix the incorrect data
    df["Price: Energy ($/MWh)"] = df["Price: Energy ($/MWh)"] / (24 * 12)
    df["Price: RegUp ($/MWh)"] = df["Price: RegUp ($/MWh)"] / (24 * 12)
    df["Price: RegDn ($/MWh)"] = df["Price: RegDn ($/MWh)"] / (24 * 12)
    df["Price: Spin ($/MWh)"] = df["Price: Spin ($/MWh)"] / (24 * 12)
    df["Price: NonSpin ($/MWh)"] = df["Price: NonSpin ($/MWh)"] / (24 * 12)

    df["Storage to Grid ($/day)"] = df["Storage to Grid ($/day)"] / (24)
    df["Storage RegUp ($/day)"] = df["Storage RegUp ($/day)"] / (24)
    df["Storage RegDn ($/day)"] = df["Storage RegDn ($/day)"] / (24)
    df["Storage Spin ($/day)"] = df["Storage Spin ($/day)"] / (24)

    return df

@st.cache_data
def read_daily_battery_degredation(folder, file):
    df = pd.read_csv(f"{folder}/{file}")
    df.rename(columns={'Storage RegUp (MWh)': "Storage Regulation Up (MWh)",
                       'Storage RegDn (MWh)': "Storage Regulation Down (MWh)",
                       'LOSS (%)': "Loss (%)",
                       'Day': "Date"}, inplace=True)
    df.drop("Unnamed: 0", axis=1, inplace=True)

    #
    df["Storage Discharge Energy to Grid (MWh)"] = df["Storage Discharge Energy to Grid (MWh)"] / (24 * 12)
    df["Storage Regulation Up (MWh)"] = df["Storage Regulation Up (MWh)"] / (24 * 12)
    df["Storage Regulation Down (MWh)"] = df["Storage Regulation Down (MWh)"] / (24 * 12)
    df["Storage Spin (MWh)"] = df["Storage Spin (MWh)"] / (24 * 12)

    df.rename(columns={"Storage Discharge Energy to Grid (MWh)": "Storage Discharge Energy to Grid (MWh/day)",
                       "Storage Regulation Up (MWh)": "Storage Regulation Up (MWh/day)",
                       "Storage Regulation Down (MWh)": "Storage Regulation Down (MWh/day)",
                       "Storage Spin (MWh)": "Storage Spin (MWh/day)"}, inplace=True)

    return df

files_long = os.listdir("csv")
files = []
for f in files_long:
    if f.endswith(".csv"):
        f = f.split("_")[-1].split(".")[0]
        if f not in files:
            files.append(f)

files.remove("Clean Currents Presentation")
files.insert(0, "Clean Currents Presentation")


plant_name = st.sidebar.selectbox("Select Case", ["Clean Currents Presentation",])

#######################################
# Annual Financial Performance
#######################################

col1, col2 = st.columns([1, 2])
col1.markdown("### Annual Financial Performance")
col1.markdown("""
This 3D plot shows total hydropower and energy storage revenue (blue dots) as a function of battery power (MW) and 
Energy (MWh). The green surface indicates the estimated revenue from the hydropower plant only (i.e., without a 
battery and assumed to only participate in the energy market)""")

# Read in the data
AFP_df = read_annual_financial_performance(folder="csv", file=f"PredictedAnnualFinancialPerformance_{plant_name}.csv")


fig = px.scatter_3d(AFP_df, x="Energy (MWh)", y="Capacity (MW)", z="Total Revenue")

hydro_only = AFP_df["Revenue: Hydro Only"].values[0]
#fig.add_trace(go.Surface(x=[AFP_df["Energy (MWh)"].min(), AFP_df["Energy (MWh)"].max()],
#                         y=[AFP_df["Capacity (MW)"].min(), AFP_df["Capacity (MW)"].max()],
#                         z=[[hydro_only, hydro_only], [hydro_only, hydro_only]], opacity=0.5, showscale=False))
fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
col2.plotly_chart(fig, use_container_width=True)

# ----------------------------------
# 5-yr ROI
st.markdown("<hr>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])

col1.markdown("### 5-year ROI")
col1.markdown("This 3D plot shows return on investment (ROI) (red dots) associated with adding a new battery to an "
              "existing hydropower plant (i.e., it is the ROI on the battery component). The horizontal axis "
              "indicates the battery size search space. The ROI is calculated based on the estimated increase in "
              "revenue possible from adding the battery system relative to the corresponding estimated battery "
              "capital and operational costs. The green text displays the battery system with the highest estimated "
              "return on investment out of the sizes assessed.")

col1.markdown(f"Max 5-yr ROI: {AFP_df['5-yr ROI (%)'].max():.2f} %")

fig = px.scatter_3d(AFP_df, x="Energy (MWh)", y="Capacity (MW)", z="5-yr ROI (%)")
fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
col2.plotly_chart(fig, use_container_width=True)

# ----------------------------------
# Payback Period
st.markdown("<hr>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])

col1.markdown("### Payback Period")
col1.markdown("This 3D plot shows payback period (red dots) associated with adding a new battery to an existing "
              "hydropower plant (i.e., it is the payback period on the battery component. The horizontal axis "
              "indicates the battery size search space. The payback period is calculated as the number of years "
              "required for the additional revenue to equal the total costs (both capital and operating). The "
              "green text displays the battery system with the lowest estimated payback period out of the "
              "sizes assessed.")



AFP_df_payback = AFP_df[(AFP_df["Payback Period (yr)"] > 0) & (AFP_df["Payback Period (yr)"] < 50)]
min_payback_period = AFP_df_payback['Payback Period (yr)'].min()
min_payback_row = AFP_df_payback[AFP_df_payback["Payback Period (yr)"] == min_payback_period]

col1.markdown(f"Shortest payback period: {min_payback_period:.2f} years at "
              f"{min_payback_row['Capacity (MW)'].values[0]:.1f} (MW) "
              f"and {min_payback_row['Energy (MWh)'].values[0]:.1f} (MWh)")

fig = px.scatter_3d(AFP_df_payback,
                    x="Energy (MWh)",
                    y="Capacity (MW)",
                    z="Payback Period (yr)")
fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
col2.plotly_chart(fig, use_container_width=True)




####################################################
# Daily Battery Degradation
####################################################
st.markdown("<hr>", unsafe_allow_html=True)
DBD_df = read_daily_battery_degredation(folder="csv", file=f"PredictedDailyBatteryDegredation_{plant_name}.csv")

capacity = st.sidebar.selectbox("Select Capacity (MW)", AFP_df["Capacity (MW)"].unique())
energy = st.sidebar.selectbox("Select Energy (MWh)", AFP_df[AFP_df["Capacity (MW)"] == capacity]["Energy (MWh)"].unique())

st.markdown(f"### Daily Battery Output")

# Need to find the group of these values
group = AFP_df[(AFP_df["Capacity (MW)"] == capacity) & (AFP_df["Energy (MWh)"] == energy)]["group"].values[0]

DBD_df = DBD_df[DBD_df["group"] == group]
DBD_df["Date"] = pd.to_datetime(DBD_df["Date"])
DBD_df.set_index("Date", inplace=True)
DBD_df.sort_index(inplace=True)

fig = px.line(DBD_df.drop("group", axis=1))
fig.update_layout(legend=dict(title='',yanchor="top", y=0.99, xanchor="left", x=0.0, bgcolor='rgba(0,0,0,0.05)'))
st.plotly_chart(fig, use_container_width=True)


########################################################
# Daily Revenue Data
########################################################
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### Daily Battery Storage Revenue")
DFP_df = read_daily_financial_performance("csv", f"PredictedDailyRevenueData_{plant_name}.csv")

DFP_df = DFP_df[DFP_df["group"] == group]
DFP_df["Date"] = pd.to_datetime(DFP_df["Date"])
DFP_df.set_index("Date", inplace=True)
DFP_df.sort_index(inplace=True)


fig = px.line(DFP_df[["Storage to Grid ($/day)",
                      "Storage RegUp ($/day)",
                      "Storage RegDn ($/day)",
                      "Storage Spin ($/day)"]])
fig.update_layout(legend=dict(title='',yanchor="top", y=0.99, xanchor="left", x=0.0, bgcolor='rgba(0,0,0,0.05)'))
st.plotly_chart(fig, use_container_width=True)




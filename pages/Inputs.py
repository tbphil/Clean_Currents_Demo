import streamlit as st
import pandas as pd
import plotly.express as px

import plotly.figure_factory as ff

st.set_page_config(page_title="Clean Currents Presentation", page_icon="static/INL.png", layout="wide", initial_sidebar_state="auto", menu_items=None)

@st.cache_data
def load_inpute_data(folder="profile_samples", hydro="EnergyGenerationProfile.csv", price="PriceProfile.csv", frequency="60T"):
    df_gen = pd.read_csv(f"{folder}/{hydro}")
    df_gen["Datetime"] = pd.to_datetime(df_gen["Datetime"])
    df_gen.set_index("Datetime", inplace=True)

    df_price = pd.read_csv(f"{folder}/{price}")
    df_price["Datetime"] = pd.to_datetime(df_price["Datetime"])
    df_price.set_index("Datetime", inplace=True)

    df = pd.concat([df_gen, df_price], axis=1)
    df = df.resample(frequency).mean()

    return df


frequency = st.sidebar.selectbox("Select Frequency", ['5min', '15min', '30min', "1hr", "12hr", "1dy"], 3)

if frequency == "1hr":
    frequency = "60min"
elif frequency == "12hr":
    frequency = "720min"
elif frequency == "1dy":
    frequency = "1440min"

df = load_inpute_data(frequency=frequency)

st.markdown("### Input Data")
fig = px.line(df)
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### Input Data Statistics")

#df.reset_index(inplace=True)
fig = ff.create_table(df.describe().round(decimals=2), index=True)

st.plotly_chart(fig, use_container_width=True)
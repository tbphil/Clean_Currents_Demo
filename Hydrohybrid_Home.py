import streamlit as st
from PIL import Image

st.set_page_config(page_title="Clean Currents Presentation", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)


hydrohybrid_image = Image.open('static/hydrohybrid_image.png')
partners_image = Image.open('static/partners_image.png')

col1, col2 = st.columns([1, 2])

col1.markdown("### Hydro + Storage Sizing Tool")
col1.markdown("The Hydro + Storage Sizing Tool is designed to help hydropower asset owners who participate in competitive electricity markets do a preliminary assessment of the value of integrating batteries with their facility. The basic requirements for using the tool are hydropower generation, electricity prices, and financial performance metrics of interest. The tool is based upon research conducted by Idaho National Laboratory and Argonne National Laboratory. It is a research product and may not be accurate for every set of conditions provided. Users should not interpret the output as financial advice. The output is meant to guide asset owners and developers down the initial steps of considering hydropower hybridization.")

col2.image(hydrohybrid_image, caption='Hydro + Storage')
col1.image(partners_image, caption=None)


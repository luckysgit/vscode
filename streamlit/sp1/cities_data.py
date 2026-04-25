import streamlit as st
import pandas as pd

st.title("Cities Data")

# Upload CSV file
file = st.file_uploader("Upload your CSV file", type=["csv"])

# If a file is uploaded
if file is not None:
    df = pd.read_csv(file)
    st.subheader("Data Preview")
    st.dataframe(df)

if file: 
    st.subheader("summary Stats")
    st.write(df.describe())

if file:
    cities = df["Outlet Location"].unique()
    selected_city = st.selectbox("filter by cities", cities)
    filter_data = df[df["Outlet Location"] ==selected_city]
    st.dataframe(filter_data)

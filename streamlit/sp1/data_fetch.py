import streamlit as st
import requests

st.title("💱 Live Currency Converter")

# User inputs
amount = st.number_input("Enter the amount in INR", min_value=1.0)
target_currency = st.selectbox("Convert to:", ["USD", "EUR", "GBP", "JPY"])

if st.button("Convert"):
    url = "https://api.exchangerate-api.com/v4/latest/INR"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rate = data["rates"].get(target_currency)  # safely get the conversion rate

        if rate:
            converted = rate * amount
            st.success(f"{amount} INR = {converted:.2f} {target_currency}")
        else:
            st.error("Currency not found in response.")
    else:
        st.error("Failed to fetch exchange rates. Please try again later.")

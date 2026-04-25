import streamlit as st

st.title("coffe tracking")
st.subheader("Brewed with streamlit")
st.write("choose your coffe")

coffee = st.selectbox("your fav coffee:", ["Masala coffee", "Lemon coffee", "Adrak Coffee",  "Kesar coffee"])

st.selectbox("sweetness:", ["sugar", "honey", "jaggre"])

st.write(f"your choose {coffee}. Excellent choose")
st.success("your coffee has been brewed")
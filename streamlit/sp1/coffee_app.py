import streamlit as st

st.title("Coffee")

# Buy button
if st.button("Buy"):
    st.success("Added to cart")

# Checkbox for 
italian = st.checkbox("Italian coffee beans")
brazil = st.checkbox("Brazil coffee beans")

if italian:
    st.write("Preference: italian")
if brazil:
    st.write("Preference: brazil")

# Radio for coffee base
coffee_type = st.radio("Pick your coffee base:", ["Milk", "Water"])
st.write(f"Selected base: {coffee_type}")

flavor = st.selectbox("choose flavour:", ["espresso", "capiceno", "late"])
st.write(f"Selected base: {flavor}")

sugar = st.slider("sugar spoon", 0, 5, 1)
st.write(f"selected spoon: {sugar}")

cups = st.number_input("how many coffee cups", min_value = 1, max_value = 50, step = 1 )
st.write(f"total cups: {cups}")

name = st.text_input("Enter your name")
if name:
    st.write(f"Welcome, {name}!")

dob = st.date_input("Select your date of birth")
st.write(f"Your date of birth: {dob}")

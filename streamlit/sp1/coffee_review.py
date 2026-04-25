import streamlit as st

st.title("Coffee Taste Poll")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.header("Italian Coffee")
    st.image("https://www.pexels.com/photo/coffee-beans-and-a-cup-of-coffee-on-a-table-17516412/", width=200)
    vote1 = st.button("Vote Italian Coffee")
    

with col2:
    st.header("Brazil Coffee")
    st.image("https://www.pexels.com/photo/hands-holding-pitcher-and-pouring-beverage-from-pitcher-to-cup-21555027/", width=200)
    vote2 = st.button("Vote Brazil Coffee")

if vote1:
    st.success("You voted for Italian Coffee!")    
elif vote2:
    st.success("You voted for Brazil Coffee!")

#sidebar

name = st.sidebar.text_input("enter your name")
coffee= st.sidebar.selectbox("choosee you ", ["italian", "Arabic"])

st.write(F"welcome {name}! ")

with st.sidebar.expander("show coffee making instruction"):
    st.write("""
             1. boil water 80c
            2. two spoon suger
             3. normal milk

""")
    
st.markdown("### welcome to coffee")
st.markdown("> BLockquote")
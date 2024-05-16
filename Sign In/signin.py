import streamlit as st

usernameshow = False
st.button("Sign In", type="primary")
if st.button("Sign Up"):
    usernameshow = True
    # Run a code to go to sign up screen
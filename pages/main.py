import streamlit as st
import requests

st.set_page_config(page_title="Main")

st.title("Main Page")

st.sidebar.write("This is the main page")


def check_logged_in():
    print("check_logged_in start")
    response = requests.get("http://localhost:8000/api/v1/users/auth")
    print(" is user logged in?")
    print(response.status_code)
    if response.status_code == 401:
        st.error("User is NOT logged in")
    else:
        st.success("User is logged in")


st.button("Check logged in", on_click=check_logged_in)

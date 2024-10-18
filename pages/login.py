import streamlit as st
import requests


# page config
st.set_page_config(page_title="Log in", initial_sidebar_state="collapsed")
username = st.session_state["user"].get("username")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("Login Page")


def login_submit():
    if not username or not password:
        st.error("Username and password must be filled")
        return False

    form = {
        "username": username,
        "password": password,
    }

    print("login_btn!")
    print(form)

    # api call
    try:
        response = requests.post("http://localhost:8000/api/v1/users/login", json=form)
        data = response.json()
    except:
        st.error("Internal Server Error")
        return False

    print("--- response check ---")
    print(response.status_code)
    print(data)

    # success
    if response.status_code == 200:
        st.session_state["user"] = {
            "username": username,
        }
        st.success("Login Success")
        return True
    # bad request
    elif response.status_code == 400:
        st.error(data["error"])
        return False
    else:
        st.error("Login Failed")
        return False


def reset_user():
    st.session_state["user"] = {}
    st.success("Reset Success")


## Page Contents

user = st.session_state.get("user")
if user and user.get("username"):
    st.write(f"Welcome {user['username']}")
else:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button(label="Login", key="login", on_click=login_submit)
    register_btn = st.button(label="Register", key="register")


reset_btn = st.button(label="Reset", key="reset", on_click=reset_user)

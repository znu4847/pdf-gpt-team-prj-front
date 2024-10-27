import streamlit as st
from utils import rest


# st.set_page_config(page_title="Log in", initial_sidebar_state="collapsed")
st.set_page_config(page_title="Log in")
username = st.session_state["user"].get("username")

st.title("로그인")


def login_submit():
    if not username or not password:
        st.error("Username과 Password를 입력해주세요")
        return False

    form = {
        "username": username,
        "password": password,
    }

    # api call
    try:
        response = rest.post("users/login", form)
        data = response.json()

        # success
        if response.status_code == 200:
            st.session_state["user"] = {
                "username": data["username"],
                "user_id": data["pk"],
            }
            rest.set_jwt(data["jwt"])
            st.success("Login Success")
            response = rest.get(f"users/llm-key/{st.session_state['user']['user_id']}")
            st.session_state["llm_config"] = response.json()
            st.rerun()
            return True
        # bad request or unauthorized
        elif response.status_code == 400 or response.status_code == 401:
            st.error(data["error"])
            return False
        else:
            st.error("Login Failed")
            return False
    except Exception:
        st.error("Internal Server Error")
        return False


def reset_user():
    st.session_state["user"] = {}
    st.success("Reset Success")


## Page Contents
user = st.session_state.get("user")
if user and user.get("username"):
    st.write(f"Welcome {user['username']}")
else:
    with st.form("login_form", enter_to_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("로그인")

    if login_btn:
        login_submit()

import streamlit as st
from utils import rest


# commit test
st.set_page_config(page_title="Log in", initial_sidebar_state="collapsed")
username = st.session_state["user"].get("username")

# collapse sidebar
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

    # api call
    try:
        response = rest.post("users/login", form)
        data = response.json()
        rest.set_jwt(data["jwt"])
    except Exception:
        st.error("Internal Server Error")
        return False

    # success
    if response.status_code == 200:
        st.session_state["user"] = {
            "username": data["username"],
            "user_id": data["pk"],
        }
        st.success("Login Success")
        response = rest.get(f"users/llm-key/{st.session_state['user']['user_id']}")
        st.session_state["llm_config"] = response.json()
        st.rerun()
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
    with st.form("login_form", enter_to_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        login_submit()

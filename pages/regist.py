import streamlit as st
from utils import rest

st.set_page_config(page_title="Register")

st.title("새로 등록하기")


def regist_submit():
    if not username or not password1 or not password2:
        st.error("Username과 Password는 필수입니다")
        return False

    if password1 != password2:
        st.error("입력된 Password가 일치하지 않습니다")
        return False
    form = {
        "username": username,
        "password1": password1,
        "password2": password2,
    }

    response = rest.post("users/", form)
    try:
        data = response.json()
    except Exception:
        st.error("Internal Server Error")
        return False

    # created
    if response.status_code == 201:
        st.session_state["user"] = {
            "username": data["username"],
        }
        st.success("Register Success")
        return True
    # conflict
    elif response.status_code == 409:
        st.error("이미 등록된 유저입니다")
        return False
    # bad request
    elif response.status_code == 400:
        errors = data["errors"]
        # error_message = ""
        for error in errors:
            # error_message += f"{error}\r\n"
            st.error(error)
        return False
    # else
    else:
        st.error("Register Failed")
        return False


user = st.session_state.get("user")
if user and user.get("username"):
    st.write(f"Welcome {user['username']}")
else:
    username = st.text_input("Username")
    password1 = st.text_input("Password", type="password")
    password2 = st.text_input("Password(confirm)", type="password")
    regist_btn = st.button(label="등록", key="regist", on_click=regist_submit)


def reset_user():
    st.session_state["user"] = {}
    st.success("Reset Success")

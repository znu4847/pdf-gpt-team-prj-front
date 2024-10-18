import streamlit as st
import requests

st.set_page_config(page_title="Register")

st.title("Register Page")


def regist_submit():
    if not username or not password1 or not password2:
        st.error("Username and password must be filled")
        return False

    if password1 != password2:
        st.error("Password and confirm password must be the same")
        return False
    form = {
        "username": username,
        "password1": password1,
        "password2": password2,
    }

    print("regist_btn!")
    print(form)

    response = requests.post("http://localhost:8000/api/v1/users/", json=form)
    print("response check222")
    print(response.status_code)
    try:
        data = response.json()
        print(data)
    except:
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
        st.error("Username already exists")
        return False
    # bad request
    elif response.status_code == 400:
        st.error(data["error"])
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
    regist_btn = st.button(label="Regist", key="regist", on_click=regist_submit)


def reset_user():
    st.session_state["user"] = {}
    st.success("Reset Success")


reset_btn = st.button(label="Reset", key="reset", on_click=reset_user)

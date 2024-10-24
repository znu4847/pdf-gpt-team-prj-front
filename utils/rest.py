import os
import streamlit as st
import requests


# set the port number. if os.environ.get("PORT") is None, then set the port number to 9000
PORT_NUM = os.environ.get("PORT_NUM") if os.environ.get("PORT_NUM") else 9000
# print(f"PORT_NUM: {os.environ.get("PORT_NUM")}")
print(f"PORT_NUM: {PORT_NUM}")


def set_jwt(jwt):
    st.session_state["jwt"] = jwt


def get_jwt_header():
    jwt = st.session_state.get("jwt")
    if jwt:
        return {"jwt": jwt}
    return {}


def reset_jwt():
    st.session_state["jwt"] = None


def get(end_point):
    response = requests.get(
        f"http://localhost:{PORT_NUM}/api/v1/{end_point}", headers=get_jwt_header()
    )
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        if "jwt" in data:
            set_jwt(data["jwt"])

    return response


def post(end_point, form):
    # post api call with header
    response = requests.post(
        f"http://localhost:{PORT_NUM}/api/v1/{end_point}",
        json=form,
        headers=get_jwt_header(),
    )
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        if "jwt" in data:
            set_jwt(data["jwt"])

    return response


def put(end_point, form):
    # post api call with header
    response = requests.put(
        f"http://localhost:{PORT_NUM}/api/v1/{end_point}",
        json=form,
        headers=get_jwt_header(),
    )
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        if "jwt" in data:
            set_jwt(data["jwt"])

    return response

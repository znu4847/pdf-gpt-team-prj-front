import os
import streamlit as st
import requests


API_URL = (
    os.environ.get("API_URL") if os.environ.get("API_URL") else "http://localhost:8000"
)


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
    response = requests.get(f"{API_URL}/api/v1/{end_point}", headers=get_jwt_header())
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        if "jwt" in data:
            set_jwt(data["jwt"])

    return response


def post(end_point, form):
    # post api call with header
    response = requests.post(
        f"{API_URL}/api/v1/{end_point}",
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
        f"{API_URL}/api/v1/{end_point}",
        json=form,
        headers=get_jwt_header(),
    )
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        if "jwt" in data:
            set_jwt(data["jwt"])

    return response


def delete(end_point):
    response = requests.delete(
        f"{API_URL}/api/v1/{end_point}", headers=get_jwt_header()
    )
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        if "jwt" in data:
            set_jwt(data["jwt"])

    return response

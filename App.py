import os
import streamlit as st
from utils import rest
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

document_page = st.Page(
    "pages/01_DocumentGPT.py",
    title="Document",
)

if "user" not in st.session_state:
    st.session_state["user"] = {}

print("is logged in?")
print(st.session_state["user"])


def logout():
    print("--- logout ---")
    st.session_state["user"] = {}
    rest.reset_jwt()
    st.rerun()


main_page = st.Page(
    "pages/01_DocumentGPT.py",
    title="Main Page",
    default=True,
)
regist_page = st.Page(
    "pages/regist.py",
    title="Register Page",
)

login_page = st.Page(
    "pages/login.py",
    title="Login Page",
)

logout_page = st.Page(
    logout,
    title="Log out",
    icon=":material/logout:",
)

account_pages = [logout_page]
noauth_pages = [login_page, regist_page]
chat_pages = [main_page]

dev_mode = os.environ.get("DEV_MODE") == "True"
print(f"dev_mode: {dev_mode}")
if not dev_mode and (
    not st.session_state.get("user") or not st.session_state["user"].get("username")
):
    pg = st.navigation(noauth_pages)
else:
    pg = st.navigation(
        {"Account": account_pages, "Main": chat_pages},
    )
pg.run()

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


def logout():
    st.session_state["user"] = {}
    st.session_state["llm_config"] = {}
    rest.reset_jwt()
    st.rerun()


main_page = st.Page(
    "pages/01_DocumentGPT.py",
    title="대화하기",
    default=True,
)
regist_page = st.Page(
    "pages/regist.py",
    title="새로 등록하기",
)

login_page = st.Page(
    "pages/login.py",
    title="로그인",
)

logout_page = st.Page(
    logout,
    title="로그아웃",
    icon=":material/logout:",
)

config_page = st.Page(
    "pages/config.py",
    title="API 설정",
)

account_pages = [logout_page, config_page]
noauth_pages = [login_page, regist_page]
chat_pages = [main_page]

dev_mode = os.environ.get("DEV_MODE") == "True"
if "llm_config" not in st.session_state:
    llm_config = {
        "llm_type": "openai",
        "openai_key": "",
        "claude_key": "",
    }


if dev_mode:
    # set test user info
    rest.set_jwt(os.getenv("TEST_USER_TOKEN"))  # JWT 설정
    st.session_state["user"] = {
        "username": os.getenv("TEST_USER_USERNAME"),
        "user_id": os.getenv("TEST_USER_PK"),
    }
    response = rest.get(f"users/llm-key/{st.session_state['user']['user_id']}")
    st.session_state["llm_config"] = response.json()


if not dev_mode and (
    not st.session_state.get("user") or not st.session_state["user"].get("username")
):
    pg = st.navigation(noauth_pages)
else:
    pg = st.navigation(
        {"유저 설정": account_pages, "채팅방": chat_pages},
    )
pg.run()

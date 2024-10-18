import streamlit as st

if not st.session_state.get("user"):
    st.session_state["user"] = {}


def logout():
    st.session_state["user"] = {}
    st.rerun()


main_page = st.Page(
    "pages/main.py",
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

settings_page = st.Page(
    "pages/settings.py",
    title="Settings",
    icon=":material/settings:",
)


account_pages = [logout_page, settings_page]
noauth_pages = [login_page, regist_page]
chat_pages = [main_page]

if not st.session_state.get("user") or not st.session_state["user"].get("username"):
    pg = st.navigation(noauth_pages)
else:
    pg = st.navigation(
        {"Account": account_pages, "Main": chat_pages},
    )

pg.run()

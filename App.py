import streamlit as st

document_page = st.Page(
    "pages/01_DocumentGPT.py",
    title="Document",
)


chat_pages = [document_page]
pg = st.navigation({"Chat": chat_pages})

pg.run()
import streamlit as st

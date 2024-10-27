import streamlit as st
from utils import rest

st.title("API 사용량")

response_conversations = rest.get("conversations/")
conversations = response_conversations.json()["data"]
st.markdown(f"## 대화 수(파일 수): {len(conversations)}")
# st.write(f"대화 수: {len(conversations)}")
st.markdown("## 대화별 메시지 수")
total_message = 0
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    st.markdown("### 제목")
with col2:
    st.markdown("### 메시지")
with col3:
    st.markdown("### 토큰")
with col4:
    st.markdown("### 비용")
for index, conversation in enumerate(conversations):
    # st.write(f"{index}: {conversation['title']}")
    conversation_id = conversation["pk"]
    response_messages = rest.get(f"messages/?conversation={conversation_id}")
    # st.write(f"메시지 수: {len(response_messages.json())}")
    num_message = len(response_messages.json())
    # st.markdown(f"### {conversation['title']}: {num_message}")
    total_message += num_message
    with col1:
        st.write(conversation["title"])
    with col2:
        st.write(num_message)
    with col3:
        st.write(conversation["tokens"])
    with col4:
        st.write(round(float(conversation["charges"]), 6))
st.markdown(f"## 총 메시지 수: {total_message}")

import streamlit as st
from utils import rest

st.title("Config Page")


class RadioOption:
    def __init__(self, label, value, key):
        self.label = label
        self.value = value
        self.key = key

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.label

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __ne__(self, other):
        return not self.__eq__(other)


llm_config = st.session_state.get("llm_config")
llm_config_type = llm_config.get("llm_type")
llm_config_openai_key = llm_config.get("openai_key")
llm_config_claude_key = llm_config.get("claude_key")

openai_opt = RadioOption("OpenAI", "openai", llm_config_openai_key)
claude_opt = RadioOption("Claude", "claude", llm_config_claude_key)


# if llm_config_type == "openai", index = 0, elif index = 1 if llm_config_type == "claude" else Nonew
index = 0 if llm_config_type == "openai" else 1 if llm_config_type == "claude" else None

selected = st.radio(
    label="AI 모델 선택",
    options=[openai_opt, claude_opt],
    index=index,
)
openai_key = st.text_input(
    "OpenAI API Key",
    value=openai_opt.key,
    max_chars=None,
    key=None,
    type="password",
    disabled=selected.value != "openai",
)
claude_key = st.text_input(
    "Claude API Key",
    value=claude_opt.key,
    max_chars=None,
    key=None,
    type="password",
    disabled=selected.value != "claude",
)

submit = st.button("저장")
if submit:
    form = {
        "llm_type": selected.value,
    }
    if selected.value == "openai":
        if not openai_key:
            st.error("OpenAI API Key를 입력해주세요.")
            st.stop()

        form["openai_key"] = openai_key
    else:
        if not claude_key:
            st.error("Claude API Key를 입력해주세요.")
            st.stop()

        form["claude_key"] = claude_key

    user_id = st.session_state["user"]["user_id"]
    response = rest.put(
        f"users/llm-key/{user_id}",
        form,
    )
    if response.status_code == 200:
        st.session_state["llm_config"] = response.json()
        st.success("저장되었습니다.")
    else:
        st.error(response.json()["error"])

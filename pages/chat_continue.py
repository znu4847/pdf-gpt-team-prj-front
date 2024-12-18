import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic

from langchain.callbacks.base import BaseCallbackHandler
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.storage import LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
import streamlit as st
from utils import rest
import tiktoken

MODEL_COST_PER_1K_TOKENS = {
    "gpt-4o-input": 0.0025,
    "gpt-4o-output": 0.01,
    "claude-3.5-sonnet-input": 0.003,
    "claude-3.5-sonnet-output": 0.015,
}

# 대화 ID 초기화
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = None

# 대화 변경 체크를 위한 ID 초기화
if "bef_conversation_id" not in st.session_state:
    st.session_state["bef_conversation_id"] = None

# 메시지 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []


def load_conversations():
    response = rest.get("conversations/")
    st.session_state["conversations"] = response.json()["data"]


if "conversations" not in st.session_state:
    load_conversations()


def get_memory():
    if "chat_memory" not in st.session_state:
        st.session_state["chat_memory"] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
        )
    return st.session_state["chat_memory"]


retriever = None


def initialize_retriever(file_path, embed_path):
    # 불러오기
    loader = PDFPlumberLoader(file_path)
    # 자르기
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    docs = loader.load_and_split(text_splitter=splitter)
    # 임베딩
    embeddings = OpenAIEmbeddings()
    folder_path = os.path.dirname(embed_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # 임베딩 캐시
    cache_dir = LocalFileStore(embed_path)
    cache_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
    vectorstores = FAISS.from_documents(docs, cache_embeddings)
    return vectorstores.as_retriever()


def save_message(text, role):
    conv_pk = st.session_state["conversation_id"]
    st.session_state["messages"].append(
        {
            "conversation": conv_pk,
            "text": text,
            "role": role,
        }
    )
    rest.post(
        "messages/",
        {
            "user": st.session_state["user"]["user_id"],
            "conversation": conv_pk,
            "text": text,
            "role": role,
        },
    )


def send_message(text, role, save=True):
    with st.chat_message(role):
        st.markdown(text)
    if save:
        save_message(text, role)


def paint_history():
    for message in st.session_state["messages"]:
        send_message(message["text"], message["role"], save=False)


def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)


def invoke_chain(chain, message, context):
    formatted_prompt = template.format(
        chat_history=memory_load(), context=context, question=message
    )
    result = chain.invoke(formatted_prompt).content.replace("$", "\$")
    if llm_type == "openai":
        encoder = tiktoken.get_encoding("o200k_base")
        prompt_token = encoder.encode(formatted_prompt)
        # print(
        #     "len - prompt_token ---------------------------------------",
        #     len(prompt_token),
        # )
        completion_token = encoder.encode(result)
        # print(len(completion_token))
        total_token = len(prompt_token) + len(completion_token)
        charge = (
            len(prompt_token) * float(MODEL_COST_PER_1K_TOKENS["gpt-4o-input"])
            + len(completion_token) * float(MODEL_COST_PER_1K_TOKENS["gpt-4o-output"])
        ) * 0.001
        # print("charge ---------------------------------------   $", charge)
    if llm_type == "claude":
        # print("formatted_prompt ------------------------------", formatted_prompt)
        len_prompt_token = llm_model.get_num_tokens(formatted_prompt)
        # print("len_prompt_token ---------------------------------", len_prompt_token)
        # print("result  ------------------------------", result)
        len_completion_token = llm_model.get_num_tokens(result)
        # print("len_result ---------------------------------", len_completion_token)
        total_token = len_prompt_token + len_completion_token
        charge = (
            len_prompt_token
            * float(MODEL_COST_PER_1K_TOKENS["claude-3.5-sonnet-input"])
            + len_completion_token
            * float(MODEL_COST_PER_1K_TOKENS["claude-3.5-sonnet-output"])
        ) * 0.001
        # print("charge ---------------------------------------   $", charge)
    response = rest.put(
        f"conversations/token/{st.session_state['conversation_id']}",
        {
            "tokens": total_token,
            "charges": charge,
        },
    )
    get_memory().save_context({"input": message}, {"output": result})


def memory_load():
    return get_memory().load_memory_variables({})["chat_history"]


class ChatCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.message = ""
        self.num_of_tokens = 0
        super().__init__()

    def on_llm_start(self, *args, **kargs):
        self.num_of_tokens = 0
        self.message_box = st.empty()

    def on_llm_end(self, *args, **kargs):
        save_message(self.message, "ai")

    def on_llm_new_token(self, token, *args, **kargs):
        self.num_of_tokens += 1
        self.message += token
        self.message_box.markdown(self.message)


llm_type = st.session_state["llm_config"]["llm_type"]
llm_model = None

if llm_type == "openai":
    key = st.session_state["llm_config"]["openai_key"]

    # if key not start with "sk-" then
    if not key or not key.startswith("sk-"):
        st.write("OpenAI API Key를 등록해주세요.")
        st.stop()
    llm_model = ChatOpenAI(
        temperature=0.1,
        model="gpt-4o",
        streaming=True,
        callbacks=[ChatCallbackHandler()],
        api_key=key,
    )
elif llm_type == "claude":
    key = st.session_state["llm_config"]["claude_key"]

    if not key or not key.startswith("sk-"):
        st.write("Claude API Key를 등록해주세요.")
        st.stop()
    llm_model = ChatAnthropic(
        temperature=0.1,
        model="claude-3-haiku-20240307",
        streaming=True,
        callbacks=[ChatCallbackHandler()],
        api_key=key,
    )

print(f"llm_model: {llm_model._llm_type}")

template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
너는 지금까지 해왔던 대화와 입력받은 pdf를 바탕으로 답변을 제공해주는 챗봇이야.
지금까지의 대화와 입력받은 내용(Context)을 바탕으로 답을 줘.
지금까지 대화했던 내용을 적고, 답변 내용을 적어줘.
모르는 내용은 모른다고 답변해줘.
지어내지 말아줘. 

Context:{context}

""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

st.title("PDF Chatbot")

select_items = None
selected_item = None
if st.session_state["conversations"] and len(st.session_state["conversations"]) > 0:
    select_items = [conv for conv in st.session_state["conversations"]]


@st.dialog("제목 변경")
def change_title():
    title = st.text_input("변경할 제목을 입력하세요")
    if st.button("제출"):
        # for conversation in st.session_state["conversations"]:
        #     if conversation["pk"] == st.session_state["conversation_id"]:
        #         conversation.[title] = title
        #         break
        response = rest.put(
            f"conversations/{st.session_state['conversation_id']}",
            {
                "title": title,
            },
        )
        load_conversations()
        st.rerun()
        return response


if len(st.session_state["conversations"]) > 0:
    # 241022 sidebar로 select box 이동
    with st.sidebar:
        selected_item = st.selectbox(
            "이전 대화를 계속합니다",
            select_items,
            placeholder="대화를 선택하세요",
            index=None,
            format_func=lambda x: x["title"],
        )
        if selected_item:
            # 대화 제목 변경
            if st.button("제목 변경"):
                response = change_title()

            # 대화 삭제
            del_button = st.button("대화 삭제")
            if del_button:
                response = rest.delete(f"conversations/{selected_item['pk']}")
                load_conversations()
                st.rerun()


def load_messages():
    conversation_id = st.session_state.get("conversation_id")
    if conversation_id is None:
        st.session_state["messages"] = []
        return
    response = rest.get(f"messages/?conversation={st.session_state['conversation_id']}")
    st.session_state["messages"] = response.json()
    paint_history()


def save_memory_history():
    get_memory().clear()
    messages = st.session_state["messages"]
    for i in range(0, len(messages), 2):
        if st.session_state["conversation_id"]:
            human_message = messages[i]
            if i + 1 >= len(messages):
                return

            ai_message = messages[i + 1]
            if human_message["role"] != "human" or ai_message["role"] != "ai":
                print("Error - human, ai 둘 다 아님!!!!")
            question = human_message["text"]
            answer = ai_message["text"]
            get_memory().save_context({"input": question}, {"output": answer})


if selected_item:
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = selected_item["pk"]
    file_path = selected_item["pdf_url"]
    embed_path = selected_item["embed_url"]
    retriever = initialize_retriever(file_path, embed_path)
    load_messages()
    if st.session_state["bef_conversation_id"] != st.session_state["conversation_id"]:
        st.session_state["bef_conversation_id"] = st.session_state["conversation_id"]
        save_memory_history()

if retriever:
    message = st.chat_input("Ask anything about your file...")
    if message:
        send_message(message, "human")
        # context = format_docs(retriever.get_relevant_documents(message))
        context = format_docs(retriever.invoke(message))
        chain = RunnablePassthrough() | llm_model

        with st.chat_message("ai"):
            invoke_chain(chain, message, context)
            # try:
            #     invoke_chain(chain, message, context)
            # except Exception as e:
            #     print(e)
            #     st.write("Error occurred while processing the request.")
            #     st.write("Please try again.")

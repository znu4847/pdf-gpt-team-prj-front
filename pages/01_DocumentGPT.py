import os
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.document_loaders.pdf import PDFPlumberLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.storage import LocalFileStore
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
import streamlit as st
from utils import rest

# 개발 모드일 때 테스트 유저 정보 설정
dev_mode = os.environ.get("DEV_MODE") == "True"
if dev_mode:
    # set test user info
    rest.set_jwt(os.getenv("TEST_USER_TOKEN"))  # JWT 설정
    st.session_state["user"] = {
        "username": os.getenv("TEST_USER_USERNAME"),
        "user_id": os.getenv("TEST_USER_PK"),
    }

# 대화 ID 초기화
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = None
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


@st.cache_resource(show_spinner="Embedding file...")
def embed_file(file):
    # file저장
    file_content = file.read()
    file_path = f"./.cache/files/{file.name}"
    folder_path = os.path.dirname(file_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(file_path, "wb") as f:
        f.write(file_content)
    embed_path = f"./.cache/embeddings/{file.name}"
    # retriever 초기화
    retriever = initialize_retriever(file_path, embed_path)

    user = st.session_state["user"]

    response = rest.post(
        "conversations/",
        {
            "user": user["user_id"],
            "title": file.name,
            "pdf_url": file_path,
            "embed_url": embed_path,
        },
    )
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = response.json()["pk"]
    load_conversations()

    return retriever


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
        if "filename" in message:
            with open(
                f"./.cache/agent/{message['filename']}.txt", "r", encoding="utf-8"
            ) as file:
                st.download_button(
                    label="File download",
                    data=file,
                    file_name=f"{message['filename']}.txt",
                )
        else:
            send_message(message["text"], message["role"], save=False)


def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)


def invoke_chain(chain, message, context):
    result = chain.invoke(
        {
            "chat_history": memory_load(),
            "context": context,
            "question": message,
        }
    ).content.replace("$", "\$")
    get_memory().save_context({"input": message}, {"output": result})


def memory_load():
    return get_memory().load_memory_variables({})["chat_history"]


class ChatCallbackHandler(BaseCallbackHandler):
    message = ""

    def on_llm_start(self, *args, **kargs):
        self.message_box = st.empty()

    def on_llm_end(self, *args, **kargs):
        save_message(self.message, "ai")

    def on_llm_new_token(self, token, *args, **kargs):
        self.message += token
        self.message_box.markdown(self.message)


choose_llm = ChatOpenAI(
    temperature=0.1,
    model="gpt-4o",
)
answer_llm = ChatOpenAI(
    temperature=0.1,
    model="gpt-4o",
    streaming=True,
    callbacks=[ChatCallbackHandler()],
)

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

st.title("DocumentGPT")

file = None

# 입력 api 확인
file = st.file_uploader(
    "PDF 파일을 업로드하여 대화를 시작합니다",
    type=["pdf"],
)

select_items = None
selected_item = None
if st.session_state["conversations"] and len(st.session_state["conversations"]) > 0:
    select_items = [conv for conv in st.session_state["conversations"]]

if select_items:
    selected_item = st.selectbox(
        "이전 대화를 계속합니다",
        select_items,
        index=None,
        format_func=lambda x: x["title"],
    )
if file:
    retriever = embed_file(file)
    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()


def load_messages():
    conversation_id = st.session_state.get("conversation_id")
    if conversation_id is None:
        st.session_state["messages"] = []
        return
    response = rest.get(f"messages/?conversation={st.session_state['conversation_id']}")
    st.session_state["messages"] = response.json()
    paint_history()


if selected_item:
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = selected_item["pk"]
    file_path = selected_item["pdf_url"]
    embed_path = selected_item["embed_url"]
    retriever = initialize_retriever(file_path, embed_path)

    load_messages()

if retriever:
    message = st.chat_input("Ask anything about your file...")
    if message:
        send_message(message, "human")
        context = format_docs(retriever.get_relevant_documents(message))
        chain = template | answer_llm

        with st.chat_message("ai"):
            invoke_chain(chain, message, context)

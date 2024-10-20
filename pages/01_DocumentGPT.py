import os
from dotenv import load_dotenv
from openai import OpenAI
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

client = OpenAI()

load_dotenv()  # .env 파일 로드

if "messages" not in st.session_state:
    st.session_state["messages"] = []


def get_memory():
    if "chat_memory" not in st.session_state:
        st.session_state["chat_memory"] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
        )
    return st.session_state["chat_memory"]


def check_api_key(api_key):
    try:
        client.api_key = api_key
        client.models.list()
        os.environ["OPENAI_API_KEY"] = api_key
        return True
    except Exception:
        st.error("Wrong API Key")
        return False


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
    cache_file_dir = f"./.cache/embeddings/{file.name}"
    folder_path = os.path.dirname(cache_file_dir)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # 임베딩 캐시
    cache_dir = LocalFileStore(cache_file_dir)
    cache_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
    vectorstores = FAISS.from_documents(docs, cache_embeddings)
    retriever = vectorstores.as_retriever()
    return retriever


def save_message(message, role):
    st.session_state["messages"].append({"message": message, "role": role})


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)


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
            send_message(message["message"], message["role"], save=False)


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

with st.sidebar:
    # api 입력
    with st.form("api_key"):
        api_key = st.text_input(label="Enter your OpenAI API key")
        submit = st.form_submit_button("Submit")
    model = "gpt-4o"  # "gpt-4o-mini"

file = None

# 입력 api 확인
if check_api_key(api_key):
    with st.sidebar:
        file = st.file_uploader(
            "Upload a .pdf file",
            type=["pdf"],
        )
    if file:
        choose_llm = ChatOpenAI(
            temperature=0.1,
            model=model,
        )
        answer_llm = ChatOpenAI(
            temperature=0.1,
            model=model,
            streaming=True,
            callbacks=[ChatCallbackHandler()],
        )
        retriever = embed_file(file)
        send_message("I'm ready! Ask away!", "ai", save=False)
        paint_history()
        message = st.chat_input("Ask anything about your file...")

        if message:
            send_message(message, "human")
            context = format_docs(retriever.get_relevant_documents(message))
            chain = template | answer_llm

            with st.chat_message("ai"):
                invoke_chain(chain, message, context)

if not file:
    st.markdown(
        """
    Welcome!
                
    Use this chatbot to ask questions to an AI about your files!
                
    1. Input your OpenAI API key.
                
    2. Upload your pdf on the sidebar.
    """
    )

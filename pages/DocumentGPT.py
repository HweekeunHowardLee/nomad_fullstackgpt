import time
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import CacheBackedEmbeddings, OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.vectorstores.faiss import FAISS
import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

class ChatCallbackHandler(BaseCallbackHandler):
    message = ""

    def on_llm_start(self, *args, **kwargs):
        self.message_box = st.empty()

    def on_llm_end(self, *args, **kwargs):
        save_message(self.message, "ai")

    def on_llm_new_token(self, token, *args, **kwargs):
        self.message += token
        self.message_box.markdown(self.message)

llm = ChatOpenAI(
    temperature=0.1,
    streaming=True,
    callbacks=[
        ChatCallbackHandler(),
    ],
)

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="☘️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# @st.cache_data(show_spinner="Embedding file...")
def embed_file(file):
    # Saves uploaded file to a specific directory
    file_content = file.read()
    file_path = f"./cache/files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Load the file and split it into chunks
    splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=100, separator="\n\n")
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(splitter)

    # Create a vector store from the documents
    cache_dir = LocalFileStore(f"./cache/embeddings/{file.name}")
    embeddings = OpenAIEmbeddings()
    cache_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
    vector_store = FAISS.from_documents(docs, cache_embeddings)
    retriever = vector_store.as_retriever()
    return retriever

def save_message(message, role):
    st.session_state.messages.append({"role": role, "message": message})

def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)    

def paint_history():
    for message in st.session_state.messages:
        send_message(message["message"], message["role"], save=False)

def process_doc(docs):
    return "\n\n".join([doc.page_content for doc in docs])

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Answer question based on only the context provided here. {context}"),
        ("human", "{question}"),
    ],
)

st.title("DocumentGPT ☘️")

st.markdown(
    """
    This is a simple DocumentGPT app that allows you to upload a document and ask questions about it.
    The app uses the `langchain` library to process the document and answer questions.
    """
)

with st.sidebar:    
    file = st.file_uploader(
        "Upload a document",
        type=["pdf", "docx", "txt", "csv"],
        help="Supported formats: PDF, DOCX, TXT, HWP",
    )

if file:
    retriever = embed_file(file)
    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()
    message = st.chat_input("Ask anything about your file...")
    if message:
        send_message(message, "human")
        chain = (
            {
            "context": retriever | RunnableLambda(process_doc),
            "question": RunnablePassthrough(),
            }
            | prompt | llm
        )
        with st.chat_message("ai"):
            response = chain.invoke(message)

else:
    st.session_state.messages = []
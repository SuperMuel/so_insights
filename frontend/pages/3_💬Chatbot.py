from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from pydantic import HttpUrl
from sdk.so_insights_client.models.workspace import Workspace
from langchain.chains import create_history_aware_retriever
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from shared.set_of_unique_articles import SetOfUniqueArticles
from src.app_settings import AppSettings
from src.shared import select_workspace, get_client
import streamlit as st
from langchain.chat_models import init_chat_model
from langchain import hub
from langchain_core.vectorstores.base import VectorStoreRetriever
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_pinecone import PineconeVectorStore
from langchain_voyageai import VoyageAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from dotenv import load_dotenv


@dataclass
class _ArticleDocument:
    id: str
    title: str
    body: str
    date: datetime
    url: HttpUrl

    @classmethod
    def from_document(cls, doc: Document) -> "_ArticleDocument":
        return cls(
            id=doc.id or "",
            title=doc.page_content,
            body=doc.metadata.get("body", ""),
            date=datetime.fromtimestamp(doc.metadata["date"]),
            url=doc.metadata["url"],
        )


load_dotenv()


settings = AppSettings()

embeddings = VoyageAIEmbeddings(  # type:ignore #Arguments missing for parameters "_client", "_aclient"
    voyage_api_key=settings.VOYAGEAI_API_KEY,
    model=settings.EMBEDDING_MODEL,
)


client = get_client()


def _select_workspace() -> Workspace:
    workspaces = select_workspace(client)
    if not workspaces:
        st.warning("Please select a workspace.")
        st.stop()
    return workspaces


def select_ai_model():
    ai_models = ["gpt-4o-mini", "gpt-4o"]
    selected = st.selectbox(
        "Select AI Model",
        ai_models,
    )

    return init_chat_model(selected)


def select_time_limit() -> int:  # TODO : use this
    days_labels = {
        1: "Last 24h",
        2: "Last 2 days",
        3: "Last 3 days",
        7: "Last week",
        15: "Last 15 days",
        30: "Last month",
        60: "Last 2 months",
        90: "Last 3 months",
    }

    selected = st.radio(
        "Select Time Limit",
        list(days_labels.keys()),
        format_func=lambda x: days_labels[x],
    )
    assert selected is not None

    return selected


with st.sidebar:
    st.subheader("Parameters")
    workspace = _select_workspace()
    llm = select_ai_model()
    time_limit_days = select_time_limit()


assert workspace.field_id
docsearch = PineconeVectorStore(
    pinecone_api_key=settings.PINECONE_API_KEY,
    index_name=settings.PINECONE_INDEX,
    embedding=embeddings,
    namespace=workspace.field_id,
    text_key="title",  # Page content of retrieved documents will be set to the articles titles
)


history = StreamlitChatMessageHistory(key="chat_history")


def display_chat_history():
    for msg in history.messages:
        with st.chat_message(msg.type):
            st.markdown(msg.content)


display_chat_history()


# @st.cache_resource()
def _fetch_contextualize_prompt():
    return hub.pull("contextualize-prompt")


def _create_history_aware_retriever(retriever: VectorStoreRetriever):
    prompt = _fetch_contextualize_prompt()
    return create_history_aware_retriever(llm, retriever, prompt)


# @st.cache_resource()
def _fetch_qa_prompt():
    return hub.pull("so-insights-qa")


def convert_docs(docs: Iterable[Document]) -> SetOfUniqueArticles:
    assert workspace.field_id
    articles = list(map(_ArticleDocument.from_document, docs))

    # deduplicate
    return SetOfUniqueArticles(articles)  # type:ignore


def format_docs(articles: SetOfUniqueArticles) -> str:
    separator = "\n\n---\n\n"
    return separator.join(
        f"{article.title} - (Published on {article.date})\n{article.url}\n{article.body}"
        for article in articles
    )


def create_chain(retriever: VectorStoreRetriever):
    # TODO : raise error if there are no documents to retrieve
    rag_chain = (
        RunnablePassthrough.assign(
            context=_create_history_aware_retriever(retriever)
            | convert_docs
            | format_docs,
            date=RunnableLambda(lambda _: datetime.now().strftime("%Y-%m-%d")),
        )
        | _fetch_qa_prompt()
        | llm
        | StrOutputParser()
    )

    return RunnableWithMessageHistory(
        rag_chain,  # type: ignore
        lambda session_id: history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )


chain = create_chain(docsearch.as_retriever(search_kwargs={"k": settings.RETRIEVER_K}))


if prompt := st.chat_input("What would you like to know about your data ?"):
    st.chat_message("user").markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in chain.stream(
            {"input": prompt},
            config={
                "metadata": {"workspace_id": workspace.field_id},
                "configurable": {"session_id": "any"},
            },
        ):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

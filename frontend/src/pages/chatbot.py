from dataclasses import dataclass
from langchain_core.runnables.config import RunnableConfig
from datetime import datetime, timedelta, timezone
from typing import Iterable, Sequence
from uuid import uuid4
from pydantic import HttpUrl
from langchain.chains import create_history_aware_retriever
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from sdk.so_insights_client.api.starters import get_latest_starters
from sdk.so_insights_client.api.workspaces import get_articles_by_ids
from sdk.so_insights_client.models.article import Article
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from shared.set_of_unique_articles import SetOfUniqueArticles
from src.app_settings import app_settings
from src.shared import get_authenticated_client, get_workspace_or_stop
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


# TODO : verify that the workspace contains data before running the chatbot

workspace = get_workspace_or_stop()

st.title("💬 Chat with your data")

if not st.session_state.get("chat_history"):
    st.info(
        "Welcome to the chatbot! Here you can ask questions about your data and get insights.",
        icon="ℹ️",
    )


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


embeddings = VoyageAIEmbeddings(  # type:ignore #Arguments missing for parameters "_client", "_aclient"
    api_key=app_settings.VOYAGEAI_API_KEY.get_secret_value(),
    model=app_settings.EMBEDDING_MODEL,
)


client = get_authenticated_client(workspace.organization_id)

if not st.session_state.get("session_id"):
    st.session_state["session_id"] = uuid4().hex


def reset_chat():
    del st.session_state["session_id"]
    del st.session_state["used_starters"]
    history.clear()


st.session_state["on_workspace_changed_chatbot"] = reset_chat


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
        -1: "All time",
    }

    selected = st.radio(
        "Select Time Limit",
        list(days_labels.keys()),
        format_func=lambda x: days_labels[x],
        index=list(days_labels.keys()).index(-1),
    )
    assert selected is not None

    return selected


history = StreamlitChatMessageHistory(key="chat_history")

with st.sidebar:
    st.subheader("Parameters")
    llm = select_ai_model()
    time_limit_days = select_time_limit()
    if st.button("🗑️ Reset Chat", use_container_width=True):
        reset_chat()
        st.rerun()


assert workspace.field_id
docsearch = PineconeVectorStore(
    pinecone_api_key=app_settings.PINECONE_API_KEY.get_secret_value(),
    index_name=app_settings.PINECONE_INDEX,
    embedding=embeddings,
    namespace=workspace.field_id,
    text_key="title",  # Page content of retrieved documents will be set to the articles titles
)


def display_chat_history():
    for msg in history.messages:
        with st.chat_message(msg.type):
            st.markdown(msg.content)


display_chat_history()


if "used_starters" not in st.session_state:
    st.session_state["used_starters"] = set()


# @st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_starters(workspace_id: str) -> list[str]:
    response = get_latest_starters.sync(client=client, workspace_id=workspace_id)
    if isinstance(response, list):
        return response
    return []


def show_starters(questions: list[str]) -> str | None:
    if not questions:
        return

    questions = list(set(questions))

    assert len(questions) <= 4
    for col, question in zip(
        st.columns(
            len(questions),
            border=True,
        ),
        questions,
    ):
        if col.button(
            question,
            use_container_width=True,
            disabled=question in st.session_state["used_starters"],
            type="tertiary",
        ):
            st.session_state["used_starters"].add(question)
            return question


selected_starter = show_starters(fetch_starters(workspace.field_id))


# @st.cache_resource()
def _fetch_contextualize_prompt():
    return hub.pull(app_settings.CONTEXTUALIZE_PROMPT_REF)


def _create_history_aware_retriever(retriever: VectorStoreRetriever):
    prompt = _fetch_contextualize_prompt()
    return create_history_aware_retriever(llm, retriever, prompt)


# @st.cache_resource()
def _fetch_qa_prompt():
    return hub.pull(app_settings.QA_RAG_PROMPT_REF)


def fetch_docs(docs: Iterable[Document]) -> SetOfUniqueArticles:
    assert workspace.field_id
    articles_ids = [doc.id for doc in docs if doc.id]

    if not articles_ids:
        st.warning(
            "No relevant articles found to ground the answer. The chatbot will rely only on its internal knowledge, which may lead to inaccurate or outdated responses."
        )
        return SetOfUniqueArticles([])
    # fetch the full articles from the backend
    articles = get_articles_by_ids.sync(
        client=client,
        workspace_id=workspace.field_id,
        article_ids=articles_ids,
    )

    if not articles or isinstance(articles, HTTPValidationError):
        st.error(f"Error fetching articles: {articles}")
        st.stop()

    print(f"Fetched {len(articles)} articles")
    # deduplicate
    return SetOfUniqueArticles(articles)  # type:ignore


def format_docs(articles: SetOfUniqueArticles | Sequence[Article]) -> str:
    if not articles:
        return "No articles found to ground the answer."
    separator = "\n\n---\n\n"
    print(f"Formatting {len(articles)} articles")
    return separator.join(
        f"# {article.title} - (Published on {article.date.strftime('%Y-%m-%d')})\n{article.url}\n{article.content if article.content else article.body}"
        for article in articles
    )


def create_chain(retriever: VectorStoreRetriever):
    # TODO : raise error if there are no documents to retrieve
    rag_chain = (
        RunnablePassthrough.assign(
            context=_create_history_aware_retriever(retriever)
            | fetch_docs
            | format_docs,
            date=RunnableLambda(lambda _: datetime.now().strftime("%Y-%m-%d")),  # noqa: DTZ005
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


search_kwargs = {
    "k": app_settings.RETRIEVER_K,
    # Filter by date
    "filter": {
        "date": {
            "$gte": (
                datetime.now(tz=timezone.utc) - timedelta(days=time_limit_days)
            ).timestamp()
        },
    }
    if time_limit_days != -1
    else None,
}


chain = create_chain(docsearch.as_retriever(search_kwargs=search_kwargs)).with_config(
    run_name="chatbot_chain"
)

config = RunnableConfig(
    metadata={"workspace_id": workspace.field_id},
    configurable={"session_id": st.session_state.session_id},
)


if prompt := (
    st.chat_input("What would you like to know about your data ?") or selected_starter
):
    st.chat_message("user").markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in chain.stream(
            {"input": prompt},
            config=config,
        ):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.rerun()

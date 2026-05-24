from __future__ import annotations

from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_text_splitter(
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def selective_split_profile_docs(
    profile_docs: list[Document],
    splitter: RecursiveCharacterTextSplitter | None = None,
) -> list[Document]:
    splitter = splitter or create_text_splitter()
    split_docs = []

    for doc in profile_docs:
        doc_type = doc.metadata.get("type")

        if doc_type in ["work_experience", "project"]:
            chunks = splitter.split_documents([doc])

            for index, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = index
                split_docs.append(chunk)
        else:
            split_docs.append(doc)

    return split_docs


def create_vectorstore(profile_chunks: list[Document], embeddings: Any) -> FAISS:
    return FAISS.from_documents(profile_chunks, embeddings)


def create_retriever(
    profile_chunks: list[Document],
    embeddings: Any,
    top_k: int = 3,
) -> Any:
    vectorstore = create_vectorstore(profile_chunks, embeddings)

    return vectorstore.as_retriever(search_kwargs={"k": top_k})

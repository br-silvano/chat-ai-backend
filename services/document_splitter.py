from collections.abc import Iterable
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging


def split_documents(docs: Iterable[Document], chunk_size: int = 1000, chunk_overlap: int = 200):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splited_documents = text_splitter.split_documents(docs)
    logging.info(f"Documentos divididos em {len(splited_documents)} segmentos.")
    return splited_documents

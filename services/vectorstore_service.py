from collections.abc import Iterable
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from services.document_loader import load_data
from services.document_splitter import split_documents
import logging
import os


class VectorStoreService:
    def __init__(self) -> None:
        self.save_path = "data/faiss"
        self.embedding_model = OpenAIEmbeddings()

    def get_or_create_vectorstore(self):
        if self.vectorstore_exists():
            logging.info("Armazenamento vetorial carregado do cache.")
            vectorstore = self.load_vectorstore()
            if not vectorstore:
                raise ValueError("Falha ao carregar o armazenamento vetorial.")
            return vectorstore

        logging.info("Armazenamento vetorial não encontrado no cache. Criando um novo.")
        documents = load_data()
        if len(documents) == 0:
            raise ValueError("Nenhum documento encontrado para carregar.")

        splited_documents = split_documents(documents)
        vectorstore = self.initialize_vectorstore(splited_documents)

        if not vectorstore:
            raise ValueError("Falha ao criar o armazenamento vetorial.")

        return vectorstore

    def initialize_vectorstore(self, documents: Iterable[Document]):
        try:
            vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding_model
            )
            logging.info("Vectorstore inicializado com sucesso.")
            vectorstore.save_local(self.save_path)
            return vectorstore
        except Exception as e:
            logging.error(f"Erro ao inicializar o vectorstore: {e}")
            return None

    def load_vectorstore(self):
        try:
            vectorstore = FAISS.load_local(
                folder_path=self.save_path,
                embeddings=self.embedding_model,
                allow_dangerous_deserialization=True
            )
            logging.info("Vectorstore carregado com sucesso.")
            return vectorstore
        except Exception as e:
            logging.error(f"Erro ao carregar o vectorstore: {e}")
            return None

    def vectorstore_exists(self):
        index_path = os.path.join(self.save_path, "index.faiss")
        return os.path.exists(index_path)

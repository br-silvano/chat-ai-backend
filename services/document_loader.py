import json
import logging
from langchain.schema import Document


def load_data():
    try:
        with open("data/meus_documentos.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
            logging.info("Dados carregados com sucesso.")
            return [Document(page_content=f"Título: {d['titulo']}\nConteúdo: {d['conteudo']}") for d in data]
    except Exception as e:
        logging.error(f"Erro ao carregar dados: {e}")
    return []

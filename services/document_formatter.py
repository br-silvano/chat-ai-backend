from collections.abc import Iterable
from langchain.schema import Document


def format_documents(docs: Iterable[Document]):
    return "\n\n".join(doc.page_content for doc in docs)

from datetime import datetime
from langchain import hub
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from models.question_request import QuestionRequest
from services.document_formatter import format_documents
from services.history_service import HistoryService
from services.rediscache_service import RedisCacheService
from services.vectorstore_service import VectorStoreService
from slugify import slugify
import logging
import redis


class QuestionProcessor:
    def __init__(
        self,
        redis_client: redis.StrictRedis,
        vectorstore_service: VectorStoreService
    ):
        self.redis_cache = RedisCacheService(redis_client)
        self.vectorstore_service = vectorstore_service
        self.history_service = HistoryService(self.redis_cache)

    def process_question(self, json_data: any):
        try:
            data = QuestionRequest(**json_data)
            user_id = data.user_id
            question = data.question

            question_slug = slugify(question)
            question_key = f"conversation_question:{question_slug}"

            cached_answer = self.redis_cache.get_cached_answer(question_key)
            if cached_answer:
                logging.info("Resposta obtida do cache Redis.")
                conversation_history = self.history_service.get_conversation_history(user_id)
                return {
                    "currentAnswer": {
                        "timestamp": datetime.now().isoformat(),
                        "question": question,
                        "answer": cached_answer
                    },
                    "history": conversation_history
                }

            vectorstore = self.vectorstore_service.get_or_create_vectorstore()
            rag_chain = self.configure_rag_chain(vectorstore)

            prompt_input = self.create_prompt_input(question)
            result = rag_chain.invoke(prompt_input)
            logging.info("Pergunta respondida com sucesso.")

            self.redis_cache.cache_answer(question_key, result)
            conversation_history = self.history_service.get_conversation_history(user_id)
            self.history_service.store_conversation_history(user_id, question, result)
            return {
                "currentAnswer": {
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "answer": result
                },
                "history": conversation_history
            }

        except Exception as e:
            logging.error(f"Erro ao processar a pergunta: {e}")
            return {"error": "Erro ao processar a pergunta."}

    def configure_rag_chain(self, vectorstore: FAISS):
        retriever = vectorstore.as_retriever()
        prompt = hub.pull("rlm/rag-prompt")

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            verbose=False,
            temperature=0.5,
            max_tokens=1000,
            timeout=30,
            max_retries=2,
        )

        rag_chain = (
            {"context": retriever | format_documents, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return rag_chain

    def create_prompt_input(self, question: str):
        return f"""
        Seja um assistente amigável e acolhedor. Responda com um tom empático e encorajador.
        Se não souber a resposta, ofereça uma resposta honesta, mas proponha alternativas ou reencaminhe a questão para que o usuário possa tentar novamente.
        Pergunta: {question}
        """

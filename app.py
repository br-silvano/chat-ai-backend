from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.question_service import QuestionProcessor
from services.vectorstore_service import VectorStoreService
import logging
import os
import redis

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", "6379"))
redis_password = os.environ.get("REDIS_PASSWORD", "")

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri=f"redis://:{redis_password}@{redis_host}:{redis_port}/0",
    default_limits=["10 per minute"]
)

redis_client = redis.StrictRedis(
    host=redis_host,
    password=redis_password,
    port=redis_port,
    db=1,
    decode_responses=True
)


@app.route('/ask', methods=['POST'])
@limiter.limit("10 per minute")
def ask_question():
    try:
        json_data = request.get_json()

        vectorstore_service = VectorStoreService()
        question_processor = QuestionProcessor(redis_client, vectorstore_service)
        response = question_processor.process_question(json_data)

        return jsonify(response)

    except Exception as e:
        logging.error(f"Erro ao processar a pergunta: {e}")
        return jsonify({"error": "Erro ao processar a pergunta."}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

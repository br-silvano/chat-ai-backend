from datetime import datetime
import json
import redis


class HistoryService:
    def __init__(self, redis_cache: redis.StrictRedis):
        self.redis_cache = redis_cache

    def store_conversation_history(self, user_id: str, question: str, answer: str):
        conversation_history = self.get_conversation_history(user_id)

        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer
        }
        conversation_history.append(new_entry)

        history_key = f"conversation_history:{user_id}"
        self.redis_cache.cache_answer(
            history_key,
            json.dumps(conversation_history),
            expiration_time=43200
        )

    def get_conversation_history(self, user_id: str):
        history_key = f"conversation_history:{user_id}"
        current_history = self.redis_cache.get_cached_answer(history_key)

        if current_history:
            return json.loads(current_history)
        else:
            return []

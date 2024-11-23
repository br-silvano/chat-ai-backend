import redis


class RedisCacheService:
    def __init__(self, redis_client: redis.StrictRedis):
        self.redis_client = redis_client

    def get_cached_answer(self, question: str):
        return self.redis_client.get(question)

    def cache_answer(self, question: str, answer: str, expiration_time: int = 3600):
        self.redis_client.setex(question, expiration_time, answer)

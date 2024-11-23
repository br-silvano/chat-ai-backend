from pydantic import BaseModel, field_validator
from utils.sanitizer import sanitize


class QuestionRequest(BaseModel):
    user_id: str
    question: str

    @field_validator('user_id')
    def validate_user_id(cls, value: str) -> str:
        if not (1 <= len(value) <= 50):
            raise ValueError("user_id deve ter entre 1 e 50 caracteres")
        return value

    @field_validator('question')
    def validate_question(cls, value: str) -> str:
        if not (5 <= len(value) <= 255):
            raise ValueError("question deve ter entre 5 e 255 caracteres")
        return sanitize(value)

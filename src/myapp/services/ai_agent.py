from __future__ import annotations
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

from myapp.models.post import Question
from myapp.models.users import Author

logger = logging.getLogger(__name__)

AI_HELP_TAG = "#ia-help"

class AIStrategy(ABC):#Interface para estrategias de IA
    @abstractmethod
    def generate_answer(self, question: Question) -> str:
        pass

class AIAgent(Author):
    def __init__(
        self,
        agent_id: int,
        name: str,
        strategy: AIStrategy,
        active_model: str = "default",
        wait_minutes: int | None = None,
    ) -> None:

        super().__init__(agent_id, name)
        if not isinstance(strategy, AIStrategy):
            raise ValueError("La estrategia debe ser una instancia válida de AIStrategy.")
        self._strategy = strategy
        self._active_model = active_model
        

        default_wait = int(os.getenv("AI_AGENT_WAIT_MINUTES","5"))
        minutes = wait_minutes if wait_minutes is not None else default_wait
        if minutes < 0:
            raise ValueError("El tiempo de espera no puede ser negativo.")
        self._wait_time = timedelta(minutes=minutes)

    @property
    def strategy(self) -> AIStrategy:
        return self._strategy

    @property
    def active_model(self) -> str:
        return self._active_model

    @property
    def wait_time(self) -> timedelta:
        return self._wait_time

    def set_strategy(self, strategy: AIStrategy, active_model: str | None = None) -> None:
        if not isinstance(strategy, AIStrategy):
            raise ValueError("La estrategia debe ser una instancia válida de AIStrategy.")
        self._strategy = strategy
        if active_model is not None:
            self._active_model = active_model

    def create_answer(self, question: Question, text: str) -> Any:
        if not isinstance(question, Question):
            raise ValueError("El parámetro 'question' debe ser una instancia válida de Question.")
        if not text or not text.strip():
            raise ValueError("El texto de la respuesta no puede estar vacío.")
        raise NotImplementedError("La creación de respuestas aún no está implementada.")

    def _get_question_answer(self, question: Question) -> list[Any]:
        if hasattr(question, "answers"):
            return question.answers
        return getattr(question, "_answers", [])

    def has_help_tag(self, question:Question) -> bool:
        return question.has_tag(AI_HELP_TAG) or question.has_tag("ia-help")

    def is_unanswered(self, question: Question, now: datetime | None = None) -> bool:
        if len (self._get_question_answer(question)) > 0:
            return False
        current_time = now if now is not None else datetime.now()
        return (current_time - question.created_at) >= self._wait_time

    def has_answered(self, question: Question) -> bool:
        for answer in self ._get_question_answer(question):
            author = getattr(answer, "author", None)
            if author is self or isinstance(author, AIAgent):
                return True
        return False 

    def should_respond(self, question: Question, now: datetime | None = None) -> bool:
        if not isinstance(question, Question):
            raise ValueError("El parámetro 'question' debe ser una instancia válida de Question.")
        if self.has_answered(question):
            logger.info(f"El agente {self.name} ya ha respondido a la pregunta {question.id}.")
            return False
        return self.has_help_tag(question) or self.is_unanswered(question, now=now)

    def process_question(self, question: Question, now: datetime | None = None) -> Any | None :
        if not self.should_respond(question, now=now):
            return None 
        try:
            answer_text = self._strategy.generate_answer(question)
        except Exception:
            logger.exception(f"Error al generar la respuesta para la pregunta {question.id}.")
            return None

        answer = self.create_answer(question, answer_text)

        if hasattr(question, "add_answer"):
            question.add_answer(answer)
        else:
            answers = self._get_question_answer(question)
            if answer not in answers:
                answers.append(answer)

        logger.info(f"El agente {self.name} ha respondido a la pregunta {question.id}.")
        return answer 
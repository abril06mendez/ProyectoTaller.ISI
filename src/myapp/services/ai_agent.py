from __future__ import annotations
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

import anthropic
from google import genai 
from openai import OpenAI

from myapp.models.post import Answer, Question
from myapp.models.users import Author

logger = logging.getLogger(__name__)

AI_HELP_TAG = "#ia-help"

class AIStrategy(ABC):#Interface para estrategias de IA
    @abstractmethod
    def generate_answer(self, question: Question) -> str:
        pass
class AIModelError(Exception):
    """Excepción para informar cuando falla el modelo de IA seleccionado"""
    pass
def _build_prompt(question: Question) -> str:
    return(
        f"Categoría: {question.category.name}\n"
        f"Título: {question.title}\n"
        f"Pregunta: {question.body}"
    )
class GeminiStrategy(AIStrategy): 
    def __init__(self, model: str = "gemini-2.5-flash") -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise AIModelError("No se pudo inicializar Geminin:falta GEMINI_API_KEY")
        self._client = genai.Client(api_key=api_key)
        self._model = model
    def generate_answer(self, question: Question) -> str:
        try:
            response =self._client.models.generate_content(
                model=self._model,
                contents=_build_prompt(question),
            )
            if not response.text:
                raise AIModelError("Gemini devolvió una respuesta vacía")
            return response.text
        except AIModelError:
            raise
        except Exception as e:
            raise AIModelError(f"Error al consultar Gemini: {e}") from e

class OpenAIStrategy(AIStrategy):
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise AIModelError("No se pudo inicializar OpenAI:falta OPEN_API_KEY")
        self._client = OpenAI(api_key=api_key)
        self._model = model
    def generate_answer(self, question: Question) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": _build_prompt(question)}],
            )
            content = response.choices[0].message.content
            if not content:
                raise AIModelError("OpenAi devolvió una respuesta vacía")
            return content
        except AIModelError:
            raise
        except Exception as e:
            raise AIModelError(f"Error al consultar OpenAI: {e}") from e

class ClaudeStrategy (AIStrategy):
    def __init__(self, model:str = "claude-3-5-sonnet-latest") -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise AIModelError("No se encontró la variable de entorno ANTHROPIC_API_KEY")
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
    def generate_answer(self, question: Question) -> str:
        try: 
            response = self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                messages=[{"role": "user", "content": _build_prompt(question)}],    
            )
            if not response.content or not getattr(response.content[0], "text", None):
                raise AIModelError("Claude devolvió una respuesta vacía")
            return response.content[0].text
        except AIModelError:
            raise
        except Exception as e:
            raise AIModelError(f"Error al consultar Claude: {e}") from e

AVAILABLE_STRATEGIES: dict[str, type[AIStrategy]] = {
    "gemini": GeminiStrategy,
    "openai": OpenAIStrategy,
    "claude": ClaudeStrategy,
}

def create_strategy(model_name: str) -> AIStrategy:
    """Crea la estrategia correspondiente al nombre del modelo elegido"""
    strategy_cls = AVAILABLE_STRATEGIES.get(model_name.strip().lower())
    if strategy_cls is None:
        raise AIModelError(
            f"Modelo '{model_name}' no soportado. Opciones válidas: gemini, openai, claude"
        )
    return strategy_cls()


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
    def select_model(self, model_name: str) -> None:
                new_strategy = create_strategy(model_name)
                self.set_strategy(new_strategy, active_model=model_name.strip().lower())


    def create_answer(self, question: Question, text: str) -> Any:
        if not isinstance(question, Question):
            raise ValueError("El parámetro 'question' debe ser una instancia válida de Question.")
        if not text or not text.strip():
            raise ValueError("El texto de la respuesta no puede estar vacío.")
        return Answer(text, self, question)

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

    
from datetime import timedelta

import pytest

from myapp.models.post import Category, Question, Tag
from myapp.models.users import User, UserType
from myapp.services.ai_agent import AIAgent, AIStrategy

class dummy_strategy(AIStrategy):
    def generate_answer(self, question: Question) -> str:
        return f"Respuesta sugerida para: {question.title}"

class AlternativeStrategy(AIStrategy):
    def generate_answer(self, question: Question) -> str:
        return f"Respuesta alternativa para: {question.title}"

class FailingStrategy(AIStrategy):
    def generate_answer(self, question: Question) -> str:
        raise RuntimeError("Fallo simulado del proveedor de IA")

@pytest.fixture
def sample_question():
    category = Category(1, "Python")
    student = User(1, "Pepe", "pepe@example.com", "123456", UserType.STUDENT)
    agent = AIAgent(2, "AI Gemini", dummy_strategy(), wait_minutes=5)
    return category, student, agent

def test_ai_agent_initialization():
    with pytest.raises(ValueError):
        AIAgent(1, "AI Agent", "not_a_strategy")  # Estrategia inválida
    with pytest.raises(ValueError):
        AIAgent(1, "AI Agent", dummy_strategy(), wait_minutes=-5)  # Tiempo de espera negativo

def test_should_respond_with_ia_help_tag(sample_question):
        category, student, agent = sample_question
        tag = Tag(1, "ia-help")
        question = Question(1, "Sample Question", "This is a sample question.", category, student, [tag])
        assert agent.should_respond(question) == True

def test_should_respond_after_wait_time(sample_question):
        category, student, agent = sample_question
        question = Question(2, "Sample Question", "This is a sample question.", category, student)
        before_wait_time = question.created_at + timedelta(minutes=3)
        after_wait_time = question.created_at + timedelta(minutes=5)

        assert agent.should_respond(question, now=before_wait_time) == False
        assert agent.should_respond(question, now=after_wait_time) == True

def test_set_strategy_updates_strategy_and_model(sample_question):
    category, student, agent = sample_question
    new_strategy = AlternativeStrategy()
    agent.set_strategy(new_strategy, active_model="new_model")
    assert agent.strategy is new_strategy
    assert agent.active_model == "new_model"

def test_process_question_responds_once_and_prevents_duplicates(sample_question):
    category, student, agent = sample_question
    tag = Tag(1, "#ia-help")
    question = Question(4, "Duda Git", "Cómo hago un projects?", category, student, tags=[tag])

    first_answer = agent.process_question(question)
    second_answer = agent.process_question(question)

    assert first_answer is not None
    assert first_answer.author is agent
    assert "Duda Git" in first_answer.body
    assert len(question.answers) == 1
    assert second_answer is None


def test_process_question_handles_strategy_failure(sample_question):
    category, student, agent = sample_question
    tag = Tag(1, "#ia-help")
    question = Question(5, "Duda Pytest", "Cómo uso fixtures?", category, student, tags=[tag])

    agent.set_strategy(FailingStrategy())
    result = agent.process_question(question)

    assert result is None
    assert len(question._answers) == 0
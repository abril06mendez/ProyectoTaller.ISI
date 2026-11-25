import pytest
from myapp.models.post import Category, Question, Tag
from myapp.models.users import Author
from myapp.services.ai_agent import(
   AIAgent,
    AIModelError,
    AIStrategy,
    ClaudeStrategy,
    GeminiStrategy,
    OpenAIStrategy,
    create_strategy,
)

class DummyAuthor(Author):
    def create_answer(self, question: Question, text: str):
        return None

class FakeSuccessStrategy(AIStrategy):
    def __init__(self, prefix: str) ->None:
        self.prefix = prefix

    def generate_answer(self,question: Question) -> str:
        return f"[{self.prefix}] Respuesta a: {question.title}"

class FakeFailingStrategy(AIStrategy):
    def generate_answer(self, question: Question) -> str:
        raise AIModelError("El proveedor de IA no respondio")
        
def _sample_question() -> Question:
    author = DummyAuthor(1, "Maria")
    category = Category(1, "ingeniería de software")
    tag = Tag(1, "#ia-help")
    return Question(
        post_id=10,
        title="¿Qué es el patron singleton?",
        body="Necesito un ejemplo practico en Java",
        category=category,
        author=author,
        tags=[tag],
    )

def test_strategies_implement_ai_strategy():
    assert issubclass (GeminiStrategy, AIStrategy)
    assert issubclass (OpenAIStrategy, AIStrategy)
    assert issubclass (ClaudeStrategy, AIStrategy)

def test_select_models(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-claude-key")

    assert isinstance(create_strategy("gemini"), GeminiStrategy)
    assert isinstance(create_strategy("openai"), OpenAIStrategy)
    assert isinstance(create_strategy("claude"), ClaudeStrategy)   

def test_switch_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-claude-key")

    agent = AIAgent(
        agent_id=99,
        name="BotIs",
        strategy=FakeSuccessStrategy("Gemini"),
        active_model="gemini",
    )
    question = _sample_question()

    assert agent.strategy.generate_answer(question) == "[Gemini] Respuesta a: ¿Qué es el patron singleton?"

    agent.select_model("Claude")
    assert agent.active_model == "claude"
    assert isinstance (agent.strategy, ClaudeStrategy)

def test_invalid_model():
    with pytest.raises(AIModelError, match="no soportado"):
        create_strategy("modelo desconocido")

def test_model_error():
        agent=AIAgent(
            agent_id=99,
            name="BotIS",
            strategy=FakeFailingStrategy(),
            active_model="gemini",
        )
        question = _sample_question()

        with pytest.raises(AIModelError, match="El proveedor de IA no respondio"):
            agent.strategy.generate_answer(question)
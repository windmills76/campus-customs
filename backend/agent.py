import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

from models import AgentReply, ChatTurn
from tools import get_product_details, get_stock, search_catalogue

BACKEND_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BACKEND_DIR / "prompts" / "prompt.md"

# The repo's shared PORTKEY_API_KEY lives in the course-root .env, several
# directories above this homework folder. Walk upward so this works no
# matter where the course directory is checked out.
for folder in [BACKEND_DIR, *BACKEND_DIR.parents]:
    if (folder / ".env").exists():
        load_dotenv(folder / ".env", override=False)

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-6-luna")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1").rstrip("/")


def require_api_key() -> str:
    key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "PORTKEY_API_KEY is missing. Add it to the course-root .env (shared across "
            "homeworks) or to backend/.env."
        )
    return key


@lru_cache(maxsize=1)
def build_model() -> OpenAIResponsesModel:
    client = AsyncOpenAI(
        api_key=require_api_key(),
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-provider": "openai"},
    )
    return OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))


@lru_cache(maxsize=1)
def _system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


shop_agent = Agent(
    output_type=AgentReply,
    instructions=_system_prompt(),
    tools=[search_catalogue, get_product_details, get_stock],
    name="campus-customs-shop-assistant",
)


def _to_model_messages(history: list[ChatTurn]) -> list[ModelMessage]:
    messages: list[ModelMessage] = []
    for turn in history:
        if turn.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        else:
            messages.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return messages


async def run_chat(message: str, history: list[ChatTurn]) -> AgentReply:
    result = await shop_agent.run(
        message,
        model=build_model(),
        message_history=_to_model_messages(history),
    )
    return result.output

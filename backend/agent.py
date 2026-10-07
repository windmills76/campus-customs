import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

from models import AgentReply, ChatTurn
from tools import get_product_info, get_stock, search_catalogue

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


@dataclass
class ShopperContext:
    """Agent deps: who's chatting, and what they're currently looking at.

    Built fresh per request in main.py from the logged-in user row (if any)
    and the frontend's page_context — never guessed or recalled from a
    previous turn.
    """

    is_guest: bool
    name: str | None = None
    email: str | None = None
    current_product_id: str | None = None


shop_agent = Agent(
    deps_type=ShopperContext,
    output_type=AgentReply,
    instructions=_system_prompt(),
    tools=[search_catalogue, get_product_info, get_stock],
    name="campus-customs-shop-assistant",
)


@shop_agent.instructions
def shopper_context_instructions(ctx: RunContext[ShopperContext]) -> str:
    deps = ctx.deps
    if deps.is_guest:
        lines = ["The shopper is browsing as a guest (not logged in) — don't address them by name."]
    else:
        lines = [f"The shopper is logged in as {deps.name} ({deps.email})."]

    if deps.current_product_id:
        lines.append(
            f'The shopper is currently viewing the product page for product_id="{deps.current_product_id}". '
            'If they refer to "this", "it", or the item without naming one, assume they mean this '
            "product unless they clearly describe something else — confirm details with a tool call "
            "using this product_id before answering."
        )

    return "\n".join(lines)


def _to_model_messages(history: list[ChatTurn]) -> list[ModelMessage]:
    messages: list[ModelMessage] = []
    for turn in history:
        if turn.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        else:
            messages.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return messages


async def run_chat(message: str, history: list[ChatTurn], deps: ShopperContext) -> AgentReply:
    result = await shop_agent.run(
        message,
        model=build_model(),
        message_history=_to_model_messages(history),
        deps=deps,
    )
    return result.output

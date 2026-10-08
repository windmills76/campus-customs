from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SizeStock(BaseModel):
    size: str
    quantity: int


class Product(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    search_tags: list[str]
    image_file_path: str
    image_url: str
    price: float
    inventory: list[SizeStock]
    total_stock: int


class ProductInfo(BaseModel):
    """Description/price facts for one product — deliberately excludes
    inventory so this tool can't be mistaken for a stock check."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    image_url: str


class ProductInfoResult(BaseModel):
    found: bool
    info: ProductInfo | None = None


class StockLookupResult(BaseModel):
    """Always includes the full by-size breakdown; the requested_size_*
    fields are only populated when the caller asked about one specific
    size, so the agent can answer either 'what sizes do you have' or
    'do you have a medium' from the same tool."""

    found: bool
    product_id: str
    total_stock: int | None = None
    by_size: list[SizeStock] = Field(default_factory=list)
    requested_size: str | None = None
    requested_size_quantity: int | None = None
    requested_size_in_stock: bool | None = None


class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def email_looks_valid(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Enter a valid email address")
        return value


class LoginRequest(BaseModel):
    email: str
    password: str


class PublicUser(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    email: str


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class PageContext(BaseModel):
    """What the shopper is currently looking at, so the agent can resolve
    "do you have this in pink" without the shopper having to name the item."""

    product_id: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    user_id: int | None = None
    history: list[ChatTurn] = Field(default_factory=list)
    page_context: PageContext | None = None


class ChatResponse(BaseModel):
    reply: str
    products: list[Product] = Field(default_factory=list)


class AgentReply(BaseModel):
    """Structured output the agent itself produces; main.py hydrates
    product_ids into full Product records before responding to the client."""

    message: str
    product_ids: list[str] = Field(default_factory=list)


class AuditEvent(BaseModel):
    """One line of output/audit_trail.json. Deliberately flat and mostly
    optional fields (rather than a tool_call/run_complete union type) so the
    log file stays simple to append to and to grep/read by hand; `type`
    tells you which fields are populated for a given line. Short, truncated
    strings only (see audit.py) — this is an activity log, not a full
    request/response dump, so it can't become a second place sensitive chat
    content leaks into."""

    timestamp: str
    type: Literal["tool_call", "run_complete"]
    tool: str | None = None
    args: str | None = None
    result: str | None = None
    message_preview: str | None = None
    stop_reason: str | None = None
    product_count: int | None = None
    is_guest: bool | None = None

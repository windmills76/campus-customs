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


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    user_id: int | None = None
    history: list[ChatTurn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    products: list[Product] = Field(default_factory=list)


class AgentReply(BaseModel):
    """Structured output the agent itself produces; main.py hydrates
    product_ids into full Product records before responding to the client."""

    message: str
    product_ids: list[str] = Field(default_factory=list)

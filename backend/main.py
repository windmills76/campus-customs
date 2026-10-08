import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import db
import safety
import security
from agent import ShopperContext, run_chat
from models import ChatRequest, ChatResponse, LoginRequest, Product, PublicUser, SignupRequest

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent
PRODUCTS_DIR = Path(os.getenv("PRODUCTS_DIR", BACKEND_DIR / ".." / "data" / "products")).resolve()

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if PRODUCTS_DIR.is_dir():
    app.mount("/media/products", StaticFiles(directory=PRODUCTS_DIR), name="product-images")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "db_path_exists": db.DB_PATH.exists(), "images_dir_exists": PRODUCTS_DIR.is_dir()}


@app.get("/api/products", response_model=list[Product])
def get_products() -> list[Product]:
    return db.list_products()


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> Product:
    product = db.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/auth/signup", response_model=PublicUser, status_code=201)
def signup(payload: SignupRequest) -> PublicUser:
    password_hash = security.hash_password(payload.password)
    try:
        return db.create_user(payload.first_name, payload.last_name, payload.email, password_hash)
    except db.EmailAlreadyRegistered:
        raise HTTPException(status_code=409, detail="An account with that email already exists")


@app.post("/api/auth/login", response_model=PublicUser)
def login(payload: LoginRequest) -> PublicUser:
    row = db.get_user_by_email(payload.email.strip().lower())
    if row is None or not security.verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return PublicUser(id=row["id"], first_name=row["first_name"], last_name=row["last_name"], email=row["email"])


def _build_shopper_context(payload: ChatRequest) -> ShopperContext:
    product_id = payload.page_context.product_id if payload.page_context else None

    user_row = db.get_user_by_id(payload.user_id) if payload.user_id is not None else None
    if user_row is None:
        return ShopperContext(is_guest=True, current_product_id=product_id)

    name = f"{user_row['first_name']} {user_row['last_name']}".strip() or user_row["name"]
    return ShopperContext(
        is_guest=False,
        name=name,
        email=user_row["email"],
        current_product_id=product_id,
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    # Code-level backstop, not just a prompt instruction: strip anything
    # that looks like a card number or SSN before it reaches the model or
    # the database, regardless of what the model would have done with it.
    safe_message = safety.redact_sensitive(payload.message)

    deps = _build_shopper_context(payload)
    agent_reply = await run_chat(safe_message, payload.history, deps)
    products = [db.get_product(pid) for pid in agent_reply.product_ids]
    products = [p for p in products if p is not None]

    # Only logged-in shoppers (a real user_id that resolved to a real user
    # row) get their conversation persisted — guests can chat, but nothing
    # is written to chat_messages for them.
    if not deps.is_guest and payload.user_id is not None:
        db.save_chat_message(payload.user_id, "user", safe_message)
        db.save_chat_message(payload.user_id, "assistant", agent_reply.message, products)

    return ChatResponse(reply=agent_reply.message, products=products)


@app.get("/api/chat/history/{user_id}")
def chat_history(user_id: int) -> list[dict]:
    return db.get_chat_history(user_id)

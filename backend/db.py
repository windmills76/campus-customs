import json
import os
import sqlite3
import time
from pathlib import Path

from models import PublicUser, Product, SizeStock


class EmailAlreadyRegistered(Exception):
    pass

BACKEND_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DB_PATH", BACKEND_DIR / ".." / "data" / "campus_customs.db")).resolve()
MEDIA_URL_PREFIX = "/media/products/"

# Usability improvement (Problem 9, agent/backend #1): list_products() does a
# full catalogue scan plus one inventory query per product, and
# tools.search_catalogue() calls it on nearly every chat turn. Nothing in
# this app writes to the catalogue/inventory at runtime, so a short-lived
# cache is safe and cuts that repeated full scan to once per TTL window —
# faster replies, fewer DB round-trips per tool call.
_CATALOGUE_CACHE_TTL_SECONDS = 60
_catalogue_cache: tuple[float, list[Product]] | None = None


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_product(row: sqlite3.Row, inventory: list[SizeStock]) -> Product:
    filename = Path(row["image_file_path"]).name
    return Product(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        search_tags=json.loads(row["search_tags"]),
        image_file_path=row["image_file_path"],
        image_url=f"{MEDIA_URL_PREFIX}{filename}",
        price=row["price"],
        inventory=inventory,
        total_stock=sum(s.quantity for s in inventory),
    )


def _inventory_for(conn: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size",
        (product_id,),
    ).fetchall()
    return [SizeStock(size=r["size"], quantity=r["quantity"]) for r in rows]


def list_products() -> list[Product]:
    global _catalogue_cache

    now = time.monotonic()
    if _catalogue_cache is not None:
        cached_at, products = _catalogue_cache
        if now - cached_at < _CATALOGUE_CACHE_TTL_SECONDS:
            return products

    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        products = [_row_to_product(row, _inventory_for(conn, row["product_id"])) for row in rows]
    finally:
        conn.close()

    _catalogue_cache = (now, products)
    return products


def get_product(product_id: str) -> Product | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None
        return _row_to_product(row, _inventory_for(conn, product_id))
    finally:
        conn.close()


def _row_to_public_user(row: sqlite3.Row) -> PublicUser:
    return PublicUser(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
    )


def create_user(first_name: str, last_name: str, email: str, password_hash: str) -> PublicUser:
    conn = _connect()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) "
            "VALUES (?, ?, ?, ?, ?)",
            (f"{first_name} {last_name}", email, password_hash, first_name, last_name),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return _row_to_public_user(row)
    except sqlite3.IntegrityError as exc:
        raise EmailAlreadyRegistered(email) from exc
    finally:
        conn.close()


def get_user_by_email(email: str) -> sqlite3.Row | None:
    conn = _connect()
    try:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    conn = _connect()
    try:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()


def save_chat_message(user_id: int, role: str, content: str, products: list[Product] | None = None) -> None:
    conn = _connect()
    try:
        products_json = json.dumps([p.model_dump() for p in products]) if products else None
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )
        conn.commit()
    finally:
        conn.close()


def get_chat_history(user_id: int) -> list[dict]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages "
            "WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
        history = []
        for row in rows:
            history.append(
                {
                    "role": row["role"],
                    "content": row["content"],
                    "products": json.loads(row["products_json"]) if row["products_json"] else [],
                    "created_at": row["created_at"],
                }
            )
        return history
    finally:
        conn.close()

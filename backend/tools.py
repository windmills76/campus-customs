import re

import db
from models import Product

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def _searchable_text(product: Product) -> str:
    return " ".join(
        [
            product.name,
            product.garment_type,
            product.description,
            " ".join(product.colors),
            " ".join(product.search_tags),
        ]
    )


def search_catalogue(query: str, max_results: int = 6) -> list[Product]:
    """Search the real product catalogue by keyword overlap and return matches.

    Use this before describing, pricing, or recommending any product. Returns
    an empty list if nothing in the catalogue matches the query — that means
    the store doesn't carry it, not that the search failed.
    """
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scored: list[tuple[int, Product]] = []
    for product in db.list_products():
        product_tokens = _tokenize(_searchable_text(product))
        score = len(query_tokens & product_tokens)
        if score > 0:
            scored.append((score, product))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [product for _, product in scored[:max_results]]


def get_product_details(product_id: str) -> Product | None:
    """Look up the full details (price, description, colors) for one exact product_id."""
    return db.get_product(product_id)


def get_stock(product_id: str, size: str | None = None) -> dict:
    """Check real inventory for a product, optionally for a specific size.

    Always call this before telling a shopper something is in or out of
    stock. Returns {"found": False} if the product_id doesn't exist.
    """
    product = db.get_product(product_id)
    if product is None:
        return {"found": False}

    if size is not None:
        size_norm = size.strip().upper()
        match = next((s for s in product.inventory if s.size.upper() == size_norm), None)
        quantity = match.quantity if match else 0
        return {
            "found": True,
            "product_id": product_id,
            "size": size_norm,
            "quantity": quantity,
            "in_stock": quantity > 0,
        }

    return {
        "found": True,
        "product_id": product_id,
        "total_stock": product.total_stock,
        "by_size": [{"size": s.size, "quantity": s.quantity} for s in product.inventory],
    }

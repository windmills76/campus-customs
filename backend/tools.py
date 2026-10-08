import re

import db
from models import Product, ProductInfo, ProductInfoResult, StockLookupResult

_WORD_RE = re.compile(r"[a-z0-9]+")


def _singularize(token: str) -> str:
    # Naive but effective for this catalogue's vocabulary: match "hoodies"
    # against a tagged "hoodie", "crewnecks" against "crewneck", etc.
    # Surfaced by a real search_catalogue("hoodies", ...) returning an empty
    # result in output/audit_trail.json even though the catalogue has
    # dozens of hoodies tagged "hoodie" (singular).
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _tokenize(text: str) -> set[str]:
    return {_singularize(token) for token in _WORD_RE.findall(text.lower())}


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


def search_catalogue(
    query: str,
    max_results: int = 6,
    max_price: float | None = None,
    min_price: float | None = None,
) -> list[Product]:
    """Search the real product catalogue by keyword overlap, optionally bounded by price.

    Use this before describing, pricing, or recommending any product. Pass
    max_price/min_price whenever the shopper gives a budget (e.g. "under $70",
    "between $30 and $50") so the real catalogue price filters the results —
    don't try to judge which results fit a budget yourself from the list.
    query can be empty if the shopper only gave a budget with no category
    (e.g. "what's under $35?"). Returns an empty list if nothing in the
    catalogue matches (or nothing fits the budget) — that means the store
    doesn't carry it, not that the search failed.
    """
    query_tokens = _tokenize(query)

    if query_tokens:
        scored: list[tuple[int, Product]] = []
        for product in db.list_products():
            product_tokens = _tokenize(_searchable_text(product))
            score = len(query_tokens & product_tokens)
            if score > 0:
                scored.append((score, product))
        scored.sort(key=lambda item: item[0], reverse=True)
        candidates = [product for _, product in scored]
    elif max_price is not None or min_price is not None:
        candidates = sorted(db.list_products(), key=lambda p: p.price)
    else:
        return []

    if max_price is not None:
        candidates = [p for p in candidates if p.price <= max_price]
    if min_price is not None:
        candidates = [p for p in candidates if p.price >= min_price]

    return candidates[:max_results]


def get_product_info(product_id: str) -> ProductInfoResult:
    """Look up the real description, price, and colors for one exact product_id.

    Always call this before stating a product's description or price — never
    state either from memory. Returns found=False if the product_id doesn't
    exist in the catalogue.
    """
    product = db.get_product(product_id)
    if product is None:
        return ProductInfoResult(found=False)

    return ProductInfoResult(
        found=True,
        info=ProductInfo(
            product_id=product.product_id,
            name=product.name,
            garment_type=product.garment_type,
            description=product.description,
            colors=product.colors,
            price=product.price,
            image_url=product.image_url,
        ),
    )


def get_stock(product_id: str, size: str | None = None) -> StockLookupResult:
    """Check real inventory for a product, by size when a size is given.

    Always call this before telling a shopper something is in or out of
    stock — never guess or assume availability. `by_size` is always the full
    breakdown; pass `size` (e.g. "M", "XL") when the shopper asked about one
    specific size and also read `requested_size_in_stock`/
    `requested_size_quantity` in the response. Returns found=False if the
    product_id doesn't exist.
    """
    product = db.get_product(product_id)
    if product is None:
        return StockLookupResult(found=False, product_id=product_id)

    result = StockLookupResult(
        found=True,
        product_id=product_id,
        total_stock=product.total_stock,
        by_size=product.inventory,
    )

    if size is not None:
        size_norm = size.strip().upper()
        match = next((s for s in product.inventory if s.size.upper() == size_norm), None)
        quantity = match.quantity if match else 0
        result.requested_size = size_norm
        result.requested_size_quantity = quantity
        result.requested_size_in_stock = quantity > 0

    return result

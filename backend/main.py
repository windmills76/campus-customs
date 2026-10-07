import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import db
from models import Product

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

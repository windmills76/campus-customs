import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProducts, imageUrl } from "../api";
import type { Product } from "../types";

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch(() => setError("Couldn't load products. Is the backend running?"))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <div className="page">Loading products…</div>;
  if (error) return <div className="page">{error}</div>;

  return (
    <div className="page page-products">
      <h1>Products</h1>
      <div className="product-grid">
        {products.map((product) => (
          <Link key={product.product_id} to={`/products/${product.product_id}`} className="product-card">
            <img src={imageUrl(product.image_url)} alt={product.name} />
            <h3>{product.name}</h3>
            <p className="product-price">${product.price.toFixed(2)}</p>
            <p className="product-description">{product.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

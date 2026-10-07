import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getProduct, imageUrl } from "../api";
import type { Product } from "../types";

export default function ProductDetail() {
  const { productId } = useParams<{ productId: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    setIsLoading(true);
    getProduct(productId)
      .then(setProduct)
      .catch(() => setError("We couldn't find that product."))
      .finally(() => setIsLoading(false));
  }, [productId]);

  if (isLoading) return <div className="page">Loading…</div>;
  if (error || !product) return <div className="page">{error ?? "Product not found."}</div>;

  return (
    <div className="page page-product-detail">
      <Link to="/products" className="back-link">
        ← Back to Products
      </Link>
      <div className="product-detail-layout">
        <img src={imageUrl(product.image_url)} alt={product.name} className="product-detail-image" />
        <div className="product-detail-info">
          <h1 className="glass-heading">{product.name}</h1>
          <p className="product-price">${product.price.toFixed(2)}</p>
          <p>{product.description}</p>

          <h3>Colors</h3>
          <p>{product.colors.join(", ")}</p>

          <h3>Sizes &amp; Stock</h3>
          <table className="size-table">
            <thead>
              <tr>
                <th>Size</th>
                <th>In Stock</th>
              </tr>
            </thead>
            <tbody>
              {product.inventory.map((item) => (
                <tr key={item.size}>
                  <td>{item.size}</td>
                  <td>
                    {item.quantity > 0 ? (
                      <span className="stock-pill in-stock">In stock · {item.quantity}</span>
                    ) : (
                      <span className="stock-pill out-of-stock">Out of stock</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

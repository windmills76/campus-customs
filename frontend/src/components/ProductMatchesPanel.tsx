import { Link, useLocation } from "react-router-dom";
import { imageUrl } from "../api";
import { useSearchResults } from "../searchResults";

// Renders whatever the chat agent most recently searched for, reusing the
// same .product-grid / .product-card markup as the Products page so these
// cards open the identical single-item detail view (Problem 3) via the
// shared /products/:productId route.
export default function ProductMatchesPanel() {
  const { query, matches, clear } = useSearchResults();
  const { pathname } = useLocation();

  // Hide on a single product's own detail page — showing a grid of other
  // matches above it would bury the page the shopper just navigated to.
  const isProductDetailPage = /^\/products\/[^/]+$/.test(pathname);
  if (matches.length === 0 || isProductDetailPage) return null;

  return (
    <section className="search-results-panel">
      <div className="search-results-header">
        <h2>From chat: &ldquo;{query}&rdquo;</h2>
        <button type="button" className="search-results-clear" onClick={clear}>
          Clear
        </button>
      </div>
      <div className="product-grid">
        {matches.map((product) => (
          <Link key={product.product_id} to={`/products/${product.product_id}`} className="product-card">
            <img src={imageUrl(product.image_url)} alt={product.name} />
            <h3>{product.name}</h3>
            <p className="product-price">${product.price.toFixed(2)}</p>
            <p className="product-description">{product.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}

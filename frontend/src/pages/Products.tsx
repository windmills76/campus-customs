import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getProducts, imageUrl } from "../api";
import type { Product } from "../types";

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchText, setSearchText] = useState("");
  const [garmentType, setGarmentType] = useState("all");

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch(() => setError("Couldn't load products. Is the backend running?"))
      .finally(() => setIsLoading(false));
  }, []);

  // Usability improvement (Problem 9, front-end #1): search + category
  // filter so a 100+ item catalogue doesn't have to be browsed by scrolling.
  const garmentTypes = useMemo(
    () => Array.from(new Set(products.map((p) => p.garment_type))).sort(),
    [products],
  );

  const filteredProducts = useMemo(() => {
    const query = searchText.trim().toLowerCase();
    return products.filter((product) => {
      if (garmentType !== "all" && product.garment_type !== garmentType) return false;
      if (!query) return true;
      const haystack = [product.name, product.description, ...product.search_tags].join(" ").toLowerCase();
      return haystack.includes(query);
    });
  }, [products, searchText, garmentType]);

  if (isLoading) return <div className="page">Loading products…</div>;
  if (error) return <div className="page">{error}</div>;

  return (
    <div className="page page-products">
      <h1 className="glass-heading">Products</h1>

      <div className="product-filters">
        <input
          type="search"
          className="product-search-input"
          placeholder="Search products…"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          aria-label="Search products"
        />
        <select
          className="product-type-select"
          value={garmentType}
          onChange={(e) => setGarmentType(e.target.value)}
          aria-label="Filter by garment type"
        >
          <option value="all">All types</option>
          {garmentTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
        <span className="product-filter-count">
          {filteredProducts.length} of {products.length} products
        </span>
      </div>

      {filteredProducts.length === 0 ? (
        <p className="product-empty-state">No products match your search. Try a different term or type.</p>
      ) : (
        <div className="product-grid">
          {filteredProducts.map((product) => (
            <Link key={product.product_id} to={`/products/${product.product_id}`} className="product-card glass-surface">
              <img src={imageUrl(product.image_url)} alt={product.name} />
              <h3>{product.name}</h3>
              <p className="product-price">${product.price.toFixed(2)}</p>
              <p className="product-description">{product.description}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

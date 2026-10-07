import type { Product } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function imageUrl(path: string): string {
  return `${API_BASE}${path}`;
}

export function getProducts(): Promise<Product[]> {
  return apiFetch<Product[]>("/api/products");
}

export function getProduct(productId: string): Promise<Product> {
  return apiFetch<Product>(`/api/products/${encodeURIComponent(productId)}`);
}

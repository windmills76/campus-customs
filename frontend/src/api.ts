import type { ChatHistoryEntry, ChatTurn, Product, PublicUser } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

function extractErrorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string };
      if (first.msg) return first.msg;
    }
  }
  return fallback;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(extractErrorMessage(body, `Request to ${path} failed: ${res.status}`));
  }
  return res.json() as Promise<T>;
}

function postJson<T>(path: string, data: unknown): Promise<T> {
  return apiFetch<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
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

export interface SignupPayload {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

export function signup(payload: SignupPayload): Promise<PublicUser> {
  return postJson<PublicUser>("/api/auth/signup", payload);
}

export interface LoginPayload {
  email: string;
  password: string;
}

export function login(payload: LoginPayload): Promise<PublicUser> {
  return postJson<PublicUser>("/api/auth/login", payload);
}

export interface PageContext {
  product_id: string | null;
}

export interface ChatPayload {
  message: string;
  user_id: number | null;
  history: ChatTurn[];
  page_context?: PageContext | null;
}

export interface ChatReply {
  reply: string;
  products: Product[];
}

export function sendChat(payload: ChatPayload): Promise<ChatReply> {
  return postJson<ChatReply>("/api/chat", payload);
}

export function getChatHistory(userId: number): Promise<ChatHistoryEntry[]> {
  return apiFetch<ChatHistoryEntry[]>(`/api/chat/history/${userId}`);
}

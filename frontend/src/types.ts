export interface SizeStock {
  size: string;
  quantity: number;
}

export interface PublicUser {
  id: number;
  first_name: string | null;
  last_name: string | null;
  email: string;
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export interface ChatHistoryEntry {
  role: "user" | "assistant";
  content: string;
  products: Product[];
  created_at: string;
}

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_file_path: string;
  image_url: string;
  price: number;
  inventory: SizeStock[];
  total_stock: number;
}

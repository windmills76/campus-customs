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

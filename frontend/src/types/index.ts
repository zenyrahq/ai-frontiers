// Content types
export interface Content {
  id: number;
  title: string;
  summary: string | null;
  content: string | null;
  original_url: string | null;
  source: string | null;
  category: string | null;
  tags: string[] | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
  view_count: number;
  like_count: number;
  is_processed: boolean;
}

// Search types
export interface SearchResult {
  id: number;
  title: string;
  summary: string | null;
  source: string | null;
  category: string | null;
  tags: string[] | null;
  published_at: string | null;
  score: number;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
  search_type: 'hybrid' | 'vector' | 'fulltext' | 'category' | 'tags' | 'popular';
}

export interface SuggestionResponse {
  query: string;
  suggestions: string[];
}

export interface RelatedContentResponse {
  content_id: number;
  related: SearchResult[];
}

// Search params
export interface SearchParams {
  q: string;
  limit?: number;
  vector_weight?: number;
  category?: string;
  source?: string;
  threshold?: number;
}

// Pagination
export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

// API Error
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: string;
  };
}

// Categories
export const CATEGORIES = [
  { value: 'machine_learning', label: '机器学习', icon: '🤖' },
  { value: 'deep_learning', label: '深度学习', icon: '🧠' },
  { value: 'natural_language', label: '自然语言处理', icon: '💬' },
  { value: 'computer_vision', label: '计算机视觉', icon: '👁️' },
  { value: 'reinforcement_learning', label: '强化学习', icon: '🎮' },
  { value: 'generative_ai', label: '生成式AI', icon: '✨' },
  { value: 'robotics', label: '机器人', icon: '🤖' },
  { value: 'other', label: '其他', icon: '📦' },
] as const;

export type CategoryValue = (typeof CATEGORIES)[number]['value'];

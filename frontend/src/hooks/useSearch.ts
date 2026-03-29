import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { SearchResponse, SuggestionResponse, SearchParams } from '@/types';

// Hybrid search
export function useSearch(params: SearchParams) {
  return useQuery<SearchResponse>({
    queryKey: ['search', params],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/search', { params });
      return data;
    },
    enabled: !!params.q && params.q.length > 0,
  });
}

// Vector search
export function useVectorSearch(params: SearchParams) {
  return useQuery<SearchResponse>({
    queryKey: ['vectorSearch', params],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/search/vector', { params });
      return data;
    },
    enabled: !!params.q && params.q.length > 0,
  });
}

// Fulltext search
export function useFulltextSearch(params: SearchParams) {
  return useQuery<SearchResponse>({
    queryKey: ['fulltextSearch', params],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/search/fulltext', { params });
      return data;
    },
    enabled: !!params.q && params.q.length > 0,
  });
}

// Category search
export function useCategorySearch(category: string, limit = 20, offset = 0) {
  return useQuery<SearchResponse>({
    queryKey: ['categorySearch', category, limit, offset],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/search/category/${category}`, {
        params: { limit, offset },
      });
      return data;
    },
    enabled: !!category,
  });
}

// Popular contents
export function usePopularContents(days = 7, limit = 20) {
  return useQuery<SearchResponse>({
    queryKey: ['popularContents', days, limit],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/search/popular', {
        params: { days, limit },
      });
      return data;
    },
  });
}

// Search suggestions
export function useSearchSuggestions(query: string, limit = 5) {
  return useQuery<SuggestionResponse>({
    queryKey: ['suggestions', query, limit],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/search/suggestions', {
        params: { q: query, limit },
      });
      return data;
    },
    enabled: query.length >= 2,
  });
}

// Related contents
export function useRelatedContents(contentId: number, limit = 10) {
  return useQuery<SuggestionResponse>({
    queryKey: ['relatedContents', contentId, limit],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/search/related/${contentId}`, {
        params: { limit },
      });
      return data;
    },
    enabled: !!contentId,
  });
}

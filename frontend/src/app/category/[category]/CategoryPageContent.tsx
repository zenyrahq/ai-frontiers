'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ContentCard, ContentCardSkeleton } from '@/components/content/ContentCard';
import { CATEGORIES } from '@/types';
import { getCategoryLabel } from '@/lib/utils';
import { ArrowLeft } from 'lucide-react';

interface CategoryPageContentProps {
  category: string;
}

export function CategoryPageContent({ category }: CategoryPageContentProps) {
  const categoryInfo = CATEGORIES.find(c => c.value === category);

  const { data, isLoading } = useQuery({
    queryKey: ['category', category],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/search/category/${category}`, {
        params: { limit: 50 },
      });
      return data;
    },
  });

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 bg-gray-50 dark:bg-slate-900">
        {/* Breadcrumb */}
        <div className="bg-white dark:bg-slate-800 border-b">
          <div className="container mx-auto px-4 py-4">
            <Link
              href="/categories"
              className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-primary-600"
            >
              <ArrowLeft className="h-4 w-4" />
              返回分类列表
            </Link>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <div className="text-5xl">{categoryInfo?.icon || '📄'}</div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
                {getCategoryLabel(category)}
              </h1>
              <p className="text-gray-500 dark:text-gray-400">
                {data?.total || 0} 篇内容
              </p>
            </div>
          </div>

          {/* Results */}
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <ContentCardSkeleton key={i} />
              ))}
            </div>
          ) : data?.results?.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data.results.map((content: any) => (
                <ContentCard key={content.id} content={content} showScore />
              ))}
            </div>
          ) : (
            <div className="text-center py-16 bg-white dark:bg-slate-800 rounded-xl">
              <div className="text-gray-400 text-6xl mb-4">📭</div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                暂无内容
              </h3>
              <p className="text-gray-500">
                该分类下暂时没有内容，请稍后再来查看
              </p>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

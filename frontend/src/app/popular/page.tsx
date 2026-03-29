'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ContentCard, ContentCardSkeleton } from '@/components/content/ContentCard';
import { TrendingUp, Clock, Eye, Heart } from 'lucide-react';
import { cn } from '@/lib/utils';

const TIME_OPTIONS = [
  { value: 7, label: '本周' },
  { value: 30, label: '本月' },
  { value: 90, label: '近三月' },
];

export default function PopularPage() {
  const [days, setDays] = useState(7);

  const { data, isLoading } = useQuery({
    queryKey: ['popular', days],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/search/popular', {
        params: { days, limit: 30 },
      });
      return data;
    },
  });

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 bg-gray-50 dark:bg-slate-900">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center gap-3 mb-8">
            <TrendingUp className="h-8 w-8 text-primary-600" />
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
                热门内容
              </h1>
              <p className="text-gray-500 dark:text-gray-400">
                发现最受关注的 AI 研究和技术文章
              </p>
            </div>
          </div>

          {/* Time Filter */}
          <div className="flex items-center gap-2 mb-6">
            <Clock className="h-5 w-5 text-gray-400" />
            <div className="flex gap-2">
              {TIME_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setDays(option.value)}
                  className={cn(
                    'px-4 py-2 rounded-full text-sm font-medium transition-colors',
                    days === option.value
                      ? 'bg-primary-600 text-white'
                      : 'bg-white dark:bg-slate-800 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-700'
                  )}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border">
              <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
                <Eye className="h-4 w-4" />
                总浏览
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {data?.results?.reduce((sum: number, c: any) => sum + (c.view_count || 0), 0) || 0}
              </div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border">
              <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
                <Heart className="h-4 w-4" />
                总点赞
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {data?.results?.reduce((sum: number, c: any) => sum + (c.like_count || 0), 0) || 0}
              </div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border">
              <div className="text-gray-500 text-sm mb-1">内容数</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {data?.total || 0}
              </div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border">
              <div className="text-gray-500 text-sm mb-1">时间范围</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {days} 天
              </div>
            </div>
          </div>

          {/* Results */}
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 9 }).map((_, i) => (
                <ContentCardSkeleton key={i} />
              ))}
            </div>
          ) : data?.results?.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.results.map((content: any, index: number) => (
                <div key={content.id} className="relative">
                  {index < 3 && (
                    <div className="absolute -top-2 -left-2 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold z-10">
                      {index + 1}
                    </div>
                  )}
                  <ContentCard content={content} showScore />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-16 bg-white dark:bg-slate-800 rounded-xl">
              <div className="text-gray-400 text-6xl mb-4">📊</div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                暂无热门内容
              </h3>
              <p className="text-gray-500">
                最近 {days} 天内没有足够的数据来生成热门排行榜
              </p>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

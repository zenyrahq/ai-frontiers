'use client';

import { useSearchParams } from 'next/navigation';
import { useState } from 'react';
import { useSearch } from '@/hooks/useSearch';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { SearchBar } from '@/components/search/SearchBar';
import { ContentCard, ContentCardSkeleton } from '@/components/content/ContentCard';
import { CATEGORIES } from '@/types';
import { Filter, Grid, List } from 'lucide-react';
import { cn } from '@/lib/utils';

export function SearchPageContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const initialCategory = searchParams.get('category') || '';

  const [query, setQuery] = useState(initialQuery);
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const { data, isLoading } = useSearch({
    q: query,
    limit: 20,
    category: selectedCategory || undefined,
  });

  const handleSearch = (newQuery: string) => {
    setQuery(newQuery);
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category === selectedCategory ? '' : category);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 bg-gray-50 dark:bg-slate-900">
        {/* Search Header */}
        <div className="bg-white dark:bg-slate-800 border-b">
          <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              搜索内容
            </h1>
            <SearchBar
              initialQuery={initialQuery}
              onSearch={handleSearch}
              className="max-w-2xl"
            />
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar Filters */}
            <aside className="lg:w-64 shrink-0">
              <div className="bg-white dark:bg-slate-800 rounded-xl border p-4 sticky top-24">
                <div className="flex items-center gap-2 mb-4">
                  <Filter className="h-5 w-5 text-gray-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">筛选</h3>
                </div>

                {/* Categories */}
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    分类
                  </h4>
                  <div className="space-y-2">
                    {CATEGORIES.map((category) => (
                      <button
                        key={category.value}
                        onClick={() => handleCategoryChange(category.value)}
                        className={cn(
                          'w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors',
                          selectedCategory === category.value
                            ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600'
                            : 'hover:bg-gray-50 dark:hover:bg-slate-700 text-gray-700 dark:text-gray-300'
                        )}
                      >
                        <span>{category.icon}</span>
                        <span>{category.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </aside>

            {/* Results */}
            <div className="flex-1">
              {/* Results Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="text-sm text-gray-500">
                  {data ? (
                    <>
                      找到 <span className="font-medium text-gray-900">{data.total}</span> 条结果
                      {query && (
                        <>
                          {' '}
                          关键词 &ldquo;<span className="font-medium">{query}</span>&rdquo;
                        </>
                      )}
                    </>
                  ) : (
                    '输入关键词开始搜索'
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={cn(
                      'p-2 rounded-lg transition-colors',
                      viewMode === 'grid'
                        ? 'bg-primary-50 text-primary-600'
                        : 'hover:bg-gray-100 text-gray-400'
                    )}
                  >
                    <Grid className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={cn(
                      'p-2 rounded-lg transition-colors',
                      viewMode === 'list'
                        ? 'bg-primary-50 text-primary-600'
                        : 'hover:bg-gray-100 text-gray-400'
                    )}
                  >
                    <List className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Results Grid/List */}
              {isLoading ? (
                <div
                  className={cn(
                    'grid gap-6',
                    viewMode === 'grid'
                      ? 'grid-cols-1 md:grid-cols-2'
                      : 'grid-cols-1'
                  )}
                >
                  {Array.from({ length: 6 }).map((_, i) => (
                    <ContentCardSkeleton key={i} />
                  ))}
                </div>
              ) : data && data.results.length > 0 ? (
                <div
                  className={cn(
                    'grid gap-6',
                    viewMode === 'grid'
                      ? 'grid-cols-1 md:grid-cols-2'
                      : 'grid-cols-1'
                  )}
                >
                  {data.results.map((content) => (
                    <ContentCard key={content.id} content={content} showScore />
                  ))}
                </div>
              ) : query ? (
                <div className="text-center py-16">
                  <div className="text-gray-400 text-6xl mb-4">🔍</div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    没有找到结果
                  </h3>
                  <p className="text-gray-500">
                    尝试使用不同的关键词或清除筛选条件
                  </p>
                </div>
              ) : (
                <div className="text-center py-16">
                  <div className="text-gray-400 text-6xl mb-4">🚀</div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    开始搜索
                  </h3>
                  <p className="text-gray-500">
                    输入关键词搜索 AI 论文、技术和新闻
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

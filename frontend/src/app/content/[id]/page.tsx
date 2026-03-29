'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ContentCard } from '@/components/content/ContentCard';
import { formatDateTime, getCategoryLabel, getSourceLabel } from '@/lib/utils';
import type { Content, RelatedContentResponse } from '@/types';
import { ExternalLink, Calendar, Tag, Eye, Heart, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

function useContent(id: number) {
  return useQuery<Content>({
    queryKey: ['content', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/contents/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

function useRelatedContents(id: number) {
  return useQuery<RelatedContentResponse>({
    queryKey: ['related', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/search/related/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export default function ContentPage() {
  const params = useParams();
  const contentId = parseInt(params.id as string, 10);

  const { data: content, isLoading } = useContent(contentId);
  const { data: relatedData } = useRelatedContents(contentId);

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 dark:bg-slate-700 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-1/2 mb-8"></div>
            <div className="space-y-4">
              {Array.from({ length: 10 }).map((_, i) => (
                <div key={i} className="h-4 bg-gray-200 dark:bg-slate-700 rounded"></div>
              ))}
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!content) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <div className="text-center py-16">
            <div className="text-gray-400 text-6xl mb-4">📄</div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              内容不存在
            </h3>
            <Link
              href="/"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              返回首页
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 bg-gray-50 dark:bg-slate-900">
        {/* Breadcrumb */}
        <div className="bg-white dark:bg-slate-800 border-b">
          <div className="container mx-auto px-4 py-4">
            <Link
              href="/"
              className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-primary-600"
            >
              <ArrowLeft className="h-4 w-4" />
              返回首页
            </Link>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <article className="lg:col-span-2">
              <div className="bg-white dark:bg-slate-800 rounded-xl border p-6 md:p-8">
                {/* Title */}
                <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-4">
                  {content.title}
                </h1>

                {/* Meta */}
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-6 pb-6 border-b">
                  {content.source && (
                    <span className="flex items-center gap-1">
                      <ExternalLink className="h-4 w-4" />
                      {getSourceLabel(content.source)}
                    </span>
                  )}
                  {content.category && (
                    <span className="px-2 py-1 bg-gray-100 dark:bg-slate-700 rounded-full">
                      {getCategoryLabel(content.category)}
                    </span>
                  )}
                  {content.published_at && (
                    <span className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {formatDateTime(content.published_at)}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    {content.view_count} 次浏览
                  </span>
                  <span className="flex items-center gap-1">
                    <Heart className="h-4 w-4" />
                    {content.like_count} 次点赞
                  </span>
                </div>

                {/* Summary */}
                {content.summary && (
                  <div className="mb-6 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                    <h3 className="text-sm font-semibold text-primary-600 mb-2">
                      内容摘要
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300">{content.summary}</p>
                  </div>
                )}

                {/* Content */}
                {content.content && (
                  <div className="prose dark:prose-invert max-w-none">
                    <div
                      dangerouslySetInnerHTML={{ __html: content.content }}
                      className="text-gray-700 dark:text-gray-300 leading-relaxed"
                    />
                  </div>
                )}

                {/* Tags */}
                {content.tags && content.tags.length > 0 && (
                  <div className="mt-8 pt-6 border-t">
                    <div className="flex items-center gap-2 mb-3">
                      <Tag className="h-4 w-4 text-gray-400" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        标签
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {content.tags.map((tag) => (
                        <Link
                          key={tag}
                          href={`/search?tags=${tag}`}
                          className="px-3 py-1 text-sm bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-primary-50 dark:hover:bg-primary-900/30 hover:text-primary-600 transition-colors"
                        >
                          {tag}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}

                {/* Original Link */}
                {content.original_url && (
                  <div className="mt-6 pt-6 border-t">
                    <a
                      href={content.original_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                    >
                      <ExternalLink className="h-4 w-4" />
                      查看原文
                    </a>
                  </div>
                )}
              </div>
            </article>

            {/* Sidebar */}
            <aside className="lg:col-span-1">
              {/* Related Contents */}
              {relatedData && relatedData.related.length > 0 && (
                <div className="bg-white dark:bg-slate-800 rounded-xl border p-4 sticky top-24">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                    相关内容
                  </h3>
                  <div className="space-y-4">
                    {relatedData.related.slice(0, 5).map((item) => (
                      <Link
                        key={item.id}
                        href={`/content/${item.id}`}
                        className="block p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors"
                      >
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2 mb-1">
                          {item.title}
                        </h4>
                        <div className="text-xs text-gray-500">
                          相似度: {(item.score * 100).toFixed(0)}%
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </aside>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

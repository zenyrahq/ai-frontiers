'use client';

import Link from 'next/link';
import { Eye, Heart, ExternalLink } from 'lucide-react';
import type { SearchResult } from '@/types';
import { formatRelativeTime, getCategoryLabel, getSourceLabel } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface ContentCardProps {
  content: SearchResult;
  showScore?: boolean;
  className?: string;
}

export function ContentCard({ content, showScore = false, className }: ContentCardProps) {
  return (
    <article
      className={cn(
        'group bg-white dark:bg-slate-800 rounded-xl border border-gray-200 dark:border-slate-700 p-5 hover:shadow-lg transition-all duration-300',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <Link href={`/content/${content.id}`} className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 transition-colors line-clamp-2">
            {content.title}
          </h3>
        </Link>
        {showScore && (
          <span className="shrink-0 px-2 py-1 bg-primary-50 dark:bg-primary-900/30 text-primary-600 text-xs font-medium rounded-full">
            {(content.score * 100).toFixed(0)}%
          </span>
        )}
      </div>

      {/* Summary */}
      {content.summary && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">
          {content.summary}
        </p>
      )}

      {/* Meta */}
      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
        {/* Source */}
        {content.source && (
          <span className="flex items-center gap-1">
            <ExternalLink className="h-3 w-3" />
            {getSourceLabel(content.source)}
          </span>
        )}

        {/* Category */}
        {content.category && (
          <span className="px-2 py-0.5 bg-gray-100 dark:bg-slate-700 rounded-full">
            {getCategoryLabel(content.category)}
          </span>
        )}

        {/* Published Time */}
        {content.published_at && (
          <span>{formatRelativeTime(content.published_at)}</span>
        )}
      </div>

      {/* Tags */}
      {content.tags && content.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {content.tags.slice(0, 3).map((tag) => (
            <Link
              key={tag}
              href={`/search?tags=${tag}`}
              className="px-2 py-1 text-xs bg-primary-50 dark:bg-primary-900/30 text-primary-600 rounded-full hover:bg-primary-100 dark:hover:bg-primary-900/50 transition-colors"
            >
              {tag}
            </Link>
          ))}
          {content.tags.length > 3 && (
            <span className="px-2 py-1 text-xs text-gray-500">
              +{content.tags.length - 3}
            </span>
          )}
        </div>
      )}
    </article>
  );
}

// Loading skeleton
export function ContentCardSkeleton() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-gray-200 dark:border-slate-700 p-5 animate-pulse">
      <div className="h-6 bg-gray-200 dark:bg-slate-700 rounded w-3/4 mb-3"></div>
      <div className="space-y-2 mb-4">
        <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded"></div>
        <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-5/6"></div>
        <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-4/6"></div>
      </div>
      <div className="flex gap-4">
        <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-20"></div>
        <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-24"></div>
      </div>
    </div>
  );
}

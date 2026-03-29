'use client';

import Link from 'next/link';
import { usePopularContents } from '@/hooks/useSearch';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { SearchBar } from '@/components/search/SearchBar';
import { ContentCard, ContentCardSkeleton } from '@/components/content/ContentCard';
import { CATEGORIES } from '@/types';
import { ArrowRight, TrendingUp, Clock, Zap } from 'lucide-react';

export default function HomePage() {
  const { data: popularData, isLoading } = usePopularContents(7, 6);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-accent-700 text-white">
          <div className="absolute inset-0 bg-grid-white/10 bg-[size:30px_30px]"></div>
          <div className="container mx-auto px-4 py-20 relative">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-4xl md:text-6xl font-bold mb-6 animate-fade-in">
                探索 AI 前沿
              </h1>
              <p className="text-lg md:text-xl text-white/80 mb-8 animate-fade-in">
                收集全球 AI 最新研究、技术和动态，为研究者和开发者提供一站式信息平台
              </p>
              <div className="animate-fade-in">
                <SearchBar
                  placeholder="搜索论文、技术、新闻..."
                  className="max-w-2xl mx-auto"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="bg-white dark:bg-slate-900 py-8 border-b">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600">1000+</div>
                <div className="text-sm text-gray-500">论文收录</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600">50+</div>
                <div className="text-sm text-gray-500">信息来源</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600">实时</div>
                <div className="text-sm text-gray-500">更新频率</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600">智能</div>
                <div className="text-sm text-gray-500">语义搜索</div>
              </div>
            </div>
          </div>
        </section>

        {/* Categories Section */}
        <section className="py-16 bg-gray-50 dark:bg-slate-800">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                浏览分类
              </h2>
              <Link
                href="/categories"
                className="flex items-center gap-1 text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                查看全部
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {CATEGORIES.slice(0, 8).map((category) => (
                <Link
                  key={category.value}
                  href={`/category/${category.value}`}
                  className="group bg-white dark:bg-slate-700 p-6 rounded-xl border border-gray-200 dark:border-slate-600 hover:shadow-lg hover:border-primary-300 transition-all"
                >
                  <div className="text-4xl mb-3">{category.icon}</div>
                  <div className="font-medium text-gray-900 dark:text-white group-hover:text-primary-600">
                    {category.label}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* Popular Section */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-primary-600" />
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  本周热门
                </h2>
              </div>
              <Link
                href="/popular"
                className="flex items-center gap-1 text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                查看更多
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {isLoading
                ? Array.from({ length: 6 }).map((_, i) => <ContentCardSkeleton key={i} />)
                : popularData?.results.map((content) => (
                    <ContentCard key={content.id} content={content} showScore />
                  ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-gray-50 dark:bg-slate-800">
          <div className="container mx-auto px-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white text-center mb-12">
              核心功能
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-white dark:bg-slate-700 p-6 rounded-xl text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Zap className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  智能搜索
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  基于向量语义搜索和全文检索的混合搜索，精准找到你需要的内容
                </p>
              </div>
              <div className="bg-white dark:bg-slate-700 p-6 rounded-xl text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Clock className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  实时更新
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  持续监控全球AI信息源，确保你获取最新的研究成果和技术动态
                </p>
              </div>
              <div className="bg-white dark:bg-slate-700 p-6 rounded-xl text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  智能推荐
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  AI 驱动的内容分析和推荐，帮你发现相关领域的重要研究
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

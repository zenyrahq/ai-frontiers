'use client';

import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { CATEGORIES } from '@/types';
import { ArrowRight } from 'lucide-react';

export default function CategoriesPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 bg-gray-50 dark:bg-slate-900">
        <div className="container mx-auto px-4 py-12">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              浏览分类
            </h1>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              按研究领域浏览 AI 论文和技术文章，发现你感兴趣的内容
            </p>
          </div>

          {/* Categories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {CATEGORIES.map((category) => (
              <Link
                key={category.value}
                href={`/category/${category.value}`}
                className="group bg-white dark:bg-slate-800 rounded-xl border border-gray-200 dark:border-slate-700 p-6 hover:shadow-lg hover:border-primary-300 transition-all"
              >
                <div className="text-5xl mb-4">{category.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 transition-colors">
                  {category.label}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  探索 {category.label} 领域的最新研究和进展
                </p>
                <div className="flex items-center text-primary-600 text-sm font-medium">
                  查看内容
                  <ArrowRight className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            ))}
          </div>

          {/* Info Section */}
          <div className="mt-16 bg-white dark:bg-slate-800 rounded-xl border p-8">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              关于分类
            </h2>
            <div className="grid md:grid-cols-2 gap-6 text-gray-600 dark:text-gray-400">
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                  🤖 机器学习 & 深度学习
                </h3>
                <p className="text-sm">
                  涵盖神经网络架构、优化算法、训练技术等核心机器学习研究
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                  💬 自然语言处理
                </h3>
                <p className="text-sm">
                  大语言模型、文本生成、机器翻译、问答系统等 NLP 前沿研究
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                  👁️ 计算机视觉
                </h3>
                <p className="text-sm">
                  图像识别、目标检测、图像分割、视觉 Transformer 等研究
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                  ✨ 生成式 AI
                </h3>
                <p className="text-sm">
                  GAN、Diffusion Models、文本到图像生成等前沿生成技术
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

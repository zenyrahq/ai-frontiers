'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Search, Menu, X, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur-md dark:bg-slate-900/80">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
              AI Frontiers
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href="/"
              className="text-sm font-medium text-gray-600 hover:text-primary-600 transition-colors"
            >
              首页
            </Link>
            <Link
              href="/search"
              className="text-sm font-medium text-gray-600 hover:text-primary-600 transition-colors"
            >
              搜索
            </Link>
            <Link
              href="/categories"
              className="text-sm font-medium text-gray-600 hover:text-primary-600 transition-colors"
            >
              分类
            </Link>
            <Link
              href="/popular"
              className="text-sm font-medium text-gray-600 hover:text-primary-600 transition-colors"
            >
              热门
            </Link>
          </nav>

          {/* Search Button */}
          <div className="flex items-center gap-4">
            <Link
              href="/search"
              className="flex items-center gap-2 px-4 py-2 bg-primary-50 hover:bg-primary-100 rounded-full text-primary-600 transition-colors"
            >
              <Search className="h-4 w-4" />
              <span className="hidden sm:inline text-sm font-medium">搜索</span>
            </Link>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div
          className={cn(
            'md:hidden overflow-hidden transition-all duration-300',
            isMenuOpen ? 'max-h-48 pb-4' : 'max-h-0'
          )}
        >
          <nav className="flex flex-col gap-2">
            <Link
              href="/"
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg"
              onClick={() => setIsMenuOpen(false)}
            >
              首页
            </Link>
            <Link
              href="/search"
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg"
              onClick={() => setIsMenuOpen(false)}
            >
              搜索
            </Link>
            <Link
              href="/categories"
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg"
              onClick={() => setIsMenuOpen(false)}
            >
              分类
            </Link>
            <Link
              href="/popular"
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg"
              onClick={() => setIsMenuOpen(false)}
            >
              热门
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}

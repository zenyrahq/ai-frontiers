import Link from 'next/link';
import { Github, Twitter, Mail } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t bg-gray-50 dark:bg-slate-900">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              AI Frontiers
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              收集全球AI前沿信息，为研究者、开发者和爱好者提供最新、最全面的AI领域动态。
            </p>
            <div className="flex gap-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Twitter className="h-5 w-5" />
              </a>
              <a
                href="mailto:contact@aifrontiers.com"
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
              快速链接
            </h4>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/search"
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  搜索内容
                </Link>
              </li>
              <li>
                <Link
                  href="/categories"
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  浏览分类
                </Link>
              </li>
              <li>
                <Link
                  href="/popular"
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  热门内容
                </Link>
              </li>
            </ul>
          </div>

          {/* API */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
              开发者
            </h4>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/api/docs"
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  API 文档
                </Link>
              </li>
              <li>
                <Link
                  href="/api/status"
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  服务状态
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-8 border-t">
          <p className="text-center text-sm text-gray-500">
            © {new Date().getFullYear()} AI Frontiers. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

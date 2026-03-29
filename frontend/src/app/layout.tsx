import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AI Frontiers - AI前沿信息平台',
  description: '收集全球AI前沿信息，提供最新、最全面的AI领域动态',
  keywords: ['AI', '人工智能', '机器学习', '深度学习', '论文', '研究'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

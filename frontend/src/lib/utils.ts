import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { zhCN } from 'date-fns/locale';

// Merge Tailwind classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format date
export function formatDate(date: string | Date | null): string {
  if (!date) return '';
  const d = typeof date === 'string' ? parseISO(date) : date;
  return format(d, 'yyyy-MM-dd', { locale: zhCN });
}

// Format relative time
export function formatRelativeTime(date: string | Date | null): string {
  if (!date) return '';
  const d = typeof date === 'string' ? parseISO(date) : date;
  return formatDistanceToNow(d, { addSuffix: true, locale: zhCN });
}

// Format datetime
export function formatDateTime(date: string | Date | null): string {
  if (!date) return '';
  const d = typeof date === 'string' ? parseISO(date) : date;
  return format(d, 'yyyy-MM-dd HH:mm', { locale: zhCN });
}

// Truncate text
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length) + '...';
}

// Get category label
export function getCategoryLabel(category: string | null): string {
  const categoryMap: Record<string, string> = {
    machine_learning: '机器学习',
    deep_learning: '深度学习',
    natural_language: '自然语言处理',
    computer_vision: '计算机视觉',
    reinforcement_learning: '强化学习',
    generative_ai: '生成式AI',
    robotics: '机器人',
    other: '其他',
  };
  return categoryMap[category || ''] || category || '未分类';
}

// Get category icon
export function getCategoryIcon(category: string | null): string {
  const iconMap: Record<string, string> = {
    machine_learning: '🤖',
    deep_learning: '🧠',
    natural_language: '💬',
    computer_vision: '👁️',
    reinforcement_learning: '🎮',
    generative_ai: '✨',
    robotics: '🤖',
    other: '📦',
  };
  return iconMap[category || ''] || '📄';
}

// Get source label
export function getSourceLabel(source: string | null): string {
  const sourceMap: Record<string, string> = {
    arxiv: 'arXiv',
    github: 'GitHub',
    huggingface: 'Hugging Face',
    openai: 'OpenAI',
    anthropic: 'Anthropic',
    google_ai: 'Google AI',
    meta_ai: 'Meta AI',
  };
  return sourceMap[source || ''] || source || '未知来源';
}

// Debounce function
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

const {
  cn,
  formatDate,
  formatRelativeTime,
  formatDateTime,
  truncate,
  getCategoryLabel,
  getCategoryIcon,
  getSourceLabel,
  debounce,
} = require('@/lib/utils')

describe('Utils', () => {
  describe('cn (class merger)', () => {
    it('should merge class names', () => {
      expect(cn('foo', 'bar')).toBe('foo bar')
    })

    it('should handle conditional classes', () => {
      expect(cn('foo', false && 'bar', 'baz')).toBe('foo baz')
    })

    it('should merge tailwind classes correctly', () => {
      expect(cn('px-2', 'px-4')).toBe('px-4')
    })
  })

  describe('formatDate', () => {
    it('should return empty string for null', () => {
      expect(formatDate(null)).toBe('')
    })

    it('should format ISO date string', () => {
      const result = formatDate('2024-01-15T10:00:00Z')
      expect(result).toMatch(/2024/)
    })

    it('should format Date object', () => {
      const date = new Date('2024-01-15T10:00:00Z')
      const result = formatDate(date)
      expect(result).toMatch(/2024/)
    })
  })

  describe('formatRelativeTime', () => {
    it('should return empty string for null', () => {
      expect(formatRelativeTime(null)).toBe('')
    })

    it('should return relative time string', () => {
      const date = new Date()
      date.setDate(date.getDate() - 1)
      const result = formatRelativeTime(date)
      expect(result).toBeTruthy()
    })
  })

  describe('formatDateTime', () => {
    it('should return empty string for null', () => {
      expect(formatDateTime(null)).toBe('')
    })

    it('should format datetime', () => {
      const result = formatDateTime('2024-01-15T10:30:00Z')
      expect(result).toMatch(/2024/)
      expect(result).toMatch(/-01-15/)
    })
  })

  describe('truncate', () => {
    it('should return original text if shorter than length', () => {
      expect(truncate('hello', 10)).toBe('hello')
    })

    it('should truncate text and add ellipsis', () => {
      expect(truncate('hello world', 5)).toBe('hello...')
    })

    it('should handle exact length', () => {
      expect(truncate('hello', 5)).toBe('hello')
    })
  })

  describe('getCategoryLabel', () => {
    it('should return label for known category', () => {
      expect(getCategoryLabel('machine_learning')).toBe('机器学习')
      expect(getCategoryLabel('deep_learning')).toBe('深度学习')
    })

    it('should return original category for unknown', () => {
      expect(getCategoryLabel('unknown_category')).toBe('unknown_category')
    })

    it('should return default for null', () => {
      expect(getCategoryLabel(null)).toBe('未分类')
    })
  })

  describe('getCategoryIcon', () => {
    it('should return emoji for known category', () => {
      expect(getCategoryIcon('machine_learning')).toBe('🤖')
      expect(getCategoryIcon('deep_learning')).toBe('🧠')
    })

    it('should return default emoji for unknown', () => {
      expect(getCategoryIcon('unknown')).toBe('📄')
    })

    it('should return default for null', () => {
      expect(getCategoryIcon(null)).toBe('📄')
    })
  })

  describe('getSourceLabel', () => {
    it('should return label for known source', () => {
      expect(getSourceLabel('arxiv')).toBe('arXiv')
      expect(getSourceLabel('github')).toBe('GitHub')
    })

    it('should return original source for unknown', () => {
      expect(getSourceLabel('unknown_source')).toBe('unknown_source')
    })

    it('should return default for null', () => {
      expect(getSourceLabel(null)).toBe('未知来源')
    })
  })

  describe('debounce', () => {
    jest.useFakeTimers()

    it('should debounce function calls', () => {
      const mockFn = jest.fn()
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn('a')
      debouncedFn('b')
      debouncedFn('c')

      expect(mockFn).not.toHaveBeenCalled()

      jest.advanceTimersByTime(100)

      expect(mockFn).toHaveBeenCalledTimes(1)
      expect(mockFn).toHaveBeenCalledWith('c')
    })

    it('should clear previous timeout', () => {
      const mockFn = jest.fn()
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn('first')
      jest.advanceTimersByTime(50)
      debouncedFn('second')
      jest.advanceTimersByTime(100)

      expect(mockFn).toHaveBeenCalledTimes(1)
      expect(mockFn).toHaveBeenCalledWith('second')
    })
  })
})

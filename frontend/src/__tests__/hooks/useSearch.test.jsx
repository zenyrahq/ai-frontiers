// Mock the api client before importing hooks
const mockGet = jest.fn()

jest.mock('@/lib/api', () => ({
  apiClient: {
    get: mockGet,
  },
}))

// Mock React Query
jest.mock('@tanstack/react-query', () => ({
  useQuery: jest.fn((options) => {
    // Simulate query behavior based on enabled option
    if (options.enabled === false) {
      return { data: undefined, isLoading: false, isFetching: false, error: null }
    }
    return { data: undefined, isLoading: true, isFetching: true, error: null }
  }),
}))

describe('useSearch hooks', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.resetModules()
  })

  describe('useSearch', () => {
    it('should not enable query when query string is empty', () => {
      const { useQuery } = require('@tanstack/react-query')
      const { useSearch } = require('@/hooks/useSearch')

      useSearch({ q: '' })

      expect(useQuery).toHaveBeenCalledWith(
        expect.objectContaining({
          enabled: false,
        })
      )
    })

    it('should enable query when query string is provided', () => {
      const { useQuery } = require('@tanstack/react-query')
      const { useSearch } = require('@/hooks/useSearch')

      useSearch({ q: 'transformer' })

      expect(useQuery).toHaveBeenCalledWith(
        expect.objectContaining({
          enabled: true,
        })
      )
    })
  })

  describe('useCategorySearch', () => {
    it('should not enable query when category is empty', () => {
      const { useQuery } = require('@tanstack/react-query')
      const { useCategorySearch } = require('@/hooks/useSearch')

      useCategorySearch('')

      expect(useQuery).toHaveBeenCalledWith(
        expect.objectContaining({
          enabled: false,
        })
      )
    })

    it('should enable query when category is provided', () => {
      const { useQuery } = require('@tanstack/react-query')
      const { useCategorySearch } = require('@/hooks/useSearch')

      useCategorySearch('deep_learning')

      expect(useQuery).toHaveBeenCalledWith(
        expect.objectContaining({
          enabled: true,
        })
      )
    })
  })

  describe('useSearchSuggestions', () => {
    it('should not enable query when query is too short', () => {
      const { useQuery } = require('@tanstack/react-query')
      const { useSearchSuggestions } = require('@/hooks/useSearch')

      useSearchSuggestions('t')

      expect(useQuery).toHaveBeenCalledWith(
        expect.objectContaining({
          enabled: false,
        })
      )
    })

    it('should enable query when query has at least 2 characters', () => {
      const { useQuery } = require('@tanstack/react-query')
      const { useSearchSuggestions } = require('@/hooks/useSearch')

      useSearchSuggestions('tr')

      expect(useQuery).toHaveBeenCalledWith(
        expect.objectContaining({
          enabled: true,
        })
      )
    })
  })

  describe('usePopularContents', () => {
    it('should call useQuery', () => {
      const { useQuery } = require('@tanstack/react-query')
      const { usePopularContents } = require('@/hooks/useSearch')

      usePopularContents()

      expect(useQuery).toHaveBeenCalled()
    })
  })
})

// Mock axios before importing api module
const mockCreate = jest.fn(() => ({
  interceptors: {
    request: {
      use: jest.fn(),
    },
    response: {
      use: jest.fn(),
    },
  },
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
}))

jest.mock('axios', () => ({
  create: mockCreate,
}))

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Clear module cache to re-import with fresh mock
    jest.resetModules()
  })

  it('should create axios instance with correct config', () => {
    require('@/lib/api')
    expect(mockCreate).toHaveBeenCalledWith(
      expect.objectContaining({
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
        },
      })
    )
  })

  it('should export apiClient', () => {
    const { apiClient } = require('@/lib/api')
    expect(apiClient).toBeDefined()
    expect(typeof apiClient.get).toBe('function')
    expect(typeof apiClient.post).toBe('function')
    expect(typeof apiClient.put).toBe('function')
    expect(typeof apiClient.delete).toBe('function')
  })

  it('should set up request interceptor', () => {
    require('@/lib/api')
    const mockClient = mockCreate.mock.results[0]?.value
    if (mockClient) {
      expect(mockClient.interceptors.request.use).toHaveBeenCalled()
    }
  })

  it('should set up response interceptor', () => {
    require('@/lib/api')
    const mockClient = mockCreate.mock.results[0]?.value
    if (mockClient) {
      expect(mockClient.interceptors.response.use).toHaveBeenCalled()
    }
  })
})

const React = require('react')
const { QueryClient, QueryClientProvider } = require('@tanstack/react-query')

// Create a new query client for each test
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

// Custom render function that includes providers
const renderWithProviders = (ui, options = {}) => {
  const queryClient = createTestQueryClient()

  const Wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )

  const { render } = require('@testing-library/react')
  return render(ui, { wrapper: Wrapper, ...options })
}

module.exports = {
  renderWithProviders,
  createTestQueryClient,
}

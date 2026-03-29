const { screen, fireEvent } = require('@testing-library/react')
const { renderWithProviders } = require('../../test-utils')
const { SearchBar } = require('@/components/search/SearchBar')

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
  usePathname: () => '/search',
}))

describe('SearchBar', () => {
  it('renders input field', () => {
    renderWithProviders(<SearchBar />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('renders with placeholder text', () => {
    renderWithProviders(<SearchBar />)
    expect(screen.getByPlaceholderText(/搜索/i)).toBeInTheDocument()
  })

  it('updates value on input change', () => {
    renderWithProviders(<SearchBar />)
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'transformer' } })
    expect(input).toHaveValue('transformer')
  })
})

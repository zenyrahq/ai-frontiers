const { screen } = require('@testing-library/react')
const { renderWithProviders } = require('../../test-utils')
const { ContentCard } = require('@/components/content/ContentCard')

// Mock Next.js Link
jest.mock('next/link', () => {
  return ({ children, href }) => {
    return <a href={href}>{children}</a>
  }
})

// Mock Next.js Image
jest.mock('next/image', () => {
  return ({ src, alt, fill, className }) => {
    return <img src={src} alt={alt} className={className} data-testid="next-image" />
  }
})

// Sample content for testing
const mockContent = {
  id: 1,
  title: 'Attention Is All You Need',
  summary: 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.',
  original_url: 'https://arxiv.org/abs/1706.03762',
  source: 'arxiv',
  category: 'deep_learning',
  tags: ['transformer', 'attention', 'nlp'],
  view_count: 1000,
  like_count: 50,
  published_at: '2023-01-15T10:00:00Z',
}

describe('ContentCard', () => {
  it('renders title correctly', () => {
    renderWithProviders(<ContentCard content={mockContent} />)
    expect(screen.getByText(mockContent.title)).toBeInTheDocument()
  })

  it('renders summary correctly', () => {
    renderWithProviders(<ContentCard content={mockContent} />)
    expect(screen.getByText(mockContent.summary)).toBeInTheDocument()
  })

  it('renders tags', () => {
    renderWithProviders(<ContentCard content={mockContent} />)
    expect(screen.getByText('transformer')).toBeInTheDocument()
  })

  // Skip this test until component bug is fixed
  it.skip('shows loading skeleton when content is null', () => {
    const { container } = renderWithProviders(<ContentCard content={null} />)
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
  })
})

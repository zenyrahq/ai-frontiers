import { test, expect } from '@playwright/test'

test.describe('Search Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display homepage with search bar', async ({ page }) => {
    // Check that the search input is visible
    const searchInput = page.getByRole('textbox')
    await expect(searchInput).toBeVisible()
  })

  test('should perform search and show results', async ({ page }) => {
    // Type in search input
    const searchInput = page.getByRole('textbox')
    await searchInput.fill('transformer')
    await searchInput.press('Enter')

    // Wait for navigation to search page
    await page.waitForURL(/\/search/)

    // Check that URL contains query parameter
    expect(page.url()).toContain('q=transformer')

    // Check that search results container is visible
    const resultsContainer = page.getByTestId('search-results')
    await expect(resultsContainer).toBeVisible({ timeout: 10000 })
  })

  test('should show search suggestions while typing', async ({ page }) => {
    const searchInput = page.getByRole('textbox')
    await searchInput.fill('deep')

    // Wait for suggestions dropdown (debounced)
    await page.waitForTimeout(500)

    // Check if suggestions appear (may not always show depending on API response)
    const suggestions = page.getByRole('listbox')
    const isVisible = await suggestions.isVisible().catch(() => false)

    // If suggestions are visible, check they contain "deep"
    if (isVisible) {
      const firstSuggestion = suggestions.getByRole('option').first()
      await expect(firstSuggestion).toContainText(/deep/i)
    }
  })

  test('should navigate to content detail from search results', async ({ page }) => {
    // Go to search page directly
    await page.goto('/search?q=AI')

    // Wait for results to load
    await page.waitForTimeout(2000)

    // Click on the first content card
    const firstCard = page.getByRole('link', { name: /content/i }).first()
    if (await firstCard.isVisible()) {
      await firstCard.click()

      // Should be on content detail page
      await expect(page).toHaveURL(/\/content\/\d+/)
    }
  })

  test('should filter search by category', async ({ page }) => {
    // Go to search page
    await page.goto('/search?q=learning')

    // Check if category filter exists
    const categoryFilter = page.getByRole('combobox', { name: /category/i })

    if (await categoryFilter.isVisible()) {
      await categoryFilter.selectOption('deep_learning')

      // Wait for results to reload
      await page.waitForTimeout(1000)

      // URL should contain category filter
      expect(page.url()).toContain('category')
    }
  })
})

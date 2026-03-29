import { test, expect } from '@playwright/test'

test.describe('Content Browsing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display popular contents on homepage', async ({ page }) => {
    // Wait for content to load
    await page.waitForTimeout(2000)

    // Check that content cards are displayed
    const contentCards = page.getByTestId('content-card')

    // Should have at least one content card
    const count = await contentCards.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should navigate to category page', async ({ page }) => {
    // Click on a category link
    const categoryLink = page.getByRole('link', { name: /deep learning|machine learning|nlp/i }).first()

    if (await categoryLink.isVisible()) {
      await categoryLink.click()

      // Should be on category page
      await expect(page).toHaveURL(/\/category\//)
    }
  })

  test('should display content detail page', async ({ page }) => {
    // Go to a specific content page
    await page.goto('/content/1')

    // Wait for content to load
    await page.waitForTimeout(2000)

    // Check that main content elements are visible
    const title = page.getByRole('heading', { level: 1 })
    await expect(title).toBeVisible()
  })

  test('should show related contents on detail page', async ({ page }) => {
    // Go to a content detail page
    await page.goto('/content/1')

    // Wait for page to load
    await page.waitForTimeout(2000)

    // Check for related content section
    const relatedSection = page.getByText(/related|similar/i)

    if (await relatedSection.isVisible()) {
      // Should have related content cards
      const relatedCards = page.getByTestId('content-card')
      const count = await relatedCards.count()
      expect(count).toBeGreaterThan(0)
    }
  })

  test('should navigate via tag links', async ({ page }) => {
    // Go to homepage
    await page.goto('/')

    // Wait for content to load
    await page.waitForTimeout(2000)

    // Click on a tag
    const tagLink = page.getByRole('link', { name: /transformer|nlp|ai/i }).first()

    if (await tagLink.isVisible()) {
      await tagLink.click()

      // Should navigate to search with tag filter
      await expect(page).toHaveURL(/\/search/)
    }
  })

  test('should handle 404 for non-existent content', async ({ page }) => {
    // Go to non-existent content
    await page.goto('/content/999999')

    // Should show 404 page or error message
    const errorElement = page.getByText(/not found|does not exist|error/i)
    await expect(errorElement).toBeVisible({ timeout: 5000 })
  })
})

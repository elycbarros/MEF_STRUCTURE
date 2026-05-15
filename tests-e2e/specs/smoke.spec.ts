import { test, expect } from '@playwright/test';

test.describe('Smoke Tests - MEF STRUCTURAL', () => {
  
  test('should load the landing page', async ({ page }) => {
    await page.goto('/');
    // Assuming the landing page has a link or text that mentions ATLAS or MEF
    // Let's check for "Mestre" as a common keyword in the navigation if available
    // or just the page title for now.
    await expect(page).toHaveTitle(/Atlas Structural Engine/i);
  });

  test('should navigate to the Mestre module', async ({ page }) => {
    await page.goto('/mestre');
    
    // Check for the breadcrumb "Mestre"
    const breadcrumb = page.locator('header').getByText('Mestre', { exact: true });
    await expect(breadcrumb).toBeVisible();

    // Check for the dynamic analysis alert
    const analysisAlert = page.getByText('Análise Dinâmica Ativa');
    await expect(analysisAlert).toBeVisible();
  });

  test('should display the memorial area', async ({ page }) => {
    await page.goto('/mestre');
    
    // Check if the Memorial section is rendered
    await expect(page.getByText(/Memorial Descritivo/i).first()).toBeVisible();
  });
});

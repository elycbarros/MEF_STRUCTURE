import { test, expect } from '@playwright/test';

test.describe('Structural Validation - MEF Engine', () => {
  
  test('should calculate a simple beam and display results', async ({ page }) => {
    await page.goto('/mestre');
    
    // 1. Ensure we are in the "Vigas" module
    // The default might be something else, let's make sure by clicking "Vigas" in the sidebar
    const vigaButton = page.getByRole('button', { name: /Viga Isolada/i });
    if (await vigaButton.isVisible()) {
      await vigaButton.click();
    }

    // 2. Wait for the Playground to load
    await expect(page.getByText('Laboratório de Vigas (MEF 3D)')).toBeVisible();

    // 3. Update the span length (L)
    const spanInput = page.getByLabel(/Vão Total/i);
    await spanInput.fill('10.0');
    // Blur to trigger potential updates
    await spanInput.blur();

    // 4. Click the calculate button
    const calculateButton = page.getByRole('button', { name: /Analisar Estrutura/i });
    await calculateButton.click();

    // 5. Verify results
    // Wait for the button to go back to normal (indicating calculation finished)
    await expect(calculateButton).toHaveText(/Analisar Estrutura/i, { timeout: 20000 });

    // Check if diagrams are visible - using specific locators to avoid ambiguity with the memorial
    const diagramContainer = page.locator('#mestre-diagrams');
    await expect(diagramContainer).toBeVisible({ timeout: 15000 });
    
    await expect(diagramContainer.getByText(/Momento Fletor/i)).toBeVisible();
    await expect(diagramContainer.getByText(/Esforço Cortante/i)).toBeVisible();
    await expect(diagramContainer.getByText(/Linha Elástica/i)).toBeVisible();

    // Check if the memorial has calculation steps
    await expect(page.getByText(/Memorial Descritivo/i).first()).toBeVisible();
  });

  test('should show error for invalid inputs', async ({ page }) => {
    await page.goto('/mestre');
    
    // Set a negative length to trigger an error
    const spanInput = page.getByLabel(/Vão Total/i);
    await spanInput.fill('0'); 
    await spanInput.blur();

    const calculateButton = page.getByRole('button', { name: /Analisar Estrutura/i });
    await calculateButton.click();

    // We expect an error message to appear eventually
    await expect(page.locator('div').filter({ hasText: /Erro/i }).first()).toBeVisible({ timeout: 15000 });
  });
});

import { test, expect } from '@playwright/test';

test.describe('Structural Validation - Columns', () => {
  
  test('should calculate a column with biaxial bending', async ({ page }) => {
    await page.goto('/mestre');
    
    // 1. Navigate to "Pilar" module
    const columnButton = page.getByRole('button', { name: /Pilar \(Flexo\)/i });
    await columnButton.click();

    // 2. Verify module loaded
    await expect(page.getByText('Laboratório de Pilares')).toBeVisible();

    // 3. Set geometry and loads
    await page.getByLabel(/Largura b \(m\)/i).fill('0.20');
    await page.getByLabel(/Altura h \(m\)/i).fill('0.40');
    await page.getByLabel(/Carga axial Nd \(kN\)/i).fill('1000');
    await page.getByLabel(/Mxd \(kNm\)/i).fill('50');
    await page.getByLabel(/Myd \(kNm\)/i).fill('30');

    // 4. Calculate
    const calculateButton = page.getByRole('button', { name: /Dimensionar Pilar/i });
    await calculateButton.click();

    // 5. Verify results (Diagrams and Metrics)
    await expect(calculateButton).toHaveText(/Dimensionar Pilar/i, { timeout: 30000 });
    
    // Check for Interaction Diagrams
    await expect(page.getByText(/Interação N x Mx/i)).toBeVisible();
    await expect(page.getByText(/Interação N x My/i)).toBeVisible();
    
    // Check for Fiber Map
    await expect(page.getByText(/Mapa de Tensões/i)).toBeVisible();
    
    // Check slenderness metrics
    await expect(page.getByText(/λx \(Esbeltez\)/i)).toBeVisible();
  });
});

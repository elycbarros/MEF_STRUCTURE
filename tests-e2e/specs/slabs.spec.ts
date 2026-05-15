import { test, expect } from '@playwright/test';

test.describe('Structural Validation - Slabs', () => {
  
  test('should calculate a standard solid slab', async ({ page }) => {
    await page.goto('/mestre');
    
    // 1. Navigate to "Laje" module
    const slabButton = page.getByRole('button', { name: /^Laje$/i });
    await slabButton.click();

    // 2. Verify module loaded
    await expect(page.getByText('Laboratório de Lajes')).toBeVisible();

    // 3. Set geometry
    await page.getByLabel(/Vão Lx/i).fill('4.0');
    await page.getByLabel(/Vão Ly/i).fill('5.0');
    await page.getByLabel(/Espessura h/i).fill('0.12');
    await page.getByLabel(/Carga q/i).fill('5.0');

    // 4. Calculate
    const calculateButton = page.getByRole('button', { name: /Analisar Laje/i });
    await calculateButton.click();

    // 5. Verify results in memorial
    await expect(calculateButton).toHaveText(/Analisar Laje/i, { timeout: 20000 });
    await expect(page.getByText(/Memorial Descritivo/i).first()).toBeVisible();
    await expect(page.getByText(/Passo 1/i)).toBeVisible();
  });

  test('should calculate an advanced raft slab (Radier)', async ({ page }) => {
    await page.goto('/mestre');
    
    // 1. Navigate to "Radier Avançado" module
    const raftButton = page.getByRole('button', { name: /Radier Avançado/i });
    await raftButton.click();

    // 2. Verify module loaded
    await expect(page.getByText('Radier Avançado e Lajes em Solo')).toBeVisible();

    // 3. Set geometry and soil properties
    await page.getByLabel(/^Lx \(m\)$/i).fill('8.0');
    await page.getByLabel(/^Ly \(m\)$/i).fill('8.0');
    await page.getByLabel(/Mod. Reação kv/i).fill('20.0');

    // 4. Add a column load
    const addColumnButton = page.getByRole('button', { name: /Adicionar Pilar/i });
    await addColumnButton.click();
    
    // Fill the newly added column Fz
    const fzInput = page.getByLabel(/Fz \(kN\)/i).first();
    await fzInput.fill('800');

    // 5. Calculate
    const calculateButton = page.getByRole('button', { name: /Analisar Sistema/i });
    await calculateButton.click();

    // 6. Verify MEF results
    await expect(calculateButton).toHaveText(/Analisar Sistema/i, { timeout: 30000 });
    
    const resultsContainer = page.locator('#advanced-slab-results');
    await expect(resultsContainer).toBeVisible();
    await expect(resultsContainer.getByText(/Recalque Máx/i)).toBeVisible();
    await expect(resultsContainer.getByText(/Momento Mx/i)).toBeVisible();
    
    // Check Status Geotécnico
    await expect(resultsContainer.getByText(/Status Geotécnico/i)).toBeVisible();
  });
});

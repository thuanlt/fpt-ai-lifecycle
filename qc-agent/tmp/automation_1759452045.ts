import { test, expect } from '@playwright/test';

test('Navigate to FPT Cloud Marketplace and login', async ({ page }) => {
  // Navigate to the FPT Cloud Marketplace homepage
  await page.goto('https://marketplace.fptcloud.com/en');

  // Click the 'Sign in/Sign up' button
  await page.locator('button').filter({ hasText: 'Sign in/Sign up' }).click();

  // Click the 'Continue with FPT ID' button
  await page.getByRole('button', { name: 'Continue with FPT ID' }).click();

  // Fill in the username
  await page.getByRole('textbox', { name: 'Username/Email' }).fill('yovex23766@daxiake.com');

  // Fill in the password
  await page.getByRole('textbox', { name: 'Password' }).fill('Ncp@12345678');

  // Click the 'Sign in' button
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Verify that the user is logged in by checking for user-specific elements
  await expect(page.locator('text=$48.16')).toBeVisible();
});
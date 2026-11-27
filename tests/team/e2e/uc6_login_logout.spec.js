// UC6: Users sign in and out (both roles). Supports FR5 and FR6 (who can see what).
const { test, expect, reset, login } = require('./helpers');

test.describe('UC6 Login and logout', () => {
  test.beforeEach(async () => {
    reset();
  });

  test('UC6-M main: an employee signs in and sees the dashboard', async ({ page }) => {
    await login(page, 'emp1');

    await expect(page).toHaveURL(/127\.0\.0\.1:8000\/$/);
    await expect(page.getByRole('heading', { name: 'Welcome, emp1!' })).toBeVisible();
  });

  test('UC6-A1 alternative: an admin signs in and lands on the admin site', async ({ page }) => {
    await login(page, 'admin1');

    await expect(page).toHaveURL(/\/admin\/$/);
  });

  test('UC6-A2 alternative: logging out ends the session', async ({ page }) => {
    await login(page, 'emp1');
    await page.locator('a.topbar-logout').click();

    await expect(page).toHaveURL(/\/accounts\/login\//);
    await page.goto('/balance/'); // postcondition: protected page needs a new login
    await expect(page).toHaveURL(/\/accounts\/login\//);
  });

  test('UC6-E1 exception: a wrong password is refused with a message', async ({ page }) => {
    await login(page, 'emp1', 'wrong-password');

    await expect(page.locator('.alert-danger')).toContainText('Please enter a correct username and password');
    await expect(page).toHaveURL(/\/accounts\/login\//);
    await page.goto('/balance/');
    await expect(page).toHaveURL(/\/accounts\/login\//);
  });

  test('UC6-E2 exception: an unknown user is refused with the same message', async ({ page }) => {
    await login(page, 'nobody');

    await expect(page.locator('.alert-danger')).toContainText('Please enter a correct username and password');
    await expect(page).toHaveURL(/\/accounts\/login\//);
  });
});
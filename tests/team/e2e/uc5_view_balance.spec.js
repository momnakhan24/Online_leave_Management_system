// UC5: Employee checks the leave balance after the admin decides (shared record, both workflows).
const { test, expect, reset, state, create, login, logout } = require('./helpers');

async function adminApprove(page) {
  await login(page, 'admin1');
  await page.goto('/leaves/admin/');
  page.once('dialog', (dialog) => dialog.accept());
  await page.locator('a[title="Approve"]').first().click();
  await expect(page.locator('.alert')).toContainText('approved successfully');
  await logout(page);
}

test.describe('UC5 View balance', () => {
  test.beforeEach(async () => {
    reset();
  });

  test('UC5-M main: the balance page shows 17 after a 3-day annual leave is approved', async ({ page }) => {
    create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await adminApprove(page);
    await login(page, 'emp1');
    await page.goto('/balance/');

    await expect(page.locator('.stat-value').nth(0)).toHaveText('17');
    expect(state().balances.emp1.annual).toBe(17);
  });

  test('UC5-A1 alternative: after a rejection the balance stays 20', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await login(page, 'admin1');
    await page.goto('/leaves/admin/');
    await page.locator(`tr:has(#rejectModal${id}) button[title="Reject"]`).click();
    await page.locator(`#rejectionReason${id}`).fill('Not possible');
    await page.locator(`#rejectModal${id}`).getByRole('button', { name: 'Reject Leave' }).click();
    await expect(page.locator('.alert')).toContainText('rejected');
    await logout(page);

    await login(page, 'emp1');
    await page.goto('/balance/');
    await expect(page.locator('.stat-value').nth(0)).toHaveText('20');
  });

  test('UC5-A2 alternative: approved sick leave reduces the sick balance to 8', async ({ page }) => {
    create('emp1', 'Sick Leave', '2027-03-01', '2027-03-02');
    await adminApprove(page);
    await login(page, 'emp1');
    await page.goto('/balance/');

    await expect(page.locator('.stat-value').nth(1)).toHaveText('8');
    await expect(page.locator('.stat-value').nth(0)).toHaveText('20');
  });

  test('UC5-E1 exception: an anonymous visitor is sent to the login page', async ({ page }) => {
    await page.goto('/balance/');

    await expect(page).toHaveURL(/\/accounts\/login\//);
  });

  test('UC5-E2 exception: an employee cannot open the admin list', async ({ page }) => {
    await login(page, 'emp1');
    const response = await page.goto('/leaves/admin/');

    expect(response.status()).toBe(404);
  });
});
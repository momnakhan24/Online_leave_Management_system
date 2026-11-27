// UC4: Admin rejects a Pending leave application with a reason (Workflow 2). FR8, BR3, BR4.
const { test, expect, reset, state, create, login, logout } = require('./helpers');

async function openAdminList(page) {
  await login(page, 'admin1');
  await page.goto('/leaves/admin/');
}

async function rejectWith(page, id, reason) {
  await page.locator(`tr:has(#rejectModal${id}) button[title="Reject"]`).click();
  const modal = page.locator(`#rejectModal${id}`);
  await expect(modal).toBeVisible();
  if (reason) {
    await modal.locator('textarea').fill(reason);
  }
  await modal.getByRole('button', { name: 'Reject Leave' }).click();
}

test.describe('UC4 Reject leave', () => {
  test.beforeEach(async () => {
    reset();
  });

  test('UC4-M main: admin rejects with a reason', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await openAdminList(page);
    await rejectWith(page, id, 'Team is short-staffed');

    await expect(page.locator('.alert')).toContainText('Leave application rejected.');
    const s = state();
    expect(s.applications[0]).toMatchObject({ status: 'Rejected', reason: 'Team is short-staffed' });
    expect(s.balances.emp1.annual).toBe(20);
  });

  test('UC4-A1 alternative: the employee sees the reason on the application', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await openAdminList(page);
    await rejectWith(page, id, 'Busy period');
    await expect(page.locator('.alert')).toContainText('rejected');

    await logout(page);
    await login(page, 'emp1');
    await page.goto(`/leave/${id}/`);
    await expect(page.getByText('Busy period')).toBeVisible();
    await expect(page.getByText('Rejected').first()).toBeVisible();
  });

  test('UC4-A2 alternative: rejecting sick leave leaves every balance unchanged', async ({ page }) => {
    const id = create('emp1', 'Sick Leave', '2027-03-01', '2027-03-02');
    await openAdminList(page);
    await rejectWith(page, id, 'Please bring a certificate');

    await expect(page.locator('.alert')).toContainText('rejected');
    expect(state().balances.emp1).toEqual({ annual: 20, sick: 10, other: 5 });
  });

  test('UC4-E1 exception: a rejection without a reason is blocked', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await openAdminList(page);
    await rejectWith(page, id, '');

    await expect(page.locator(`#rejectionReason${id}:invalid`)).toHaveCount(1);
    expect(state().applications[0].status).toBe('Pending');
  });

  test('UC4-E2 exception: admin closes the dialog with Cancel, nothing changes', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await openAdminList(page);
    await page.locator(`tr:has(#rejectModal${id}) button[title="Reject"]`).click();
    const modal = page.locator(`#rejectModal${id}`);
    await expect(modal).toBeVisible();
    await modal.getByRole('button', { name: 'Cancel' }).click();

    await expect(modal).toBeHidden();
    expect(state().applications[0].status).toBe('Pending');
  });
});
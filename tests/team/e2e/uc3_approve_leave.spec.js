// UC3: Admin approves a Pending leave application (Workflow 2). FR6, FR7, FR9, BR1, BR3.
const { test, expect, reset, state, create, login } = require('./helpers');

async function openAdminList(page) {
  await login(page, 'admin1'); // admin login lands on /admin/
  await page.goto('/leaves/admin/');
}

test.describe('UC3 Approve leave', () => {
  test.beforeEach(async () => {
    reset();
  });

  test('UC3-M main: admin approves, the balance is deducted', async ({ page }) => {
    create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await openAdminList(page);
    page.once('dialog', (dialog) => dialog.accept());
    await page.locator('tr', { hasText: 'emp1' }).locator('a[title="Approve"]').click();

    await expect(page.locator('.alert')).toContainText('Leave application approved successfully.');
    const s = state();
    expect(s.applications[0].status).toBe('Approved');
    expect(s.balances.emp1.annual).toBe(17); // 3 days deducted
    expect(s.notifications).toBe(1);
  });

  test('UC3-A1 alternative: approving sick leave deducts the sick balance only', async ({ page }) => {
    create('emp1', 'Sick Leave', '2027-03-01', '2027-03-02');
    await openAdminList(page);
    page.once('dialog', (dialog) => dialog.accept());
    await page.locator('tr', { hasText: 'emp1' }).locator('a[title="Approve"]').click();

    await expect(page.locator('.alert')).toContainText('approved successfully');
    const b = state().balances.emp1;
    expect(b.sick).toBe(8);
    expect(b.annual).toBe(20);
  });

  test('UC3-A2 alternative: admin filters by Pending and approves', async ({ page }) => {
    create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03', 'Approved');
    create('emp2', 'Annual Leave', '2027-04-01', '2027-04-02', 'Pending');
    await openAdminList(page);
    await page.locator('#status').selectOption('Pending');
    await page.getByRole('button', { name: 'Apply' }).click();

    await expect(page.locator('tbody tr')).toHaveCount(1);
    page.once('dialog', (dialog) => dialog.accept());
    await page.locator('a[title="Approve"]').click();

    await expect(page.locator('.alert')).toContainText('approved successfully');
    const s = state();
    expect(s.applications.map((a) => a.status)).toEqual(['Approved', 'Approved']);
    expect(s.balances.emp2.annual).toBe(18);
  });

  test('UC3-E1 exception: admin dismisses the confirmation, nothing changes', async ({ page }) => {
    create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await openAdminList(page);
    page.once('dialog', (dialog) => dialog.dismiss());
    await page.locator('tr', { hasText: 'emp1' }).locator('a[title="Approve"]').click();

    const s = state();
    expect(s.applications[0].status).toBe('Pending');
    expect(s.balances.emp1.annual).toBe(20);
  });

  test('UC3-E2 exception: an already processed application cannot be approved again', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03', 'Rejected');
    await openAdminList(page);
    await page.goto(`/leaves/admin/${id}/approve/`);

    await expect(page.locator('.alert')).toContainText('This leave application has already been processed.');
    const s = state();
    expect(s.applications[0].status).toBe('Rejected');
    expect(s.balances.emp1.annual).toBe(20);
  });
});
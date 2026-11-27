// UC2: Employee cancels a Pending leave application (Workflow 1). FR4, BR3.
const { test, expect, reset, state, create, login, fillApplyForm } = require('./helpers');

test.describe('UC2 Cancel leave', () => {
  test.beforeEach(async ({ page }) => {
    reset();
    await login(page, 'emp1');
  });

  test('UC2-M main: employee cancels a Pending application', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await page.goto(`/leave/${id}/`);
    page.once('dialog', (dialog) => dialog.accept());
    await page.getByRole('link', { name: 'Cancel Application' }).click();

    await expect(page.locator('.alert')).toContainText('Leave application cancelled successfully.');
    const s = state();
    expect(s.applications[0].status).toBe('Cancelled');
    expect(s.balances.emp1.annual).toBe(20);
  });

  test('UC2-A1 alternative: employee changes their mind and dismisses the confirmation', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await page.goto(`/leave/${id}/`);
    page.once('dialog', (dialog) => dialog.dismiss());
    await page.getByRole('link', { name: 'Cancel Application' }).click();

    expect(state().applications[0].status).toBe('Pending');
  });

  test('UC2-A2 alternative: cancelled dates can be applied for again', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await page.goto(`/leave/${id}/`);
    page.once('dialog', (dialog) => dialog.accept());
    await page.getByRole('link', { name: 'Cancel Application' }).click();
    await expect(page.locator('.alert')).toContainText('cancelled successfully');

    await fillApplyForm(page, { start: '2027-03-01', end: '2027-03-03' });
    await page.getByRole('button', { name: 'Submit Application' }).click();

    await expect(page.locator('.alert')).toContainText('Leave application submitted successfully.');
    const statuses = state().applications.map((a) => a.status).sort();
    expect(statuses).toEqual(['Cancelled', 'Pending']);
  });

  test('UC2-E1 exception: an Approved application cannot be cancelled', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03', 'Approved');
    await page.goto(`/leave/${id}/`);
    await expect(page.getByRole('link', { name: 'Cancel Application' })).toHaveCount(0);

    await page.goto(`/leave/${id}/cancel/`); // direct address
    await expect(page.locator('.alert')).toContainText('Only pending leave applications can be cancelled.');
    expect(state().applications[0].status).toBe('Approved');
  });

  test('UC2-E2 exception: another employee cannot open or cancel the application', async ({ page }) => {
    const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await page.goto('/logout/');
    await login(page, 'emp2');

    const detail = await page.goto(`/leave/${id}/`);
    expect(detail.status()).toBe(404);
    const cancel = await page.goto(`/leave/${id}/cancel/`);
    expect(cancel.status()).toBe(404);
    expect(state().applications[0].status).toBe('Pending');
  });
});
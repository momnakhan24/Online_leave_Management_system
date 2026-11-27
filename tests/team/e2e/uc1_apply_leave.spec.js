// UC1: Employee applies for leave (Workflow 1). Requirements FR1, FR2, FR3; rules BR1, BR2.
// Main flow, 2 alternative flows (A1, A2) and 2 exception flows (E1, E2).
const { test, expect, reset, state, create, login, fillApplyForm } = require('./helpers');

test.describe('UC1 Apply for leave', () => {
  test.beforeEach(async ({ page }) => {
    reset();
    await login(page, 'emp1');
  });

  test('UC1-M main: employee submits a valid annual leave application', async ({ page }) => {
    await fillApplyForm(page, { start: '2027-03-01', end: '2027-03-03' });
    await page.getByRole('button', { name: 'Submit Application' }).click();

    await expect(page).toHaveURL(/127\.0\.0\.1:8000\/$/);
    await expect(page.locator('.alert')).toContainText('Leave application submitted successfully.');
    const s = state();
    expect(s.applications).toHaveLength(1);
    expect(s.applications[0]).toMatchObject({ user: 'emp1', status: 'Pending', start: '2027-03-01', end: '2027-03-03' });
    expect(s.balances.emp1.annual).toBe(20); // postcondition: balance unchanged until approval
  });

  test('UC1-A1 alternative: employee applies for sick leave', async ({ page }) => {
    await fillApplyForm(page, { type: 'Sick Leave', start: '2027-03-01', end: '2027-03-02', reason: 'Flu' });
    await page.getByRole('button', { name: 'Submit Application' }).click();

    await expect(page.locator('.alert')).toContainText('Leave application submitted successfully.');
    const s = state();
    expect(s.applications[0]).toMatchObject({ type: 'Sick Leave', status: 'Pending' });
    expect(s.balances.emp1.sick).toBe(10);
  });

  test('UC1-A2 alternative: one-day leave (start equals end)', async ({ page }) => {
    await fillApplyForm(page, { start: '2027-03-10', end: '2027-03-10' });
    await page.getByRole('button', { name: 'Submit Application' }).click();

    await expect(page.locator('.alert')).toContainText('Leave application submitted successfully.');
    const s = state();
    expect(s.applications).toHaveLength(1);
    expect(s.applications[0]).toMatchObject({ start: '2027-03-10', end: '2027-03-10' });
  });

  test('UC1-E1 exception: overlapping dates are refused with an explanation', async ({ page }) => {
    create('emp1', 'Annual Leave', '2027-03-01', '2027-03-05');

    await fillApplyForm(page, { start: '2027-03-03', end: '2027-03-04' });
    await page.getByRole('button', { name: 'Submit Application' }).click();

    await expect(page.locator('.alert')).toContainText('overlaps with these dates');
    await expect(page).toHaveURL(/\/apply\/$/);
    expect(state().applications).toHaveLength(1); // postcondition: nothing new stored
  });

  test('UC1-E2 exception: missing reason blocks the submission', async ({ page }) => {
    await fillApplyForm(page, { start: '2027-03-01', end: '2027-03-02', reason: '' });
    await page.getByRole('button', { name: 'Submit Application' }).click();

    await expect(page).toHaveURL(/\/apply\/$/);
    await expect(page.locator('#message:invalid')).toHaveCount(1);
    expect(state().applications).toHaveLength(0);
  });
});
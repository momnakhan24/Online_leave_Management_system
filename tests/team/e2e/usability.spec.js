// Usability tests, one per workflow.
//  U1 (Workflow 1, apply for leave): a rule violation is refused with an explanation, then the employee
//     corrects the dates using the KEYBOARD ONLY and submits. Focus order and keyboard submit are asserted.
//  U2 (Workflow 2, approve leave): the admin completes the approval task and sees the confirmation.
const { test, expect, reset, state, create, login } = require('./helpers');

// Presses Tab until the target gets focus. A date field has several internal tab stops
// (month, day, year), so up to 4 presses are allowed before the target must have focus.
async function tabTo(page, selector) {
  const target = page.locator(selector);
  for (let i = 0; i < 4; i += 1) {
    await page.keyboard.press('Tab');
    if (await target.evaluate((el) => el === document.activeElement)) {
      return;
    }
  }
  await expect(target).toBeFocused();
}

test.describe('Usability', () => {
  test.beforeEach(async () => {
    reset();
  });

  test('U1 apply for leave: clear error, then keyboard-only correction and submit', async ({ page }) => {
    create('emp1', 'Annual Leave', '2027-03-01', '2027-03-05'); // an existing Pending application
    await login(page, 'emp1');
    await page.goto('/apply/');

    // Step 1: dates that overlap the existing application are refused with an explanation.
    await page.getByLabel('Leave Type').selectOption('Annual Leave');
    await page.locator('#startDate').fill('2027-03-03');
    await page.locator('#endDate').fill('2027-03-04');
    await page.locator('#message').fill('Family event');
    await page.getByRole('button', { name: 'Submit Application' }).click();
    const alert = page.locator('.alert');
    await expect(alert).toContainText('overlaps');
    await expect(alert).toContainText('dates'); // the message names what to change: the dates
    expect(state().applications).toHaveLength(1);

    // Step 2: correct the dates with the keyboard only. First reach the leave type field.
    let reached = false;
    for (let i = 0; i < 80 && !reached; i += 1) {
      await page.keyboard.press('Tab');
      reached = await page.locator('#leaveType').evaluate((el) => el === document.activeElement);
    }
    expect(reached).toBe(true); // the form can be reached with Tab

    await expect(page.locator('#leaveType')).toBeFocused();
    await page.keyboard.press('ArrowDown'); // first real option: Annual Leave
    await tabTo(page, '#startDate');
    await page.keyboard.type('03082027'); // month, day, year (en-US)
    await tabTo(page, '#endDate');
    await page.keyboard.type('03092027');
    await tabTo(page, '#message');
    await page.keyboard.type('Family event');
    await tabTo(page, 'a.btn-outline-secondary');   // the Cancel link comes before Submit
    await tabTo(page, 'button[type="submit"]');
    await expect(page.getByRole('button', { name: 'Submit Application' })).toBeFocused();
    await page.keyboard.press('Enter'); // submit with the keyboard

    await expect(page.locator('.alert')).toContainText('Leave application submitted successfully.');
    const s = state();
    expect(s.applications).toHaveLength(2);
    expect(s.applications[1]).toMatchObject({ start: '2027-03-08', end: '2027-03-09', status: 'Pending' });
  });

  test('U2 approve leave: the admin completes the task and sees the confirmation', async ({ page }) => {
    create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
    await login(page, 'admin1');
    await page.goto('/leaves/admin/');
    page.once('dialog', (dialog) => dialog.accept());
    await page.locator('tr', { hasText: 'emp1' }).locator('a[title="Approve"]').click();

    await expect(page.locator('.alert')).toContainText('Leave application approved successfully.');
    expect(state().applications[0].status).toBe('Approved');
  });
});

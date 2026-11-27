const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const base = require('@playwright/test');

const PASSWORD = 'Test@12345';

// The pages load Bootstrap, icons and Chart.js from a CDN. Tests serve those files from
// node_modules instead (same versions) and block every other outside request, so the
// tests do not depend on the internet connection.
const test = base.test.extend({
  context: async ({ context }, use) => {
    await context.route(/^https?:\/\/(?!127\.0\.0\.1)/, async (route) => {
      const url = new URL(route.request().url());
      const match = url.hostname === 'cdn.jsdelivr.net'
        && url.pathname.match(/^\/npm\/((?:@[^/]+\/)?[^@/]+)@[^/]+\/(.+)$/);
      if (match) {
        let file = path.join('node_modules', match[1], match[2]);
        if (!fs.existsSync(file)) {
          file = file.replace(/\.min\.(js|css)$/, '.$1'); // the CDN minifies on the fly
        }
        if (fs.existsSync(file)) {
          return route.fulfill({ path: file });
        }
      }
      return route.abort();
    });
    await use(context);
  },
});
const expect = base.expect;

// Runs scripts/e2e_state.py and returns its JSON output (preconditions and postconditions).
function py(...args) {
  const out = execFileSync('python', ['scripts/e2e_state.py', ...args], { encoding: 'utf8' });
  return JSON.parse(out.trim().split(/\r?\n/).pop());
}

const reset = () => py('reset');
const state = () => py('state');
const create = (user, type, start, end, status = 'Pending') =>
  py('create', user, type, start, end, status).id;

async function login(page, username, password = PASSWORD) {
  await page.goto('/accounts/login/');
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign In' }).click();
}

async function fillApplyForm(page, { type = 'Annual Leave', start, end, reason = 'Family event' }) {
  await page.goto('/apply/');
  await page.getByLabel('Leave Type').selectOption(type);
  await page.locator('#startDate').fill(start);
  await page.locator('#endDate').fill(end);
  await page.locator('#message').fill(reason);
}

module.exports = { test, expect, PASSWORD, reset, state, create, login, fillApplyForm };
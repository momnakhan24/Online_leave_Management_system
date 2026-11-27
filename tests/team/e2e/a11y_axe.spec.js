// Full axe-core scan of the key screen of each use case. The scan results are saved as JSON
// (evidence/reports/axe/) for the findings table. Set AXE_LABEL=after for the second run.
const fs = require('fs');
const path = require('path');
const { AxeBuilder } = require('@axe-core/playwright');
const { test, expect, reset, create, login } = require('./helpers');

const LABEL = process.env.AXE_LABEL || 'before';
const OUT = path.join('evidence', 'reports', 'axe');

const SCREENS = [
  { name: 'login', user: null, path: () => '/accounts/login/' },
  { name: 'apply', user: 'emp1', path: () => '/apply/' },
  { name: 'balance', user: 'emp1', path: () => '/balance/' },
  { name: 'admin_list', user: 'admin1', path: () => '/leaves/admin/' },
  { name: 'detail', user: 'emp1', path: (id) => `/leave/${id}/` },
];

test.describe(`axe scan (${LABEL})`, () => {
  for (const screen of SCREENS) {
    test(`axe scan: ${screen.name}`, async ({ page }) => {
      reset();
      const id = create('emp1', 'Annual Leave', '2027-03-01', '2027-03-03');
      if (screen.user) {
        await login(page, screen.user);
      }
      await page.goto(screen.path(id));
      const results = await new AxeBuilder({ page }).analyze();

      fs.mkdirSync(OUT, { recursive: true });
      fs.writeFileSync(path.join(OUT, `axe_${screen.name}_${LABEL}.json`), JSON.stringify({
        screen: screen.name, url: page.url(), label: LABEL,
        violations: results.violations.map((v) => ({
          id: v.id, impact: v.impact, help: v.help,
          elements: v.nodes.map((n) => n.target.join(' ')),
        })),
      }, null, 2));
      const elements = results.violations.reduce((sum, v) => sum + v.nodes.length, 0);
      console.log(`${screen.name} [${LABEL}]: ${results.violations.length} rule violations, ${elements} elements`);

      expect(results.passes.length).toBeGreaterThan(0); // the scan ran; findings are reported, not failed
    });
  }
});
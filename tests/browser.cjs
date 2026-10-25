/* Pruebas de navegador con servidor y Excel temporales propios. */
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const { spawn } = require('node:child_process');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');

const root = path.resolve(__dirname, '..');
const output = process.env.TEST_OUTPUT_DIR || path.join(root, 'test-results');
const port = Number(process.env.TEST_PORT || 5083);
const base = `http://127.0.0.1:${port}`;
const sizes = [[1440, 900], [1024, 768], [768, 1024], [390, 844], [320, 667]];
const report = { views: [], problems: [], runtimeErrors: [], workflows: [] };

async function main() {
  await fs.mkdir(output, { recursive: true });
  const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'dataconnect-ui-'));
  const server = spawn(process.env.PYTHON_PATH || 'python', ['-m', 'flask', '--app', 'app', 'run', '--port', String(port), '--no-debugger', '--no-reload'], {
    cwd: root, stdio: 'ignore', windowsHide: true,
    env: { ...process.env, DATACONNECT_DEMO: '1', DATACONNECT_DATA_FILE: path.join(temporary, 'contacts.xlsx') },
  });
  let serverError;
  server.on('error', error => { serverError = error; });
  let browser;
  try {
    let ready = false;
    for (let attempt = 0; attempt < 80; attempt++) {
      if (serverError) throw serverError;
      try { ready = (await fetch(base + '/login')).status === 200; } catch { /* El servidor todavía está iniciando. */ }
      if (ready) break;
      await new Promise(resolve => setTimeout(resolve, 150));
    }
    assert(ready, 'El servidor temporal no pudo iniciar. Activá el entorno Python con las dependencias instaladas.');
    browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}) });
    for (const [width, height] of sizes) {
      const context = await browser.newContext({ viewport: { width, height }, reducedMotion: 'reduce', hasTouch: width < 600 });
      const page = await context.newPage();
      page.on('pageerror', error => report.runtimeErrors.push(error.message));
      page.on('requestfailed', request => report.runtimeErrors.push(request.url() + ': ' + request.failure()?.errorText));
      const inspect = async name => {
        await page.evaluate(() => document.fonts.ready);
        const metrics = await page.evaluate(() => {
          const ids = [...document.querySelectorAll('[id]')].map(element => element.id);
          const labelsMissing = [...document.querySelectorAll('input:not([type="hidden"]), select, textarea')].filter(element => !element.labels?.length && !element.getAttribute('aria-label')).map(element => element.name);
          return {
            overflow: document.documentElement.scrollWidth > innerWidth,
            viewportCorrect: innerWidth === visualViewport.width,
            duplicateIds: ids.filter((id, index) => ids.indexOf(id) !== index),
            labelsMissing,
            brokenReferences: [...document.querySelectorAll('[aria-labelledby], [aria-describedby]')].filter(element => ['aria-labelledby', 'aria-describedby'].some(attribute => (element.getAttribute(attribute) || '').split(/\s+/).filter(Boolean).some(id => !document.getElementById(id)))).length,
            h1Count: document.querySelectorAll('h1').length,
            fontLoaded: [...document.fonts].some(face => face.family === 'Inter' && face.status === 'loaded'),
            externalResources: performance.getEntriesByType('resource').filter(entry => !entry.name.startsWith(location.origin)).map(entry => entry.name),
          };
        });
        if (metrics.overflow || !metrics.viewportCorrect || metrics.duplicateIds.length || metrics.labelsMissing.length || metrics.brokenReferences || metrics.h1Count !== 1 || !metrics.fontLoaded || metrics.externalResources.length) report.problems.push({ name, width, ...metrics });
        if (width === 1440 || width === 390 || width === 320) await page.screenshot({ path: path.join(output, `${name}-${width}.png`), fullPage: true });
        report.views.push({ name, width, height, ...metrics });
      };
      await page.goto(base + '/login');
      await inspect('login');
      await page.getByLabel('Usuario', { exact: true }).fill('demo');
      await page.getByLabel('Contraseña', { exact: true }).fill('dataconnect-demo');
      await page.getByRole('button', { name: 'Entrar al directorio' }).click();
      await page.waitForURL(base + '/contactos');
      await inspect('contactos');
      const firstContact = await page.locator('.contact-identity a').first().getAttribute('href');
      await page.goto(base + '/contactos/nuevo');
      await inspect('crear');
      await page.goto(base + firstContact);
      await inspect('detalle');
      await page.getByRole('link', { name: 'Editar contacto', exact: true }).click();
      await inspect('editar');
      await page.goto(base + '/estadisticas');
      await inspect('estadisticas');
      await page.goto(base + '/contactos?q=sin-coincidencias');
      await inspect('sin-resultados');
      await page.goto(base + '/contactos?favoritos=1');
      assert.equal(await page.locator('.contacts-table tbody tr').count(), 2);

      if (width === 1440 || width === 390) {
        await page.goto(base + '/contactos/nuevo');
        await page.getByRole('button', { name: 'Crear contacto', exact: true }).click();
        assert(await page.locator('.error-summary').isVisible());
        assert.equal(await page.evaluate(() => document.activeElement.hasAttribute('data-error-summary')), true);
        await inspect('errores-formulario');
        await page.getByLabel('Nombre completo', { exact: true }).fill(`Contacto QA ${width}`);
        await page.getByLabel('Teléfono', { exact: true }).fill('00000999');
        await page.getByLabel('Correo electrónico', { exact: true }).fill('qa@example.technology');
        await page.getByLabel('Categoría', { exact: true }).selectOption('Otros');
        await page.getByRole('button', { name: 'Crear contacto', exact: true }).click();
        await page.getByRole('heading', { name: 'Detalle del contacto', exact: true }).waitFor();
        const createdUrl = page.url();
        await page.getByRole('link', { name: 'Editar contacto', exact: true }).click();
        await page.getByLabel('Nombre completo', { exact: true }).fill(`Contacto Editado ${width}`);
        await page.getByRole('button', { name: 'Guardar cambios', exact: true }).click();
        await page.waitForURL(createdUrl);
        assert(await page.getByRole('heading', { name: `Contacto Editado ${width}`, exact: true }).isVisible());
        await page.getByRole('button', { name: `Agregar a Contacto Editado ${width} a favoritos`, exact: true }).click();
        assert.equal(await page.getByRole('button', { name: `Quitar a Contacto Editado ${width} de favoritos`, exact: true }).getAttribute('aria-pressed'), 'true');
        const deleteLink = page.getByRole('link', { name: `Eliminar a Contacto Editado ${width}`, exact: true });
        await deleteLink.click();
        assert(await page.locator('#delete-dialog').evaluate(element => element.open));
        assert.equal(await page.evaluate(() => document.activeElement.textContent.trim()), 'Cancelar');
        await page.keyboard.press('Escape');
        assert.equal(await page.locator('#delete-dialog').evaluate(element => element.open), false);
        await deleteLink.click();
        await page.screenshot({ path: path.join(output, `confirmacion-${width}.png`) });
        await page.getByRole('button', { name: 'Sí, eliminar contacto', exact: true }).click();
        await page.waitForURL(base + '/contactos');
        assert.equal(await page.locator('.contacts-table tbody tr').count(), 6);
        assert(!(await page.locator('body').textContent()).includes(`Contacto Editado ${width}`));
        report.workflows.push({ width, actions: 'crear → editar → favorito → cancelar eliminación → eliminar', result: 'pass' });
      }
      await page.getByRole('button', { name: 'Cerrar sesión', exact: true }).click();
      await page.waitForURL(base + '/login');
      await context.close();
    }

    const noJs = await browser.newPage({ javaScriptEnabled: false });
    await noJs.goto(base + '/login');
    await noJs.getByLabel('Usuario', { exact: true }).fill('demo');
    await noJs.getByLabel('Contraseña', { exact: true }).fill('dataconnect-demo');
    await noJs.getByRole('button', { name: 'Entrar al directorio' }).click();
    const original = await noJs.locator('.contact-identity a').first().getAttribute('href');
    await noJs.goto(base + original + '/eliminar');
    assert(await noJs.getByRole('heading', { name: 'Eliminar contacto', exact: true }).isVisible());
    report.workflows.push({ javascript: false, actions: 'login y confirmación HTML sin borrar datos', result: 'pass' });
    await noJs.close();
    await fs.writeFile(path.join(output, 'browser-report.json'), JSON.stringify(report, null, 2) + '\n');
    assert.deepEqual(report.runtimeErrors, [], 'Errores de ejecución o recursos');
    assert.deepEqual(report.problems, [], 'Problemas de estructura o adaptación; revisar browser-report.json');
    console.log(`PASS: ${report.views.length} vistas a cinco tamaños, formularios, CRUD, favoritos, modal, sesión y alternativa sin JavaScript.`);
  } finally {
    if (browser) await browser.close();
    server.kill();
    await new Promise(resolve => server.once('exit', resolve));
    await fs.rm(temporary, { recursive: true, force: true });
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });

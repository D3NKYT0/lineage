#!/usr/bin/env node
/**
 * Script para build do PWA e cópia dos artefatos para static/pwa.
 * Uso: node deploy-pwa.js [--no-build]
 *      --no-build  apenas copia (não roda npm run build)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname);
const DIST = path.join(ROOT, 'dist');
const PUBLIC = path.join(ROOT, 'public');
const STATIC_PWA = path.join(ROOT, '..', '..', 'static', 'pwa');

// ---------------------------------------------------------------------------

function runBuild() {
  if (process.argv.includes('--no-build')) {
    console.log('Modo --no-build: pulando build.');
    return;
  }
  console.log('Executando npm run build...');
  execSync('npm run build', { cwd: ROOT, stdio: 'inherit' });
  console.log('Build concluído.\n');
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function copyFile(src, dest) {
  ensureDir(path.dirname(dest));
  fs.copyFileSync(src, dest);
  console.log(`  Copiado: ${path.relative(ROOT, src)}  →  ${path.relative(ROOT, dest)}`);
}

// ---------------------------------------------------------------------------

/** Remove bundles antigos (bundle.*.js e bundle.*.js.LICENSE.txt) de static/pwa/ */
function cleanOldBundles() {
  if (!fs.existsSync(STATIC_PWA)) return;
  const old = fs.readdirSync(STATIC_PWA).filter(n => /^bundle\..+\.(js|txt)$/.test(n));
  for (const name of old) {
    fs.unlinkSync(path.join(STATIC_PWA, name));
    console.log(`  Removido bundle antigo: ${name}`);
  }
}

/** Copia os bundles gerados em dist/ para static/pwa/ (ignora index.html aqui) */
function copyBundles() {
  if (!fs.existsSync(DIST)) {
    console.error('ERRO: pasta dist/ não encontrada. Execute sem --no-build primeiro.');
    process.exit(1);
  }
  ensureDir(STATIC_PWA);

  for (const name of fs.readdirSync(DIST)) {
    if (name === 'index.html') continue;            // index.html tratado separado
    const src = path.join(DIST, name);
    if (fs.statSync(src).isFile()) {
      copyFile(src, path.join(STATIC_PWA, name));
    }
  }
}

/** Copia manifest.json e service-worker.js do public/ para static/pwa/ */
function copyPublicAssets() {
  for (const name of ['manifest.json', 'service-worker.js']) {
    const src = path.join(PUBLIC, name);
    if (fs.existsSync(src)) copyFile(src, path.join(STATIC_PWA, name));
  }
}

/**
 * Copia dist/index.html → static/pwa/index.html.
 * Como o webpack já usa publicPath '/static/pwa/', os src dos scripts
 * já saem corretos. A função aplica uma correção defensiva caso o
 * publicPath seja alterado no futuro.
 */
function copyIndexHtml() {
  const src = path.join(DIST, 'index.html');
  const dest = path.join(STATIC_PWA, 'index.html');

  if (!fs.existsSync(src)) {
    console.error('ERRO: dist/index.html não encontrado. Verifique o HtmlWebpackPlugin.');
    process.exit(1);
  }

  let html = fs.readFileSync(src, 'utf8');

  // Garante prefixo correto nos srcs de bundle (segurança para mudanças futuras)
  html = html.replace(
    /src="(?!\/static\/pwa\/)(bundle\.[^"]+\.js)"/g,
    'src="/static/pwa/$1"'
  );

  ensureDir(path.dirname(dest));
  fs.writeFileSync(dest, html, 'utf8');
  console.log('  Copiado: dist/index.html  →  static/pwa/index.html');
}

// ---------------------------------------------------------------------------

function main() {
  console.log('PDL PWA — Deploy para static/pwa\n');

  console.log('[1/5] Build...');
  runBuild();

  console.log('[2/5] Limpando bundles antigos...');
  cleanOldBundles();

  console.log('[3/5] Copiando bundles...');
  copyBundles();

  console.log('[4/5] Copiando assets públicos...');
  copyPublicAssets();

  console.log('[5/5] Copiando index.html...');
  copyIndexHtml();

  console.log('\n✓ Concluído. Arquivos em static/pwa/ atualizados.');
}

main();

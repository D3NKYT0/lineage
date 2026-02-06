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

function runBuild() {
  const hasNoBuild = process.argv.includes('--no-build');
  if (hasNoBuild) {
    console.log('Modo --no-build: pulando build.');
    return;
  }
  console.log('Executando npm run build...');
  execSync('npm run build', {
    cwd: ROOT,
    stdio: 'inherit',
  });
  console.log('Build concluído.\n');
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log('Criado:', dir);
  }
}

function copyFile(src, dest) {
  ensureDir(path.dirname(dest));
  fs.copyFileSync(src, dest);
  console.log('Copiado:', path.relative(ROOT, src), '->', path.relative(ROOT, dest));
}

function copyDistToStatic() {
  if (!fs.existsSync(DIST)) {
    console.error('Pasta dist/ não encontrada. Execute o build primeiro (sem --no-build).');
    process.exit(1);
  }

  ensureDir(STATIC_PWA);

  const distFiles = fs.readdirSync(DIST);
  for (const name of distFiles) {
    const src = path.join(DIST, name);
    if (fs.statSync(src).isFile()) {
      copyFile(src, path.join(STATIC_PWA, name));
    }
  }
}

function copyPublicAssets() {
  const assets = ['manifest.json', 'service-worker.js'];
  for (const name of assets) {
    const src = path.join(PUBLIC, name);
    if (fs.existsSync(src)) {
      copyFile(src, path.join(STATIC_PWA, name));
    }
  }
}

function main() {
  console.log('PDL PWA — Deploy para static/pwa\n');
  runBuild();
  copyDistToStatic();
  copyPublicAssets();
  console.log('\nConcluído. Arquivos em static/pwa/ atualizados.');
}

main();

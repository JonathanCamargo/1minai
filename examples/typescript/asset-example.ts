// Run: npx tsx asset-example.ts
// asset-example.ts -- demonstrates upload() and list() for file management
import { OneMinClient } from 'onemin';

const apiKey = process.env.ONEMIN_API_KEY;
if (!apiKey) {
  console.error('Set ONEMIN_API_KEY environment variable to run this example.');
  console.error('  export ONEMIN_API_KEY=your-key-here');
  process.exit(1);
}

const client = new OneMinClient({ apiKey });

// --- Demo 1: Upload a file (minimal 1x1 transparent PNG) ---
const tinyPng = new Uint8Array([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
  0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
  0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00,
  0x0a, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9c, 0x63, 0x00, 0x01, 0x00, 0x00,
  0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49,
  0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
]);

const result = await client.asset.upload(['test.png', tinyPng]);
console.log('=== Asset Uploaded ===');
console.log(`Asset ID:     ${result.assetId}`);
console.log(`URL:          ${result.url}`);
console.log(`Content-type: ${result.contentType}`);
console.log();

// --- Demo 2: List assets ---
const assets = await client.asset.list();
console.log('=== Asset List ===');
if (Array.isArray(assets) && assets.length > 0) {
  for (const asset of assets.slice(0, 5)) {
    console.log(`  - ${asset.id} | ${asset.contentType} | ${asset.location ?? ''}`);
  }
} else {
  console.log('  (no assets found)');
}
console.log();

// --- Demo 3: Get a specific asset by ID ---
if (result.assetId) {
  const fetched = await client.asset.get(result.assetId);
  console.log('=== Asset Retrieved ===');
  console.log(`URL: ${fetched.url}`);
  console.log();
}

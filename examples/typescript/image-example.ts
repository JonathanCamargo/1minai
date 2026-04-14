// Run: npx tsx image-example.ts
// image-example.ts -- demonstrates generate(), removeBackground(), and model constants
import { OneMinClient, Models } from 'onemin';

const apiKey = process.env.ONEMIN_API_KEY;
if (!apiKey) {
  console.error('Set ONEMIN_API_KEY environment variable to run this example.');
  console.error('  export ONEMIN_API_KEY=your-key-here');
  process.exit(1);
}

const client = new OneMinClient({ apiKey });

// --- Demo 1: Generate an image with DALL-E 3 ---
const result1 = await client.image.generate(
  'A photorealistic golden retriever playing in autumn leaves',
  { model: Models.Image.DALL_E_3, width: 1024, height: 1024 },
);
console.log('=== Generated image (DALL-E 3) ===');
console.log(`URL: ${result1.url}`);
console.log();

// --- Demo 2: Generate with Flux Schnell (faster model) ---
const result2 = await client.image.generate(
  'A minimalist logo of a mountain peak at sunrise',
  { model: Models.Image.FLUX_SCHNELL },
);
console.log(`=== Generated image (${Models.Image.FLUX_SCHNELL}) ===`);
console.log(`URL: ${result2.url}`);
console.log();

// --- Demo 3: Remove background from an online image ---
const sampleImageUrl = 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/320px-Cat03.jpg';
const result3 = await client.image.removeBackground(sampleImageUrl);
console.log('=== Background removed ===');
console.log(`URL: ${result3.url}`);
console.log();

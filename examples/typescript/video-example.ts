// Run: npx tsx video-example.ts
// video-example.ts -- demonstrates generate() (text-to-video) with model constants
import { OneMinClient, Models } from 'onemin';

const apiKey = process.env.ONEMIN_API_KEY;
if (!apiKey) {
  console.error('Set ONEMIN_API_KEY environment variable to run this example.');
  console.error('  export ONEMIN_API_KEY=your-key-here');
  process.exit(1);
}

const client = new OneMinClient({ apiKey });

// --- Demo 1: Generate a video with Luma AI ---
// Note: video generation auto-polls until completion (may take 1-3 minutes)
console.log('Generating video with Luma AI (this may take a few minutes)...');
const result1 = await client.video.generate(
  'A serene time-lapse of clouds drifting over mountain peaks at golden hour',
  { model: Models.Video.LUMA_AI, aspectRatio: '16:9' },
);
console.log('=== Generated video (Luma AI) ===');
console.log(`URL: ${result1.url}`);
console.log();

// --- Demo 2: Generate a video with Kling ---
console.log('Generating video with Kling...');
const result2 = await client.video.generate(
  'A butterfly landing on a flower in slow motion',
  { model: Models.Video.KLING },
);
console.log(`=== Generated video (${Models.Video.KLING}) ===`);
console.log(`URL: ${result2.url}`);
console.log();

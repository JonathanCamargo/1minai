// Run: npx tsx writing-example.ts
// writing-example.ts -- demonstrates summarize(), translate(), and checkGrammar()
import { OneMinClient, Models } from 'onemin';

const apiKey = process.env.ONEMIN_API_KEY;
if (!apiKey) {
  console.error('Set ONEMIN_API_KEY environment variable to run this example.');
  console.error('  export ONEMIN_API_KEY=your-key-here');
  process.exit(1);
}

const client = new OneMinClient({ apiKey });

const LONG_TEXT =
  'Artificial intelligence has undergone rapid advancement over the past decade. ' +
  'Machine learning models have grown from simple classifiers to large language models ' +
  'capable of reasoning, writing, and even generating images and video. ' +
  'These systems are now integrated into products used by billions of people worldwide, ' +
  'transforming how we work, communicate, and create.';

// --- Demo 1: Summarize a block of text ---
const result1 = await client.writing.summarize(LONG_TEXT, { model: Models.Text.GPT_4O });
console.log('=== Summarize ===');
console.log(result1.content);
console.log();

// --- Demo 2: Translate text to Spanish ---
const result2 = await client.writing.translate(
  'Hello, how are you today?',
  { targetLanguage: 'es', model: Models.Text.GPT_4O },
);
console.log('=== Translate to Spanish ===');
console.log(result2.content);
console.log();

// --- Demo 3: Check grammar ---
const result3 = await client.writing.checkGrammar(
  'Their going to the store to buys some groceries.',
  { model: Models.Text.GPT_4O },
);
console.log('=== Grammar Check ===');
console.log(result3.content);
console.log();

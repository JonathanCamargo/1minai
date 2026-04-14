// Run: npx tsx text-example.ts
// text-example.ts -- demonstrates chat() with default and named model constants
import { OneMinClient, Models } from 'onemin';

const apiKey = process.env.ONEMIN_API_KEY;
if (!apiKey) {
  console.error('Set ONEMIN_API_KEY environment variable to run this example.');
  console.error('  export ONEMIN_API_KEY=your-key-here');
  process.exit(1);
}

const client = new OneMinClient({ apiKey });

// --- Demo 1: Basic chat with default model (gpt-4o) ---
const result1 = await client.text.chat('What is the speed of light in a vacuum?');
console.log('=== Basic chat (gpt-4o) ===');
console.log(result1.content);
console.log();

// --- Demo 2: Chat with a specific model via Models constant ---
const result2 = await client.text.chat(
  'Explain recursion in one sentence.',
  { model: Models.Text.CLAUDE_3_5_SONNET },
);
console.log(`=== Chat with ${Models.Text.CLAUDE_3_5_SONNET} ===`);
console.log(result2.content);
console.log();

// --- Demo 3: Streaming chat ---
console.log('=== Streaming chat (gpt-4o) ===');
const stream = await client.text.chat('Count from 1 to 5.', { stream: true });
for await (const token of stream as AsyncIterable<string>) {
  process.stdout.write(token);
}
console.log();

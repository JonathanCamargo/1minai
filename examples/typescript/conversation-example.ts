// Run: npx tsx conversation-example.ts
// conversation-example.ts -- demonstrates create() and send() for multi-turn chat
import { OneMinClient, Models } from 'onemin';

const apiKey = process.env.ONEMIN_API_KEY;
if (!apiKey) {
  console.error('Set ONEMIN_API_KEY environment variable to run this example.');
  console.error('  export ONEMIN_API_KEY=your-key-here');
  process.exit(1);
}

const client = new OneMinClient({ apiKey });

// --- Demo 1: Create a conversation ---
const conv = await client.conversation.create({
  title: 'SDK Demo Conversation',
  model: Models.Text.GPT_4O,
});
console.log('=== Conversation Created ===');
console.log(`Conversation ID: ${conv.conversationId}`);
console.log();

// --- Demo 2: Send messages in the conversation ---
const reply1 = await client.conversation.send(
  conv.conversationId,
  'Hi! My name is Alice. Can you remember that?',
  { model: Models.Text.GPT_4O },
);
console.log('=== First message ===');
console.log(`Response: ${reply1.content}`);
console.log();

const reply2 = await client.conversation.send(
  conv.conversationId,
  'What is my name?',
  { model: Models.Text.GPT_4O },
);
console.log('=== Follow-up message ===');
console.log(`Response: ${reply2.content}`);
console.log();

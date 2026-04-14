import { describe, it, expect } from 'vitest';
import { streamSSE, extractToken, MAX_BUFFER_SIZE } from '../src/streaming.js';

// ---------------------------------------------------------------------------
// Helpers: create mock Response objects with ReadableStream bodies
// ---------------------------------------------------------------------------

function makeStreamResponse(chunks: string[], status = 200): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk));
      }
      controller.close();
    },
  });
  return new Response(stream, {
    status,
    headers: { 'Content-Type': 'text/event-stream' },
  });
}

function openAIChunk(content: string): string {
  return `data: ${JSON.stringify({ choices: [{ delta: { content } }] })}\n\n`;
}

function simpleChunk(data: string): string {
  return `data: ${JSON.stringify({ data })}\n\n`;
}

async function collectTokens(response: Response): Promise<string[]> {
  const tokens: string[] = [];
  for await (const token of streamSSE(response)) {
    tokens.push(token);
  }
  return tokens;
}

// ---------------------------------------------------------------------------
// Tests for extractToken
// ---------------------------------------------------------------------------

describe('extractToken', () => {
  it('returns choices[0].delta.content for OpenAI-style payloads', () => {
    const obj = { choices: [{ delta: { content: 'Hello' } }] };
    expect(extractToken(obj)).toBe('Hello');
  });

  it('returns obj.data for simple format payloads', () => {
    const obj = { data: 'world' };
    expect(extractToken(obj)).toBe('world');
  });

  it('falls back to JSON.stringify for unrecognized payloads', () => {
    const obj = { unknown: 'value' };
    const result = extractToken(obj);
    expect(typeof result).toBe('string');
    expect(result.length).toBeGreaterThan(0);
  });

  it('returns empty string when choices present but content is empty string', () => {
    const obj = { choices: [{ delta: { content: '' } }] };
    expect(extractToken(obj)).toBe('');
  });
});

// ---------------------------------------------------------------------------
// Tests for streamSSE
// ---------------------------------------------------------------------------

describe('streamSSE', () => {
  it('yields 3 token strings from 3 SSE data events', async () => {
    const response = makeStreamResponse([
      openAIChunk('tok1'),
      openAIChunk('tok2'),
      openAIChunk('tok3'),
    ]);

    const tokens = await collectTokens(response);
    expect(tokens).toEqual(['tok1', 'tok2', 'tok3']);
  });

  it('stops at [DONE] sentinel and does not yield tokens after it', async () => {
    const response = makeStreamResponse([
      openAIChunk('first'),
      'data: [DONE]\n\n',
      openAIChunk('after'),
    ]);

    const tokens = await collectTokens(response);
    expect(tokens).toEqual(['first']);
  });

  it('handles partial JSON across chunk boundaries without crashing', async () => {
    // Split a valid JSON SSE line across two chunks
    const fullLine = openAIChunk('merged');
    const half = Math.floor(fullLine.length / 2);
    const part1 = fullLine.slice(0, half);
    const part2 = fullLine.slice(half);

    const response = makeStreamResponse([
      part1,
      part2,
      'data: [DONE]\n\n',
    ]);

    const tokens = await collectTokens(response);
    expect(tokens).toEqual(['merged']);
  });

  it('skips empty data lines (SSE keepalives)', async () => {
    const response = makeStreamResponse([
      'data: \n\n',              // empty data line
      openAIChunk('tok'),
      'data: [DONE]\n\n',
    ]);

    const tokens = await collectTokens(response);
    expect(tokens).toEqual(['tok']);
  });

  it('skips non-data SSE lines (comments, event:, id: lines)', async () => {
    const response = makeStreamResponse([
      ': this is a comment\n',
      'event: message\n',
      'id: 123\n',
      openAIChunk('tok'),
      'data: [DONE]\n\n',
    ]);

    const tokens = await collectTokens(response);
    expect(tokens).toEqual(['tok']);
  });

  it('throws Error if buffer exceeds 1MB', async () => {
    // Create a data line longer than MAX_BUFFER_SIZE
    const bigData = 'x'.repeat(MAX_BUFFER_SIZE + 1);
    const response = makeStreamResponse([`data: ${bigData}\n\n`]);

    await expect(collectTokens(response)).rejects.toThrow('SSE buffer overflow');
  });

  it('throws APIError if response is not ok', async () => {
    const response = new Response('Unauthorized', { status: 401 });
    await expect(collectTokens(response)).rejects.toThrow();
  });

  it('handles simple data format payloads', async () => {
    const response = makeStreamResponse([
      simpleChunk('hello'),
      simpleChunk('world'),
      'data: [DONE]\n\n',
    ]);

    const tokens = await collectTokens(response);
    expect(tokens).toEqual(['hello', 'world']);
  });

  it('does not yield empty token strings', async () => {
    const response = makeStreamResponse([
      `data: ${JSON.stringify({ choices: [{ delta: { content: '' } }] })}\n\n`,
      openAIChunk('real'),
      'data: [DONE]\n\n',
    ]);

    const tokens = await collectTokens(response);
    expect(tokens).toEqual(['real']);
  });
});

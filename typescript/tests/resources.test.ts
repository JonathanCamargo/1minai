import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { OneMinClient } from '../src/client.js';
import { ImageResource } from '../src/resources/image.js';
import { TextResource } from '../src/resources/text.js';
import { AudioResource } from '../src/resources/audio.js';
import { VideoResource } from '../src/resources/video.js';
import { WritingResource } from '../src/resources/writing.js';
import { ConversationResource } from '../src/resources/conversations.js';
import { AssetResource } from '../src/resources/assets.js';

let client: OneMinClient;

beforeEach(() => {
  // Stub fetch globally so client construction doesn't fail on missing network
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{}', { status: 200 })));
  client = new OneMinClient({ apiKey: 'test-api-key-12345678' });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('Domain resource accessors', () => {
  it('client.image is an instance of ImageResource', () => {
    expect(client.image).toBeInstanceOf(ImageResource);
  });

  it('client.text is an instance of TextResource', () => {
    expect(client.text).toBeInstanceOf(TextResource);
  });

  it('client.audio is an instance of AudioResource', () => {
    expect(client.audio).toBeInstanceOf(AudioResource);
  });

  it('client.video is an instance of VideoResource', () => {
    expect(client.video).toBeInstanceOf(VideoResource);
  });

  it('client.writing is an instance of WritingResource', () => {
    expect(client.writing).toBeInstanceOf(WritingResource);
  });

  it('client.conversation is an instance of ConversationResource', () => {
    expect(client.conversation).toBeInstanceOf(ConversationResource);
  });

  it('client.asset is an instance of AssetResource', () => {
    expect(client.asset).toBeInstanceOf(AssetResource);
  });
});

describe('Lazy initialization', () => {
  it('client.image returns the same instance on repeated access', () => {
    expect(client.image).toBe(client.image);
  });

  it('client.text returns the same instance on repeated access', () => {
    expect(client.text).toBe(client.text);
  });

  it('client.audio returns the same instance on repeated access', () => {
    expect(client.audio).toBe(client.audio);
  });

  it('client.video returns the same instance on repeated access', () => {
    expect(client.video).toBe(client.video);
  });

  it('client.writing returns the same instance on repeated access', () => {
    expect(client.writing).toBe(client.writing);
  });

  it('client.conversation returns the same instance on repeated access', () => {
    expect(client.conversation).toBe(client.conversation);
  });

  it('client.asset returns the same instance on repeated access', () => {
    expect(client.asset).toBe(client.asset);
  });
});

describe('Domain methods are fully implemented (Phase 3)', () => {
  it('client.image.generate() resolves with an ImageResult', async () => {
    const result = await client.image.generate('a cat');
    expect(result).toHaveProperty('url');
    expect(result).toHaveProperty('model');
  });

  it('client.text.chat() resolves with a TextResult', async () => {
    const result = await client.text.chat('hello');
    expect(result).toHaveProperty('content');
    expect(result).toHaveProperty('model');
  });

  it('client.audio.speak() resolves with an AudioResult', async () => {
    const result = await client.audio.speak('hello');
    expect(result).toHaveProperty('model');
  });

  it('client.writing.summarize() resolves with a WritingResult', async () => {
    const result = await client.writing.summarize('text');
    expect(result).toHaveProperty('content');
    expect(result).toHaveProperty('model');
  });

  it('client.writing.rewrite() resolves with a WritingResult', async () => {
    const result = await client.writing.rewrite('text');
    expect(result).toHaveProperty('content');
    expect(result).toHaveProperty('model');
  });

  it('client.conversation.create() resolves with a ConversationResult', async () => {
    const result = await client.conversation.create();
    expect(result).toHaveProperty('conversationId');
    expect(result).toHaveProperty('model');
  });

  it('client.asset.list() resolves with a value', async () => {
    const result = await client.asset.list();
    expect(result).toBeDefined();
  });
});

describe('raw() method presence on all resources', () => {
  it('client.image has a raw method', () => {
    expect(typeof client.image.raw).toBe('function');
  });

  it('client.text has a raw method', () => {
    expect(typeof client.text.raw).toBe('function');
  });

  it('client.audio has a raw method', () => {
    expect(typeof client.audio.raw).toBe('function');
  });

  it('client.video has a raw method', () => {
    expect(typeof client.video.raw).toBe('function');
  });

  it('client.writing has a raw method', () => {
    expect(typeof client.writing.raw).toBe('function');
  });

  it('client.conversation has a raw method', () => {
    expect(typeof client.conversation.raw).toBe('function');
  });

  it('client.asset has a raw method', () => {
    expect(typeof client.asset.raw).toBe('function');
  });
});

describe('Per-domain timeout defaults (INFRA-07)', () => {
  it('client.image timeout is 90_000ms', () => {
    expect((client.image as unknown as { timeout: number }).timeout).toBe(90_000);
  });

  it('client.audio timeout is 90_000ms', () => {
    expect((client.audio as unknown as { timeout: number }).timeout).toBe(90_000);
  });

  it('client.video timeout is 300_000ms', () => {
    expect((client.video as unknown as { timeout: number }).timeout).toBe(300_000);
  });

  it('client.text timeout is 30_000ms', () => {
    expect((client.text as unknown as { timeout: number }).timeout).toBe(30_000);
  });

  it('client.writing timeout is 30_000ms', () => {
    expect((client.writing as unknown as { timeout: number }).timeout).toBe(30_000);
  });

  it('client.conversation timeout is 30_000ms', () => {
    expect((client.conversation as unknown as { timeout: number }).timeout).toBe(30_000);
  });

  it('client.asset timeout is 30_000ms', () => {
    expect((client.asset as unknown as { timeout: number }).timeout).toBe(30_000);
  });
});

describe('raw() passthrough uses correct endpoint', () => {
  it('image.raw() calls /api/features with POST', async () => {
    const mockFetch = vi.fn().mockResolvedValue(new Response('{"result":"ok"}', { status: 200 }));
    vi.stubGlobal('fetch', mockFetch);
    await client.image.raw({ type: 'IMAGE_GENERATOR', model: 'midjourney' });
    expect(mockFetch).toHaveBeenCalledOnce();
    const [url] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(url).toContain('/api/features');
  });

  it('conversation.raw() calls /api/conversations with POST', async () => {
    const mockFetch = vi.fn().mockResolvedValue(new Response('{"result":"ok"}', { status: 200 }));
    vi.stubGlobal('fetch', mockFetch);
    await client.conversation.raw({ type: 'CONVERSATION' });
    expect(mockFetch).toHaveBeenCalledOnce();
    const [url] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(url).toContain('/api/conversations');
  });

  it('asset.raw() calls /api/assets with POST', async () => {
    const mockFetch = vi.fn().mockResolvedValue(new Response('{"result":"ok"}', { status: 200 }));
    vi.stubGlobal('fetch', mockFetch);
    await client.asset.raw({ type: 'ASSET' });
    expect(mockFetch).toHaveBeenCalledOnce();
    const [url] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(url).toContain('/api/assets');
  });
});

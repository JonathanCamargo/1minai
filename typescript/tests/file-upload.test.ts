import { describe, it, expect, vi, afterEach } from 'vitest';
import { normalizeFile, uploadFile, extractUrl, type FileInput } from '../src/file-upload.js';
import { APIError } from '../src/error.js';

afterEach(() => {
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------
// normalizeFile tests
// ---------------------------------------------------------------------------

describe('normalizeFile', () => {
  it('Uint8Array input returns ["upload", same_array]', () => {
    const data = new Uint8Array([1, 2, 3]);
    const [name, content] = normalizeFile(data);
    expect(name).toBe('upload');
    expect(content).toBe(data);
  });

  it('[name, Uint8Array] tuple returns the same tuple', () => {
    const data = new Uint8Array([4, 5, 6]);
    const result = normalizeFile(['my_image.png', data]);
    expect(result).toEqual(['my_image.png', data]);
    expect(result[1]).toBe(data);
  });

  it('throws TypeError for a number input', () => {
    expect(() => normalizeFile(123 as unknown as FileInput)).toThrow(TypeError);
  });

  it('throws TypeError for a string input (not supported in TS)', () => {
    expect(() => normalizeFile('some/path.png' as unknown as FileInput)).toThrow(TypeError);
  });

  it('throws TypeError for null input', () => {
    expect(() => normalizeFile(null as unknown as FileInput)).toThrow(TypeError);
  });

  it('throws TypeError for a plain array [name] with one element', () => {
    expect(() => normalizeFile(['only_name'] as unknown as FileInput)).toThrow(TypeError);
  });

  it('throws TypeError for tuple with wrong types [bytes, string]', () => {
    const data = new Uint8Array([1]);
    expect(() => normalizeFile([data as unknown as string, 'string' as unknown as Uint8Array])).toThrow(TypeError);
  });
});

// ---------------------------------------------------------------------------
// extractUrl tests
// ---------------------------------------------------------------------------

describe('extractUrl', () => {
  it('returns data.asset.location (nested path)', () => {
    expect(extractUrl({ asset: { location: 'https://cdn.example.com/file.png' } })).toBe(
      'https://cdn.example.com/file.png',
    );
  });

  it('throws APIError when "asset" key is absent', () => {
    expect(() => extractUrl({ unknownField: 'value', count: 1 })).toThrow(APIError);
  });

  it('throws APIError when "asset.location" is absent', () => {
    expect(() => extractUrl({ asset: { otherField: 'value' } })).toThrow(APIError);
  });

  it('throws APIError when "asset.location" is an empty string', () => {
    expect(() => extractUrl({ asset: { location: '' } })).toThrow(APIError);
  });

  it('throws APIError when "asset" is not an object', () => {
    expect(() => extractUrl({ asset: 'not-a-dict' })).toThrow(APIError);
  });

  it('throws APIError with response body in message for debugging', () => {
    let error: APIError | undefined;
    try {
      extractUrl({ someOtherField: 'value' });
    } catch (e) {
      error = e as APIError;
    }
    expect(error).toBeDefined();
    expect(error!.message).toContain('No asset URL found');
    expect(error!.message).toContain('someOtherField');
  });
});

// ---------------------------------------------------------------------------
// uploadFile tests
// ---------------------------------------------------------------------------

describe('uploadFile', () => {
  it('sends FormData POST to /api/assets and returns URL string', async () => {
    const mockResponse = new Response(
      JSON.stringify({ asset: { location: 'development/images/abc.png' } }),
      { status: 200, headers: { 'Content-Type': 'application/json' } },
    );
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(mockResponse);

    const url = await uploadFile('https://api.1min.ai', 'test-key', new Uint8Array([1, 2, 3]));
    expect(url).toBe('development/images/abc.png');
  });

  it('sends the API-KEY header in the request', async () => {
    let capturedHeaders: Headers | undefined;
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (_input, init) => {
      capturedHeaders = new Headers(init?.headers as HeadersInit);
      return new Response(
        JSON.stringify({ asset: { location: 'some/path.png' } }),
        { status: 200 },
      );
    });

    await uploadFile('https://api.1min.ai', 'my-secret-key', new Uint8Array([1]));
    expect(capturedHeaders?.get('API-KEY')).toBe('my-secret-key');
  });

  it('sends FormData as the request body (not JSON)', async () => {
    let capturedBody: BodyInit | null | undefined;
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (_input, init) => {
      capturedBody = init?.body;
      return new Response(
        JSON.stringify({ asset: { location: 'some/path.png' } }),
        { status: 200 },
      );
    });

    await uploadFile('https://api.1min.ai', 'key', new Uint8Array([1]));
    expect(capturedBody).toBeInstanceOf(FormData);
  });

  it('posts to the correct URL /api/assets', async () => {
    let capturedUrl: string | undefined;
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, _init) => {
      capturedUrl = input as string;
      return new Response(
        JSON.stringify({ asset: { location: 'ok' } }),
        { status: 200 },
      );
    });

    await uploadFile('https://api.1min.ai', 'key', new Uint8Array([1]));
    expect(capturedUrl).toBe('https://api.1min.ai/api/assets');
  });

  it('throws APIError when response JSON has no recognized URL field', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ unknownField: 'value' }), { status: 200 }),
    );
    await expect(uploadFile('https://api.1min.ai', 'key', new Uint8Array([1]))).rejects.toThrow(APIError);
  });

  it('throws APIError when response returns a non-2xx status', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Unauthorized', { status: 401 }),
    );
    await expect(uploadFile('https://api.1min.ai', 'bad-key', new Uint8Array([1]))).rejects.toThrow(APIError);
  });

  it('uses filename from a [name, Uint8Array] tuple', async () => {
    let formDataFile: File | Blob | undefined;
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (_input, init) => {
      const fd = init?.body as FormData;
      formDataFile = fd.get('asset') as File | Blob;
      return new Response(
        JSON.stringify({ asset: { location: 'uploads/audio.mp3' } }),
        { status: 200 },
      );
    });

    const url = await uploadFile('https://api.1min.ai', 'key', ['audio.mp3', new Uint8Array([1, 2])]);
    expect(url).toBe('uploads/audio.mp3');
    // The Blob/File appended should exist
    expect(formDataFile).toBeDefined();
  });
});

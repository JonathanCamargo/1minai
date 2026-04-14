export const BASE_URL = 'https://api.1min.ai';
export const DEFAULT_TIMEOUT = 30_000; // milliseconds
export const DEFAULT_MAX_RETRIES = 2;
export const DEFAULT_BASE_DELAY = 500; // milliseconds
export const RETRYABLE_STATUS_CODES = new Set([408, 429, 500, 502, 503, 504]);
export const API_KEY_HEADER = 'API-KEY';

/**
 * Per-domain timeout defaults (milliseconds) per INFRA-07.
 * Resources pass their domain timeout to request() so that
 * image/video/audio operations get longer timeouts than text.
 */
export const DOMAIN_TIMEOUTS: Record<string, number> = {
  text: 30_000,
  image: 90_000,
  audio: 90_000,
  video: 300_000,
  writing: 30_000,
  conversation: 30_000,
  asset: 30_000,
};

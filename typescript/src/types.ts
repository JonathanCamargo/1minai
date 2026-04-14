/**
 * Typed result interfaces for all 1min.ai API domain responses.
 *
 * All domain methods return one of these typed objects instead of raw Records.
 * Extra fields from the API are preserved in the metadata catch-all.
 */

export interface TextResult {
  content: string;
  model: string;
  usage?: Record<string, unknown>;
}

export interface ImageResult {
  url: string;
  model: string;
  urls?: string[];
  metadata?: Record<string, unknown>;
}

export interface AudioResult {
  url?: string;
  content?: string;
  model: string;
  metadata?: Record<string, unknown>;
}

export interface VideoResult {
  url: string;
  model: string;
  metadata?: Record<string, unknown>;
}

export interface WritingResult {
  content: string;
  model: string;
  metadata?: Record<string, unknown>;
}

export interface ConversationResult {
  content: string;
  conversationId: string;
  model: string;
  metadata?: Record<string, unknown>;
}

export interface AssetResult {
  url: string;
  assetId: string;
  contentType?: string;
  metadata?: Record<string, unknown>;
}

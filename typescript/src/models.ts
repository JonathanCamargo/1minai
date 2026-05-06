/**
 * Public model constants for the 1min.ai TypeScript SDK.
 *
 * This module re-exports the generated catalogue from `models-data`. The
 * catalogue itself is generated from `data/models.json` at the repository root
 * by `scripts/sync_models.py` and validated against the live API by
 * `scripts/validate_models.py`. To add or remove a model, edit
 * `data/models.json` and run the sync script -- do NOT hand-edit the
 * generated file.
 *
 * @example
 * ```typescript
 * import { Models } from 'onemin';
 *
 * const text = Models.Text.GPT_4O;
 * const img  = Models.Image.MIDJOURNEY;
 * const stt  = Models.Audio.WHISPER_1;
 * const vid  = Models.Video.LUMA_AI;
 * ```
 */
export { Models, MODEL_CATALOGUE, allIds } from './models-data.js';
export type { ModelId, ModelEntry } from './models-data.js';

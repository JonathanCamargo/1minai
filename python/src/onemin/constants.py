"""Public model constants for the 1min.ai SDK.

This module re-exports the generated catalogue from ``_models_data``. The
catalogue itself is generated from ``data/models.json`` at the repository root
by ``scripts/sync_models.py`` and validated against the live API by
``scripts/validate_models.py``. To add or remove a model, edit
``data/models.json`` and run the sync script -- do NOT hand-edit the
generated file.

Usage::

    from onemin import Models

    model = Models.Text.GPT_4O
    model = Models.Image.MIDJOURNEY
    model = Models.Audio.WHISPER_1
    model = Models.Video.LUMA_AI
"""

from onemin._models_data import MODEL_CATALOGUE, Models, all_ids

__all__ = ["Models", "MODEL_CATALOGUE", "all_ids"]

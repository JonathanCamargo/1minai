"""Domain resource classes for the 1min.ai SDK.

Each resource corresponds to an API domain and provides:
- ``raw(payload)``: Low-level passthrough with per-domain timeout
- High-level methods (stubs in Phase 1, implemented in Phase 3)
"""

from onemin.resources.image import ImageResource
from onemin.resources.text import TextResource
from onemin.resources.audio import AudioResource
from onemin.resources.video import VideoResource
from onemin.resources.writing import WritingResource
from onemin.resources.conversations import ConversationResource
from onemin.resources.assets import AssetResource

__all__ = [
    "ImageResource",
    "TextResource",
    "AudioResource",
    "VideoResource",
    "WritingResource",
    "ConversationResource",
    "AssetResource",
]

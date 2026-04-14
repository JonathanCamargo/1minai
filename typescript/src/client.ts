import { BaseOneMinClient } from './base-client.js';
import type { ClientOptions } from './base-client.js';
import { ImageResource } from './resources/image.js';
import { TextResource } from './resources/text.js';
import { AudioResource } from './resources/audio.js';
import { VideoResource } from './resources/video.js';
import { WritingResource } from './resources/writing.js';
import { ConversationResource } from './resources/conversations.js';
import { AssetResource } from './resources/assets.js';

export class OneMinClient extends BaseOneMinClient {
  private _image?: ImageResource;
  private _text?: TextResource;
  private _audio?: AudioResource;
  private _video?: VideoResource;
  private _writing?: WritingResource;
  private _conversation?: ConversationResource;
  private _asset?: AssetResource;

  constructor(options: ClientOptions = {}) {
    super(options);
  }

  get image(): ImageResource {
    return (this._image ??= new ImageResource(this));
  }

  get text(): TextResource {
    return (this._text ??= new TextResource(this));
  }

  get audio(): AudioResource {
    return (this._audio ??= new AudioResource(this));
  }

  get video(): VideoResource {
    return (this._video ??= new VideoResource(this));
  }

  get writing(): WritingResource {
    return (this._writing ??= new WritingResource(this));
  }

  get conversation(): ConversationResource {
    return (this._conversation ??= new ConversationResource(this));
  }

  get asset(): AssetResource {
    return (this._asset ??= new AssetResource(this));
  }
}

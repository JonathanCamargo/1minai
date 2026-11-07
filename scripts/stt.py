#!/usr/bin/env python3
"""Continuous speech-to-text from the microphone using 1min.ai.

Waits for speech. When the first word is heard, it records a fixed window
(default 4s, including a little audio from just before the word so it isn't
clipped), sends it to the API, and goes back to waiting for the next word.
Windows that don't contain enough actual sound are never sent, so silence
costs nothing.

    python scripts/stt.py
    python scripts/stt.py -w 6 -l en -m gpt-4o-transcribe
    python scripts/stt.py --list-devices
"""
import argparse
import io
import math
import os
import queue
import threading
import time
import wave
from collections import deque
from pathlib import Path

import numpy as np
import sounddevice as sd
from fileman.envars import load_env
from onemin import OneMinClient


# Load env vars: system env → ~/.env → <project_root>/.env (system wins)
load_env(project_env=Path(__file__).parent / ".." / ".env")

RATE = 16000  # Hz, mono: plenty for speech and keeps uploads small
FRAME_MS = 30
FRAME = RATE * FRAME_MS // 1000


def dbfs(frame: np.ndarray) -> float:
    """Loudness of an int16 frame in dB relative to full scale (0 = max)."""
    rms = math.sqrt(float(np.mean(np.square(frame.astype(np.float32))))) / 32768.0
    return 20 * math.log10(max(rms, 1e-9))


def to_wav(frames: list[np.ndarray]) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(np.concatenate(frames).tobytes())
    return buf.getvalue()


def transcriber(client: OneMinClient, jobs: queue.Queue, args) -> None:
    """Worker thread: sends windows to the API one at a time, in order."""
    extra = {"language": args.language} if args.language else {}
    while True:
        job = jobs.get()
        if job is None:
            return
        stamp, wav = job
        try:
            result = client.audio.transcribe(
                ("window.wav", wav), model=args.model, **extra
            )
            text = (result.content or "").strip()
            if text:
                print(f"[{stamp}] {text}", flush=True)
        except Exception as exc:  # keep listening even if one request fails
            print(f"[{stamp}] ! transcription failed: {exc}", flush=True)


def calibrate(audio_q: queue.Queue, args) -> float:
    """Pick the loudness threshold: ambient noise + margin, unless given."""
    if args.threshold is not None:
        return args.threshold
    print("Measuring background noise (stay quiet for 1s)...", flush=True)
    levels = [dbfs(audio_q.get()) for _ in range(1000 // FRAME_MS)]
    noise = float(np.percentile(levels, 90))
    threshold = max(noise + args.margin, args.min_threshold)
    if noise > -35:
        print(
            f"Warning: background level is very high ({noise:.0f} dBFS), so speech"
            f" must exceed {threshold:.0f} dBFS to be heard. Lower the mic input"
            " volume, move away from noise/speakers, or use --margin 6 / --threshold.",
            flush=True,
        )
    return threshold


def listen(args, jobs: queue.Queue) -> None:
    audio_q: queue.Queue = queue.Queue()

    def on_audio(indata, frames, time_info, status):
        if status:
            print(f"(audio status: {status})", flush=True)
        audio_q.put(indata[:, 0].copy())

    window_frames = int(args.window * 1000 / FRAME_MS)
    preroll = deque(maxlen=args.preroll // FRAME_MS)

    with sd.InputStream(
        samplerate=RATE, channels=1, dtype="int16",
        blocksize=FRAME, device=args.device, callback=on_audio,
    ):
        threshold = calibrate(audio_q, args)
        print(
            f"Listening (threshold {threshold:.0f} dBFS, {args.window:g}s windows)."
            " Ctrl+C to stop.",
            flush=True,
        )
        run = 0  # consecutive loud frames
        while True:
            frame = audio_q.get()
            preroll.append(frame)
            run = run + 1 if dbfs(frame) > threshold else 0
            if run < args.onset:
                continue

            # First word heard: the window starts with the pre-roll audio.
            frames = list(preroll)
            start = time.strftime("%H:%M:%S")
            while len(frames) < window_frames:
                frames.append(audio_q.get())
            preroll.clear()
            run = 0

            loud = sum(dbfs(f) > threshold for f in frames)
            speech_s = loud * FRAME_MS / 1000
            if speech_s < args.min_speech:
                print(f"[{start}] (skipped: only {speech_s:.1f}s of sound)", flush=True)
                continue
            jobs.put((start, to_wav(frames)))


def test_mic(args) -> None:
    """Show a live level meter so you can see whether the mic is heard."""
    audio_q: queue.Queue = queue.Queue()

    def on_audio(indata, frames, time_info, status):
        audio_q.put(indata[:, 0].copy())

    dev = sd.query_devices(args.device, "input")
    print(f"Device: {dev['name']} (default rate {dev['default_samplerate']:.0f} Hz)")
    print("Say something. Testing for 8s (Ctrl+C to stop)...\n", flush=True)
    levels: list[float] = []
    try:
        with sd.InputStream(
            samplerate=RATE, channels=1, dtype="int16",
            blocksize=FRAME, device=args.device, callback=on_audio,
        ):
            end = time.time() + 8
            noise = None
            while time.time() < end:
                try:
                    frame = audio_q.get(timeout=2)
                except queue.Empty:
                    print("\nNo audio arrived from the device in 2s.")
                    break
                db = dbfs(frame)
                levels.append(db)
                if noise is None and len(levels) >= 1000 // FRAME_MS:
                    noise = float(np.percentile(levels, 90))
                thr = args.threshold if args.threshold is not None else (
                    max(noise + args.margin, args.min_threshold) if noise is not None else None
                )
                bar = "#" * max(0, int((db + 80) / 2))
                mark = "SOUND" if thr is not None and db > thr else "     "
                thr_txt = f"{thr:6.1f}" if thr is not None else "  (cal)"
                print(f"\r{db:6.1f} dBFS  thr {thr_txt}  {mark} {bar:<40}", end="", flush=True)
    except KeyboardInterrupt:
        pass
    print()
    if not levels:
        print("Nothing recorded: wrong device or no permission to use the mic.")
        return
    lo, hi = min(levels), max(levels)
    print(f"Quietest {lo:.1f} dBFS, loudest {hi:.1f} dBFS.")
    if hi < -70:
        print("Almost digital silence: the mic is muted, wrong device, or input volume is 0.")
        print("Try --list-devices and --device N, or check your sound settings.")
    elif hi < -45:
        print("Very quiet signal: raise input volume, or lower --min-threshold / --margin.")
    else:
        print("Mic works. If stt.py still hears nothing, lower --margin or set --threshold.")


def main() -> None:
    p = argparse.ArgumentParser(description="Mic speech-to-text using 1min.ai.")
    p.add_argument(
        "-k", "--api-key", default=os.environ.get("ONEMIN_API_KEY"),
        help="1min.ai API key (falls back to ONEMIN_API_KEY env var)",
    )
    p.add_argument(
        "-m", "--model", default=None,
        help="STT model (default: the API default, whisper-1)",
    )
    p.add_argument("-l", "--language", help="Language code, e.g. en (skips auto-detect)")
    p.add_argument("-w", "--window", type=float, default=4.0, help="Window length in seconds (default 4)")
    p.add_argument("--device", help="Input device name or index (see --list-devices)")
    p.add_argument("--list-devices", action="store_true", help="List audio devices and exit")
    p.add_argument("--test-mic", action="store_true", help="Show a live level meter for 8s and exit (no API key needed)")
    p.add_argument(
        "--threshold", type=float,
        help="Speech loudness threshold in dBFS (default: auto from background noise)",
    )
    p.add_argument("--margin", type=float, default=12.0, help="dB above background noise counted as sound (default 12)")
    p.add_argument("--min-threshold", type=float, default=-50.0, help="Never go below this dBFS (default -50)")
    p.add_argument("--onset", type=int, default=3, help="Loud frames in a row that count as a word starting (30ms each, default 3)")
    p.add_argument("--preroll", type=int, default=300, help="ms of audio kept from before the first word (default 300)")
    p.add_argument("--min-speech", type=float, default=0.3, help="Seconds of sound a window needs before it is sent (default 0.3)")
    args = p.parse_args()

    if args.list_devices:
        print(sd.query_devices())
        return
    if args.device is not None and args.device.isdigit():
        args.device = int(args.device)
    if args.test_mic:
        test_mic(args)
        return
    if not args.api_key:
        p.error("API key is required. Set ONEMIN_API_KEY or use -k/--api-key.")

    client = OneMinClient(api_key=args.api_key)
    jobs: queue.Queue = queue.Queue()
    worker = threading.Thread(target=transcriber, args=(client, jobs, args), daemon=True)
    worker.start()

    try:
        listen(args, jobs)
    except KeyboardInterrupt:
        print("\nStopping; finishing queued transcriptions...", flush=True)
    finally:
        jobs.put(None)
        worker.join()


if __name__ == "__main__":
    main()

from __future__ import annotations

import io
import math
import random
import wave
from array import array

import pygame


def _build_tone(
    frequency: float,
    duration: float,
    *,
    volume: float = 0.45,
    sample_rate: int = 44100,
    waveform: str = "sine",
    decay: float = 2.4,
) -> bytes:
    sample_count = max(1, int(duration * sample_rate))
    samples = array("h")
    for idx in range(sample_count):
        t = idx / sample_rate
        phase = 2.0 * math.pi * frequency * t
        if waveform == "triangle":
            value = 2.0 * abs(2.0 * ((frequency * t) % 1.0) - 1.0) - 1.0
        elif waveform == "noise":
            value = random.uniform(-1.0, 1.0)
        else:
            value = math.sin(phase)
        envelope = math.exp(-decay * t / max(0.001, duration))
        amp = int(max(-32767, min(32767, value * envelope * volume * 32767)))
        samples.append(amp)

    with io.BytesIO() as buffer:
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(samples.tobytes())
        return buffer.getvalue()


def _build_sound(*segments: tuple[float, float, str], volume: float, decay: float) -> bytes:
    chunks: list[bytes] = []
    for frequency, duration, waveform in segments:
        chunks.append(
            _build_tone(
                frequency=frequency,
                duration=duration,
                volume=volume,
                waveform=waveform,
                decay=decay,
            )
        )

    if not chunks:
        return b""

    with io.BytesIO() as output:
        with wave.open(output, "wb") as wav_out:
            wav_out.setnchannels(1)
            wav_out.setsampwidth(2)
            wav_out.setframerate(44100)
            for chunk in chunks:
                with io.BytesIO(chunk) as src_buffer:
                    with wave.open(src_buffer, "rb") as src:
                        wav_out.writeframes(src.readframes(src.getnframes()))
        return output.getvalue()


class AudioManager:
    def __init__(self) -> None:
        self.enabled = False
        self._music_channel: pygame.mixer.Channel | None = None
        self._music: pygame.mixer.Sound | None = None
        self._sfx_flap: pygame.mixer.Sound | None = None
        self._sfx_coin: pygame.mixer.Sound | None = None
        self._sfx_pass: pygame.mixer.Sound | None = None
        self._sfx_die: pygame.mixer.Sound | None = None
        self._init_audio()

    def _init_audio(self) -> None:
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

            self._music = pygame.mixer.Sound(
                file=io.BytesIO(
                    _build_sound(
                        (220.0, 0.55, "triangle"),
                        (277.2, 0.55, "triangle"),
                        (329.6, 0.55, "triangle"),
                        (277.2, 0.55, "triangle"),
                        volume=0.17,
                        decay=1.1,
                    )
                )
            )
            self._sfx_flap = pygame.mixer.Sound(
                file=io.BytesIO(
                    _build_sound(
                        (780.0, 0.04, "triangle"),
                        (920.0, 0.04, "triangle"),
                        volume=0.36,
                        decay=4.8,
                    )
                )
            )
            self._sfx_coin = pygame.mixer.Sound(
                file=io.BytesIO(
                    _build_sound(
                        (1046.5, 0.03, "triangle"),
                        (1318.5, 0.05, "sine"),
                        volume=0.36,
                        decay=4.6,
                    )
                )
            )
            self._sfx_pass = pygame.mixer.Sound(
                file=io.BytesIO(
                    _build_sound(
                        (660.0, 0.06, "sine"),
                        (840.0, 0.06, "sine"),
                        volume=0.34,
                        decay=3.6,
                    )
                )
            )
            self._sfx_die = pygame.mixer.Sound(
                file=io.BytesIO(
                    _build_sound(
                        (220.0, 0.10, "triangle"),
                        (164.8, 0.14, "triangle"),
                        (92.5, 0.18, "noise"),
                        volume=0.44,
                        decay=2.0,
                    )
                )
            )

            self._music.set_volume(0.23)
            self._sfx_flap.set_volume(0.45)
            self._sfx_coin.set_volume(0.55)
            self._sfx_pass.set_volume(0.50)
            self._sfx_die.set_volume(0.6)
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def play_music(self) -> None:
        if not self.enabled or self._music is None:
            return
        if self._music_channel and self._music_channel.get_busy():
            return
        self._music_channel = self._music.play(loops=-1)

    def play_flap(self) -> None:
        if self.enabled and self._sfx_flap is not None:
            self._sfx_flap.play()

    def play_pass(self) -> None:
        if self.enabled and self._sfx_pass is not None:
            self._sfx_pass.play()

    def play_coin(self) -> None:
        if self.enabled and self._sfx_coin is not None:
            self._sfx_coin.play()

    def play_die(self) -> None:
        if self.enabled and self._sfx_die is not None:
            self._sfx_die.play()

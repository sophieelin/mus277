import os
import numpy as np
import sounddevice as sd
import wave
from threading import Thread, Event


class AudioMixer:
    def __init__(self):
        self.stems = {}
        self.playback_event = Event()
        self.mute_states = {}
        self.sample_rate = 44100

    def load_stem(self, name, filepath):
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File {filepath} not found")
        with wave.open(filepath, "rb") as wf:
            print(self.sample_rate)
            if wf.getframerate() != self.sample_rate:
                raise ValueError(f"Unsupported sample rate: {wf.getframerate()}")
            audio_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            self.stems[name] = audio_data
            self.mute_states[name] = False

    def mute_stem(self, name, mute=True):
        if name not in self.stems:
            raise ValueError(f"Stem {name} not loaded")
        self.mute_states[name] = mute

    def _mix_stems(self):
        if not self.stems:
            return np.zeros((self.sample_rate,), dtype=np.int16)
        min_length = min(len(data) for data in self.stems.values())
        mixed = np.zeros(min_length, dtype=np.float32)
        for name, data in self.stems.items():
            if not self.mute_states[name]:
                mixed[:min_length] += data[:min_length].astype(np.float32)
        mixed = np.clip(mixed, -32768, 32767).astype(np.int16)
        return mixed

    def play(self):
        self.playback_event.set()
        playback_thread = Thread(target=self._playback_loop)
        playback_thread.start()

    def stop(self):
        self.playback_event.clear()

    def _playback_loop(self):
        mixed_audio = self._mix_stems()
        stream = sd.OutputStream(samplerate=self.sample_rate, channels=1, dtype="int16")
        with stream:
            stream.start()
            while self.playback_event.is_set():
                stream.write(mixed_audio)


# Example usage:
if __name__ == "__main__":
    mixer = AudioMixer()
    try:
        # Load stems (replace with your file paths)
        mixer.load_stem("stem1", "miss.wav")
        mixer.load_stem("stem2", "yto.wav")

        # Start playback
        mixer.play()

        # Mute/unmute stems dynamically
        while True:
            cmd = input("Enter command (mute/unmute/stop): ").strip()
            if cmd.startswith("mute "):
                stem = cmd.split(" ")[1]
                mixer.mute_stem(stem, mute=True)
            elif cmd.startswith("unmute "):
                stem = cmd.split(" ")[1]
                mixer.mute_stem(stem, mute=False)
            elif cmd == "stop":
                mixer.stop()
                break
    except Exception as e:
        print(f"Error: {e}")

import numpy as np
import sounddevice as sd
import soundfile as sf
import numpy as np


class SimultaneousWAVPlayer:
    def __init__(self, file1, file2):
        """
        wav player obj
        """

        self.data1, self.samplerate1 = sf.read(file1)
        self.data2, self.samplerate2 = sf.read(file2)

        if self.samplerate1 != self.samplerate2:
            raise ValueError("mismatched sample rates")

        self.mute1 = False
        self.mute2 = False

        if self.data1.ndim == 1:
            self.data1 = np.column_stack((self.data1, self.data1))
        if self.data2.ndim == 1:
            self.data2 = np.column_stack((self.data2, self.data2))

        self.max_length = min(len(self.data1), len(self.data2))
        self.data1 = self.data1[: self.max_length]
        self.data2 = self.data2[: self.max_length]

        self.stream = None
        self.playing = False
        self.playback_position = 0

    def _audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)

        end = self.playback_position + frames

        chunk1 = self.data1[self.playback_position : end]
        chunk2 = self.data2[self.playback_position : end]

        if self.mute1:
            chunk1 *= 0
        if self.mute2:
            chunk2 *= 0

        mixed_chunk = chunk1 + chunk2
        outdata[: len(mixed_chunk)] = mixed_chunk

        if len(mixed_chunk) < len(outdata):
            outdata[len(mixed_chunk) :] = 0

        self.playback_position = end

        if end >= self.max_length:
            raise sd.CallbackStop()

    def play(self):
        """
        start playing both audio files simultaneously
        """
        if not self.playing:
            self.playback_position = 0
            self.playing = True
            self.stream = sd.OutputStream(
                samplerate=self.samplerate1, channels=2, callback=self._audio_callback
            )
            self.stream.start()

    def stop(self):
        """
        stop playback
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.playing = False
            self.playback_position = 0

    def toggle_mute1(self):
        """
        toggle mute for the first audio file
        """
        self.mute1 = not self.mute1
        print(f"File 1 muted: {self.mute1}")

    def toggle_mute2(self):
        """
        toggle mute for the second audio file
        """
        self.mute2 = not self.mute2
        print(f"File 2 muted: {self.mute2}")


def main():

    player = SimultaneousWAVPlayer("1.wav", "2.wav")
    player.play()

    try:
        while True:
            cmd = input("commands: m1 (mute file 1), m2 (mute file 2), q (quit): ")
            if cmd == "m1":
                player.toggle_mute1()
            elif cmd == "m2":
                player.toggle_mute2()
            elif cmd == "q":
                break
    except KeyboardInterrupt:
        pass
    finally:
        player.stop()


if __name__ == "__main__":
    main()

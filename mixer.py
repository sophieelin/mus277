import numpy as np
import sounddevice as sd
import soundfile as sf
import numpy as np

class SimultaneousWAVPlayer:
    ending = False
    def __init__(self, file1, file2, file3, file4, file5):
        """
        wav player obj
        """
        self.data1, self.samplerate1 = sf.read(file1)
        self.data2, self.samplerate2 = sf.read(file2)
        self.data3, self.samplerate3 = sf.read(file3)
        self.data4, self.samplerate4 = sf.read(file4)
        self.data5, self.samplerate5 = sf.read(file5)
        if self.samplerate1 != self.samplerate2:
            raise ValueError("mismatched sample rates")

        self.mute1 = False
        self.mute2 = False
        self.mute3 = False 
        self.mute4 = False
        self.mute5 = False

        if self.data1.ndim == 1:
            self.data1 = np.column_stack((self.data1, self.data1))
        if self.data2.ndim == 1:
            self.data2 = np.column_stack((self.data2, self.data2))
        if self.data3.ndim == 1:
            self.data3 = np.column_stack((self.data3, self.data3))
        if self.data4.ndim == 1:
            self.data4 = np.column_stack((self.data4, self.data4))
        if self.data5.ndim == 1:
            self.data5 = np.column_stack((self.data5, self.data5))

        self.max_length = min(len(self.data1), len(self.data2), len(self.data3), len(self.data4), len(self.data5))
        self.data1 = self.data1[: self.max_length]
        self.data2 = self.data2[: self.max_length]
        self.data3 = self.data3[: self.max_length]
        self.data4 = self.data4[: self.max_length]
        self.data5 = self.data5[: self.max_length]

        self.stream = None
        self.playing = False
        self.playback_position = 0
        self.volumes = [1.0, 1.0, 1.0, 1.0, 1.0]

    def _audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)

        end = self.playback_position + frames
        chunk1 = self.data1[self.playback_position : end] * self.volumes[0]
        chunk2 = self.data2[self.playback_position : end] * self.volumes[1]
        chunk3 = self.data3[self.playback_position : end] * self.volumes[2]
        chunk4 = self.data4[self.playback_position : end] * self.volumes[3]
        chunk5 = self.data5[self.playback_position : end] * self.volumes[4]

        if self.mute1:
            chunk1 *= 0
        if self.mute2:
            chunk2 *= 0
        if self.mute3:
            chunk3 *= 0
        if self.mute4:
            chunk4 *= 0
        if self.mute5:
            chunk5 *= 0

        mixed_chunk = chunk1 + chunk2 + chunk3 + chunk4 + chunk5
        outdata[: len(mixed_chunk)] = mixed_chunk

        if len(mixed_chunk) < len(outdata):
            outdata[len(mixed_chunk) :] = 0

        self.playback_position = end

        if end >= self.max_length:
            self.playback_position = 0
            end = frames

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

    def toggle_mute3(self):
        """
        toggle mute for the first audio file
        """
        self.mute3 = not self.mute3
        print(f"File 3 muted: {self.mute1}")

    def toggle_mute4(self):
        """
        toggle mute for the second audio file
        """
        self.mute4 = not self.mute4
        print(f"File 24 muted: {self.mute4}")

    def toggle_mute5(self):
        """
        toggle mute for the second audio file
        """
        self.mute5 = not self.mute5
        print(f"File 2 muted: {self.mute5}")
    def set_volumes(self, hand_heights):
        for i in range(min(len(hand_heights), 5)):
            self.volumes[i] = hand_heights[i]

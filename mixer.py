import numpy as np
import sounddevice as sd
import soundfile as sf
import numpy as np


class SimultaneousWAVPlayer:
    def __init__(self, file1, file2, file3, file4, file5):
        """
        wav player obj
        """
        self.data1, self.samplerate1 = sf.read(file1)
        self.data2, self.samplerate2 = sf.read(file2)
        self.data3, self.samplerate3 = sf.read(file3)
        self.data4, self.samplerate4 = sf.read(file4)
        self.data5, self.samplerate5 = sf.read(file5)
        #for file in list:
        #    self.data1, self.samplerate1 = sf.read(file)

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

    def _audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)

        end = self.playback_position + frames

        chunk1 = self.data1[self.playback_position : end]
        chunk2 = self.data2[self.playback_position : end]
        chunk3 = self.data3[self.playback_position : end]
        chunk4 = self.data4[self.playback_position : end]
        chunk5 = self.data5[self.playback_position : end]

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
            raise sd.CallbackStop()

    def play(self):
        """
        start playing both audio files simultaneously
        """
        if not self.playing:
            self.playback_position = 0
            self.playing = True
            self.stream = sd.OutputStream(
                sam
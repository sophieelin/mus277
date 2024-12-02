import numpy as np
import sounddevice as sd
import soundfile as sf
import os

class SimultaneousWAVPlayer:
    def __init__(self, file_list):
        """
        initializes WAV player with all files
        
        :param file_list: list of paths to audio files
        """
        #if not enough input
        if not file_list or len(file_list) < 2:
            raise ValueError("At least two audio files are required")

        self.data = []
        self.sample_rates = []
        self.mute_states = []

        initial_sample_rate = None
        first_max_length = None

         # read audio files
        for file in file_list:
            data, sample_rate = sf.read(file)
            
            # plays simultaneously
            if data.ndim == 1:
                data = np.column_stack((data, data))
            
            # Check sample rate consistency
            if initial_sample_rate is None:
                initial_sample_rate = sample_rate
            elif sample_rate != initial_sample_rate:
                raise ValueError(f"Mismatched sample rates: {file}")
            
            self.data.append(data)
            self.sample_rates.append(sample_rate)
            self.mute_states.append(False)

        #all the same length
        self.max_length = min(len(data) for data in self.data)
        self.data = [data[:self.max_length] for data in self.data]

        # Playback setup
        self.stream = None
        self.playing = False
        self.pos = 0
        self.sample_rate = initial_sample_rate

    def _audio_callback(self, output, frames, time, status):
        if status:
            print(status)

        end = self.pos + frames

        #slicing into chunks
        chunks = [
            data[self.pos:end] * (0 if mute else 1)
            for data, mute in zip(self.data, self.mute_states)
        ]

        # combine chunks
        mixed_chunk = np.sum(chunks, axis=0)
        
        output[: len(mixed_chunk)] = mixed_chunk
        if len(mixed_chunk) < len(output):
            output[len(mixed_chunk) :] = 0


        self.pos = end

        # looping if reached the end!!
        if end >= self.max_length:
            self.pos = 0
            end = frames

    def play(self):
        """Start playing audio files simultaneously"""
        if not self.playing:
            self.pos = 0 #position of the audio during playback
            self.playing = True
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate, 
                channels=2, 
                callback=self._audio_callback
            )
            self.stream.start()

    def stop(self):
        """stops playback"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.playing = False
            self.pos = 0

    def toggle_mute(self, index):
        """
        toggle mute for a specific audio file
        
        :param index: index of the audio file to mute/unmute -- this is 0 indexed
        """
        if 0 <= index < len(self.mute_states):
            self.mute_states[index] = not self.mute_states[index]
            print(f"File {index + 1} muted: {self.mute_states[index]}")
        else:
            print(f"Invalid file index: {index}")

def main():
    keyword = "SOUND ART"
    wav_files = [f for f in os.listdir('.') if f.endswith('.wav') and keyword in f]
    
    if not wav_files:
        print("no wav files in directory")
        return

    print("wav files directory:")
    for i, file in enumerate(wav_files, 1):
        print(f"{i}. {file}")
    try:
        player = SimultaneousWAVPlayer(wav_files)
        player.play()

        while True:
            # shows commands for all files 
            cmd_options = ', '.join([f"{i}({wav_files[i-1]})" for i in range(1, len(wav_files) + 1)]) #got some help with this line
            cmd = input(f"commands: {cmd_options}, q (quit): ")

            try:
                # quit program
                if cmd == 'q':
                    break
                
                index = int(cmd) - 1
                if 0 <= index < len(wav_files):
                    player.toggle_mute(index)
                else:
                    print("Invalid input. Please try again.")
            
            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")

    except KeyboardInterrupt:
        print("\nPlayback interrupted.")
    finally:
        player.stop()

if __name__ == "__main__":
    main()
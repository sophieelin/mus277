from mixer3 import SimultaneousWAVPlayer
from controller import start_tracking_thread, get_current_hand_heights
import time
import os

def main():
    keyword = "SOUND ART"
    wav_files = [f for f in os.listdir('.') if f.endswith('.wav') and keyword in f]
    
    if not wav_files:
        print("No WAV files found in the directory")
        return

    player = SimultaneousWAVPlayer(wav_files)
    
    tracking_thread = start_tracking_thread()
    
    player.play()
    
    try:
        while True:
            hand_heights = get_current_hand_heights()
            
            if not hand_heights:
                # Set all volumes to 0 if no hands are detected
                for i in range(len(wav_files)):
                    player.set_volume(i, 0)
            else:
                # Adjust volume for detected hands
                for i, height in enumerate(hand_heights):
                    if i < len(wav_files):
                        player.set_volume(i, height)
                    else:
                        break
                    
                # Mute any remaining tracks
                for i in range(len(hand_heights), len(wav_files)):
                    player.set_volume(i, 0)
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping playback...")
    finally:
        player.stop()

if __name__ == "__main__":
    main()
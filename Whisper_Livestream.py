import whisper, os
from threading import Thread


''' Variables '''
ffmpeg_livestream_url = "http://lyd.nrk.no/nrk_radio_alltid_nyheter_mp3_h"
ffmpeg_segment_time = 5
whisper_model = "medium"


# load the whisper module
model = whisper.load_model(whisper_model)

# Make audio folder if not exists, clear all files in it if anny
os.makedirs("./audio/", exist_ok=True)
for fi in os.listdir('./audio/'): os.remove(f"./audio/{fi}")

def audioSplitterFunc():
    os.system(f'ffmpeg -hide_banner -loglevel error -i "{ffmpeg_livestream_url}" -codec mp3 -f segment -segment_time {ffmpeg_segment_time} -strftime 1 ./audio/%Y-%m-%d_%H-%M-%S.mp3')

# Start a new thread with the audio splitter instance
Thread(target=audioSplitterFunc).start()

while True:
    clips = os.listdir('./audio/')
    clips.sort()
    # If excists more or exactly 2 clips in audio folder, ffmpeg has started on a new file, and the old one is ready
    # ffmpeg continually writes to file untill the disered length is reached, then it starts on a new, the delay is therefore minimal.
    if len(clips) >= 2:
        # print("Current audio clip is:", clips[0])
        transcription = model.transcribe(f"./audio/{clips[0]}", fp16=False)
        print(transcription["text"])
        os.remove(f"./audio/{clips[0]}")
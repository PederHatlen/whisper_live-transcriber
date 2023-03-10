'''
Transcribe a Folder of audio segments
Can be added realtime
'''

import whisper_live, time

whisper_model = "large-v2"
whisper_lang = "no"
folder_location = './audio/'

# Load whisper model
model = whisper_live.setup(whisper_model, folder_location)

last_out = ""
while True:
    time_start = time.time()
    try:
        res = whisper_live.transcribe(folder_location, model, whisper_lang, last_out)
    except Exception as e:
        print("Transcription failed:", e)
    if res['run']:
        print(f"[Queue: {res['queue']}, Time: {round((time.time() - time_start)*1000)}ms]", res['res'].text)
        last_out = res['res'].text
    time.sleep(0.5)
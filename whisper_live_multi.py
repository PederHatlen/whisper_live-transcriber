import whisper_live, time, os
from threading import Thread

whisper_model = "large-v2"
whisper_urls = ["http://lyd.nrk.no/nrk_radio_alltid_nyheter_aac_h", "http://lyd.nrk.no/nrk_radio_p1_stor-oslo_aac_h", "http://lyd.nrk.no/nrk_radio_p3_aac_h"]
whisper_names = ["AN", "P1", "P3"]
whisper_previous = ["", "", ""]
whisper_lang = "no"
folder_location = "./audio_local/"

model = whisper_live.setup(whisper_model, folder_location)

for i, url in enumerate(whisper_urls):
    folder_location_spesific = folder_location+whisper_names[i]+"/"
    
    # Make audio folder if not exists, clear all files in it if anny
    os.makedirs(folder_location_spesific, exist_ok=True)
    
    Thread(target=whisper_live.audioSplitterFunc, args=(url, 5, folder_location_spesific)).start()

while True:
    time_total = time.time()
    success = 0
    for i in range(len(whisper_urls)):
        time_start = time.time()
        try:
            res = whisper_live.transcribe(f'{folder_location}{whisper_names[i]}/', model, whisper_lang, whisper_previous[i])
        except Exception as e:
            print("Transcription failed:", e)
        if res['run']:
            print(f"[name: {whisper_names[i]}, Queue: {res['queue']}, Time: {round((time.time() - time_start)*1000)}ms]", res['res'].text)
            whisper_previous[i] = res['res'].text
            success+=1
    if success > 0: print(f"Total looptime was {round((time.time()-time_total), 2)}s")
    time.sleep(0.5)
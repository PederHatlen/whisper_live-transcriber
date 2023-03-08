import whisper_live, time, os
from threading import Thread

whisper_model = "large-v2"
whisper_urls = ["http://lyd.nrk.no/nrk_radio_alltid_nyheter_aac_h", "http://lyd.nrk.no/nrk_radio_p1_stor-oslo_aac_h", "http://lyd.nrk.no/nrk_radio_p3_aac_h"]
whisper_names = ["AN", "P1", "P3"]
whisper_previous = ["", "", ""]

model = whisper_live.setup(whisper_model)

for url in whisper_urls:
    file_location = f'./audio/{url}/'
    
    # Make audio folder if not exists, clear all files in it if anny
    os.makedirs(file_location, exist_ok=True)
    for fi in os.listdir(file_location): os.remove(file_location+fi)
    
    Thread(target=whisper_live.audioSplitterFunc, args=(url, 5)).start()

while True:
    time_total = time.time()
    runs = 0
    for i in range(len(whisper_urls)):
        time_start = time.time()
        res = whisper_live.transcribe(f'./audio/{whisper_urls[i]}/', model, last_out=whisper_previous[i])
        if res['run']:
            print(f"[name: {whisper_names[i]}, Queue: {res['queue']}, Time: {round((time.time() - time_start)*1000)}ms]", res['res'].text)
            whisper_previous[i] = res['res'].text
            runs+=1
    if runs > 0: print(f"Total looptime was {round((time.time()-time_total), 2)}s")
    time.sleep(0.5)
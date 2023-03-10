import whisper, os, shutil

global bad_results

bad_results = [
    "Undertekster av Ai-Media",
    "Teksting av Nicolai Winther",
    "🎵 Outro-musikk 🎵",
    "Outro-musikk 🎵",
    "🎵",
    ""
]

def setup(whisper_model, folder_location="./audio/"):
    # load the whisper module
    print(f"Loading whisper {whisper_model}...")
    model = whisper.load_model(whisper_model)
    print("Done!")
    
    # Make audio folder if not exists, clear all files in it if anny
    os.makedirs(folder_location, exist_ok=True)
    for root, dirs, files in os.walk(folder_location):
        for fi in files: os.remove(root+fi)
        for dirs in dirs: shutil.rmtree(root+dirs)
    
    return model

def audioSplitterFunc(ffmpeg_input_source, ffmpeg_segment_length, ffmpeg_output_path="./audio"):
    # Start a process with ffmpeg to save temporary segments from livestream (Not great, but io functionality with segments are non existent)
    os.system(f'ffmpeg -i "{ffmpeg_input_source}" -map 0:a -hide_banner -loglevel error -f segment -segment_time {ffmpeg_segment_length} -strftime 1 ./{ffmpeg_output_path}/%Y-%m-%d_%H-%M-%S.mp3')

def transcribe(folder_location, model, whisper_lang, last_out=""):
    # Gather all clips, and sort (since name = datetime)
    clips = os.listdir(folder_location)
    clips.sort()
    # If excists more or exactly 2 clips in audio folder, ffmpeg has started on a new file, and the old one is ready
    # ffmpeg continually writes to file untill the desired length is reached, then it starts on a new, the delay is therefore minimal.
    if len(clips) >= 2:
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(folder_location+clips[0])
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # decode the audio
        options = whisper.DecodingOptions(prompt=last_out, language=whisper_lang, fp16=False)
        result = whisper.decode(model, mel, options)
    
        # remove the audio file and return the values
        os.remove(folder_location+clips[0])
                
        if result.text in bad_results: return {"run":False}
        
        return {"run":True, "res":result, "queue":len(clips)-2, "clip":clips[0]}
    return {"run":False} # If no clips

def liveTranscription(ffmpeg_input_source, whisper_model="large-v2", folder_location="./audio/", ffmpeg_segment_length=5, whisper_lang="no", debug=False):
    import time
    from threading import Thread
    
    # Load model and clear folder
    model = setup(whisper_model, folder_location)
    
    # Start a new thread with the audio splitter instance
    # Multiprocessing, becouse closes with main aplication
    Thread(target=audioSplitterFunc, args=(ffmpeg_input_source, ffmpeg_segment_length, folder_location)).start()
    
    # Loop for transcribing
    last_out = ""
    while True:
        # Track time for debug
        time_start = time.time()
        # Transcribing with the transcribe function, if transcribed, print result and update last
        try:
            res = transcribe(folder_location, model, whisper_lang, last_out)
        except Exception as e:
            print("Transcription failed", e)
        if res['run']:
            print((f"[Queue: {res['queue']}, Time: {round((time.time() - time_start)*1000)}ms] " if debug else "") + res['res'].text)
            last_out = res['res'].text
            
            # if more in the queue, don't sleep
            if res['queue'] > 0: continue
        # Sleep for resource management
        time.sleep(0.5)

if __name__ == "__main__":
    import argparse
    
    ffmpeg_input_source = "http://lyd.nrk.no/nrk_radio_alltid_nyheter_aac_h"
    ffmpeg_segment_length = 5
    whisper_model = "large-v2"
    whisper_lang = "no"
    folder_location = "./audio_local/"

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-input", default=ffmpeg_input_source, type=str, help="URL of the audio/video-stream to transcribe")
    parser.add_argument("-sl", "--segment_length", default=ffmpeg_segment_length, type=int, help="Length of audio segments")
    parser.add_argument("-wm", "--whisper_model", default=whisper_model, type=str, help="name of the Whisper model to use")
    parser.add_argument("-wl", "--whisper_lang", default=whisper_lang, type=str, help="Language to use for transcription, default norwegian")
    parser.add_argument("-d", "--debug", action='store_true', help="print time to transcribe")

    args = parser.parse_args()

    liveTranscription(args.input, args.whisper_model, folder_location, args.segment_length, args.whisper_lang, args.debug)
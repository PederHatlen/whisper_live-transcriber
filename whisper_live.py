import whisper, os, time, argparse
from threading import Thread

def setup(whisper_model):
    # load the whisper module
    print(f"Loading whisper {whisper_model}...")
    model = whisper.load_model(whisper_model)
    print("Loading complete!")
    return model

def audioSplitterFunc(ffmpeg_livestream_url, ffmpeg_segment_length):
    # Start a process with ffmpeg to save temporary segments from livestream (Not great, but io functionality with segments are non existent)
    os.system(f'ffmpeg -i "{ffmpeg_livestream_url}" -map 0:a -hide_banner -loglevel error -f segment -segment_time {ffmpeg_segment_length} -strftime 1 ./audio/{ffmpeg_livestream_url}/%Y-%m-%d_%H-%M-%S.mp3')

def transcribe(file_location, model, last_out="", whisper_lang="no"):
    # Gather all clips, and sort (since name = datetime)
    clips = os.listdir(file_location)
    clips.sort()
    # If excists more or exactly 2 clips in audio folder, ffmpeg has started on a new file, and the old one is ready
    # ffmpeg continually writes to file untill the desired length is reached, then it starts on a new, the delay is therefore minimal.
    if len(clips) >= 2:
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(file_location+clips[0])
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # decode the audio
        options = whisper.DecodingOptions(prompt=last_out, language=whisper_lang, fp16=True)
        result = whisper.decode(model, mel, options)
    
        # remove the audio file and return the values
        os.remove(file_location+clips[0])
        return {"run":True, "res":result, "queue":len(clips)-2}
    return {"run":False} # If no clips

def liveTranscription(ffmpeg_livestream_url, model, ffmpeg_segment_length=5, whisper_lang="no", debug=False):
    file_location = f'./audio/{ffmpeg_livestream_url}/'
    
    # Make audio folder if not exists, clear all files in it if anny
    os.makedirs(file_location, exist_ok=True)
    for fi in os.listdir(file_location): os.remove(file_location+fi)

    # Start a new thread with the audio splitter instance
    # Multiprocessing, becouse closes with main aplication
    Thread(target=audioSplitterFunc, args=(ffmpeg_livestream_url, ffmpeg_segment_length)).start()
    
    # Loop for transcribing
    last_out = ""
    while True:
        # Track time for debug
        time_start = time.time()
        # Transcribing with the transcribe function, if transcribed, print result and update last
        res = transcribe(file_location, model, last_out=last_out, whisper_lang=whisper_lang)
        if res['run']:
            print((f"[Queue: {res['queue']}, Time: {round((time.time() - time_start)*1000)}ms] " if debug else "") + res['res'].text)
            last_out = res['res'].text
            
            # if more in the queue, don't sleep
            if res['queue'] > 0: continue
        # Sleep for resource management
        time.sleep(0.5)

if __name__ == "__main__":
    ffmpeg_segment_length = 5
    whisper_model = "large-v2"
    whisper_lang = "no"

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("url", type=str, help="URL of the audio/video-stream to transcribe")
    parser.add_argument("-sl", "--segment_length", default=ffmpeg_segment_length, type=int, help="Length of audio segments")
    parser.add_argument("-wm", "--whisper_model", default=whisper_model, type=str, help="name of the Whisper model to use")
    parser.add_argument("-wl", "--whisper_lang", default=whisper_lang, type=str, help="Language to use for transcription, default norwegian")
    parser.add_argument("-d", "--debug", action='store_true', help="print time to transcribe")

    args = parser.parse_args()
    
    model = setup(args.whisper_model)

    liveTranscription(args.url, ffmpeg_segment_length=args.segment_length, model=model, whisper_lang=args.whisper_lang, debug=args.debug)
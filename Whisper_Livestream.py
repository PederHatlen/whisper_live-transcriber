import whisper, os, argparse
from threading import Thread


def audioSplitterFunc(ffmpeg_livestream_url, ffmpeg_segment_length):
    # Start a process with ffmpeg to save temporary segments from livestream (Not great, but io functionality with segments are non existent)
    os.system(f'ffmpeg -i "{ffmpeg_livestream_url}" -map a -hide_banner -loglevel error -f segment -segment_time {ffmpeg_segment_length} -strftime 1 ./audio/%Y-%m-%d_%H-%M-%S.mp3')

def liveTranscription(ffmpeg_livestream_url, ffmpeg_segment_length, whisper_model, queue = False):
    # load the whisper module
    print(f"Loading whisper {whisper_model} model...")
    model = whisper.load_model(whisper_model)
    print("Loading complete!")

    # Make audio folder if not exists, clear all files in it if anny
    os.makedirs("./audio/", exist_ok=True)
    for fi in os.listdir('./audio/'): os.remove(f"./audio/{fi}")

    # Start a new thread with the audio splitter instance
    # Multiprocessing, becouse closes with main aplication
    Thread(target=audioSplitterFunc, args=(ffmpeg_livestream_url, ffmpeg_segment_length)).start()

    while True:
        # Gather all clips, and sort (since name = datetime)
        clips = os.listdir('./audio/')
        clips.sort()
        # If excists more or exactly 2 clips in audio folder, ffmpeg has started on a new file, and the old one is ready
        # ffmpeg continually writes to file untill the desired length is reached, then it starts on a new, the delay is therefore minimal.
        if len(clips) >= 2:
            transcription = model.transcribe(f'./audio/{clips[0]}', fp16=False)
            print(f"[queue: {len(clips)-2}] " if queue else "" + transcription["text"])
            os.remove(f"./audio/{clips[0]}")

if __name__ == "__main__":
    ffmpeg_segment_length = 5
    whisper_model = "medium"

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("url", type=str, help="URL of the audio/video-stream to transcribe")
    parser.add_argument("-sl", "--segment_length", default=ffmpeg_segment_length, type=int, help="Length of audio segments")
    parser.add_argument("-wm", "--whisper_model", default=whisper_model, type=str, help="name of the Whisper model to use")
    parser.add_argument("-q", "--queue", action='store_true', help="print queue possition")

    args = parser.parse_args()

    liveTranscription(args.url, args.segment_length, args.whisper_model, queue = args.queue)
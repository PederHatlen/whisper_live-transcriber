# Whisper Live-audio transcriber

## Description

This is a basic python program, which uses ffmpeg to split an audiostream into 5 second clips.  
The clips are then run through whisper, via the python library.  
Performance of this programm is as fast as the system can handle whisper.  

## Requirements

`FFmpeg`,  
`Python3.10` (whisper only supports 3.10 for now),  
`whisper` installation instructions can be found here: [https://github.com/openai/whisper]

## Note

If your intention is to run with cuda, ensure the correct cuda-included PyTorch version is installed.

# Screen Recorder
This is a Python-based screen recorder that captures audio from the system, audio from the microphone, and screen video. The recordings are merged into a single file and uploaded to an AWS S3 bucket for storage.

# Features
Screen Recording: Captures screen activity as video frames.

Microphone Audio Recording: Records audio input from the microphone.

System Audio Recording: Records audio output from the system (e.g., sound from speakers).

Audio-Video Merging: Combines screen video, microphone audio, and system audio into a single file using FFmpeg.

AWS S3 Upload: Uploads the final recording to an Amazon S3 bucket for secure storage.

User-Friendly GUI: Provides a simple interface to start and stop recordings.

# Requirements
Software
Python 3.x (Tested on Python 3.8+)

FFmpeg (Required for merging audio and video)

Python Libraries
Install the required libraries using pip:
pip install sounddevice soundfile numpy pyautogui opencv-python boto3 soundcard ttkbootstrap getmac

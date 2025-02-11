# Screen Recorder

This Python project captures the screen and system audio, allowing users to record their screen with synchronized audio. It saves the recording as an MP4 file and automatically uploads it to an AWS S3 bucket.

# Features

Records screen at approximately 20 FPS.

Captures system audio using a loopback device.

Saves recordings to the desktop in a ScreenRecordings folder.

Automatically uploads recordings to an AWS S3 bucket.

Start/stop recording with the F9 key.

# Requirements

Before running the script, install the required dependencies:

pip install numpy pynput mss sounddevice moviepy boto3

# Setup

Ensure your system has an audio loopback device for capturing system sound.

Modify self.audio_device_index in the script to match your system's loopback device.

Set up AWS credentials for S3 uploads.

Run the script.


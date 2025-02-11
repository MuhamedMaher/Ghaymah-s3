import threading
import time
import os
import numpy as np
from pynput import keyboard
from mss import mss
import sounddevice as sd
from moviepy import ImageSequenceClip
from moviepy.audio.AudioClip import AudioArrayClip
import boto3

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.audio_frames = []
        self.sct = mss()
        self.monitor = self.sct.monitors[1]  # Primary monitor

        # Query and set up audio device for system loopback
        print("Available audio devices:")
        devices = sd.query_devices()
        print(devices)

        # ADJUST THIS INDEX TO MATCH YOUR SYSTEM'S LOOPBACK DEVICE
        self.audio_device_index = 3  # Replace with your loopback device index
        device_info = sd.query_devices(self.audio_device_index)
        print(f"Using audio device: {device_info['name']}")

        self.fs = int(device_info['default_samplerate'])
        self.audio_channels = device_info['max_input_channels']
        self.audio_stream = None
        self.listener = None
        self.start_time = None
        self.end_time = None

        # Create output folder on Desktop
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_folder = os.path.join(desktop_dir, "ScreenRecordings")
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def start_recording(self):
        print("Recording started...")
        self.recording = True
        self.frames = []
        self.audio_frames = []
        self.start_time = time.time()

        # Start screen recording thread
        self.screen_thread = threading.Thread(target=self.record_screen)
        self.screen_thread.start()

        # Start audio stream with loopback device
        self.audio_stream = sd.InputStream(
            device=self.audio_device_index,
            samplerate=self.fs,
            channels=self.audio_channels,
            callback=self.audio_callback
        )
        self.audio_stream.start()

    def stop_recording(self):
        print("Recording stopped. Processing video...")
        self.recording = False
        self.screen_thread.join()
        self.audio_stream.stop()
        self.end_time = time.time()
        video_path = self.save_video()
        self.upload_to_s3(video_path)
        print(f"Video saved to: {video_path}")

    def audio_callback(self, indata, frames, time_info, status):
        self.audio_frames.append(indata.copy())

    def record_screen(self):
        sct_local = mss()
        while self.recording:
            frame = np.array(sct_local.grab(self.monitor))
            if frame.shape[2] == 4:
                frame = frame[..., :3]  # Remove alpha channel
            frame = frame[..., ::-1]  # BGR to RGB
            self.frames.append(frame)
            time.sleep(0.05)  # ~20 FPS

    def save_video(self):
        duration = self.end_time - self.start_time
        actual_fps = len(self.frames) / duration
        filename = f"recording_{time.strftime('%Y%m%d-%H%M%S')}.mp4"
        video_path = os.path.join(self.output_folder, filename)

        # Create video clip
        clip = ImageSequenceClip(self.frames, fps=actual_fps)

        # Add audio if captured
        if self.audio_frames:
            try:
                audio_data = np.concatenate(self.audio_frames, axis=0)
                audio_clip = AudioArrayClip(audio_data, fps=self.fs)
                clip = clip.set_audio(audio_clip)
            except Exception as e:
                print(f"Audio processing failed: {e}")

        # Write video file
        clip.write_videofile(
            video_path,
            codec="libx264",
            audio_codec="aac",
            ffmpeg_params=["-preset", "medium", "-crf", "18"]
        )
        return video_path

    def upload_to_s3(self, video_path):
        s3 = boto3.client('s3')
        bucket_name = "ghaymah-course-bucket"
        s3_key = f"lasheen-team/recording/{os.path.basename(video_path)}"
        try:
            s3.upload_file(video_path, bucket_name, s3_key)
            print(f"Uploaded to S3: s3://{bucket_name}/{s3_key}")
        except Exception as e:
            print(f"S3 upload error: {e}")

    def on_press(self, key):
        if key == keyboard.Key.f9:
            if not self.recording:
                self.start_recording()
            else:
                self.stop_recording()

    def start(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        print("Press F9 to start/stop recording...")
        self.listener.join()

if __name__ == "__main__":
    recorder = ScreenRecorder()
    recorder.start()

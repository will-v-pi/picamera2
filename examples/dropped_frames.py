#!/usr/bin/python3

# Example of requesting a specific framerate, and measuring
# the number of dropped frames and the actual framerate

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
import time


def post_callback(request):
    """Keeps track of the number of dropped frames
    """
    global num_frames, next_timestamp, dropped_frames, start_timestamp, end_timestamp
    metadata = request.get_metadata()
    if next_timestamp is not None:
        diff = int(metadata["SensorTimestamp"] / 1000 - next_timestamp)
    else:
        start_timestamp = metadata["SensorTimestamp"]
        diff = 0
    if metadata["SensorTimestamp"] > 0:
        # Occasionally errors occur with timestamp, just skip these
        next_timestamp = metadata["SensorTimestamp"] / 1000 + metadata["FrameDuration"]
        dropped_frames += round(diff / metadata["FrameDuration"])
    num_frames += 1
    end_timestamp = metadata["SensorTimestamp"]


picam2 = Picamera2()

num_frames = 0
dropped_frames = 0
next_timestamp = None
start_timestamp = 0
end_timestamp = 0
picam2.post_callback = post_callback

picam2.video_configuration = picam2.create_video_configuration(
    # Experiment with how different resolution affect frame drops
    main={"size": (1920, 1080)}
)

picam2.configure("video")

encoder = H264Encoder()
output = FfmpegOutput('test.mp4')

# Set the fps
fps = 50
picam2.set_controls({"FrameRate": fps})

picam2.start_recording(encoder, output, quality=Quality.LOW)
time.sleep(5)
picam2.stop_recording()

total_frames = num_frames + dropped_frames
duration = (end_timestamp - start_timestamp) / 1e9
sensor_fps = total_frames / duration
recorded_fps = num_frames / duration
print("Total frames", total_frames)
print("Recorded frames", num_frames)
print("Dropped frames", dropped_frames)
print(f"Requested {fps}fps")
print(f"Sensor provided {sensor_fps:.1f}fps")
print(f"Recorded at {recorded_fps:.1f}fps")
print(f"Dropped {dropped_frames / total_frames * 100:.1f}% of frames")

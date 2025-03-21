import os
import argparse
import subprocess




"""
Extracts a segment of the video with a specified duration starting from a given point.
"""
def take_x_min(duration, input, output_path, start_point=0):
    """
    Extracts a segment of the video with a specified duration starting from a given point.

    Parameters:
        duration (int): The length of the video segment in minutes.
        input (str): The input video file path.
        output_path (str): The output video file path.
        start_point (int): The starting point in seconds. Default is 0.
    """
    duration_sec = 60 * int(duration)  # Convert duration to seconds
    start_point_sec= 60 * int(start_point)
    print(f"start_point in seconds: {start_point_sec}")
    out_dir = os.path.dirname(output_path)
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    # Build the ffmpeg command
    cmd = f"ffmpeg -i {input} -ss {start_point_sec} -t {duration_sec} -c copy {output_path}"
    
    # Execute the command
    os.system(cmd)
    
def get_fps(video_path):
    cmd=f"ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate {video_path}"
    fps = os.popen(cmd).read()
    return fps

def get_frame_count(video_path):
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-count_frames",
            "-show_entries", "stream=nb_read_frames",
            "-of", "default=nokey=1:noprint_wrappers=1",
            video_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise ValueError(f"ffprobe error: {result.stderr.strip()}")
        frame_count = result.stdout.strip()
        return int(frame_count)
    except Exception as e:
        print(f"Error: {e}")
        return None
    


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--duration", required=True, help="Duration of the video in minutes")
    argparser.add_argument("--start_point", type=int, required=True, help="Duration of the video in minutes")

    argparser.add_argument("--input", required=True, help="Path to the input video")
    argparser.add_argument("--output_path", required=True, help="Path to the output video")
    args=argparser.parse_args()
    duration = args.duration
    start_point = args.start_point
    input = args.input
    output_path = args.output_path
    
    take_x_min(duration,input,output_path,start_point)
    
    frame_count=get_frame_count(output_path)
    print(f"Frame count of new video: {frame_count}")
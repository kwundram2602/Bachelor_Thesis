import os
import argparse
import subprocess


def take_x_min(duration,input,output_path):
    
    duration_min=60*int(duration)
    out_dir=os.path.dirname(output_path)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    cmd=f"ffmpeg -i {input} -t {duration_min} -c copy {output_path}"
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
    argparser.add_argument("--input", required=True, help="Path to the input video")
    argparser.add_argument("--output_path", required=True, help="Path to the output video")
    args=argparser.parse_args()
    duration = args.duration
    input = args.input
    output_path = args.output_path
    
    take_x_min(duration,input,output_path)
    
    frame_count=get_frame_count(output_path)
    print(f"Frame count of new video: {frame_count}")
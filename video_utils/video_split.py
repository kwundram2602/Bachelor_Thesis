import sys, subprocess, datetime, argparse, math
#from moviepy.editor import VideoFileClip
import os
from create_path import create_path
#import cv2

"""
functions for splitting videos in batches. and converting them to frame count consistency
"""
def convert_to_frame_count_consistency(input_mp4:str,output_mp4:str):
    """
    Converts video so frame count consistency is guaranteed

    :param input_mp4: Path to mp4 file.
    :param output_mp4: path to output file e.g : video_converted.mp4 .
    """
    command= f"ffmpeg -i {input_mp4} -vcodec libx264 -acodec aac {output_mp4}"
    print("Processing : ",command,"\n")
    os.system(command)
    
def get_video_duration(video_path:str):
    """
    Returns duration of video in seconds

    :param video_path: Path to mp4 file.
    :return duration of video in seconds
    """
    #duration = VideoFileClip(video_path).duration
    #print(f"video is {duration} seconds long")
    #return duration

##accepts interval in seconds
##accepts video_path as .mp4 file
def time_split(video_path, interval:int):
    """
    Splits video in segments. Each segment has interval as its duration.
    Only works if frame count consistency is guaranteed

    :param video_path: Path to mp4 file.
    :param interval: interval in seconds. The video duration should be be divided by the interval without a remainder.
    """
    # total duration of video in seconds
    video_duration = get_video_duration(video_path)
    # total number of frames
    cap = cv2.VideoCapture(video_path)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print(f"Video has {total_frames} frames")
    
    if not(video_duration % interval == 0):
        raise ValueError("The video duration cannot be divided by the interval without a remainder.")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    # fps * interval_time = frame number for each split 
    frames_per_split=fps*interval
    frames_per_split=int(frames_per_split)
    print(f"{fps} frames per second")
    print(f"{frames_per_split} frames per split")
    
    # numbers of splits based on video duration and duration of one split
    loop_num = math.ceil(video_duration/float(interval))
    print("loop_num",loop_num)
    # format video duration with datetime
    video_duration = datetime.timedelta(seconds=video_duration) ##format video_duration
    print("video_duration",video_duration)
    # fomat interval with datetime
    interval_delta = datetime.timedelta(seconds=interval) ##format interval
    print("interval_delta",interval_delta)
    #initialize iteration count
    
    i = 0
    
    # split video 
    while i < loop_num:
        # starting position of split ( first split starts with 0 )
        position = datetime.timedelta(seconds=(interval*i))
        print("position",position)
        # new file name
        new_file = video_path.replace('.mp',(f"_chunk_{frames_per_split*i}_{frames_per_split*(i+1)}"+'.mp'))
        print("new_file",new_file)
        # ffmpeg command formatting
        command = 'ffmpeg -ss {0} -t {1} -i {2} -acodec copy -vcodec copy {3}'.format(position,interval_delta,video_path,new_file)
        print("command",command)
        #subprocess.Popen([command], shell=True, stdout=subprocess.PIPE).stdout.read()
        os.system(command)
        
        
        # update iteration counter
        i = i+1 
        # try
        # ffmpeg -i INPUT.mp4 -acodec copy -f segment -vcodec copy \ -reset_timestamps 1 -map 0 OUTPUT%d.mp4
        # or
        # ffmpeg -i "D:\Bachelorarbeit\data_split\Batch1\B1D1\B1D1_C1\B1D1_C1_ST0.mp4" -c copy -map 0 -segment_time 60 -f segment -reset_timestamps 1 "D:\Bachelorarbeit\video_%04d.mp4"
    
    #"D:\Bachelorarbeit\data_split\Batch1\B1D1\B1D1_C1_ST.mp4"
    # time split
    #  python ./yolo_utils/video_split.py --video_path "D:\Bachelorarbeit\data_split\Batch1\B1D1\B1D1_C1_ST_converted.mp4" --interval 50
    #  python ./yolo_utils/video_split.py --video_path "D:\Bachelorarbeit\data_split\Batch1\B1D1\B1D1_C1\B1D1_C1_ST0.mp4" --interval 50
    # convert:
    #python ./yolo_utils/video_split.py --video_path "D:\Bachelorarbeit\data_split\Batch1\B1D1\B1D1_C1_ST.mp4" --convert_output "D:\Bachelorarbeit\data_split\Batch1\B1D1\B1D1_C1_ST_converted.mp4"

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description='Split video ')
    parser.add_argument('--video_path',required=True,type=str, help='path to video')
    parser.add_argument('--convert_output',required=False, type=str, help='duration in seconds for each split ')
    parser.add_argument('--interval',required=False, type=int, help='duration in seconds for each split ')
    args = parser.parse_args()
    
    convenvert_dir= os.path.dirname(args.convert_output)
    create_path(convenvert_dir)
    convert_to_frame_count_consistency(args.video_path,args.convert_output)
    #get_video_duration(args.video_path)
    #time_split(args.video_path, args.interval)
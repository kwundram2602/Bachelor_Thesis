import cv2
import os
import argparse
import matplotlib.pyplot as plt
import re
import numpy as np
from datetime import datetime



def build_video_from_frames(frames_path,fps,output_video):
    
    frame_files = [f for f in os.listdir(frames_path) if f.endswith('.png')]
    frame_files = sorted(frame_files) 
    first_frame = cv2.imread(os.path.join(frames_path, frame_files[0]))
    height, width, layers = first_frame.shape
    # Define the video codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for .avi
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # Write each frame to the video
    for frame_file in frame_files:
        frame_path = os.path.join(frames_path, frame_file)
        frame = cv2.imread(frame_path)
        
        if frame is not None:
            video.write(frame)
        else:
            print(f"Warning: Could not read frame {frame_file}")

    # Release the video writer
    video.release()

    print(f"Video saved as {output_video}")
    
def get_fps(video_path):
    video = cv2.VideoCapture(video_path)

    # Check if the video file opened successfully
    if not video.isOpened():
        print("Error: Could not open video. FPS could not be read")
    else:
        # Get the FPS of the video
        fps = video.get(cv2.CAP_PROP_FPS)
        
    # Release the video object
    video.release()
    return fps
    
def get_frame_count(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return None

    # Get the frame count
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Release the video capture object
    cap.release()

    return frame_count

def count_detections(labels_folder,frame_folder,output_path,mean_factor,dw,dh):
    
    # Get the current date and time
    frames=sorted(os.listdir(frame_folder))
    nframes=len(frames)
    print(f"Number of frames: {nframes}")
    now = datetime.now()
    formatted_date = now.strftime("%H.%M.%S")  
    print("Formatted date:", formatted_date)
    masc_list=[]
    for i in range(0,nframes+1):
        masc = np.zeros((image_height,image_width),dtype = np.float32)
        masc_list.append(masc)
    print(f"Number of mascs: {len(masc_list)}")

    # for all label txt files
    for labeltxt in sorted(os.listdir(labels_folder)):
        match = re.search(r'\d+', labeltxt)  
        if match:
            frame_id = int(match.group())  # get frame id
        print(f"frame {frame_id}")
        masc=np.zeros((image_height,image_width),dtype = np.float32)
        
        with open(os.path.join(labels_folder, labeltxt), 'r') as file:
            data=file.readlines()
        # for line in text file
        for dt in data:

            # Split string to float
            #normalized center coordinates, w and h are the normalized width
            # and height of the bounding box
            _, x, y, w, h = map(float, dt.split(' '))
            # convert to pixel coordinates
            # left, right, top, bottom
            l = int((x - w / 2) * dw)
            r = int((x + w / 2) * dw)
            t = int((y - h / 2) * dh)
            b = int((y + h / 2) * dh)
            
            #ensure the bounding box coordinates do not exceed the image dimensions
            if l < 0:
                l = 0
            if r > dw - 1:
                r = dw - 1
            if t < 0:
                t = 0
            if b > dh - 1:
                b = dh - 1
            
            # add 1 from top to bottom , left to right
            masc[t:b,l:r]+=1
            # next line
        #next label file
        masc_list[frame_id]=masc
    cumsum_arrays = []
    current_cumsum = np.zeros_like(masc_list[0])
    for array in masc_list:
        current_cumsum += array
        cumsum_arrays.append(current_cumsum.copy()) 
    for idx, masc in enumerate(cumsum_arrays):
        print(f"Array {idx}: max={np.max(masc)}, contains inf: {np.isinf(masc).any()}")
    # normalize masc with maximum
    masc_u8_list=[]
    # max value of all mascs
    max_value=  max(np.max(masc) for masc in cumsum_arrays)
    print("max ",max_value)
    for masc in cumsum_arrays:
        masc_u8 = ((masc / max_value) * 256).astype(np.uint8)
        masc_u8_list.append(masc_u8)
        
    cmap_n=2
    divisor=2
    colorMap= cv2.applyColorMap(masc_u8 , cmap_n)
    # write image
    for masc_u8,frame in zip(masc_u8_list,frames):
        frame_file=os.path.join(frame_folder,frame)
        img=cv2.imread(frame_file)
        
        colorMap= cv2.applyColorMap(masc_u8 , cmap_n)
        # weaken color map
        colorMap=colorMap/divisor
        # merge color map with image
        merged_u8 = img+colorMap
        cv2.imwrite(os.path.join(output_path,"heatmap_"+f"{frame}"), colorMap)
        
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/heatmap_over_time.sh
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--labels_folder', type=str, required=True, help='path to label txts')
    parser.add_argument('--frame_folder', type=str, required=True, help='folder with extracted frames of video')
    parser.add_argument('--video_path', type=str, required=True, help='path to origin video')
    parser.add_argument('--output_path', type=str, required=True, help='path to label txts')
    parser.add_argument('--image_height', type=str, required=False, help='image_height')
    parser.add_argument('--image_width', type=str, required=False, help='image_width')
    
    args = parser.parse_args()
    labels_folder =args.labels_folder
    output_path=args.output_path
    image_height=1024
    image_width=1280
    frames=args.frame_folder
    count_detections(labels_folder,frames,output_path,0.025,image_width,image_height)
    video_path=args.video_path
    fps=get_fps(video_path)
    output_mp4=r"/scratch/tmp/kwundram/bcth/data/whole_data/heatmaps/heatmap_videos/heatmap.mp4"
    build_video_from_frames(output_path,fps,output_mp4)

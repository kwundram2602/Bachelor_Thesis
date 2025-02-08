import cv2
import os
import argparse
import matplotlib.pyplot as plt
import re
import numpy as np
from datetime import datetime

def create_path(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def extract_frames(video_path,output_folder):
    create_path(output_folder)
    cmd=f"ffmpeg -i {video_path} {output_folder}/frame%05d.png"
    os.system(cmd)
    
def detect_wrapper(detect_script,source,weight,confidence,image_size,project,name,aoi):
    print(f"aoi {aoi}")
    aoi_string = " ".join([f"{x[0]} {x[1]} {x[2]} {x[3]}" for x in aoi])
    print(f"aoi_string {aoi_string}")
    cmd =f"python {detect_script} --weights {weight} --conf {confidence} --img-size {image_size} --source {source} --save-txt --project {project} --name {name} --aoi {aoi_string}"
    os.system(cmd)
    
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
    # 0 to nframes
    for i in range(0,nframes+1):
        masc = np.zeros((image_height,image_width),dtype = np.float32)
        masc_list.append(masc)
    print(f"Number of mascs: {len(masc_list)}")

    # for all label txt files
    for labeltxt in sorted(os.listdir(labels_folder)):
        match = re.search(r'(\d+)\.txt$', labeltxt)  
        if match:
            frame_id = int(match.group(1))  # get frame id
        print(f" .txt  {labeltxt} has frame id {frame_id}")
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
        masc_u8 = ((masc / max_value) * 255).astype(np.uint8)
        masc_u8_list.append(masc_u8)
        
    cmap_n=2
    colorMap_factor=0.8
    # write image
    for masc_u8,frame in zip(masc_u8_list,frames):
        colorMap= cv2.applyColorMap(masc_u8 , cmap_n)

        frame_file=os.path.join(frame_folder,frame)
        frame_im=cv2.imread(frame_file)
        #print("frame ",frame)
        print(f"colorMap {colorMap.shape} frame_im {frame_im.shape}")
        
        alpha = 0.7
        beta = (1.0 - alpha)
        frame_mask_merged = cv2.addWeighted(frame_im, alpha, colorMap, beta, 0) 
        
        hm_frame=os.path.join(output_path,"heatmap_"+f"{frame}")
        print(f"Writing to {hm_frame}")
        cv2.imwrite(hm_frame, frame_mask_merged)
        
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/heatmap_over_time.sh
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--video_path', type=str, required=False, help='path to origin video')
    parser.add_argument('--frames_output_path', type=str, required=True, help='path to extracted frames. output for extraction and input for ')
    parser.add_argument('--output_path', type=str, required=True, help='output path for heatmap mascs')
    parser.add_argument('--image_height', type=str, required=False, help='image_height')
    parser.add_argument('--image_width', type=str, required=False, help='image_width')
    parser.add_argument('--weights', type=str, required=True, help='path to origin video')
    parser.add_argument('--confidence', type=str, required=True, help='object confidence threshold')
    parser.add_argument('--project', type=str, required=True, help='project')
    parser.add_argument('--name', type=str, required=True, help='name')
    parser.add_argument("--already_detected", action="store_true", help="Skip detection step if specified")
    parser.add_argument("--already_extracted", action="store_true", help="Skip extraction step if specified")
    parser.add_argument('--mp4_output', type=str, required=False, help='heat map video ouput path')
    parser.add_argument('--aoi', nargs='+', type=str, action='append', help='Area of Interest in [x_min, y_min, x_max, y_max] format')

    args = parser.parse_args()

    frames_output_path=args.frames_output_path    
    video_path=args.video_path
    already_extracted=args.already_extracted
    if already_extracted:
        print("Skipping extraction")
    else:
        print("Extracting ...")
        extract_frames(video_path,frames_output_path)
        print("Extraction done ...")
    
    weights=args.weights
    detect_script="/home/k/kwundram/bcth/Bachelor_Thesis/yolov7/detect_aoi.py"
    confidence=args.confidence
    image_height=1024
    image_width=1280
    project=args.project
    name=args.name
    
    already_detected=args.already_detected
    aoi = args.aoi
    if already_detected:
        print(f"Skipping detection for {frames_output_path}")
        print(f"Detection under {os.path.join(project,name)} ?")
    else:
        print(f"Detecting ... on frames in {frames_output_path}")
        print(f"Detection under {os.path.join(project,name)} ?")
        detect_wrapper(detect_script,frames_output_path,weights,confidence,image_height,project,name,aoi)
    
    output_path=args.output_path
    labels_folder=os.path.join(project,name,"labels")
    print(f"Labels folder: {labels_folder}")
    print("Creating Heatmap ...")
    count_detections(labels_folder,frames_output_path,output_path,0.025,image_width,image_height)
    
    #fps=get_fps(video_path)
    mp4_output=args.mp4_output
    
    print(f"Saving video to {mp4_output}")
    #build_video_from_frames(output_path,fps,mp4_output)


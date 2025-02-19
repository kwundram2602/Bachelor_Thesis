import os
import argparse
import matplotlib
import matplotlib.pyplot as plt
import re
import math

def count_objects_in_folder(folder_path):
    """
    Counts the number of detected objects for each frame label .txt file in folder path.
    Extracts frame number from file name. Text files should be named accordingly.
    """
    counts = {}
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".txt"):
            match = re.search(r'(\d+)\.txt$', filename)
            if match:
                frame_number = int(match.group(1))
                with open(os.path.join(folder_path, filename), 'r') as file:
                    count = sum(1 for line in file)
                counts[frame_number] = count
    return counts

def plot_counts_percentage(counts, save_path):
    """
    
    """
    total_counts = sum(counts.values())
    percentages = {frame: (count / total_counts) * 100 for frame, count in counts.items()}
    
    plt.figure()
    plt.plot(list(percentages.keys()), list(percentages.values()), marker='o')
    plt.xlabel('Frame')
    plt.ylabel('Percentage of Total Objects')
    plt.title('Percentage of Objects Detected Over Frames')
    plt.grid(True)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

def plot_counts_over_time(counts,groundtruth_count, save_path, n_subplots=1, highlight_threshold=5, highlight_frames=48, ncols=2):
    """
    Plots the number of detected objects framewise and compares woth ground truth if available."""
    #print(f"First {20} elements of counts: {list(counts.keys())[:20]}")
    frames = list(counts.keys())    
    print(f"first 10 frames: {frames[:10]}")
    counts_values = list(counts.values())
    ground_truth_counts_values = list(groundtruth_count.values())
    print(f"ground_truth_counts_values in function: {ground_truth_counts_values[:10]}")
    total_frames = len(frames)
    frames_per_subplot = total_frames // n_subplots

    nrows = (n_subplots + ncols - 1) // ncols  # Calculate the number of rows needed
    fig, axes = plt.subplots(nrows, ncols, figsize=(10 * ncols, 5 * nrows), sharex=False)
    axes = axes.flatten()  # Flatten the axes array for easy iteration
    # 0 ... n_subplots - 1
    for i in range(n_subplots):
        
        # start index of plot
        start_idx = (i * frames_per_subplot) + 1
        # end index of 
        end_idx = (i + 1) * frames_per_subplot +1 if i < n_subplots - 1 else total_frames
        print(f" i {i} start_idx: {start_idx}, end_idx: {end_idx}")
        # frame ids and counts as plot variables
        x = frames[start_idx:end_idx]
        y = counts_values[start_idx:end_idx]
        y_gt = ground_truth_counts_values[start_idx:end_idx]

        axes[i].plot(x, y, marker='o', linestyle='-', linewidth=0.5, markersize=1, color='blue')
        if groundtruth_count:
            axes[i].plot(x, y_gt, marker='o', linestyle='-', linewidth=0.5, markersize=1, color='green')
        axes[i].set_xlabel('Frame')
        axes[i].set_ylabel('Number of Objects')
        axes[i].set_title(f'Number of Objects Detected Over Frames (Part {i + 1})')
        axes[i].grid(True)
        y_ticks = range(0, 7, 1)  # Adjust the step size as needed
        axes[i].set_yticks(y_ticks)
        
        # Highlight segments where count value is below the threshold for a continuous number of frames
        below_threshold = [j for j in range(len(y)) if y[j] < highlight_threshold]
        segments = []
        current_segment = []

        for idx in below_threshold:
            if not current_segment or idx == current_segment[-1] + 1:
                current_segment.append(idx)
            else:
                if len(current_segment) >= highlight_frames:
                    segments.append(current_segment)
                current_segment = [idx]

        if len(current_segment) >= highlight_frames:
            segments.append(current_segment)

        for segment in segments:
            axes[i].plot([x[j] for j in segment], [y[j] for j in segment], marker='o', linestyle='-', linewidth=0.5, markersize=1, color='red')

        # Set x-axis ticks to show only a subset of frames
        x_ticks = frames[start_idx:end_idx]
        x_len=len(x_ticks)
        step=  max(1, x_len // 10)
        x_ticks_show= x_ticks[::step]
        print(f" x_ticks_show: {x_ticks_show}")
        axes[i].set_xticks(x_ticks_show)  

    # Hide any unused subplots
    for j in range(n_subplots, len(axes)):
        fig.delaxes(axes[j])

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

def yolo_to_image_coordinates(line, dw, dh):
    # Split string to float
    _, x, y, w, h = map(float, line.split(' '))

    l = int((x - w / 2) * dw)
    r = int((x + w / 2) * dw)
    t = int((y - h / 2) * dh)
    b = int((y + h / 2) * dh)
    
    if l < 0:
        l = 0
    if r > dw - 1:
        r = dw - 1
    if t < 0:
        t = 0
    if b > dh - 1:
        b = dh - 1
    return l, r, t, b
def is_in_aoi(cx, cy, aoi, tolerance=1):
    
    x_min, y_min, x_max, y_max = aoi

    return (x_min - tolerance <= cx <= x_max + tolerance) and \
           (y_min - tolerance <= cy <= y_max + tolerance)
                
# aoi : x_min, y_min, x_max, y_max  
def count_in_aoi(labels_folder, aois, dw, dh):    
    aoi_dict={}
    if aois[0][0] < aois[1][0]:
        aoi_dict['left'] = aois[0]
        aoi_dict['right'] = aois[1]
    elif aois[0][0] > aois[1][0]:
        aoi_dict['right'] = aois[0]
        aoi_dict['left'] = aois[1]
    else:
        print("Invalid AOIs")
        print(aois)
        return
    aoi_counts = {"left": 0 , "right": 0}
    outside_aoi_count = 0

    for filename in os.listdir(labels_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(labels_folder, filename), 'r') as file:
                for line in file:
                    l, r, t, b = yolo_to_image_coordinates(line, dw, dh)
                    center_x = (l + r) / 2
                    center_y = (t + b) / 2

                    assigned = False
                    # ymin xmin ymax xmax
                    
                    if is_in_aoi(center_x, center_y, aoi_dict['left']):
                        print(f"line: {line} in left AOI \n")
                        aoi_counts["left"] += 1
                        assigned = True
                        break
                    
                    if is_in_aoi(center_x, center_y, aoi_dict['right']):
                        print(f"line: {line} in right AOI \n")
                        aoi_counts["right"] += 1
                        assigned = True
                        break

                    if not assigned:
                        print(f" Object found outside AOIs in line: {line} in file {filename} \n")
                        print(f"center_x: {center_x}, center_y: {center_y}")
                        print(f"left AOI: {aoi_dict['left']}, right AOI: {aoi_dict['right']}")
                        outside_aoi_count += 1

    return aoi_counts, outside_aoi_count

def aoi_count_framewise(labels_folder,aois,dw,dh):
    aoi_dict={}
    print(f" aois {aois}")
    if aois[0][0] < aois[1][0]:
        aoi_dict['left'] = aois[0]
        aoi_dict['right'] = aois[1]
    elif aois[0][0] > aois[1][0]:
        aoi_dict['right'] = aois[0]
        aoi_dict['left'] = aois[1]
    else:
        print("Invalid AOIs")
        print(aois)
        return
    aoi_counts = {"left": {} , "right": {}}
    outside_aoi_count= {}
    # iterate over frames 
    # need to get frame id
    for filename in sorted(os.listdir(labels_folder)):
        if filename.endswith(".txt"):
            if filename.endswith(".txt"):
                match = re.search(r'(\d+)\.txt$', filename)
            if match:
                frame_number = int(match.group(1))
            else:
                print(f"could not get frame number from match {match} ")
                continue
            if frame_number not in aoi_counts["left"]:
                aoi_counts["left"][frame_number] = 0
            if frame_number not in aoi_counts["right"]:
                aoi_counts["right"][frame_number] = 0
            if frame_number not in outside_aoi_count:
                outside_aoi_count[frame_number] = 0
            with open(os.path.join(labels_folder, filename), 'r') as file:
                for line in file:
                    l, r, t, b = yolo_to_image_coordinates(line, dw, dh)
                    center_x = (l + r) / 2
                    center_y = (t + b) / 2
                    assigned=False
                    if is_in_aoi(center_x, center_y, aoi_dict['left']):
                        print(f"line: {line} in left AOI \n")
                        aoi_counts["left"][frame_number]+= 1
                        assigned = True
                        break
                    
                    if is_in_aoi(center_x, center_y, aoi_dict['right']):
                        print(f"line: {line} in right AOI \n")
                        aoi_counts["right"][frame_number] += 1
                        assigned = True
                        break
                    if not assigned:
                        #print(f" Object found outside AOIs in line: {line} in file {filename} \n")
                        #print(f"center_x: {center_x}, center_y: {center_y}")
                        #print(f"left AOI: {aoi_dict['left']}, right AOI: {aoi_dict['right']}")
                        outside_aoi_count[frame_number] += 1
                     
                print(f' frame {frame_number}: left {aoi_counts["left"][frame_number]}, right {aoi_counts["right"][frame_number]}')
        print(f"aoi_counts,outside_aoi_count : {aoi_counts['left'][frame_number],aoi_counts['right'][frame_number],outside_aoi_count[frame_number]}")  
    return aoi_counts,outside_aoi_count

def frame_id_to_timestamp(frame_id,fps=24):
    
    seconds = frame_id / fps
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{int(minutes):02}:{seconds:02.0f}"

def majority(iterable, fraction=0.90):
    """
    Returns True if the proportion of True values in the iterable
    is >= fraction.
    """
    values = list(iterable)  
    num_true = sum(values)   
    return num_true >= fraction * len(values)

def check_for_pipe_event(aoi_counts, counts, x=24):
    pipe_events = {"left": {}, "right": {}}
    last_frame= max(counts.keys())
    print(f"last_frame: {last_frame}")
    pipe_events["left"] = {key: 0 for key in aoi_counts["left"].keys()}
    pipe_events["right"] = {key: 0 for key in aoi_counts["right"].keys()}
    for i in range(1, len(counts) - x):
        if majority((i + j in counts and i in counts and counts[i] > counts[i + j] for j in range(1, x + 1)),fraction=0.90):
            #print(f"count decrease from frame {i} to frame {i + 1} ")
            if majority((i + j in aoi_counts["right"] and i in aoi_counts["right"] and aoi_counts["right"][i] > aoi_counts["right"][i + j] for j in range(1, x + 1)), fraction=0.90):
                print(f" Decrease in right AOI in frame {i} to frame {i + 1} --> {frame_id_to_timestamp(i)}")
                pipe_events["right"][i + 1] += 1
            if majority((i + j in aoi_counts["left"] and i in aoi_counts["left"] and aoi_counts["left"][i] > aoi_counts["left"][i + j] for j in range(1, x + 1)),fraction=0.90):
                print(f" Decrease in left AOI in frame {i} to frame {i + 1}--> {frame_id_to_timestamp(i)}")
                pipe_events["left"][i + 1] += 1

    return pipe_events

def time_stamp_to_frame_id(time_stamp,fps=24):
    time = time_stamp.split(':')
    #print(f"time: {time}")
    minutes = int(time[0])
    seconds = int(time[1])
    frame_id = (minutes * 60 + seconds) * fps
    return frame_id
def plot_pipe_events(pipe_events,gt_pipe_events, output_path,precision,recall):
    frames_left = list(pipe_events["left"].keys())
    events_left = list(pipe_events["left"].values())
    frames_right = list(pipe_events["right"].keys())
    events_right = list(pipe_events["right"].values())

    frames_with_events_left = [frame for frame, event in pipe_events["left"].items() if event > 0] 
    frames_with_events_right = [frame for frame, event in pipe_events["right"].items() if event > 0]
    
  
    timestamps_left = list(frame_id_to_timestamp(i) for i in frames_with_events_left)
    timestamps_right = list(frame_id_to_timestamp(i) for i in frames_with_events_right)
    # Count the number of instances where pipe events are not 0
    non_zero_pipe_events_left =[event for event in events_left if event != 0]
    non_zero_pipe_events_right = [event for event in events_right if event != 0]
    non_zero_pipe_events_left_count = sum(event for event in events_left if event != 0)
    non_zero_pipe_events_right_count = sum(event for event in events_right if event != 0)
    # Remove duplicate timestamps and adjust events
    unique_timestamps_left = {}
    frames_with_events_left_adjusted = []
    non_zero_pipe_events_left_adjusted = []

    for frame, event, timestamp in zip(frames_with_events_left, non_zero_pipe_events_left, timestamps_left):
        if timestamp in unique_timestamps_left:
            # Add +1 to the corresponding event
            non_zero_pipe_events_left_adjusted[unique_timestamps_left[timestamp]] += 1
        else:
            unique_timestamps_left[timestamp] = len(non_zero_pipe_events_left_adjusted)
            frames_with_events_left_adjusted.append(frame)
            non_zero_pipe_events_left_adjusted.append(event)
    frames_with_events_left = frames_with_events_left_adjusted
    non_zero_pipe_events_left = non_zero_pipe_events_left_adjusted
    
    # right aoi
    unique_timestamps_right = {}
    frames_with_events_right_adjusted = []
    non_zero_pipe_events_right_adjusted = []
    for frame, event, timestamp in zip(frames_with_events_right, non_zero_pipe_events_right, timestamps_right):
        if timestamp in unique_timestamps_right:
            # Add +1 to the corresponding event
            non_zero_pipe_events_right_adjusted[unique_timestamps_right[timestamp]] += 1
        else:
            unique_timestamps_right[timestamp] = len(non_zero_pipe_events_right_adjusted)
            frames_with_events_right_adjusted.append(frame)
            non_zero_pipe_events_right_adjusted.append(event)

    frames_with_events_right = frames_with_events_right_adjusted
    non_zero_pipe_events_right = non_zero_pipe_events_right_adjusted
    
    plt.figure()
    plt.ylim(0, 5)
    plt.scatter(frames_with_events_left, non_zero_pipe_events_left,s=30,alpha=0.5, color='blue', label='Left AOI')
    plt.scatter(frames_with_events_right, non_zero_pipe_events_right,s=30,alpha=0.5, color='green', label='Right AOI')
    plt.xlabel('Frame')
    plt.ylabel('Number of Pipe Events')
    plt.title('Pipe Events Detected Over Frames')
    plt.legend()
    plt.grid(True)
    
    # Add text for total number of events
    plt.text(0.05, 0.95, f'Detected events left AOI: {non_zero_pipe_events_left_count}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', color='blue')
    plt.text(0.05, 0.90, f'Detected events in right AOI: {non_zero_pipe_events_right_count}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', color='green')
    plot_time = False
    for i, (txt, event_left) in enumerate(zip(unique_timestamps_left, non_zero_pipe_events_left)):    
        vorzeichen = -1 if i % 2 == 0 else 1
        #y = 2.0 +  0.4 * math.sin(i)
        y = event_left + +0.5 + 0.2* i
        x = frames_with_events_left[i]
        #print(f"frames_with_events_left[i], {frames_with_events_left[i]}")
        
        try:
            if non_zero_pipe_events_left_count < 40 and non_zero_pipe_events_right_count < 40 and plot_time:
                plt.text(x,y, txt, fontsize=8, ha='center', color='blue')
        except Exception as e:
            print(f"Error : {e}")

    for i, (txt, event_right) in enumerate(zip(unique_timestamps_right, non_zero_pipe_events_right)):
        vorzeichen= -1**i #(0.15*vorzeichen)
        #y = 3.5 + 0.4*math.sin(i)
        y = event_right +0.5 + 0.2 *i
        x = frames_with_events_right[i]
        if non_zero_pipe_events_right_count < 40 and non_zero_pipe_events_left_count < 40 and plot_time:
            plt.text(x,y, txt, fontsize=8, ha='center', color='green')
    
    timestamps_x= [time_stamp_to_frame_id(time_stamp) for time_stamp in gt_pipe_events]
    number_gt_pipe_events = len(gt_pipe_events)
    plt.text(0.05, 0.85, f'Total ground truth events: {number_gt_pipe_events}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', color='red')
    for i, txt in enumerate(gt_pipe_events):
        vorzeichen = -1 if i % 2 == 0 else 1
        #y = 3.0 + 0.5 * math.sin(i)*vorzeichen
        y = 1 
        x = timestamps_x[i]
        plt.scatter(x, y, color='red', s=30,alpha=0.5, marker='o')
        if plot_time:
            ytxt =0.5 - 0.2 * vorzeichen
            plt.text(x,ytxt, txt, fontsize=8, ha='center', color='red')
    plt.text(0.05, 0.80, f'Recall: {recall} %', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', color='orange')
    plt.text(0.05, 0.75, f'Precision: {precision} %', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', color='black')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path)
    #plt.show()
   
def plot_aoi_counts(aoi_counts, outside_aoi_count,ymax, save_path):
    labels = list(aoi_counts.keys()) + ['Outside AOIs']
    counts = list(aoi_counts.values()) + [outside_aoi_count]

    plt.figure()
    plt.bar(labels, counts, color=['blue', 'green', 'red'])
    plt.xlabel('AOI')
    plt.ylabel('Number of Objects')
    plt.title('Number of Objects Detected in Each AOI')
    plt.ylim(top= ymax) 
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

def time_stamp_to_seconds(time_stamp):
    """Converts a time stamp in the format MM:SS to total seconds."""
    minutes, seconds = map(float, time_stamp.split(':'))
    return minutes * 60 + seconds

def compare_time_stamps(ground_truth, predicted, tolerance=2):
    """
    Compares two lists of time stamp strings. 
    A predicted time stamp is considered a true prediction if it exactly matches
    a ground truth time stamp or if it differs by at most 'tolerance' seconds.
    
    Returns:
        true_predictions: List of predicted time stamps considered true predictions.
        false_predictions: List of predicted time stamps that did not match.
    """
    true_predictions = []
    false_predictions = []
    
    # Convert ground truth time stamps to seconds once
    gt_seconds = [time_stamp_to_seconds(ts) for ts in ground_truth]
    
    for pred in predicted:
        pred_sec = time_stamp_to_seconds(pred)
        # Find any ground truth time stamp within the tolerance range (inclusive)
        if any(abs(pred_sec - gt_sec) <= tolerance for gt_sec in gt_seconds):
            true_predictions.append(pred)
        else:
            false_predictions.append(pred)
    
    return true_predictions, false_predictions
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--folder_path", required=True, help="Path to the folder containing the label files")
    argparser.add_argument("--ground_truth", required=False, help="Path to ground truth folder")
    argparser.add_argument("--output_path", required=True, help="Path to the output file")
    argparser.add_argument("--plot_type", required=True, choices=['percentage', 'count','aoi_cb','aoi'], help="Type of plot to generate")
    argparser.add_argument("--highlight_threshold", type=int, default=5, help="Threshold for highlighting segments")
    argparser.add_argument("--highlight_frames", type=int, default=120, help="Number of frames to highlight")
    argparser.add_argument("--dw", required=False, type=int, help="Width of the image")
    argparser.add_argument("--dh", required=False, type=int, help="Height of the image")
    argparser.add_argument('--aois', nargs='+', type=int,action='append', help='Area of Interest in [x_min, y_min, x_max, y_max] format')
    argparser.add_argument('--gt_pipe_events',nargs='+', type=str, action="append", required=False, help='time stamps for events where fish enters pipe')

    args = argparser.parse_args()

    highlight_threshold = args.highlight_threshold
    highlight_frames = args.highlight_frames
    folder_path = args.folder_path
    # object counts for every frame
    counts = count_objects_in_folder(folder_path)
    ground_truth = args.ground_truth
    ground_truth_counts = count_objects_in_folder(ground_truth) if ground_truth else None
    print(f"ground_truth_counts: {ground_truth_counts}")
    if not os.path.exists(args.output_path):
        os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    if args.plot_type == 'percentage':
        plot_counts_percentage(counts, save_path=args.output_path)
    elif args.plot_type == 'count':
        plot_counts_over_time(counts,ground_truth_counts, save_path=args.output_path,n_subplots=2, highlight_threshold=5, highlight_frames=highlight_frames, ncols=2)
        
    elif args.plot_type == 'aoi':
        aois = args.aois
        print(f"AOIs: {aois}")
        aoi_counts, outside_aoi_count = count_in_aoi(folder_path, aois, args.dw, args.dh)

        print(f"AOI counts: {aoi_counts}")
        print(f"Detections outside AOIs: {outside_aoi_count}")
        plot_aoi_counts(aoi_counts, outside_aoi_count,11000, args.output_path)
        
    elif args.plot_type== 'aoi_cb':
        gt_pipe_events=args.gt_pipe_events
        gt_pipe_events = [x[0] for x in gt_pipe_events]
        
        aois = args.aois
        aoi_counts,outside_aoi_count = aoi_count_framewise(folder_path,aois,args.dw, args.dh)
        xframes=18
        pipe_events=check_for_pipe_event(aoi_counts,counts,xframes)
        non_zero_pipe_events_left = {frame: event for frame, event in pipe_events["left"].items() if event != 0}
        non_zero_pipe_events_right = {frame: event for frame, event in pipe_events["right"].items() if event != 0}
        for frame, event in non_zero_pipe_events_left.items():
            timestamp = frame_id_to_timestamp(frame)
            print(f"Left AOI - Frame {frame} ({timestamp}): {event} events")
        for frame, event in non_zero_pipe_events_right.items():
            timestamp = frame_id_to_timestamp(frame)
            print(f"Right AOI - Frame {frame} ({timestamp}): {event} events")
            
        print("gt_pipe_events",gt_pipe_events)
        print(f"pipe_events_left: {non_zero_pipe_events_left}")
        print(f"pipe_events_right: {non_zero_pipe_events_right}")
        
        true_right, false_right = compare_time_stamps(gt_pipe_events, [frame_id_to_timestamp(frame) for frame in non_zero_pipe_events_right.keys()], tolerance=2)
        true_left, false_left = compare_time_stamps(gt_pipe_events, [frame_id_to_timestamp(frame) for frame in non_zero_pipe_events_left.keys()], tolerance=2)
        tp=len(true_right) + len(true_left)
        fp=len(false_right) + len(false_left)
        
        print(f"True right: {true_right}")
        print(f"True left: {true_left}")
        print(f"True positives: {tp}")
        print(f"False positives: {fp}")
        fn = len(gt_pipe_events) - tp
        print(f"False negatives: {fn}")
        precision = tp / (tp + fp)
        precision = round(precision * 100, 2)
        recall = tp / (tp + fn)
        recall = round(recall * 100, 2)
        print(f"Precision: {precision}")
        print(f"Recall: {recall}")
        if args.output_path.endswith('.png'):
            output = args.output_path.replace('.png', f'_{xframes}.png')
        else:
            output = args.output_path 
        plot_pipe_events(pipe_events,gt_pipe_events,output,precision,recall)
        #print(f"pipe_events,{pipe_events}")
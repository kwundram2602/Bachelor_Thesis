import os
import argparse
import matplotlib.pyplot as plt
import re

def count_objects_in_folder(folder_path):
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
    
    #print(f"First {20} elements of counts: {list(counts.keys())[:20]}")
    frames = list(counts.keys())
    counts_values = list(counts.values())
    ground_truth_counts_values = list(groundtruth_count.values())
    print(f"ground_truth_counts_values in function: {ground_truth_counts_values}")
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
        # frame ids and counts as plot variables
        x = frames[start_idx:end_idx]
        y = counts_values[start_idx:end_idx]
        y_gt = ground_truth_counts_values[start_idx:end_idx]

        axes[i].plot(x, y, marker='o', linestyle='-', linewidth=0.5, markersize=1, color='blue')
        axes[i].plot(x, y_gt, marker='o', linestyle='-', linewidth=0.5, markersize=1, color='green')
        axes[i].set_xlabel('Frame')
        axes[i].set_ylabel('Number of Objects')
        axes[i].set_title(f'Number of Objects Detected Over Frames (Part {i + 1})')
        axes[i].grid(True)
        
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
        axes[i].set_xticks(x_ticks[::max(1, len(x_ticks)//10)])  # Show only 10 ticks or fewer

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

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--folder_path", required=True, help="Path to the folder containing the label files")
    argparser.add_argument("--ground_truth", required=False, help="Path to ground truth folder")
    argparser.add_argument("--output_path", required=True, help="Path to the output file")
    argparser.add_argument("--plot_type", required=True, choices=['percentage', 'count','aoi'], help="Type of plot to generate")
    argparser.add_argument("--highlight_threshold", type=int, default=5, help="Threshold for highlighting segments")
    argparser.add_argument("--highlight_frames", type=int, default=120, help="Number of frames to highlight")
    argparser.add_argument("--dw", required=False, type=int, help="Width of the image")
    argparser.add_argument("--dh", required=False, type=int, help="Height of the image")
    argparser.add_argument('--aois', nargs='+', type=int, action='append', help='Area of Interest in [x_min, y_min, x_max, y_max] format')

    args = argparser.parse_args()

    highlight_threshold = args.highlight_threshold
    highlight_frames = args.highlight_frames
    folder_path = args.folder_path
    counts = count_objects_in_folder(folder_path)
    ground_truth = args.ground_truth
    ground_truth_counts = count_objects_in_folder(ground_truth) if ground_truth else None
    print(f"ground_truth_counts: {ground_truth_counts}")
    if not os.path.exists(args.output_path):
        os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    if args.plot_type == 'percentage':
        plot_counts_percentage(counts, save_path=args.output_path)
    elif args.plot_type == 'count':
        plot_counts_over_time(counts,ground_truth_counts, save_path=args.output_path,n_subplots=4, highlight_threshold=5, highlight_frames=highlight_frames, ncols=2)
        
    elif args.plot_type == 'aoi':
        aois = args.aois
        print(f"AOIs: {aois}")
        aoi_counts, outside_aoi_count = count_in_aoi(args.folder_path, aois, args.dw, args.dh)

        print(f"AOI counts: {aoi_counts}")
        print(f"Detections outside AOIs: {outside_aoi_count}")
        plot_aoi_counts(aoi_counts, outside_aoi_count,11000, args.output_path)
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

def plot_counts_over_time(counts, save_path, n_subplots=1, highlight_threshold=5, highlight_frames=48, ncols=2):
    frames = list(counts.keys())
    counts_values = list(counts.values())
    total_frames = len(frames)
    frames_per_subplot = total_frames // n_subplots

    nrows = (n_subplots + ncols - 1) // ncols  # Calculate the number of rows needed
    fig, axes = plt.subplots(nrows, ncols, figsize=(10 * ncols, 5 * nrows), sharex=False)
    axes = axes.flatten()  # Flatten the axes array for easy iteration

    for i in range(n_subplots):
        start_idx = i * frames_per_subplot
        end_idx = (i + 1) * frames_per_subplot if i < n_subplots - 1 else total_frames
        x = frames[start_idx:end_idx]
        y = counts_values[start_idx:end_idx]

        axes[i].plot(x, y, marker='o', linestyle='-', linewidth=0.5, markersize=1, color='blue')
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

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--folder_path", required=True, help="Path to the folder containing the label files")
    argparser.add_argument("--output_path", required=True, help="Path to the output file")
    argparser.add_argument("--plot_type", required=True, choices=['percentage', 'count'], help="Type of plot to generate")
    argparser.add_argument("--highlight_threshold", type=int, default=5, help="Threshold for highlighting segments")
    argparser.add_argument("--highlight_frames", type=int, default=120, help="Number of frames to highlight")
    args = argparser.parse_args()
    
    highlight_threshold = args.highlight_threshold
    highlight_frames = args.highlight_frames
    folder_path = args.folder_path
    counts = count_objects_in_folder(folder_path)
    
    if args.plot_type == 'percentage':
        plot_counts_percentage(counts, save_path=args.output_path)
    elif args.plot_type == 'count':
        plot_counts_over_time(counts, save_path=args.output_path,n_subplots=4, highlight_threshold=5, highlight_frames=highlight_frames, ncols=2)
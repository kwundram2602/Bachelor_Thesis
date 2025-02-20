from interpolate_detections import match_bounding_boxes_hungarian,read_yolo_file
import argparse
import os
import random

def get_x_colors(n_colors):
    
    return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n_colors)]
def track_bounding_boxes(detections,dw,dh,png_dir,max_misses=10):
    tracks = {}  # track_id -> track_state (e.g., current bounding box, missed count, etc.)
    next_track_id = 0
    
    for frame_id,frame_det in enumerate(detections):
        track_boxes = [tracks[tid][frame_id]['bbox'] for tid in tracks]
        n_det= len(frame_det)
        print(f"track_boxes, {track_boxes}")
        matches = match_bounding_boxes_hungarian(track_boxes, frame_det, dw, dh, max_dist=50)
        print(f"matches, {matches}")
        # 4. Update matched tracks
        matched_track_ids = set()
        matched_detection_ids = set()
        # matches has track index as key and detection index as value
        for track_idx, det_idx in matches.items():
            track_id = list(tracks.keys())[track_idx]  # get track id corresponding to the index
            tracks[track_id][frame_id]['bbox']  = frame_det[det_idx]
            tracks[track_id]['missed'] = 0  # reset missed count
            matched_track_ids.add(track_id)
            matched_detection_ids.add(det_idx)

        # 5. For tracks that were not matched, increase the missed count
        for track_id in list(tracks.keys()):
            if track_id not in matched_track_ids:
                tracks[track_id]['missed'] += 1
                # Remove track if missed for too many consecutive frames
                if tracks[track_id]['missed'] > max_misses:
                    del tracks[track_id]

        # 6. For detections that were not matched, create new tracks
        for det_idx, det in enumerate(frame_det):
            if det_idx not in matched_detection_ids:
                tracks[next_track_id] = {'bbox': det, 'missed': 0}
                next_track_id += 1
    colors = get_x_colors(len(tracks))
    for frame in sorted(os.listdir(png_dir)):
        frame_path=os.path.join(png_dir,frame)
    return tracks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--label_folder', type=str, required=True,help='Path to folder containing YOLO label files.')
    parser.add_argument('--pngs', type=str, required=True,help='Path to folder containing PNG files.')
    args=parser.parse_args()
    label_folder = args.label_folder
    label_folder="/scratch/tmp/kwundram/bcth/runs/test_track/labels"
    png_dir=args.pngs
    
    label_files = []
    for file in sorted(os.listdir(label_folder)):
        if file.endswith(".txt"):
            file_path = os.path.join(label_folder, file)
            
            label_files.append(file_path)
            
    print(label_files[:8])
    all_detections = [read_yolo_file(f) for f in sorted(label_files)]
    tracks=track_bounding_boxes(all_detections, 1280, 1024,png_dir,10)
    print(tracks)
    

from interpolate_detections import match_bounding_boxes_hungarian,read_yolo_file,yolo_to_image_coordinates
import argparse
import os
import random
import cv2
def get_bbox_center(det,dw,dh):
    _, x, y, w, h = det
    l,r,t,b=yolo_to_image_coordinates(x,y,w,h,dw,dh)
    x_c=(l+r)/2
    y_c=(t+b)/2
    return x_c,y_c
def get_x_colors(n_colors):
    
    return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n_colors)]

def del_det_from_txt(label_file,output_file,det):
    _, x, y, w, h = det
    det_string = f"{_} {x} {y} {w} {h}\n"
    with open(label_file, "r") as f:
        lines = f.readlines()
    with open(output_file, "w") as f:
        for line in lines:
            
            if line.strip() != det_string.strip():
                f.write(line)
            else:
                print(f"deleted {det_string} from {label_file}")
                
def del_short_tracks(tracks, min_length,label_files,output_folder):
    for tid in list(tracks.keys()):
        if len(tracks[tid]['bboxes']) < min_length:
            print(f"deleting track {tid} with length {len(tracks[tid]['bboxes'])}")
            for frame_id in tracks[tid]['bboxes']:
                label_file = label_files[frame_id]
                det = tracks[tid]['bboxes'][frame_id]
                del_det_from_txt(label_file,output_folder, det)
            
def track_bounding_boxes(detections,dw,dh,png_dir,max_dist,max_misses):
    print(f"max_dist {max_dist} max_misses {max_misses}")
    tracks = {}  # track_id -> track_state (e.g., current bounding box, missed count, etc.)
    next_track_id = 0
    
    for frame_id,frame_det in enumerate(detections):
        track_boxes = []
        track_ids = []
        for tid in tracks:
            # Get the most recent bounding box by taking the maximum frame key
            last_frame = max(tracks[tid]['bboxes'].keys())
            track_boxes.append(tracks[tid]['bboxes'][last_frame])
            track_ids.append(tid)
        #track_boxes = [tracks[tid]['bboxes'][frame_id-1] for tid in tracks]
        n_det= len(frame_det)
        #print(f"track_boxes, {track_boxes}")    
        matches = match_bounding_boxes_hungarian(track_boxes, frame_det, dw, dh, max_dist=max_dist)
        #print(f"matches, {matches}")
        # 4. Update matched tracks
        matched_track_ids = set()
        matched_detection_ids = set()
        # matches has track index as key and detection index as value
        # track_idx is index of bounding box from track_boxes
        for track_idx, det_idx in matches.items():
            # get track_id that belongs to track_idx_bbox
            track_id = list(tracks.keys())[track_idx]  
            # then the new bounding box with index det_idx is assigned to that track
            tracks[track_id]['bboxes'][frame_id] = frame_det[det_idx]
            tracks[track_id]['missed'] = 0  # reset missed count
            matched_track_ids.add(track_id)
            matched_detection_ids.add(det_idx)

        # For tracks that were not matched, increase the missed count
        for track_id in list(tracks.keys()):
            if track_id not in matched_track_ids:
                tracks[track_id]['missed'] += 1
                # Remove track if missed for too many consecutive frames
                if tracks[track_id]['missed'] > max_misses:
                    print(f"deleting track {track_id} with missed count {tracks[track_id]['missed']}")
                    del tracks[track_id]

        # For detections that were not matched, create new tracks
        # iterate over detections in frame
        for det_idx, det in enumerate(frame_det):
            if det_idx not in matched_detection_ids:
                tracks[next_track_id] = {'bboxes': {frame_id: det}, 'missed': 0}
                next_track_id += 1
    
    max_track_id=max(tracks.keys())
    colors = get_x_colors(max_track_id+1)
    print(f"number of tracks {len(tracks)} number of colors {len(colors)}")
    # draw x,y center of bounding box to every frame with track specific color
    frames=[frame for frame in sorted(os.listdir(png_dir)) if frame.endswith(".png")]
    last_frame = frames[-1]
    last_frame_path=os.path.join(png_dir,last_frame)
    last_frame_im=cv2.imread(last_frame_path)
    for idx, frame in enumerate(frames):
        frame_path=os.path.join(png_dir,frame)
        frame_im=cv2.imread(frame_path)
        
        for tid in tracks:
            if idx not in tracks[tid]['bboxes']:
                continue
            else:
                x,y = get_bbox_center(tracks[tid]['bboxes'][idx],dw,dh)
                point = (int(x),int(y))
                #print(f"tid {tid}")
                cv2.circle(frame_im,point , 5, colors[tid], 3)
                
                cv2.circle(last_frame_im,point , 1, colors[tid], 1)
                output_dir=os.path.join(png_dir,"tracked")
                output_path=os.path.join(output_dir,frame)
                #cv2.imwrite(output_path,frame_im)
    n_tracks=len(tracks)
    cv2.putText(frame_im, str(n_tracks), (dw//2, dh//4), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    last_frame_output_path=os.path.join(output_dir,f"trajectories_dist{max_dist}_miss{max_misses}.png")
    cv2.imwrite(last_frame_output_path,last_frame_im)
    return tracks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--label_folder', type=str, required=True,help='Path to folder containing YOLO label files.')
    parser.add_argument('--pngs', type=str, required=True,help='Path to folder containing PNG files.')
    parser.add_argument('--output_folder', type=str, required=True,help='Path to output folder for text labels without short trajectories.')

    args=parser.parse_args()
    label_folder = args.label_folder
    png_dir=args.pngs
    
    label_files = []
    for file in sorted(os.listdir(label_folder)):
        if file.endswith(".txt"):
            file_path = os.path.join(label_folder, file)
            
            label_files.append(file_path)
            
    print(label_files[:8])
    all_detections = [read_yolo_file(f) for f in sorted(label_files)]
    print(f"all_detections, {all_detections[:8]}")
    tracks=track_bounding_boxes(all_detections, 1280, 1024,png_dir,160,20000)
    print(tracks)
    print(f" number of tracks",len(tracks))
    
    for tid in tracks:
        track_len=len(tracks[tid]['bboxes'])
        print(f"track {tid} length {track_len}")
        n_missed=tracks[tid]['missed']
        print(f"track {tid} missed {n_missed} times")
    
    output_folder=args.output_folder
    #del_short_tracks(tracks, 24, label_files,output_folder)
    

import os
import glob
import math
import argparse


def yolo_to_image_coordinates(x, y, w, h, dw, dh):
   
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

def read_yolo_file(filepath):
    """
    Reads a YOLO label file and returns a list of (class_id, x, y, w, h).
    """
    detections = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            class_id = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            w = float(parts[3])
            h = float(parts[4])
            detections.append((class_id, x, y, w, h))
    return detections

def write_yolo_file(filepath, detections):
    """
    Writes the list of detections to a YOLO label file.
    """
    with open(filepath, 'w') as f:
        for det in detections:
            class_id, x_c, y_c, w, h = det
            f.write(f"{class_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")

def pixel_center_distance(b1, b2, dw, dh):
    """
    Computes Euclidean distance between the centers of two YOLO bboxes:
      b1, b2 = (class_id, x, y, w, h)
    """
    # Unpack the YOLO tuples (ignore the class_id for distance)
    _, x1, y1, w1, h1 = b1
    _, x2, y2, w2, h2 = b2

    l1, r1, t1, b1 = yolo_to_image_coordinates(x1, y1, w1, h1, dw, dh)
    l2, r2, t2, b2 = yolo_to_image_coordinates(x2, y2, w2, h2, dw, dh)
    
    cx1 = (l1 + r1) / 2.0
    cy1 = (t1 + b1) / 2.0
    cx2 = (l2 + r2) / 2.0
    cy2 = (t2 + b2) / 2.0
    
    return math.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)


def match_bounding_boxes_pixel(detsA, detsB, dw, dh):
    """
    Greedy match of bounding boxes from detsA to detsB based on minimal pixel-center distance.
    detsA, detsB = [(class_id, x, y, w, h), ...]
    Returns a dict: index_in_A -> index_in_B
    """
    usedB = set()
    matches = {}
    
    for i, boxA in enumerate(detsA):
        best_idx = None
        best_dist = float('inf')
        for j, boxB in enumerate(detsB):
            if j in usedB:
                continue
            dist = pixel_center_distance(boxA, boxB, dw, dh)
            if dist < best_dist:
                best_dist = dist
                best_idx = j
        matches[i] = best_idx
        if best_idx is not None:
            usedB.add(best_idx)
    return matches
def interpolate_box(boxA, boxB):
    """
    Given box in frame i (boxA) and frame i+2 (boxB),
    return an interpolated box for frame i+1.
    """
    class_id = boxA[0]  # assuming same class
    x_c = (boxA[1] + boxB[1]) / 2.0
    y_c = (boxA[2] + boxB[2]) / 2.0
    w = (boxA[3] + boxB[3]) / 2.0
    h = (boxA[4] + boxB[4]) / 2.0
    return (class_id, x_c, y_c, w, h)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--label_folder', type=str, required=True,help='Path to folder containing YOLO label files.')
    parser.add_argument('--output_folder', type=str, required=True,help='Output directory for interpolated YOLO label files.')
    args = parser.parse_args()
    label_folder = args.label_folder
    output_folder = args.output_folder
    
    label_files = []
    output_files = []
    for file in sorted(os.listdir(label_folder)):
        if file.endswith(".txt"):
            file_path = os.path.join(label_folder, file)
            output_file_path = os.path.join(output_folder, file)
            label_files.append(file_path)
            output_files.append(output_file_path)
    print(label_files[:10])
    print(output_files[:10])


    all_detections = [read_yolo_file_as_strings(f) for f in sorted(label_files)]
    print(all_detections[:10])

number_changed_files= 0
for i in range(0,len(all_detections)-2):
    # Count of detections in frames i, i+1, i+2
    n_i   = len(all_detections[i])
    n_i1  = len(all_detections[i+1])
    n_i2  = len(all_detections[i+2])
    print(f"Frame {i}: {n_i} detections")
    print(f"Frame {i+1}: {n_i1} detections")
    print(f"Frame {i+2}: {n_i2} detections")
    # Check if there's a dip in frame (i+1)
    if n_i == n_i2 > n_i1:
       
        if n_i == n_i2:
            # match bounding boxes in frame i and i+2
            print("all_detections[i]",all_detections[i])
            matches = match_bounding_boxes_pixel(all_detections[i], all_detections[i+2],1280,1024)
            print("matches",matches)
            # Identify which boxes might be missing in frame i+1.
            # if frame i+1 has fewer boxes, see which ones from frame i
            # have no close match in frame i+1.
            
            # Build a match from i->(i+1):
            if len(all_detections[i+1]) > 0:
                match_i_i1 = match_bounding_boxes_pixel(all_detections[i], all_detections[i+1],1280,1024)
                print(f"match_i_i1: {match_i_i1}")
                
            else:
                match_i_i1 = {}
            
            for idxA, idxB in matches.items():
                # bounding box i
                boxA = all_detections[i][idxA]
                # bounding box i+2
                boxB = all_detections[i+2][idxB]
                
                # Check if boxA is matched to something in i+1
                if idxA not in match_i_i1:
                    # This means we didn't find a match in i+1 -> likely missing
                    # Interpolate
                    interpolated_box = interpolate_box(boxA, boxB)
                    print(f"Interpolated box: {interpolated_box} for frame {i+1}")
                    print(f"will be written to {output_files[i+1]}")
                    
                    # Insert into frame i+1
                    len_before = len(all_detections[i+1])
                    all_detections[i+1].append(interpolated_box)
                    len_after = len(all_detections[i+1])
                    print(f" len Before: {len_before}, After: {len_after}")
   
    # sort ?

# write back the updated YOLO files
for idx, file_path in enumerate(output_files,start=0):
    if idx == 0:
        print(f"file {file_path} idx 0")
    write_yolo_file(file_path, all_detections[idx])


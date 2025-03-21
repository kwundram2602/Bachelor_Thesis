import os
import glob
import math
import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment


"""
interpolation script
contains matching functions
"""
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
def pixel_distance_matrix(detsA, detsB, dw, dh):
    """
    Build cost matrix for Hungarian algorithm:
    cost_matrix[i,j] = distance between detsA[i] and detsB[j].
    """
    nA, nB = len(detsA), len(detsB)
    cost = np.zeros((nA, nB), dtype=np.float32)
    for i, boxA in enumerate(detsA):
        for j, boxB in enumerate(detsB):
            cost[i, j] = pixel_center_distance(boxA, boxB, dw, dh)
    return cost
def pixel_distance_matrix_one_frame(dets, dw, dh):
    """
    Computes distances for all pairs of bounding boxes in a single frame.
    """
    ndet = len(dets)
    distances = np.zeros((ndet, ndet), dtype=np.float32)
    for i, boxA in enumerate(dets):
        for j, boxB in enumerate(dets):
            distances[i, j] = pixel_center_distance(boxA, boxB, dw, dh)
    return distances
def match_bounding_boxes_hungarian(detsA, detsB, dw, dh, max_dist=None):
    """
    Match bounding boxes using the Hungarian algorithm.
    If max_dist is set, any pair above that distance is left unmatched.
    Returns dict: index_in_A -> index_in_B (or None if unmatched).
    """
    nA, nB = len(detsA), len(detsB)
    if nA == 0 or nB == 0:
        return {}
    
    cost = pixel_distance_matrix(detsA, detsB, dw, dh)
    # returns the indices of the optimal assignment
    row_ind, col_ind = linear_sum_assignment(cost)  
    
    # Build the assignment
    # first dets in detsA dont have a match
    matches = {i: None for i in range(nA)}
    # rows and columns are matched
    for i, r in enumerate(row_ind):
        c = col_ind[i]
        dist_ij = cost[r, c]
        if max_dist is not None and dist_ij > max_dist:
            print(f"Distance {dist_ij} exceeds max_dist {max_dist} for {detsA[r]} and {detsB[c]}")
            continue
        # row r is matched to column c
        matches[r] = c
    # Remove unmatched entries
    matches = {k: v for k, v in matches.items() if v is not None}
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

def compute_bb_area(box, dw, dh):
    """
    Compute the area of a bounding box in pixels.
    """
    _, x, y, w, h = box
    l, r, t, b = yolo_to_image_coordinates(x, y, w, h, dw, dh)
    return (r - l) * (b - t)
def get_non_zero_min(ndarray):
    """
    Returns the minimum value of a numpy array that is not zero.
    """
    ndarray_mod = np.where(ndarray == 0, np.inf, ndarray)

    # Get the index of the minimum value
    min_index = np.argmin(ndarray_mod)
    i, j = np.unravel_index(min_index, ndarray.shape)
    i = int(i)
    j = int(j)
    return i, j
def check_overlap(boxA, boxB, dw, dh):
    l1, r1, t1, b1 = yolo_to_image_coordinates(boxA[1], boxA[2], boxA[3], boxA[4], dw, dh)
    l2, r2, t2, b2 = yolo_to_image_coordinates(boxB[1], boxB[2], boxB[3], boxB[4], dw, dh)
    
    inter_left = max(l1, l2)
    inter_right = min(r1, r2)
    inter_top = max(t1, t2)
    inter_bottom = min(b1, b2)
    
    inter_width = max(0, inter_right - inter_left)
    inter_height = max(0, inter_bottom - inter_top)
    inter_area = inter_width * inter_height
    
    box1_area = (r1 - l1) * (b1 - t1)
    box2_area = (r2 - l2) * (b2 - t2)
    
    union_area = box1_area + box2_area - inter_area
    overlap = inter_area / union_area if union_area > 0 else 0
    
    return overlap

def plot_yolo_line(det,image_path,output_path):
    img = cv2.imread(image_path)
    dh, dw, _ = img.shape
    _, x, y, w, h = det
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

    cv2.rectangle(img, (l, t), (r, b), (0, 0, 255), 1)

    cv2.imwrite(output_path, img)
    #plt.imshow(img)
    #plt.tight_layout()
    #plt.savefig(output_path)
    
def plot_bbox_to_image(image_path:str,label_path:str,output_path:str):
    """
    Plots bounding box from coordinates in label file to image using opencv and matplotlib.
    YOLO format gives x and y center of bounding box and width and height

    :param image_path: Path to image.
    :param label_path: Path to label text file.
    """
    
    img = cv2.imread(image_path)
    dh, dw, _ = img.shape

    fl = open(label_path, 'r')
    data = fl.readlines()
    fl.close()

    for dt in data:

        # Split string to float
        _, x, y, w, h = map(float, dt.split(' '))

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

        cv2.rectangle(img, (l, t), (r, b), (0, 0, 255), 1)

    plt.imshow(img)
    plt.tight_layout()
    plt.savefig(output_path)
    
def plot_removed_boxes(label_file,removed_bbox,png_dir):
    filename = os.path.basename(label_file)
    image = filename.replace(".txt",".png")
    image_path = os.path.join(png_dir,image)
    output=os.path.join(png_dir,"deleted_bbox",image.replace(".png","bbox_removed.png"))
    plot_yolo_line(removed_bbox,image_path,output)

def remove_sixth_det(detections,labels,pngs_dir,dw,dh):
    """
    """
    for i,frame_det in enumerate(detections):
        while len(frame_det) > 5:
            distances = pixel_distance_matrix_one_frame(frame_det, dw, dh)
            # Find the pair with the smallest distance
            z, j = get_non_zero_min(distances)
            # Remove the box with the smaller area
            if compute_bb_area(frame_det[z], dw, dh) < compute_bb_area(frame_det[j], dw, dh):
                plot_removed_boxes(labels[i],frame_det[z],pngs_dir)
                print(f"Removed box {frame_det[z]}")
                frame_det.pop(z)
                
            else:
                plot_removed_boxes(labels[i],frame_det[j],pngs_dir)
                print(f"Removed box {frame_det[j]}")
                frame_det.pop(j)
                
            detections[i] = frame_det
            print(f"Removed box from frame {i+1} [{labels[i]}]")
            
    return detections
                    
def filter_by_aoi(aoi,detections,label_files,dw,dh,png_dir):
    """
    Filter detections by Area of Interest
    aoi: tuple (x_min, y_min, x_max, y_max)
    detections: list of list of detections
    dw, dh: image dimensions
    image_path: path to image for visualization
    output_path: path to show the bounding box outside the aoi
    """
    x_min, y_min, x_max, y_max = aoi
    print(f"x_min, y_min, x_max, y_max in filter_by_aoi: {x_min, y_min, x_max, y_max}")
    filtered_detections = []
    for i,frame_det in enumerate(detections):
        
        if len(frame_det) < 6:
            filtered_detections.append(frame_det)
            continue
        fitered_frame_det = []
        for det in frame_det:
            _, x, y, w, h = det
            l, r, t, b = yolo_to_image_coordinates(x, y, w, h, dw, dh)
            center_x = (l + r) / 2
            center_y = (t + b) / 2
            # center of bounding box is inside the aoi
            if x_min <= center_x <= x_max and y_min <= center_y <= y_max:
                print(f"det  center_x, center_y :{center_x, center_y} is inside aoi {aoi}")
                fitered_frame_det.append(det)
            # center of bounding box is outside the aoi
            else:
                label_file = label_files[i]
                filename = os.path.basename(label_file)
                image = filename.replace(".txt",".png")
                image_path = os.path.join(png_dir,image)
                print("image path:", image_path)
                im0 = cv2.imread(image_path)
                
                output=os.path.join(png_dir,"aoi_filtered",image.replace(".png","aoi_filtered.png"))
                # plot filtered bounding box to image for checking
                plot_yolo_line(det,image_path,output)
                im0=cv2.imread(output)
                if im0 is None:
                    raise ValueError("Image not found or unable to load image from path: " + output)
                im1=cv2.rectangle(im0, (x_min, y_min), (x_max, y_max), (0, 0, 255), thickness=4)
                cv2.imwrite(output, im1)
                
        filtered_detections.append(fitered_frame_det)
    return filtered_detections      
            
        
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--label_folder', type=str, required=True,help='Path to folder containing YOLO label files.')
    parser.add_argument('--output_folder', type=str, required=True,help='Output directory for interpolated YOLO label files.')
    parser.add_argument('--pngs_dir', type=str, required=True,help='Path to folder containing images.')
    parser.add_argument('--aoi', nargs='+', type=int,action='append', help='Area of Interest in [x_min, y_min, x_max, y_max] format')
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


    all_detections = [read_yolo_file(f) for f in sorted(label_files)]
    print(all_detections[:10])
    aoi = args.aoi[0]
    print(f"aoi: {aoi}")
    pngs_dir = args.pngs_dir
    print(f"length before aoi : {len(all_detections)}")
    filtered_detections = filter_by_aoi(aoi,all_detections,sorted(label_files),1280,1024,pngs_dir)
    
    # Remove the sixth detection if it exists
    print(f"length before remove sixth : {len(filtered_detections)}")
    all_detections = remove_sixth_det(filtered_detections,sorted(label_files),pngs_dir,1280,1024)
    print(f"length after remove sixth : {len(all_detections)}")
    number_changed_files= 0
    for i in range(0,len(all_detections)-2):
        # Count of detections in frames i, i+1, i+2
        n_i   = len(all_detections[i])
        n_i1  = len(all_detections[i+1])
        n_i2  = len(all_detections[i+2])
        print(f"Frame {i}: {n_i} detections")
        if n_i == 6:
            print(f"six detections in i = {i} : {all_detections[i]}")
        # Check if there's a dip in frame (i+1)
        if n_i == n_i2 > n_i1 and n_i < 6:
        
            if n_i == n_i2:
                # match bounding boxes in frame i and i+2
                print("all_detections[i]",all_detections[i])
                #matches = match_bounding_boxes_pixel(all_detections[i], all_detections[i+2],1280,1024)
                matches = match_bounding_boxes_hungarian(all_detections[i], all_detections[i+2], dw=1280, dh=1024)       
                print("matches",matches)
                # Identify which boxes might be missing in frame i+1.
                # if frame i+1 has fewer boxes, see which ones from frame i
                # have no close match in frame i+1.
                
                # Build a match from i->(i+1):
                if len(all_detections[i+1]) > 0:
                    match_i_i1 = match_bounding_boxes_hungarian(all_detections[i], all_detections[i+1],1280,1024)
                    
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
                        number_changed_files += 1
                        print(f"Interpolated box: {interpolated_box} for frame {i+2}")
                        print(f"will be written to {output_files[i+1]}")
                        
                        # Insert into frame i+1
                        len_before = len(all_detections[i+1])
                        all_detections[i+1].append(interpolated_box)
                        len_after = len(all_detections[i+1])
                        print(f" len Before: {len_before}, After: {len_after}")
    
        # sort ?
    print("Number of changed files: ",number_changed_files)
    # write back the updated YOLO files
    for idx, file_path in enumerate(output_files,start=0):
        if idx == 0:
            print(f"file {file_path} idx 0")
        write_yolo_file(file_path, all_detections[idx])


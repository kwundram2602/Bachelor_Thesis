import argparse
import json
import cv2
import matplotlib.pyplot as plt
import os



def plot_labelbox_bbox(bbox,image_path,output_path,save:bool=True):
    
    left = int(bbox["left"])
    top = int(bbox["top"])
    width = int(bbox["width"])
    height = int(bbox["height"])
    
    right=left+width
    bottom=top+height
    img = cv2.imread(image_path)
    cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 1)
    if save:
        cv2.imwrite(output_path, img)
    else:
        plt.imshow(img)
        plt.show()
    
def bbox_to_yolo(bbox,image_width,image_height):
    left = int(bbox["left"])
    top = int(bbox["top"])
    w = int(bbox["width"])
    h = int(bbox["height"])
    
    x_c = left + w / 2
    y_c = top + h / 2
    x_c /= image_width
    y_c /= image_height
    w /= image_width
    h /= image_height
    return x_c, y_c, w, h

def write_labelfile(label_class,xc,yc,dw,dh,output_path):
    
    try:
        with open(output_path, "a") as f: 
            f.write(f"{label_class} {xc:.6f} {yc:.6f} {dw:.6f} {dh:.6f}\n")
        print(f"Label file written successfully to {output_path}")
    except Exception as e:
        print(f"An error occurred while writing the label file: {e}")

def extract_labels(ndjson,project_id,output_folder,pngs):
    with open(ndjson, 'r', encoding='utf-8') as ndjson_file:
        for line_number, line in enumerate(ndjson_file, start=1):
            # Parse die Zeile als JSON
            try:
                json_data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error while parsing line {line_number}: {e}")
                continue
            data_row=json_data.get("data_row", {})
            #print(data_row)
            external_id=data_row.get("external_id")
            project=json_data.get("projects", {})[project_id]
            frame_source_path=os.path.join(pngs,external_id)
            frame_dest_path=os.path.join(output_folder,external_id)
            if os.path.isfile(frame_dest_path):
                print(f"Frame already exists at: {frame_dest_path}")
            else:
                print(f"Copy {frame_source_path} to {frame_dest_path}")
                cmd = f"cp {frame_source_path} {frame_dest_path}"
                os.system(cmd)
            if ("labels" in project and len(project["labels"]) > 0 ):
                objects=project["labels"][0]["annotations"]["objects"]
                label_file = os.path.splitext(external_id)[0]+".txt"
                output_txt=os.path.join(output_folder,label_file)
                for object in objects:
                    bbox=object["bounding_box"]
                    print(bbox)
                    x_c, y_c, w, h = bbox_to_yolo(bbox,1280,1024)
                    write_labelfile(0,x_c, y_c, w, h,output_txt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract labels from ndjson')
    parser.add_argument('--ndjson', type=str, required=True, help='NDJSON file path')
    parser.add_argument('--output_folder', type=str, required=True, help='Output directory for label text files')
    parser.add_argument('--pngs', type=str, required=True, help='folder path with extracted frames')

    args = parser.parse_args()
    ndjson=args.ndjson
    output_folder=args.output_folder
    pngs=args.pngs
    extract_labels(ndjson,"cm3zzwwe5013507xg40mg2ubu",output_folder,pngs)
    
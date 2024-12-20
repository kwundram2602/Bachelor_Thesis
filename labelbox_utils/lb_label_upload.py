import labelbox as lb
import labelbox.types as lb_types
import uuid
from PIL import Image
import requests
import base64
from io import BytesIO
import os
import re
import json
from labelbox import MALPredictionImport
# optional, if you need to install labelbox
# !pip3 install -q labelbox[data]
import labelbox.data.annotation_types as lb_types
import argparse


def initialize_lbbx_client(api_key):
    client = lb.Client(api_key)
    return client

def read_labels(labels_folder:str,dh:int, dw:int):
    """
    Reads Every label .txt file from a given folder.
    Function will return dict with frame ids as keys and arrays containing one or more bbox dimensions as values.
    A bbox dimension contains top,left, bottom, right positions of the bbox. \n
    e.g. : \n   bbox_dm = {
                "top":t,
                "left":l,
                "height":h,
                "width":w
                }

    :param labels_folder: Path to label folder
    :param dh: height of image
    param dh: width of image 
    """
    # all label files in folder
    all_labels ={}
    
    for labeltxt in sorted(os.listdir(labels_folder)):
        match = re.search(r'\d+', labeltxt)  # Find the numeric part
        if match:
            number = int(match.group())  # Convert to an integer, removing leading zeros
            #print(labeltxt,number)
            frame_id= number
        # open label file
        label_file_annos=[]
        with open(os.path.join(labels_folder, labeltxt), 'r') as file:
            # read lines where each line contains one detection
            data=file.readlines()
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
                bbox_dm = {
                "top":t,
                "left":l,
                "height":h*dh,
                "width":w*dw
                }
                label_file_annos.append(bbox_dm)
            #all_labels[f"{frame_id}"].append(label_file_annos)
            all_labels[frame_id]=label_file_annos
        
    
    return all_labels
                
def create_video_bbox_anno(name:str,keyframe:bool,frame_id,top,left,height,width):
    # bbox dim
    bbox_dm = {
    "top":top,
    "left":left,
    "height":height,
    "width":width
    }
    # new annotation
    anno = lb_types.VideoObjectAnnotation(
    name = name,
    keyframe=keyframe,
    frame=frame_id,
    segment_index=0,
    value = lb_types.Rectangle(
          start=lb_types.Point(x=bbox_dm["left"], y=bbox_dm["top"]), # x = left, y = top
          end=lb_types.Point(x=bbox_dm["left"] + bbox_dm["width"], y=bbox_dm["top"] + bbox_dm["height"]), # x= left + width , y = top + height
      )
    )
    return anno

def create_image_bbox_anno(name:str,top,left,height,width):
    # bbox dim
    bbox_dm = {
    "top":top,
    "left":left,
    "height":height,
    "width":width
    }
    # new annotation
    anno = lb_types.ObjectAnnotation(
    name=name,  # must match your ontology feature's name
    value=lb_types.Rectangle(
        start=lb_types.Point(x=bbox_dm["left"], y=bbox_dm["top"]),  # x = left, y = top 
        end=lb_types.Point(x=bbox_dm["left"]+bbox_dm["width"], y=bbox_dm["top"]+bbox_dm["height"]),  # x= left + width , y = top + height
    ))
    return anno
        
def read_global_keys(ndjson):
    """
    Reads Global Keys from ndjson file and returns them as a list.

    :param ndjson: Path to ndjson file
    """
    with open(ndjson, 'r', encoding='utf-8') as ndjson_file:
        global_keys=[]
        for line_number, line in enumerate(ndjson_file, start=1):
            # Parse die Zeile als JSON
            try:
                json_data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error while parsing line {line_number}: {e}")
                continue
            global_key=json_data.get("data_row", {}).get("global_key")
            
            global_keys.append(global_key)
    print(global_keys)
    return global_keys

def upload_labels_job(labels,client,project_id):
    """
    Creates Upload Job to upload labels

    :param labels: label objects
    :param client: labelbox client instance
    """
    # Upload MAL label for this data row in project
    upload_job = MALPredictionImport.create_from_objects(
    client = client,
    project_id = project_id,
    
    name = "mal_job"+str(uuid.uuid4()),
    predictions = labels)
    upload_job.wait_till_done(1,True)
    print("Errors:", upload_job.errors)
    print(f"Status of uploads: {upload_job.statuses}")


def get_all_external_ids_from_ndjson(ndjson):
    """
    Gets all external IDs from an NDJSON file, including duplicates, and returns them as a list.

    :param ndjson: Path to NDJSON file containing data rows with external IDs.
    :return: List of external IDs.
    """
    with open(ndjson, 'r', encoding='utf-8') as ndjson_file:
        external_ids=[]
        for line_number, line in enumerate(ndjson_file, start=1):
            # Parse die Zeile als JSON
            try:
                json_data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error while parsing line {line_number}: {e}")
                continue
            
            read_external_id=json_data.get("data_row", {}).get("external_id")
            if read_external_id is not None:
                external_ids.append(read_external_id)
            else:
                print(f"No 'external_id' found in line {line_number}.")
    return external_ids

def get_unique_external_ids(external_ids:list):
    """
    Takes a list of external IDs and returns it without duplicates.
    Parameters
    
    :param list[str] external_ids: list of External ids
    :return: List of  unique external IDs.
    """
    seen = set()
    unique_ids = []
    for external_id in external_ids:
        if external_id not in seen:
            unique_ids.append(external_id)
            seen.add(external_id)
    return unique_ids
               
def get_global_key_by_external_id(ndjson,external_id):
    with open(ndjson, 'r', encoding='utf-8') as ndjson_file:
        for line_number, line in enumerate(ndjson_file, start=1):
            # Parse die Zeile als JSON
            try:
                json_data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error while parsing line {line_number}: {e}")
                continue
            read_external_id=json_data.get("data_row", {}).get("external_id")
            if external_id==read_external_id:
                global_key=json_data.get("data_row", {}).get("global_key")
                return global_key
            
        return None

def get_datarow_id_by_external_id(ndjson,external_id):
    with open(ndjson, 'r', encoding='utf-8') as ndjson_file:
        for line_number, line in enumerate(ndjson_file, start=1):
            # Parse die Zeile als JSON
            try:
                json_data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error while parsing line {line_number}: {e}")
                continue
            read_external_id=json_data.get("data_row", {}).get("external_id")
            if external_id==read_external_id:
                id=json_data.get("data_row", {}).get("id")
                return id
            
        return None
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--ndjson_path', type=str, required=True, help='path to ndjson. for reading gloabl key and external id')
    parser.add_argument('--label_path', type=str, required=True, help='Label folder path.')
    parser.add_argument('--external_id', type=str, required=True, help='external_id of data row. used to get global_key')

    args = parser.parse_args()
    # client init
    client = initialize_lbbx_client("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHZnanVhMncwcDN4MDcxZmRhdnJieHd4Iiwib3JnYW5pemF0aW9uSWQiOiJjbDN0dGpmd2IwN29jMDc1Yzhubno3YjV4IiwiYXBpS2V5SWQiOiJjbTNzb2dvMzUwMWU5MDd6cWRmNTExNzFkIiwic2VjcmV0IjoiMDRkNjdmODQ3YjExMzRjZDZkYjE2NWJjYWUzNzdkMGIiLCJpYXQiOjE3MzIyNzYwOTgsImV4cCI6MjM2MzQyODA5OH0.n4BU4BITKb84cennBDKZDXBcf2OhF6QcNWbLxyKQlHo")
    label_path=args.label_path
    ndjson_path= args.ndjson_path
    external_id= args.external_id
    #label_path =r"D:\Bachelorarbeit\test_labels"
    # read labels from folder and return dict
    labels_from_txt = read_labels(label_path,1024,1280)
    #print(labels)
    #print("labels_from_txt\n")
    #print(labels_from_txt)
    annotation_list=[]
    # get global key
    global_key = get_global_key_by_external_id(ndjson_path,external_id)
    # for every frame ...
    for key in labels_from_txt:
        # ...iterate over bboxes...
        for bbox in labels_from_txt[key]:
            #print(bbox)
            # ...and create bbxo annotation 
            bbox_anno=create_image_bbox_anno("zebrafish",bbox["top"],bbox["left"],bbox["height"],bbox["width"])
            annotation_list.append(bbox_anno)     
            
        
    #print("annotation list: \n")
    #print(annotation_list)
    labels=[]
    #global_keys = read_global_keys("D:\Bachelorarbeit\global_keytest.ndjson")
    
    #for annotation in annotation_list:
    labels.append(
        lb_types.Label(
            data= {"global_key": global_key},
            annotations = annotation_list,
            # Optional: set the label as a benchmark
            # Only supported for groud truth imports
            is_benchmark_reference = False
        )
    )
    upload_labels_job(labels,client)
    #print("labels:\n")   
    #print(labels)


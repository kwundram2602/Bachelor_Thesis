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
from lbox.exceptions import ResourceNotFoundError,LabelboxError
# optional, if you need to install labelbox
# !pip3 install -q labelbox[data]
import labelbox.data.annotation_types as lb_types
import argparse
import logging
from lb_label_upload import ( initialize_lbbx_client ,upload_labels_job,
                             read_global_keys,get_datarow_id_by_external_id, get_global_key_by_external_id, get_all_external_ids_from_ndjson, get_unique_external_ids)

"""
script for uploading image labels to labelbox
"""
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
def read_labels(labels_folder:str,dh:int, dw:int):
    """
    Reads Every label .txt file from a given folder.
    Function will return dict with external ids as keys and arrays containing one or more bbox dimensions as values.
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
        external_id = os.path.splitext(labeltxt)[0]+".png"
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
            all_labels[external_id]=label_file_annos
    return all_labels                   
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--ndjson_path', type=str, required=True, help='path to ndjson. for reading gloabl key and external id')
    parser.add_argument('--label_path', type=str, required=True, help='Label folder path.')

    args = parser.parse_args()
    logging.basicConfig(level = logging.INFO,format='%(asctime)s - %(levelname)s: %(message)s',datefmt='%H:%M:%S')

    # client init
    client = initialize_lbbx_client("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHZnanVhMncwcDN4MDcxZmRhdnJieHd4Iiwib3JnYW5pemF0aW9uSWQiOiJjbDN0dGpmd2IwN29jMDc1Yzhubno3YjV4IiwiYXBpS2V5SWQiOiJjbTNzb2dvMzUwMWU5MDd6cWRmNTExNzFkIiwic2VjcmV0IjoiMDRkNjdmODQ3YjExMzRjZDZkYjE2NWJjYWUzNzdkMGIiLCJpYXQiOjE3MzIyNzYwOTgsImV4cCI6MjM2MzQyODA5OH0.n4BU4BITKb84cennBDKZDXBcf2OhF6QcNWbLxyKQlHo")
    label_path=args.label_path
    ndjson_path= args.ndjson_path
    #label_path =r"D:\Bachelorarbeit\test_labels"
    # read labels from folder and return dict
    labels_from_txt = read_labels(label_path,1024,1280)
    
    
    for external_id in labels_from_txt:
        print(external_id)
        label = []
        annotation_list=[]
        
        global_key = get_global_key_by_external_id(ndjson_path,external_id)
        #did=get_datarow_id_by_external_id(ndjson_path,external_id)
        #print(did)
        if global_key is None:
            logging.error(f"Could not get global key for {external_id}")
            continue
        
        logging.info(f" Global Key {global_key}")
        try:
            for bbox in labels_from_txt[external_id]:
                anno=create_image_bbox_anno("zebrafish",bbox["top"],bbox["left"],bbox["height"],bbox["width"])
                annotation_list.append(anno)
        except Exception as e:
            logging.error(e)
            continue
        
        if len(annotation_list) > 0:
            label.append(
            lb_types.Label(data={"global_key" : global_key
                                },
                        annotations=annotation_list))
            print("label",label)
        else:
            logging.info(f"No annotations for {external_id}")
            continue
        try:
            upload_labels_job(label,client,"cm3zzwwe5013507xg40mg2ubu")
        except LabelboxError as e:
            logging.error(e)



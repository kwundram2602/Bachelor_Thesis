import labelbox as lb
import labelbox.types as lb_types
import uuid
from PIL import Image
import requests
import base64
import argparse
import os 
from lbox.exceptions import ResourceNotFoundError,LabelboxError
import json
from lb_label_upload import get_datarow_id_by_external_id
import logging
import random
import itertools

def load_ndjson(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]

def check_if_id_exists(external_id,dataset):
    #id=get_datarow_id_by_external_id(ndjson,external_id)
    try:
        # returns data row
        datarow= dataset.data_row_for_external_id(external_id)
        return 1
        #id = data_row.id
    except ResourceNotFoundError as e:
        logging.info(e)
        #logging.error(external_id+" \n no DataRow in this DataSet with the given external ID, or there are multiple DataRows for it")
        return 0
    
def create_image_dic(file_url,global_key,external_id):
    dic ={
        "row_data": file_url,
        "global_key": global_key,
        "external_id":external_id
        }
    return dic
    
def upload_image_dict_list(dict_list,dataset,file_upload_thread_count):
    # create the data row with a global key
    types = {type(item).__name__ for item in dict_list}
    logging.info("data types in dictionary:")
    logging.info(types)
    task = dataset.create_data_rows(dict_list,file_upload_thread_count)
    
    task.wait_till_done()
    
def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--images_folder', type=str, required=True, help='images folder path')
    #parser.add_argument('--ndjson', type=str, required=True, help='ndjson path')
    parser.add_argument('--slice_size', type=int, required=True, help='upload batch size')

    args = parser.parse_args()
    images_folder=args.images_folder
    # client init
    logging.basicConfig(level = logging.INFO,format='%(asctime)s - %(levelname)s: %(message)s',datefmt='%H:%M:%S')
    client = lb.Client("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHZnanVhMncwcDN4MDcxZmRhdnJieHd4Iiwib3JnYW5pemF0aW9uSWQiOiJjbDN0dGpmd2IwN29jMDc1Yzhubno3YjV4IiwiYXBpS2V5SWQiOiJjbTNzb2dvMzUwMWU5MDd6cWRmNTExNzFkIiwic2VjcmV0IjoiMDRkNjdmODQ3YjExMzRjZDZkYjE2NWJjYWUzNzdkMGIiLCJpYXQiOjE3MzIyNzYwOTgsImV4cCI6MjM2MzQyODA5OH0.n4BU4BITKb84cennBDKZDXBcf2OhF6QcNWbLxyKQlHo")
    
    # upload to this dataset
    dataset = client.get_dataset("cm3h8xqz9000b0758oacx744d")
    # for checking if external id exists already
    #ndjson=args.ndjson
    #dataset.data_row_for_external_id()# !!!!
    images= os.listdir(images_folder)
    random.shuffle(images)
    
    
    # take some images
    slice_size=args.slice_size
    #images_slice=list(itertools.islice(images,slice_size))
    chunk_list=split_list(images,slice_size)
    for list in chunk_list:
        image_dicts= []
        #print(images_slice)
        for image in list:
            # file name is external_id
            try:
                external_id =image
                # if exists = 1
                exists = check_if_id_exists(external_id,dataset)
                if exists == 1:
                    continue
                else:
                    image_path=os.path.join(images_folder,image)
                    #print(f"Processing {image} ...")
                    # create dictionary
                    global_key = str(uuid.uuid4())
                    # upload file
                    file_url = client.upload_file(image_path)
                    #image dict
                    dict= create_image_dic(file_url,global_key,external_id)
                    image_dicts.append(dict)
            except LabelboxError as e:
                logging.error(e)
                logging.info(f"Could not upload {image}")
                continue
        
        
        file_upload_thread_count=50
        try:
            if len(image_dicts) > 0:
                upload_size = len(image_dicts)
                logging.info(f"Upload size : {upload_size} ")
                logging.info("Starting upload of dictionaries ... \n")
                upload_image_dict_list(image_dicts,dataset,file_upload_thread_count)
            else:
                logging.info("image_dicts empty. Continue with next slice")
                continue
        except LabelboxError as e:
            logging.error(e)
            logging.info( f"{image_dicts} were not uploaded")
            continue
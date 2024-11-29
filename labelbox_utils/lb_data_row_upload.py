import labelbox as lb
import labelbox.types as lb_types
import uuid
from PIL import Image
import requests
import base64
import argparse
import os 
from lbox.exceptions import ResourceNotFoundError
import json
from lb_bbox_upload import get_datarow_id_by_external_id
import logging
import random

def load_ndjson(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]


    
def check_if_id_exists(client,external_id,ndjson):
    id=get_datarow_id_by_external_id(ndjson,external_id)
    if id == None:
        logging.info(f"external_id {external_id} does not exist already")
        return 0
    try:
        data_row = client.get_data_row(id)
        # external id exists already
        return 1
    except ResourceNotFoundError as e:
        logging.error(e)
        logging.error(f"external_id {external_id}")
        # external id doesnt exist yet
        return 0
    
def upload_image(file_path,client,dataset,external_id,ndjson):
    # upload the file to Labelbox storage
    exists = check_if_id_exists(client,external_id,ndjson)
    if exists == 1:
        logging.info(f"external_id {external_id} exists already")
        return
    else:  
        file_url = client.upload_file(file_path)
        global_key = str(uuid.uuid4())
        # create the data row with a global key
        task = dataset.create_data_rows([{
        "row_data": file_url,
        "global_key": global_key,
        "external_id":external_id
        }])
        logging.info(f"Processing {file_path} ...\n")
        task.wait_till_done()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--images_folder', type=str, required=True, help='images folder path')
    parser.add_argument('--ndjson', type=str, required=True, help='ndjson path')

    args = parser.parse_args()
    images_folder=args.images_folder
    # client init
    logging.basicConfig(level = logging.ERROR)
    client = lb.Client("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHZnanVhMncwcDN4MDcxZmRhdnJieHd4Iiwib3JnYW5pemF0aW9uSWQiOiJjbDN0dGpmd2IwN29jMDc1Yzhubno3YjV4IiwiYXBpS2V5SWQiOiJjbTNzb2dvMzUwMWU5MDd6cWRmNTExNzFkIiwic2VjcmV0IjoiMDRkNjdmODQ3YjExMzRjZDZkYjE2NWJjYWUzNzdkMGIiLCJpYXQiOjE3MzIyNzYwOTgsImV4cCI6MjM2MzQyODA5OH0.n4BU4BITKb84cennBDKZDXBcf2OhF6QcNWbLxyKQlHo")
    
    dataset = client.get_dataset("cm3h8xqz9000b0758oacx744d")
    ndjson=args.ndjson
    
    images= os.listdir(images_folder)
    random.shuffle(images)
    
    for image in images:
        image_path=os.path.join(images_folder,image)
        print(image_path)
        upload_image(image_path,client,dataset,image,ndjson)
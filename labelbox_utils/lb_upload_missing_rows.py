from lb_label_upload import get_all_external_ids_from_ndjson,get_unique_external_ids
from lb_data_row_upload_chunkwise import create_image_dic,upload_image_dict_list,check_if_id_exists,LabelboxError,ResourceNotFoundError
import json
import argparse
import os
import labelbox as lb
import logging
import uuid


"""
script for uploading missing rows to labelbox
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--ndjson_path', type=str, required=True, help='path to ndjson. for reading gloabl key and external id')
    parser.add_argument('--local_files', type=str, required=True, help='path to local files')

    args = parser.parse_args()
    
    ndjson=args.ndjson_path
    local_files=args.local_files
    
    all_external_ids = get_all_external_ids_from_ndjson(ndjson)
    unique_external_ids=get_unique_external_ids(all_external_ids)
    
    local_file_ids = os.listdir(local_files)
    print(len(local_file_ids))
    
    #missing_rows = [id for id in local_file_ids if id not in unique_external_ids]
    missing_rows = list(set(local_file_ids) - set(unique_external_ids))

    print(len(missing_rows))
    
    logging.basicConfig(level = logging.INFO,format='%(asctime)s - %(levelname)s: %(message)s',datefmt='%H:%M:%S')
    client = lb.Client("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHZnanVhMncwcDN4MDcxZmRhdnJieHd4Iiwib3JnYW5pemF0aW9uSWQiOiJjbDN0dGpmd2IwN29jMDc1Yzhubno3YjV4IiwiYXBpS2V5SWQiOiJjbTNzb2dvMzUwMWU5MDd6cWRmNTExNzFkIiwic2VjcmV0IjoiMDRkNjdmODQ3YjExMzRjZDZkYjE2NWJjYWUzNzdkMGIiLCJpYXQiOjE3MzIyNzYwOTgsImV4cCI6MjM2MzQyODA5OH0.n4BU4BITKb84cennBDKZDXBcf2OhF6QcNWbLxyKQlHo")
    
    # upload to this dataset
    dataset = client.get_dataset("cm3h8xqz9000b0758oacx744d")
    image_dicts=[]
    for row in missing_rows:
        try:
            external_id =row
            # if exists = 1
            exists = check_if_id_exists(external_id,dataset)
            if exists == 1:
                continue
            else:
                image_path=os.path.join(local_files,row)
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
            logging.info(f"Could not upload {row}")
            continue
    file_upload_thread_count=50
    try:
        if len(image_dicts) > 0:
            upload_size = len(image_dicts)
            logging.info(f"Upload size : {upload_size} ")
            logging.info("Starting upload of dictionaries ... \n")
            upload_image_dict_list(image_dicts,dataset,file_upload_thread_count)
        else:
            logging.info("image_dicts empty.")
    except LabelboxError as e:
        logging.error(e)
        logging.info( f"{image_dicts} were not uploaded")
        